from flask import json
from werkzeug import exceptions

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
