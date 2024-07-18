from flask import Flask
import joblib
from flask_cors import CORS
from werkzeug import exceptions
from .error_handling import handle_http_exception, handle_generic_exception


def create_app():
    # set up app and cross origin
    app = Flask(__name__)
    CORS(app)

    # register routes
    from .views import views

    app.register_blueprint(views, url_prefix="/")

    # register error handlers
    app.register_error_handler(exceptions.HTTPException, handle_http_exception)
    # app.register_error_handler(Exception, handle_generic_exception)
    return app
