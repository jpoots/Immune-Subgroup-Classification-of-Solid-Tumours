from flask import (
    request,
    jsonify,
    Blueprint,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from ..utils import parse_csv, parse_json, validate_csv_upload
from werkzeug import exceptions
from ..ml_models.predictions import predict, probability
import uuid
import os
from werkzeug import exceptions
from .celery_tasks import confidence_celery, tsne_celery, analyse
from flasgger import swag_from
from app import limiter
import pandas as pd

"""
The main api endpoints for the system to perform analysis
"""

# file path to documentation
DOCUMENTATION_PATH = "../documentation"
LIMIT_MESSAGE = "Request are limited to 5 per minute"

admin = Blueprint("admin", __name__)

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# the location of the trained model
FILE_LOCATION = os.path.join(current_dir, "gene_list.csv")


@admin.route("/genelist", methods=["GET", "PUT"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "parsesamples.yaml"))
def edit_gene_list():
    if request.method == "GET":
        with open(FILE_LOCATION) as f:
            s = f.read()
    if request.method == "PUT":
        content = request.get_json()["newContent"]
        print(content)
        with open(FILE_LOCATION, "w") as f:
            s = f.write(content)

    return (jsonify(s), 200)
