from flask import request, jsonify, Blueprint, current_app
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from ..utils import parse_csv, parse_json, validate_csv_upload
from werkzeug import exceptions
from ..ml_models.predictions import predict
import uuid
import os
from werkzeug import exceptions
from .celery_tasks import confidence_celery, tsne_celery, analyse
from flasgger import swag_from
from app import limiter
import pandas as pd
from .. import DOCUMENTATION_PATH, LOW_LIMIT, LOW_LIMIT_MESSAGE, API_ROOT

"""
The main api endpoints for the system to perform analysis
"""

# the pca pipeline to be used
PCA_PIPE = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])

# API results endpoint
RESULTS_ENDPOINT = f"{API_ROOT}/ results"

main = Blueprint("main", __name__)


@limiter.limit(LOW_LIMIT, error_message=LOW_LIMIT_MESSAGE)
@main.route("/parsesamples", methods=["POST"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "parsesamples.yaml"))
def parse_samples():
    """Endpoint to extract data from a csv file attached as samples to an HTTP from using delimtier delimtiter. Full details of request input in swagger docs.

    Returns:
        A json response object including key the sample data, number of invlaid samples.

        "data": {
            "predom": 1,
            "nc": 1,
            "invalid": 0,
            "samples": [
            {
                "genes": {
                "ACTL6A_S5": 745.567,
                },
                "sampleID": "TCGA.02.0047.GBM.C4"
                "typeid": GBM
            },
            ]
        }
    """

    # validate csv
    file, delimiter = validate_csv_upload(request)

    # save for research
    filename = f"{uuid.uuid4()}"
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # parse data
    data = parse_csv(filepath, delimiter)

    # strucutre data for ease of surfing
    features = pd.DataFrame(data["features"], columns=data["gene_names"])
    features = features.T.to_dict()

    # structure for return
    returnData = []
    for sample_id, feature_index, type_id in zip(
        data["ids"], features, data["type_ids"]
    ):
        returnData.append(
            {"sampleID": sample_id, "genes": features[feature_index], "typeid": type_id}
        )

    return (jsonify({"data": {"samples": returnData, "invalid": data["invalid"]}}), 200)


@limiter.limit(LOW_LIMIT, error_message=LOW_LIMIT_MESSAGE)
@main.route("/predict", methods=["POST"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "predict.yaml"))
def predictgroup():
    """Endpoint to form predictions from json data in a request. Full details of request input in swagger docs.

    Returns:
        A json response object including the sample id and prediction

        "data": {
            "samples": [
            {
                "prediction": 1
                "sampleID": "TCGA.02.0047.GBM.C1"
                "probs": [0.95, 0.01, 0.01, 0.01, 0.01, 0.01],
                "predomPrediction": Null
                "predomProbs": Null
            },
            ],
            "predom": 1,
            "nc": 1
        }
    """

    # parse json
    data = request.get_json()
    data = parse_json(data)

    idx = data["ids"]
    features = data["features"]

    # predict
    predictions, prediction_probs, num_nc, num_predom = predict(features)

    # prepare for response
    results = []
    for pred, id, prob_list in zip(predictions, idx, prediction_probs):
        results.append({"sampleID": id, "prediction": pred, "probs": prob_list})

    return jsonify({"data": {"samples": results, "nc": num_nc, "predom": num_predom}})


@limiter.limit(LOW_LIMIT, error_message=LOW_LIMIT_MESSAGE)
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
            },]
        }

    Raises:
        BadRequest: The JSON sent is missing or invalid
    """
    data = request.get_json()
    data = parse_json(data)

    # if too few features
    if len(data["features"]) < 3:
        raise exceptions.BadRequest(
            "At least 3 samples is requried to perform PCA analysis"
        )
    else:
        # perform pca analysis and parcel for return
        pc = PCA_PIPE.fit_transform(data["features"]).tolist()
        idx = data["ids"]

        results = [
            {"sampleID": sample_id, "pca": pca} for sample_id, pca in zip(idx, pc)
        ]

        return jsonify({"data": results})


@limiter.limit(LOW_LIMIT, error_message=LOW_LIMIT_MESSAGE)
@main.route("/analyse", methods=["POST"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "analyse.yaml"))
def analyse_async():
    """Endpoint to begin a full async analysis from a csv file attached as samples to an HTTP request. Full details of request input in swagger docs.

    Returns:
        A dict containing the location of the result
        data: {
            "resultURL": "localhost:3000/results/analyse/123-abc
        }


    Raises:
        BadRequest: The file is missing from the request or the sample file is invalid
    """
    # is file in request and is it a valid CSV
    file, delimiter = validate_csv_upload(request)

    filename = f"{uuid.uuid4()}"
    file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
    task = analyse.apply_async(
        args=[os.path.join(current_app.config["UPLOAD_FOLDER"], filename), delimiter]
    )
    return jsonify(data={"resultURL": f"{RESULTS_ENDPOINT}/analyse/{task.id}"}), 202


@limiter.limit(LOW_LIMIT, error_message=LOW_LIMIT_MESSAGE)
@main.route("/tsne", methods=["POST"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "tsne.yaml"))
def tsne_async():
    """Endpoint to begin tsne analysis from JSON. Full details of request input in swagger docs.

    Returns:
        A dict containing the location of the result

        data: {"resultURL": "localhost:3000/results/tsne/123-abc}

    Raises:
        BadRequest: The JSON sent is missing or invalid
    """
    # handles error automatically if the request isn't JSON
    data = request.get_json()

    # check for necessary params
    if "numDimensions" not in data:
        raise exceptions.BadRequest("t-SNE requires a number of dimensions")
    if "perplexity" not in data:
        raise exceptions.BadRequest("t-SNE requires perplexity")

    # start celery task
    task = tsne_celery.apply_async(args=[data])
    return jsonify(data={"resultURL": f"{RESULTS_ENDPOINT}/tsne/{task.id}"}), 202


@limiter.limit(LOW_LIMIT, error_message=LOW_LIMIT_MESSAGE)
@main.route("/confidence", methods=["POST"])
@swag_from(os.path.join(DOCUMENTATION_PATH, "confidence.yaml"))
def confidence_async():
    """Endpoint to begin confidence analysis from JSON. Full details of request input in swagger docs.

    Returns:
        A dict containing the location of the result

        data: {"resultURL": "localhost:3000/results/confidence/123-abc}

    """
    # handles error automatically if the request isn't JSON
    data = request.get_json()

    # start celery task
    task = confidence_celery.apply_async(args=[data])
    return jsonify(data={"resultURL": f"{RESULTS_ENDPOINT}/confidence/{task.id}"}), 202
