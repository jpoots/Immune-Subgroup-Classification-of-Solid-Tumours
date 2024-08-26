from flask import (
    jsonify,
    Blueprint,
)
from .. import celery
from flasgger import swag_from
import os

"""
API endpoints for getting async results. While these could be combined into one route, for seperation of concerns they are best divided
"""

# documentation location
DOCUMENTATION_PATH = "../documentation"
results = Blueprint("results", __name__)


def celery_task_results(task_id):
    """Handles http exceptions and returns an appropriate response
    Args:
        task_id: The id of the task to check

    Returns:
        The result of the task and the status.
    """
    task = celery.AsyncResult(task_id)

    if task.status == "SUCCESS":
        result = jsonify({"data": task.result})
        status = 200
    elif task.status == "PENDING":
        status = 201
        result = jsonify({"status": "PENDING"})
    else:
        err = task.result
        raise err

    return result, status


@swag_from(os.path.join(DOCUMENTATION_PATH, "results_analyse.yaml"))
@results.route("/analyse/<task_id>", methods=["GET"])
def analysis_task_status(task_id):
    """Returns the task status or results for the analyse task
    Args:
        task_id: The id of the task to check

    Returns:
        tuple: A tuple containing
            - results: A response including key the sample data, number of invalid samples and key analysis insights or an appropriate eror.
            "data": {
                "invalid": 0,
                "geneNames": ["abc", "def"],
                "predominant": 0,
                "invalid": 0
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
                ]
            }
            - status: status of results
    """
    result, status = celery_task_results(task_id)
    return result, status


@swag_from(os.path.join(DOCUMENTATION_PATH, "results_tsne.yaml"))
@results.route("/tsne/<task_id>", methods=["GET"])
def tsne_task_status(task_id):
    """Returns the task status for the tsne task
    Args:
        task_id: The id of the task to check

    Returns:
        tuple: a tuple containing
            - results: A response including the sample id and tsne results or an appropriate error
                "data": {
                    [{
                        "sampleID": "TCGA.02.0047.GBM.C4",
                        "tsne": [1,2,3],
                    },]
                }
            - status: status of output
    """
    result, status = celery_task_results(task_id)
    return result, status


@swag_from(os.path.join(DOCUMENTATION_PATH, "results_confidence.yaml"))
@results.route("/confidence/<task_id>", methods=["GET"])
def confidence_task_status(task_id):
    """Returns the task status for the confidence task
    Args:
        task_id: The id of the task to check

    Returns:
        tuple: a tuple containing
            - results: A response including the sample id and confidence results or an appropriate error
                "data": {[
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
                ]}
            - status: the status of the task
    """
    result, status = celery_task_results(task_id)
    return result, status
