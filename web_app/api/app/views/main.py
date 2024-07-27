from flask import (
    request,
    jsonify,
    Blueprint,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from ..utils import csv_func, json_func
from werkzeug import exceptions
from ..ml_models.predictions import predict, probability
import base64
import uuid
import os
from werkzeug import exceptions
from .celery_tasks import confidence_celery, tsne_celery, analyse
from app.utils import (
    gene_preprocessing,
)
from flasgger import swag_from

main = Blueprint("main", __name__)

TSNE_PIPE = Pipeline(
    steps=[("scaler", MinMaxScaler()), ("dr", TSNE(n_components=3, perplexity=4))]
)

PCA_PIPE = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])

# all data validation should occur at the middleware level. Unexpected failure at this level handled as a generic error


@swag_from("./documentation/extractgenes.yaml")
@main.route("/extractgenes", methods=["POST"])
def extract_genes():
    try:
        file = request.files["samples"]
    except Exception as e:
        raise exceptions.BadRequest("Missing file")

    data = csv_func(file)
    returnData = gene_preprocessing(full_analysis=False, features=data["features"])
    return (jsonify({"data": {"samples": returnData, "invalid": data["invalid"]}}), 200)


@swag_from("./documentation/predict.yaml")
@main.route("/predict", methods=["POST"])
def predictgroup():
    data = request.get_json()
    data = json_func(data)

    idx = data["ids"]
    features = data["features"]

    predictions, prediction_probs = predict(features)

    # prepare for response
    results = []
    for pred, id, prob_list in zip(predictions, idx, prediction_probs):
        results.append({"sampleID": id, "prediction": pred, "probs": prob_list})

    return jsonify({"data": results})


@swag_from("./documentation/probability.yaml")
@main.route("/probability", methods=["POST"])
def probaility():
    data = request.get_json()
    data = json_func(data)

    # make prediction
    probs = probability(data["features"])

    # prepare for response
    results = []
    for pred, id in zip(probs, data["ids"]):
        results.append({"sampleID": id, "probs": pred})

    return jsonify({"data": results})


@swag_from("./documentation/pca.yaml")
@main.route("/pca", methods=["POST"])
def pca():
    data = request.get_json()
    data = json_func(data)

    pc = PCA_PIPE.fit_transform(data["features"]).tolist()

    return jsonify({"data": pc})


@swag_from("./documentation/analyseasync.yaml")
@main.route("/analyseasync", methods=["POST"])
def analyse_async():
    # is file in request and is it a valid CSV
    try:
        file = request.files["samples"]
    except Exception as e:
        raise exceptions.BadRequest("Missing file")

    filename = f"{uuid.uuid4()}.csv"
    file.save("./temp/" + filename)
    task = analyse.apply_async(args=["./temp/" + filename])
    return jsonify({"id": task.id}), 200


@swag_from("./documentation/tsneasync.yaml")
@main.route("/tsneasync", methods=["POST"])
def tsne_async():
    # handles error automatically if the request isn't JSON
    data = request.get_json()
    task = tsne_celery.apply_async(args=[data])
    return jsonify({"id": task.id}), 200


@swag_from("./documentation/confidenceasync.yaml")
@main.route("/confidenceasync", methods=["POST"])
def confidence_async():
    # handles error automatically if the request isn't JSON
    data = request.get_json()
    task = confidence_celery.apply_async(args=[data])
    return jsonify({"id": task.id}), 200
