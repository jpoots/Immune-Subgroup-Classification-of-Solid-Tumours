from ..ml_models.predictions import predict, confidence_intervals, probability
from .. import celery
from ..errors.BadRequest import BadRequest
from ..utils import parse_csv, parse_json
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import os

PCA_PIPE = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])


def delete_file_on_return(self, status, retval, task_id, args, kwargs, einfo):
    """
    Takes args from a celery task given a file name as input and deletes the file on return.

    Args:
    See the celery on_return documentation
    """
    os.remove(args[0])
    return


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
    data = parse_json(data)

    features = data["features"]
    sample_ids = data["ids"]
    interval = data["interval"]

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
    data = parse_json(data)

    idx = data["ids"]
    features = data["features"]
    perplexity = data["perplexity"]

    tsne_pipeline = Pipeline(
        steps=[
            ("scaler", MinMaxScaler()),
            ("dr", TSNE(n_components=3, perplexity=perplexity)),
        ]
    )

    results = []
    tsne = tsne_pipeline.fit_transform(features).tolist()
    for id, tsne_result in zip(idx, tsne):
        results.append({"sampleID": id, "tsne": tsne_result})

    return results


@celery.task(throws=(BadRequest,), after_return=delete_file_on_return)
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
    data = parse_csv(filepath, delimiter)
    predictions, prediction_probs, num_nc = predict(data["features"])
    pc = PCA_PIPE.fit_transform(data["features"]).tolist()

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
        print(feature_list)
        print(data["gene_names"])
        genes = {
            gene_name: expression
            for gene_name, expression in zip(data["gene_names"], feature_list)
        }

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
