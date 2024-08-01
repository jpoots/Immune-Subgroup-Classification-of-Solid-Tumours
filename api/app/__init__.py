from flask import Flask
from flask_cors import CORS
from werkzeug import exceptions
from .handlers import (
    handle_http_exception,
    handle_generic_exception,
)
from celery import Celery
from flasgger import Swagger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

"""
instantiates an instance of the flask app
"""

load_dotenv()
PORT = os.getenv("PORT")
REDIS_URL = os.getenv("REDIS_URL")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE"))
RESULTS_TIMEOUT = os.getenv("RESULTS_TIMEOUT")

# https://blog.miguelgrinberg.com/post/celery-and-the-flask-application-factory-pattern I used the code from here to add celery to a factory pattern application
celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

# rate limiting for the api, add a default limit in prod
limiter = Limiter(
    get_remote_address,
    storage_uri=REDIS_URL,
    default_limits=[None],
)


def create_app():
    """Creates an app object

    Returns:
        An app object
    """
    # set up app and cross origin
    app = Flask(__name__)
    CORS(app)
    limiter.init_app(app)
    # there are issues running this on a development server (see flask docs) but the file size limit should work properly on WSGI serve
    app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE * 1024 * 1024

    # set up swagger
    Swagger(
        app,
        template={
            "info": {
                "title": "ICST",
                "version": "1.0",
                "description": f"API endpoints for ICST which can be found at http://localhost:{PORT}. All requests are limited t0 {MAX_FILE_SIZE}MB",
            }
        },
    )

    # register routes
    from .views.main import main
    from .views.get_results import get_results

    app.register_blueprint(main, url_prefix="/")
    app.register_blueprint(get_results, url_prefix="/getresults")

    celery.conf.update(app.config)

    # Set result_expires to 1 hours
    celery.conf.result_expires = RESULTS_TIMEOUT

    # register error handlers
    app.register_error_handler(exceptions.HTTPException, handle_http_exception)
    # app.register_error_handler(Exception, handle_generic_exception)
    return app
