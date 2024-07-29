from flask import json
from werkzeug import exceptions


def handle_http_exception(err):
    response = err.get_response()
    response.data = json.dumps(
        {"error": {"code": err.code, "name": err.name, "description": err.description}}
    )
    response.content_type = "application/json"
    return response


def handle_generic_exception(err):
    err = exceptions.InternalServerError()
    response = err.get_response()
    response.data = json.dumps(
        {"error": {"code": err.code, "name": err.name, "description": err.description}}
    )
    response.content_type = "application/json"
    return response
