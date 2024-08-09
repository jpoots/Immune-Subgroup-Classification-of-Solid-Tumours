from ..ml_models.predictions import predict, confidence_intervals, probability
from .. import celery
from ..errors.BadRequest import BadRequest
from ..utils import parse_csv, parse_json, delete_file_on_failure
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import os

PCA_PIPE = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])


@celery.task(
    throws=(BadRequest,),
)
def confidence_celery(data):
    """
    Calculates confidence intervals for JSON input samples
    Args:
    data: The json data dict to processe

    Returns:
        The confidence results as a dict
            "data": {
        {
            "sampleID": "TCGA.02.0047.GBM.C4",
            "confidence": {
                "upper": 6
                "lower": 4
                "median": 5
                "max": 10
                "min": 1
            },
        },
    }

    Throws: BadRequest if invalid JSON data is input
    """
    # extract data from JSON
    data = parse_json(data)

    if not data["interval"]:
        raise BadRequest(body="missing interval")

    # divide features
    features = data["features"]
    sample_ids = data["ids"]
    interval = data["interval"]

    # parcel for return
    results = []
    for interval, id in zip(confidence_intervals(features, interval), sample_ids):

        results.append(
            {
                "sampleID": id,
                "min": interval[0],
                "lower": interval[1],
                "median": interval[2],
                "upper": interval[3],
                "max": interval[4],
            }
        )
    return results


@celery.task(
    throws=(BadRequest,),
)
def tsne_celery(data):
    """
    Performs t-SNE analysis on input JSON data
    Args:
    data: The json data dict to processe

    Returns:
        The confidence results as a dict
            "data": {
        {
            "sampleID": "TCGA.02.0047.GBM.C4",
            "tsne": [1,2,3],
        },
    }

    Throws: BadRequest if invalid JSON data is input
    """

    # extract data from JSON
    data = parse_json(data)

    # seperate features
    idx = data["ids"]
    features = data["features"]
    perplexity = data["perplexity"]
    num_dimensions = data["num_dimensions"]

    if (
        perplexity > len(idx)
        or perplexity < 1
        or perplexity > 500
        or num_dimensions < 2
        or num_dimensions > 100
    ):
        raise BadRequest(body="Bad perplexity or number of dimensions.")

    # perform tSNE
    tsne_pipeline = Pipeline(
        steps=[
            ("scaler", MinMaxScaler()),
            ("dr", TSNE(n_components=num_dimensions, perplexity=perplexity)),
        ]
    )

    # parcel for return
    results = []
    tsne = tsne_pipeline.fit_transform(features).tolist()
    for id, tsne_result in zip(idx, tsne):
        results.append({"sampleID": id, "tsne": tsne_result})

    return results


@celery.task(throws=(BadRequest,), on_failure=delete_file_on_failure)
def analyse(filepath, delimiter):
    """
    Performs a full non-configurable analysis on a csv file
    Args:
    filepath: The path of the csv file to analyse
    delimiter: the files delimiter

    Returns:
        The analysis results as a dict

    "data": {
        "invalid": 0,
        "samples": [
        {
            "genes": {
            "ACTL6A_S5": 745.567,
            },
            "sampleID": "TCGA.02.0047.GBM.C4",
            "probs":[0.1,0.1,0.1,0.1,0.1,0.5],
            "prediction: 1,
            "pca": [1,2,3],
            "typeid: "GBM
        },
    }

    Throws: BadRequest if invalid JSON data is input
    """
    # extract data from CSV
    data = parse_csv(filepath, delimiter)

    # predict
    predictions, prediction_probs, num_nc = predict(data["features"])

    # perform PCA
    pc = PCA_PIPE.fit_transform(data["features"]).tolist()

    # parcel for return
    results = []
    for (
        sample_id,
        feature_list,
        prediction,
        prob_list,
        pc_comps,
        type_id,
    ) in zip(
        data["ids"],
        data["features"],
        predictions,
        prediction_probs,
        pc,
        data["type_ids"],
    ):
        # for each gene in sample extract expression
        genes = {
            gene_name: expression
            for gene_name, expression in zip(data["gene_names"], feature_list)
        }

        # append for sample
        results.append(
            {
                "sampleID": sample_id,
                "genes": genes,
                "prediction": prediction,
                "probs": prob_list,
                "pca": pc_comps,
                "typeid": type_id,
            }
        )

    return {"samples": results, "invalid": data["invalid"], "nc": num_nc}
