from flask import render_template, request, session, redirect, jsonify, Blueprint
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from .middleware import parse_json
from werkzeug import exceptions
from .ml_models.predictions import predict, confidence_intervals, probability

views = Blueprint("views", __name__)

TSNE_PIPE = Pipeline(
    steps=[("scaler", MinMaxScaler()), ("dr", TSNE(n_components=3, perplexity=9))]
)

PCA_PIPE = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])


def gene_preprocessing(full_analysis, request):
    try:
        # is file in request and is it a valid CSV
        file = request.files["samples"]
        data = pd.read_csv(file, index_col=0)
        data = data.T
    except Exception as e:
        raise exceptions.BadRequest("NO/INVALID FILE GIV")

    # drop empty rows
    data.dropna(how="all", inplace=True)
    # drop rows with more than 2 empty genes, calculate diff
    original_size = data.shape[0]
    data.dropna(thresh=438, inplace=True)
    invalid = original_size - data.shape[0]

    # is data of valid shape
    n_col, n_row = data.shape[0], data.shape[1]
    if n_row != 440 or n_row == 0:
        raise exceptions.BadRequest("INVALID GENE OR SAMPLE NUMBER")

    # impute missing values - note, imputation could've been done in pipeline but seperation allows us to keep the gene expression values
    features = data.values
    imp = IterativeImputer().set_output(transform="pandas")
    features = imp.fit_transform(data)

    # if being sent back in JSON or if part of full analysis
    if not full_analysis:
        features = features.T.to_dict()
        returnData = []
        for sample in features.keys():
            returnData.append({"sampleID": sample, "genes": features[sample]})
    else:
        # split data for further processing
        idx = [sample_id for sample_id in data.index]
        genes = [gene for gene in data.columns.values]
        features = data.values.tolist()

        returnData = {
            "ids": idx,
            "gene_names": genes,
            "features": features,
        }
    return (returnData, invalid)


@views.route("/extractgenes", methods=["POST"])
def extract_genes():
    returnData, invalid = gene_preprocessing(full_analysis=False, request=request)
    return (jsonify({"data": {"samples": returnData, "invalid": invalid}}), 200)


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


@views.route("/analyse", methods=["POST"])
def analyse():
    results = []
    return jsonify({"results": results})


@views.route("/probability", methods=["POST"])
def probaility():
    data = request.get_json()

    # make prediction
    probs = probability(data["features"])

    # prepare for response
    results = []
    for pred, id in zip(probs, data["ids"]):
        results.append({"sampleID": id, "probs": pred})

    return jsonify({"results": results})


@views.route("/pca", methods=["POST"])
@parse_json
def pca():
    idx = request.idx
    features = request.features

    pc = PCA_PIPE.fit_transform(features).tolist()

    return jsonify({"results": pc})


@views.route("/tsne", methods=["POST"])
@parse_json
def tsne():
    features = request.features

    tsne = TSNE_PIPE.fit_transform(features).tolist()

    return jsonify({"results": tsne})


@views.route("/confidence", methods=["POST"])
@parse_json
def confidence():
    features = request.features
    sample_ids = request.idx

    results = []
    for interval, id in zip(confidence_intervals(features), sample_ids):

        results.append(
            {
                "sampleID": id,
                "confidence": {
                    "min": interval[0],
                    "lower": interval[1],
                    "median": interval[2],
                    "upper": interval[3],
                    "max": interval[4],
                },
            }
        )
    return jsonify({"results": results})


@views.route("/performanalysis", methods=["POST"])
def perform_analysis():
    data, invalid = gene_preprocessing(full_analysis=True, request=request)

    predictions, prediction_probs = predict(data["features"])
    confidence_interval_list = confidence_intervals(data["features"])
    pc = PCA_PIPE.fit_transform(data["features"]).tolist()
    tsne = TSNE_PIPE.fit_transform(data["features"]).tolist()

    results = []

    for (
        sample_id,
        feature_list,
        prediction,
        prob_list,
        tsne_comps,
        pc_comps,
        confidence_interval,
    ) in zip(
        data["ids"],
        data["features"],
        predictions,
        prediction_probs,
        tsne,
        pc,
        confidence_interval_list,
    ):
        genes = {
            gene_name: expression
            for gene_name, expression in zip(data["gene_names"], feature_list)
        }

        confidence = {
            "min": confidence_interval[0],
            "lower": confidence_interval[1],
            "median": confidence_interval[2],
            "upper": confidence_interval[3],
            "max": confidence_interval[4],
        }

        results.append(
            {
                "sampleID": sample_id,
                "genes": genes,
                "prediction": prediction,
                "probs": prob_list,
                "pcs": pc_comps,
                "tsne": tsne_comps,
                "confidence": confidence,
            }
        )

    return jsonify({"results": results})
