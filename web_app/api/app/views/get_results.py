from flask import (
    request,
    jsonify,
    Blueprint,
)
from .. import celery
from flasgger import swag_from


get_result = Blueprint("get_result", __name__)


def celery_task_results(task_id):
    task = celery.AsyncResult(task_id)
    status = 200

    if task.status == "SUCCESS":
        result = jsonify({"status": "SUCCESS", "data": task.result})
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


@swag_from("./documentation/getresults_analyse.yaml")
@get_result.route("/analysis/<task_id>", methods=["GET"])
def analysis_task_status(task_id):
    return celery_task_results(task_id)


@swag_from("./documentation/getresults_tsne.yaml")
@get_result.route("/tsne/<task_id>", methods=["GET"])
def tsne_task_status(task_id):
    return celery_task_results(task_id)


@swag_from("./documentation/getresults_confidence.yaml")
@get_result.route("/confidence/<task_id>", methods=["GET"])
def confidence_task_status(task_id):
    return celery_task_results(task_id)
