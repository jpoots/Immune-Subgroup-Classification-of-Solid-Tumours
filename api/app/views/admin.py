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
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
import csv
from secrets import token_urlsafe

"""
Admin API endpoints for setting the gene lists
"""

# file path to documentation
DOCUMENTATION_PATH = "../documentation"

admin = Blueprint("admin", __name__)


@admin.route("/authenticate", methods=["POST"])
def authenticate():
    request_json = request.get_json()
    if "password" not in request_json or "username" not in request_json:
        raise exceptions.BadRequest("Missing credentials")

    # get creds from request
    password = request_json["password"]
    username = request_json["username"]

    # get user
    user = Admin.query.filter_by(username=username).first()

    # validate and return
    if user and user.verify_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token})

    # none found, raise exception
    raise exceptions.Unauthorized()


@admin.route("/admin", methods=["POST"])
@jwt_required()
def admins():
    admin_id = Admin.query.order_by(Admin.id.desc()).first().id + 1
    password = token_urlsafe(16)
    username = f"ICSTADMIN{admin_id}"
    new_admin = Admin(username=username, pass_hash=password)

    db.session.add(new_admin)
    db.session.commit()

    return jsonify({"username": username, "password": password}), 200


@admin.route("/genelist", methods=["GET", "PUT"])
@jwt_required()
@swag_from(os.path.join(DOCUMENTATION_PATH, "parsesamples.yaml"))
def edit_gene_list():
    if request.method == "GET":
        return jsonify({"results": utils.gene_list_csv.columns.tolist()})
    if request.method == "PUT":

        request_json = request.get_json()
        if "geneList" not in request_json:
            raise exceptions.BadRequest("missing gene list")
        if (
            not isinstance(request_json["geneList"], list)
            or len(request_json["geneList"]) == 0
        ):
            raise exceptions.BadRequest("bad gene list")

        new_gene_list = request_json["geneList"]
        lock = FileLock("file.lock")

        with lock:
            try:
                with open(utils.GENE_LIST_FILE_LOCATION, "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(new_gene_list)
                time.sleep(0.1)
                utils.reload_gene_list()
            except Exception as e:
                raise exceptions.BadRequest("Error writing to file")
        return jsonify({"message": "success"}), 200
