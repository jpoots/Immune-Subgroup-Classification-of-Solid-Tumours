from flask import (
    jsonify,
    Blueprint,
)
from .. import celery
from flasgger import swag_from
import os
from ..errors.BadRequest import BadRequest
from celery.exceptions import NotRegistered
from werkzeug.exceptions import NotFound

"""
API endpoints for getting async resylts
"""

# documentation location
DOCUMENTATION_PATH = "../documentation"
get_results = Blueprint("get_results", __name__)


def celery_task_results(task_id):
    task = celery.AsyncResult(task_id)

    if task.status == "SUCCESS":
        result = jsonify({"status": "SUCCESS", "data": task.result})
        status = 200
    elif task.status == "PENDING":
        status = 201
        result = jsonify({"status": "PENDING"})
    else:
        err = task.result
        result = jsonify(
            {
                "error": {
                    "code": err.status_code,
                    "name": err.headers,
                    "description": err.body,
                }
            },
        )
        status = err.status_code
    return result, status


@swag_from(os.path.join(DOCUMENTATION_PATH, "getresults_analyse.yaml"))
@get_results.route("/analyse/<task_id>", methods=["GET"])
def analysis_task_status(task_id):
    """
    Returns:
    A dict including key the sample data, number of invlaid samples.

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
            "pca": [1,2,3]
        },
    }
    """
    try:
        result, status = celery_task_results(task_id)
    except NotRegistered as e:
        raise NotFound("Task not found")

    return result, status


@swag_from(os.path.join(DOCUMENTATION_PATH, "getresults_tsne.yaml"))
@get_results.route("/tsne/<task_id>", methods=["GET"])
def tsne_task_status(task_id):
    try:
        result, status = celery_task_results(task_id)
    except NotRegistered as e:
        raise NotFound("Task not found")

    return result, status


@swag_from(os.path.join(DOCUMENTATION_PATH, "getresults_confidence.yaml"))
@get_results.route("/confidence/<task_id>", methods=["GET"])
def confidence_task_status(task_id):
    try:
        result, status = celery_task_results(task_id)
    except NotRegistered as e:
        raise NotFound("Task not found")

    return result, status
