from flask import (
    request,
    jsonify,
    Blueprint,
)
from .. import utils
from werkzeug import exceptions
import os
from flasgger import swag_from
from app import limiter
from filelock import FileLock
from ..models import Admin
from .. import db
from flask_jwt_extended import create_access_token
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
@swag_from(os.path.join(DOCUMENTATION_PATH, "authenticate.yaml"))
def authenticate():
    """Endpoint to authenticate and admin. See swagger docs for full details

    Returns:
        An access token dict

        "data": {
            "accessToken": ABCDEFG
        }

    Raises:
        BadRequest: The JSON sent is invalid
        Unauthorised: The credentials are bad
    """

    # validate json
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
        return jsonify(data={"accessToken": access_token})

    # none found, raise exception
    raise exceptions.Unauthorized()


@admin.route("/admin", methods=["POST"])
@jwt_required()
@swag_from(os.path.join(DOCUMENTATION_PATH, "admin.yaml"))
def admins():
    """Endpoint to create a new admin user. See swagger docs for full info

    Returns:
        A json object containing username and password for the new user
            data:{
            "username": "ABCDEFG",
            "password: "123456"
            }
    """

    # get latest admin and increment the id by 1
    admin_id = Admin.query.order_by(Admin.id.desc()).first().id + 1

    # generate password and username
    password = token_urlsafe(16)
    username = f"ICSTADMIN{admin_id}"

    # add to DB
    new_admin = Admin(username=username, pass_hash=password)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify(data={"username": username, "password": password}), 200


@admin.route("/genelist", methods=["GET", "PUT"])
@jwt_required(optional=True)
@swag_from(os.path.join(DOCUMENTATION_PATH, "genelist_get.yaml"), methods=["GET"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "genelist_put.yaml"), methods=["PUT"])
def edit_gene_list():
    """Endpoint to get the gene list or replace it given one. See swagger docs for full info.

    Returns:
        A json object containing the gene list on get
            data:{
            "geneList": ["ABCDEFG",...]
            }
        or a success message on put
            data:{
            "message": "success"
            }
    Raises:
        Unauthorised: an attempt to modify the gene list is made without login
        BadRequest: the gene list is invalid
        InternalServerError: there is some error writing to the file
    """
    if request.method == "GET":
        return jsonify(data={"results": utils.gene_list_csv.columns.tolist()})
    if request.method == "PUT":
        # is not auth
        if not get_jwt_identity():
            raise exceptions.Unauthorized

        # get geneList and validate
        request_json = request.get_json()
        if "geneList" not in request_json:
            raise exceptions.BadRequest("missing gene list")
        elif (
            not isinstance(request_json["geneList"], list)
            or len(request_json["geneList"]) == 0
        ):
            raise exceptions.BadRequest("bad gene list")

        new_gene_list = request_json["geneList"]

        # lock to prevent race condition
        lock = FileLock("file.lock")

        with lock:
            try:
                with open(utils.GENE_LIST_FILE_LOCATION, "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(new_gene_list)

                # live reload the gene list
                utils.reload_gene_list()
            except Exception as e:
                raise exceptions.InternalServerError("Error writing to file")
        return jsonify(data={"message": "success"}), 200
