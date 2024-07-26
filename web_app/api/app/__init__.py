from flask import Flask
import joblib
from flask_cors import CORS
from werkzeug import exceptions
from .error_handling import handle_http_exception, handle_generic_exception
from celery import Celery

# https://blog.miguelgrinberg.com/post/celery-and-the-flask-application-factory-pattern
celery = Celery(
    __name__, broker="redis://localhost:6379", backend="redis://localhost:6379"
)


def create_app():
    # set up app and cross origin
    app = Flask(__name__)
    CORS(app)

    # register routes
    from .views import views

    app.register_blueprint(views, url_prefix="/")

    celery.conf.update(app.config)

    # Set result_expires to 1 hours
    celery.conf.result_expires = 36000

    # register error handlers
    app.register_error_handler(exceptions.HTTPException, handle_http_exception)
    # app.register_error_handler(Exception, handle_generic_exception)
    return app
