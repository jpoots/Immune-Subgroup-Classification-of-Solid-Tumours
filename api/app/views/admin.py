from flask import (
    request,
    jsonify,
    Blueprint,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from .. import utils
from werkzeug import exceptions
from ..ml_models.predictions import predict, probability
import uuid
import os
from werkzeug import exceptions
from .celery_tasks import confidence_celery, tsne_celery, analyse
from flasgger import swag_from
from app import limiter
import pandas as pd
import time

"""
The main api endpoints for the system to perform analysis
"""

# file path to documentation
DOCUMENTATION_PATH = "../documentation"

admin = Blueprint("admin", __name__)


@admin.route("/genelist", methods=["GET", "PUT"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "parsesamples.yaml"))
def edit_gene_list():
    if request.method == "GET":
        return jsonify({"results": utils.gene_list_csv.columns.tolist()})
    if request.method == "PUT":
        request_json = request.get_json()

        if "geneList" not in request_json:
            raise exceptions.BadRequest("missing gene list")

        new_gene_list = request_json["geneList"]
        try:
            with open(utils.GENE_LIST_FILE_LOCATION, "w") as f:
                f.write(new_gene_list)
            time.sleep(0.1)
            utils.reload_gene_list()
        except Exception as e:
            raise exceptions.BadRequest("Error writing to file")
        return jsonify({"done": "done"})
