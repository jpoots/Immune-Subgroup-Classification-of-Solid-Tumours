from flask import json
from werkzeug import exceptions
from . import jwt

"""
error handlers for the app
"""


def handle_http_exception(err):
    """Handles http exceptiosn and returns an appropriate response
    Args:
    err: The error to handle

    Returns:
        An appropriate response object
    """
    response = err.get_response()
    response.data = json.dumps(
        {"error": {"code": err.code, "name": err.name, "description": err.description}}
    )
    response.content_type = "application/json"
    return response


def handle_custom_bad_request(err):
    """Handles the custom bad request error needed by celery
    Args:
    err: The error to handle

    Returns:
        An appropriate response object
    """
    message = err.body
    err = exceptions.BadRequest()

    response = err.get_response()
    response.data = json.dumps(
        {
            "error": {
                "code": err.code,
                "name": err.name,
                "description": message,
            }
        }
    )
    response.content_type = "application/json"
    return response


def handle_generic_exception(err):
    """Handles generic unknown errors
    Args:
    err: The error to handle

    Returns:
        An appropriate response object
    """
    err = exceptions.InternalServerError()
    response = err.get_response()
    response.data = json.dumps(
        {"error": {"code": err.code, "name": err.name, "description": err.description}}
    )
    response.content_type = "application/json"
    return response


@jwt.invalid_token_loader
@jwt.unauthorized_loader
def missing_invalid_token_callback(reason):
    err = exceptions.Unauthorized()
    response = err.get_response()
    response.data = json.dumps(
        {"error": {"code": err.code, "name": err.name, "description": err.description}}
    )
    response.content_type = "application/json"
    return response


@jwt.expired_token_loader
def expired_token_callback(header, payload):
    err = exceptions.Unauthorized("Token timed out")
    response = err.get_response()
    response.data = json.dumps(
        {"error": {"code": err.code, "name": err.name, "description": err.description}}
    )
    response.content_type = "application/json"
    return response
