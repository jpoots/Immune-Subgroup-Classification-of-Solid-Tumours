from flask import (
    render_template,
    request,
    session,
    redirect,
    jsonify,
    Blueprint,
)
from flask import current_app
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np
import pandas as pd
import time
from .middleware import parse_json, parse_csv, csv_func, json_func
from werkzeug import exceptions
from .ml_models.predictions import predict, confidence_intervals, probability
from . import celery
import base64
import uuid
import os
from werkzeug import exceptions
from .errors.BadRequest import BadRequest

views = Blueprint("views", __name__)

TSNE_PIPE = Pipeline(
    steps=[("scaler", MinMaxScaler()), ("dr", TSNE(n_components=3, perplexity=4))]
)

PCA_PIPE = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])

# all data validation should occur at the middleware level. Unexpected failure at this level handled as a generic error


def gene_preprocessing(full_analysis, features):
    # if being sent back in JSON or if part of full analysis
    if not full_analysis:
        features = features.T.to_dict()
        returnData = []
        for sample in features.keys():
            returnData.append({"sampleID": sample, "genes": features[sample]})
    else:
        # split data for further processing
        idx = [sample_id for sample_id in features.index]
        genes = [gene for gene in features.columns.values]
        features = features.values.tolist()

        returnData = {
            "ids": idx,
            "gene_names": genes,
            "features": features,
        }
    return returnData


@views.route("/extractgenes", methods=["POST"])
@parse_csv
def extract_genes():
    returnData = gene_preprocessing(full_analysis=False, features=request.features)
    return (jsonify({"data": {"samples": returnData, "invalid": request.invalid}}), 200)


@views.route("/predict", methods=["POST"])
@parse_json
def predictgroup():
    idx = request.idx
    features = request.features

    predictions, prediction_probs = predict(features)

    # prepare for response
    results = []
    for pred, id, prob_list in zip(predictions, idx, prediction_probs):
        results.append({"sampleID": id, "prediction": pred, "probs": prob_list})

    return jsonify({"data": results})


@views.route("/probability", methods=["POST"])
def probaility():
    data = request.get_json()

    # make prediction
    probs = probability(data["features"])

    # prepare for response
    results = []
    for pred, id in zip(probs, data["ids"]):
        results.append({"sampleID": id, "probs": pred})

    return jsonify({"data": results})


@views.route("/pca", methods=["POST"])
@parse_json
def pca():
    idx = request.idx
    features = request.features

    pc = PCA_PIPE.fit_transform(features).tolist()

    return jsonify({"data": pc})


@views.route("/tsne", methods=["POST"])
@parse_json
def tsne():

    idx = request.idx
    features = request.features
    perplexity = request.perplexity

    print(perplexity)
    Pipeline(
        steps=[
            ("scaler", MinMaxScaler()),
            ("dr", TSNE(n_components=3, perplexity=perplexity)),
        ]
    )

    results = []
    tsne = TSNE_PIPE.fit_transform(features).tolist()
    for id, tsne_result in zip(idx, tsne):
        results.append({"sampleID": id, "tsne": tsne_result})

    return jsonify({"data": results})


@views.route("/confidence", methods=["POST"])
@parse_json
def confidence():
    features = request.features
    sample_ids = request.idx
    interval = request.interval

    results = []
    for interval, id in zip(confidence_intervals(features, interval), sample_ids):

        results.append(
            {
                "sampleID": id,
                "min": interval[0],
                "lower": interval[1],
                "median": interval[2],
                "upper": interval[3],
                "max": interval[4],
            }
        )
    return jsonify({"data": results})


