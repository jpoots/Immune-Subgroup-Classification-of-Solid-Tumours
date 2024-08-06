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
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

"""
creates an instance of the flask app
"""

# load config vars stored in .env
load_dotenv()
PORT = os.getenv("PORT")
REDIS_URL = os.getenv("REDIS_URL")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE"))
RESULTS_TIMEOUT = os.getenv("RESULTS_TIMEOUT")
JWT_ACCESS_EXPIRY = int(os.getenv("JWT_ACCESS_EXPIRY"))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
DATABASE_URI = os.getenv("DATABASE_URI")

# https://blog.miguelgrinberg.com/post/celery-and-the-flask-application-factory-pattern I used the code from here to add celery to a factory pattern application
celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

# rate limiting for the api, add a default limit in prod
limiter = Limiter(
    get_remote_address,
    storage_uri=REDIS_URL,
    default_limits=[None],
)

# start libraries
db = SQLAlchemy()
bcrypt = Bcrypt()
cors = CORS()
jwt = JWTManager()


def create_app():
    """Creates an app object

    Returns:
        An app object
    """
    # set up app and cross origin
    app = Flask(__name__)
    # set up db
    app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE * 1024 * 1024
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWT_ACCESS_EXPIRY

    # init libraries with current app
    cors.init_app(app)
    limiter.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

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
    from .views.admin import admin

    app.register_blueprint(main, url_prefix="/")
    app.register_blueprint(get_results, url_prefix="/getresults")
    app.register_blueprint(admin, url_prefix="/")

    celery.conf.update(app.config)

    # Set result_expires to 1 hours
    celery.conf.result_expires = RESULTS_TIMEOUT

    with app.app_context():
        from . import models

        db.create_all()

    # register error handlers
    app.register_error_handler(exceptions.HTTPException, handle_http_exception)
    # app.register_error_handler(Exception, handle_generic_exception)
    return app
