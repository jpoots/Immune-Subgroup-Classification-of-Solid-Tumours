from ..ml_models.predictions import predict, confidence_intervals
from .. import celery
from ..errors.BadRequest import BadRequest
from ..utils import parse_csv, parse_json, delete_file_on_failure
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np

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
        results: The confidence results as a dict
            "data": {
                [{
                    "sampleID": "TCGA.02.0047.GBM.C4",
                    "confidence": {
                        "upper": 6
                        "lower": 4
                        "median": 5
                        "max": 10
                        "min": 1
                    },
                },]
            }

    Throws:
        BadRequest if invalid JSON data is input
    """
    # extract data from JSON
    data = parse_json(data)

    if not data["interval"]:
        raise BadRequest(body="missing interval")

    # divide features
    features = data["features"]
    sample_ids = data["ids"]
    interval = data["interval"]

    if interval > 100 or interval < 0:
        raise BadRequest(body="invalid interval")

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


@celery.task(throws=(BadRequest,))
def tsne_celery(data):
    """Performs t-SNE analysis on input JSON data
    Args:
        data: The json data dict to processe

    Returns:
        results: The confidence results as a dict
        "data": {
            [{
                "sampleID": "TCGA.02.0047.GBM.C4",
                "tsne": [1,2,3],
            },]
        }

    Throws:
        BadRequest if invalid JSON data is input
    """

    # extract data from JSON
    data = parse_json(data)

    # seperate features
    idx = data["ids"]
    features = data["features"]
    perplexity = data["perplexity"]
    num_dimensions = data["num_dimensions"]

    # check for necessary paras
    if not perplexity:
        raise BadRequest(body="Missing perplexity")

    if not num_dimensions:
        raise BadRequest(body="Missing dimension")

    # check sample length
    if len(idx) < 3:
        raise BadRequest(body="At least 3 samples is required for t-SNE analysis")

    # check for valid perplexity and dimensions
    if (
        perplexity >= len(idx)
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
    tsne = tsne_pipeline.fit_transform(features).tolist()

    # parcel for return
    results = []
    for id, tsne_result in zip(idx, tsne):
        results.append({"sampleID": id, "tsne": tsne_result})

    return results


@celery.task(throws=(BadRequest,), on_failure=delete_file_on_failure)
def analyse(filepath, delimiter, gene_list):
    """Performs a full non-configurable analysis on a csv file and deletes invalid csvs
    Args:
        filepath: The path of the csv file to analyse
        delimiter: the files delimiter
        gene_list: the up to date gene list

    Returns:
        results: The analysis results as a dict

        "data": {
            "invalid": 0,
            "nc": 0,
            "predom": 0,
            "samples": [
            {
                "genes": {
                "ACTL6A_S5": 745.567,
                },
                "sampleID": "TCGA.02.0047.GBM.C4",
                "probs":[0.1,0.1,0.1,0.1,0.1,0.5],
                "prediction: 1,
                "pca": [1,2,3],
                "typeid: "GBM"
                "predomPrediction": Null
                "predomProbs": Null
            },]
        }

    Throws:
        BadRequest if invalid JSON data is input
    """
    # extract data from CSV
    data = parse_csv(filepath, delimiter, gene_list)
    # predict
    predictions, prediction_probs, num_nc, num_predom = predict(data["features"])

    # perform PCA
    if len(predictions) < 3:
        pc = [None] * len(predictions)
    else:
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
        genes = [expression for expression in feature_list]

        predom_prediction = None
        predom_probs = None

        # get the predom data where relevant
        if prediction == 7:
            sorted_probs = np.argsort(prob_list).tolist()
            predom_1_index = sorted_probs[-1]
            predom_2_index = sorted_probs[-2]

            predom_probs = [
                prob_list[predom_1_index],
                prob_list[predom_2_index],
            ]
            predom_prediction = [predom_1_index + 1, predom_2_index + 1]

        # append for sample
        results.append(
            {
                "sampleID": sample_id,
                "genes": genes,
                "prediction": prediction,
                "probs": prob_list,
                "pca": pc_comps,
                "typeid": type_id,
                "predomPrediction": predom_prediction,
                "predomProbs": predom_probs,
            }
        )
    return {
        "samples": results,
        "invalid": data["invalid"],
        "nc": num_nc,
        "predominant": num_predom,
        "geneNames": data["gene_names"],
    }