@views.route("/performanalysis", methods=["POST"])
@parse_csv
def perform_analysis():
    data = gene_preprocessing(full_analysis=True, features=request.features)

    predictions, prediction_probs, num_nc = predict(data["features"])
    pc = PCA_PIPE.fit_transform(data["features"]).tolist()

    results = []

    for (
        sample_id,
        feature_list,
        prediction,
        prob_list,
        pc_comps,
        type_id,
    ) in zip(
        data["ids"],
        data["features"],
        predictions,
        prediction_probs,
        pc,
        request.typeids,
    ):
        genes = {
            gene_name: expression
            for gene_name, expression in zip(data["gene_names"], feature_list)
        }

        results.append(
            {
                "sampleID": sample_id,
                "genes": genes,
                "prediction": prediction,
                "probs": prob_list,
                "pca": pc_comps,
                "typeid": type_id,
            }
        )

    return jsonify(
        {"data": {"samples": results, "invalid": request.invalid, "nc": num_nc}}
    )


@views.route("/getresults/<task_id>", methods=["GET"])
def task_status(task_id):
    task = celery.AsyncResult(task_id)
    status = 200

    if task.status == "SUCCESS":
        result = jsonify({"status": "SUCCESS", "data": task.result})
    elif task.status == "PENDING":
        result = jsonify({"status": "PENDING"})
    else:
        err = task.result
        result = jsonify(
            {
                "error": {
                    "code": err.status_code,
                    "name": err.headers,
                    "description": err.body,
                }
            },
        )
        status = err.status_code
    return result, status


def celery_return(self, status, retval, task_id, args, kwargs, einfo):
    os.remove(args[0])
    return


@celery.task(
    throws=(BadRequest,),
    after_return=celery_return,
)
def analyse(filepath):
    parsed_results = csv_func(filepath)
    data = gene_preprocessing(full_analysis=True, features=parsed_results["features"])

    predictions, prediction_probs, num_nc = predict(data["features"])
    pc = PCA_PIPE.fit_transform(data["features"]).tolist()

    results = []

    for (
        sample_id,
        feature_list,
        prediction,
        prob_list,
        pc_comps,
        type_id,
    ) in zip(
        data["ids"],
        data["features"],
        predictions,
        prediction_probs,
        pc,
        parsed_results["type_ids"],
    ):
        genes = {
            gene_name: expression
            for gene_name, expression in zip(data["gene_names"], feature_list)
        }

        results.append(
            {
                "sampleID": sample_id,
                "genes": genes,
                "prediction": prediction,
                "probs": prob_list,
                "pca": pc_comps,
                "typeid": type_id,
            }
        )

    return {"samples": results, "invalid": parsed_results["invalid"], "nc": num_nc}


@celery.task(
    throws=(BadRequest,),
)
def tsne_celery(data):
    data = json_func(data)

    idx = data["ids"]
    features = data["features"]
    perplexity = data["perplexity"]

    Pipeline(
        steps=[
            ("scaler", MinMaxScaler()),
            ("dr", TSNE(n_components=3, perplexity=perplexity)),
        ]
    )

    results = []
    tsne = TSNE_PIPE.fit_transform(features).tolist()
    for id, tsne_result in zip(idx, tsne):
        results.append({"sampleID": id, "tsne": tsne_result})

    return results


@views.route("/analyseasync", methods=["POST"])
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


@views.route("/tsneasync", methods=["POST"])
def tsne_async():
    # handles error automatically if the request isn't JSON
    data = request.get_json()
    task = tsne_celery.apply_async(args=[data])
    return jsonify({"id": task.id}), 200


@views.route("/confidenceasync", methods=["POST"])
def confidence_async():
    # handles error automatically if the request isn't JSON
    data = request.get_json()

    task = confidence_celery.apply_async(args=[data])
    return jsonify({"id": task.id}), 200


@celery.task(
    throws=(BadRequest,),
)
def confidence_celery(data):
    data = json_func(data)

    features = data["features"]
    sample_ids = data["ids"]
    interval = data["interval"]

    results = []
    for interval, id in zip(confidence_intervals(features, interval), sample_ids):

        results.append(
            {
                "sampleID": id,
                "min": interval[0],
                "lower": interval[1],
                "median": interval[2],
                "upper": interval[3],
                "max": interval[4],
            }
        )
    return results
