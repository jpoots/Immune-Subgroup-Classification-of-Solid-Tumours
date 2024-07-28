from flask import Flask
import joblib
from flask_cors import CORS
from werkzeug import exceptions
from .handlers import handle_http_exception, handle_generic_exception
from celery import Celery
from flasgger import Swagger, swag_from, LazyString

# https://blog.miguelgrinberg.com/post/celery-and-the-flask-application-factory-pattern
celery = Celery(
    __name__, broker="redis://localhost:6379", backend="redis://localhost:6379"
)


def create_app():
    # set up app and cross origin
    app = Flask(__name__)
    CORS(app)
    Swagger(
        app,
        template={
            "info": {
                "title": "ICST",
                "version": "1.0",
                "description": "API access for ICST",
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
