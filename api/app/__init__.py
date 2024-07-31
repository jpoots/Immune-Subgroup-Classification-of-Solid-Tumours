from flask import Flask
from flask_cors import CORS
from werkzeug import exceptions
from .handlers import handle_http_exception, handle_generic_exception
from celery import Celery
from flasgger import Swagger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

"""
instantiates an instance of the flask app
"""


# https://blog.miguelgrinberg.com/post/celery-and-the-flask-application-factory-pattern I used the code from here to add celery to a factory pattern application
celery = Celery(
    __name__, broker="redis://localhost:6379", backend="redis://localhost:6379"
)

# rate limiting for the api
limiter = Limiter(
    get_remote_address,
    storage_uri="redis://localhost:6379",
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

    # set up swagger
    Swagger(
        app,
        template={
            "info": {
                "title": "ICST",
                "version": "1.0",
                "description": "API endpoints for ICST which can be found at http://localhost:3000",
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
    celery.conf.result_expires = 36000

    # register error handlers
    app.register_error_handler(exceptions.HTTPException, handle_http_exception)
    # app.register_error_handler(Exception, handle_generic_exception)
    return app
