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
from filelock import FileLock
from ..models import Admin
from .. import db

"""
The main api endpoints for the system to perform analysis
"""

# file path to documentation
DOCUMENTATION_PATH = "../documentation"

admin = Blueprint("admin", __name__)


@admin.route("/authenticate", methods=["POST"])
def authenticate():
    return jsonify({"done": 1})


@admin.route("/admin", methods=["GET", "POST"])
def get_admins():
    if request.method == "GET":
        admins = Admin.query.all()
        json_admin = list(map(lambda x: x.to_json(), admins))
        return jsonify(json_admin), 200
    if request.method == "POST":
        request_json = request.get_json()
        admin_id = request_json["adminID"]
        pass_hash = request_json["passHash"]

        new_admin = Admin(username=admin_id, pass_hash=pass_hash)
        try:
            db.session.add(new_admin)
            db.session.commit()
        except Exception as e:
            return jsonify("ERROR"), 400
    return jsonify("success")


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
        lock = FileLock("file.lock")

        with lock:
            try:
                with open(utils.GENE_LIST_FILE_LOCATION, "w") as f:
                    f.write(new_gene_list)
                time.sleep(0.1)
                utils.reload_gene_list()
            except Exception as e:
                raise exceptions.BadRequest("Error writing to file")
        return jsonify({"done": "done"})
