from flask import (
    request,
    jsonify,
    Blueprint,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from ..utils import parse_csv, parse_json
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

# the pca pipeline to be used
PCA_PIPE = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])
# the endpoint to get async results
RESULTS_ENDPOINT = "http://127.0.0.1:3000/getresults"
# file path to documentation
DOCUMENTATION_PATH = "../documentation"
LIMIT = "1000 per minute"
LIMIT_MESSAGE = "Request are limited to 5 per minute"

main = Blueprint("main", __name__)


print(os.path.join(DOCUMENTATION_PATH, "parsesamples.yaml"))


@limiter.limit(LIMIT, error_message=LIMIT_MESSAGE)
@main.route("/parsesamples", methods=["POST"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "parsesamples.yaml"))
def parse_samples():
    """Endpoint to extract data from a csv file attached as samples to an HTTP request. Full details of request input in swagger docs.

    Returns:
        A dict including key the sample data, number of invlaid samples.

        "data": {
            "invalid": 0,
            "samples": [
            {
                "genes": {
                "ACTL6A_S5": 745.567,
                },
                "sampleID": "TCGA.02.0047.GBM.C4"
                "typeid": GBM
            },
        }

    Raises:
        BadRequest: The file is missing from the request or the sample file is invalid
    """
    try:
        file = request.files["samples"]
    except Exception as e:
        raise exceptions.BadRequest("Missing file")

    data = parse_csv(file)

    features = pd.DataFrame(data["features"], columns=data["gene_names"])
    features = features.T.to_dict()

    returnData = []
    for sample_id, feature_index, type_id in zip(
        data["ids"], features, data["type_ids"]
    ):
        returnData.append(
            {"sampleID": sample_id, "genes": features[feature_index], "typeid": type_id}
        )

    return (jsonify({"data": {"samples": returnData, "invalid": data["invalid"]}}), 200)


@limiter.limit(LIMIT, error_message=LIMIT_MESSAGE)
@main.route("/predict", methods=["POST"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "predict.yaml"))
def predictgroup():
    """Endpoint to form predictions from json data in a request. Full details of request input in swagger docs.

    Returns:
        A dict including the sample id and prediction

        "data": {
            "samples": [
            {
                "prediction": 4
                "sampleID": "TCGA.02.0047.GBM.C4"
            },
        }

    Raises:
        BadRequest: The JSON sent is missing or invalid
    """

    data = request.get_json()
    data = parse_json(data)

    idx = data["ids"]
    features = data["features"]

    predictions, prediction_probs = predict(features)

    # prepare for response
    results = []
    for pred, id, prob_list in zip(predictions, idx, prediction_probs):
        results.append({"sampleID": id, "prediction": pred, "probs": prob_list})

    return jsonify({"data": results})


@limiter.limit(LIMIT, error_message=LIMIT_MESSAGE)
@swag_from(os.path.join(DOCUMENTATION_PATH, "probability.yaml"))
@main.route("/probability", methods=["POST"])
def probaility():
    """Endpoint to get prediction probabilities from JSON. Full details of request input in swagger docs.

    Returns:
        A dict including the sample id and an array of the 6 probabilites for each subgroup.

        "data": {
            "invalid": 0,
            "samples": [
            {
                "genes": {
                "ACTL6A_S5": 745.567,
                },
                "sampleID": "TCGA.02.0047.GBM.C4",
                "probs": [0.1,0.1,0.1,0.1,0.1,0.5]

            },
        }

    Raises:
        BadRequest: The JSON sent is missing or invalid
    """
    data = request.get_json()
    data = parse_json(data)

    # make prediction
    probs = probability(data["features"])

    # prepare for response
    results = []
    for pred, id in zip(probs, data["ids"]):
        results.append({"sampleID": id, "probs": pred})

    return jsonify({"data": results})


@limiter.limit(LIMIT, error_message=LIMIT_MESSAGE)
@main.route("/pca", methods=["POST"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "pca.yaml"))
def pca():
    """Endpoint to perform PCA analysis. Full details of request input in swagger docs.

    Returns:
        A dict including the sample id and an array of 3 principle componets.

        "data": {
            "samples": [
            {
                "pca": [1,2,3]
                "sampleID": "TCGA.02.0047.GBM.C4"
            },
        }

    Raises:
        BadRequest: The JSON sent is missing or invalid
    """
    data = request.get_json()
    data = parse_json(data)

    pc = PCA_PIPE.fit_transform(data["features"]).tolist()

    return jsonify({"data": pc})


@limiter.limit(LIMIT, error_message=LIMIT_MESSAGE)
@main.route("/analyse", methods=["POST"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "analyse.yaml"))
def analyse_async():
    """Endpoint to begin a full async analysis from a csv file attached as samples to an HTTP request. Full details of request input in swagger docs.

    Returns:
        A dict containing the location of the result

        "resultURL": "localhost:3000/getresults/analyse/123-abc

    Raises:
        BadRequest: The file is missing from the request or the sample file is invalid
    """
    # is file in request and is it a valid CSV
    try:
        file = request.files["samples"]
    except Exception as e:
        raise exceptions.BadRequest("Missing file")

    filename = f"{uuid.uuid4()}.csv"
    file.save("./temp/" + filename)
    task = analyse.apply_async(args=["./temp/" + filename])
    return jsonify({"resultURL": f"{RESULTS_ENDPOINT}/analyse/{task.id}"}), 202


@limiter.limit(LIMIT, error_message=LIMIT_MESSAGE)
@main.route("/tsne", methods=["POST"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "tsne.yaml"))
def tsne_async():
    """Endpoint to begin tsne analysis from JSON. Full details of request input in swagger docs.

    Returns:
        A dict containing the location of the result

        "resultURL": "localhost:3000/getresults/tsne/123-abc

    Raises:
        BadRequest: JSON is missing
    """
    # handles error automatically if the request isn't JSON
    data = request.get_json()
    task = tsne_celery.apply_async(args=[data])
    return jsonify({"resultURL": f"{RESULTS_ENDPOINT}/tsne/{task.id}"}), 202


@limiter.limit(LIMIT, error_message=LIMIT_MESSAGE)
@main.route("/confidence", methods=["POST"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "confidence.yaml"))
def confidence_async():
    """Endpoint to begin confidence analysis from JSON. Full details of request input in swagger docs.

    Returns:
        A dict containing the location of the result

        "resultURL": "localhost:3000/confidence/tsne/123-abc

    Raises:
        BadRequest: JSON is missing
    """
    # handles error automatically if the request isn't JSON
    data = request.get_json()
    task = confidence_celery.apply_async(args=[data])
    return jsonify({"resultURL": f"{RESULTS_ENDPOINT}/confidence/{task.id}"}), 202
