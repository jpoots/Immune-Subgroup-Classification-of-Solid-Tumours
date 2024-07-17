
# prediction

# upload

# PCA 2,3

# TSNE 2,3

# Gene expression

# probability

# confidence
from flask import render_template, request, session, redirect, jsonify
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from config import app, model, bootstrap_models
import numpy as np
import pandas as pd
from requests.exceptions import HTTPError
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer


@app.route("/extractgenes", methods=["POST"])
def extract_genes():
        # is file in request and is it a valid CSV
        file =  request.files["samples"]
        data = pd.read_csv(file, index_col=0)
        data = data.T
        
        # drop empty rows
        data.dropna(how="all", inplace=True)

        # drop rows with more than 2 empty genes, calculate diff
        original_size = data.shape[0]
        data.dropna(thresh=438, inplace=True)
        invalid = original_size - data.shape[0]

        # get rows that need imputed
        # look at me
        # imputed_rows = np.where(data.isnull().any(axis=1))[0].tolist()

        # is data of valid shape
        n_col, n_row = data.shape[0], data.shape[1]

        if n_row != 440 or n_row == 0 : raise HTTPError()

        # split data for further processing
        idx = [sample_id for sample_id in data.index]
        genes = [gene for gene in data.columns.values]
        features = data.values

        # impute missing values - note, imputation could've been done in pipeline but seperation allows us to keep the gene expression values
        imp = IterativeImputer().set_output(transform="pandas")
        features = imp.fit_transform(data)

        features = features.T.to_dict()
        returnData = []
        for sample in features.keys():
            returnData.append({
                "sampleID": sample,
                "genes": features[sample]
            })

        request.returndata = returnData            

        return(jsonify({
            "results": returnData
        }))

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    # extract data from JSON
    idx = [sample["sampleID"] for sample in data]
    features = [list(sample["genes"].values()) for sample in data]

    # get probabilites and mark those below QC
    qc_threshold = 0.982
    prediction_probs = model.predict_proba(features)
    nc_indicies = [index for index, prob in enumerate(prediction_probs) if np.amax(prob) < qc_threshold]

    # make prediction
    predictions = model.predict(features).tolist()
    predictions = [prediction + 1 if index not in nc_indicies else "NC" for index, prediction in enumerate(predictions)]

    # prepare for response
    results = []
    for pred, id, prob_list in zip(predictions, idx, prediction_probs.tolist()):
        results.append({
            "sampleID": id,
            "prediction": pred,
            "probs": prob_list
        })

    return jsonify({
        "results": results
    })


@app.route("/analyse", methods=["POST"])
def analyse():
    # get data from files
    data = request.data

    # get probabilites and mark those below QC
    qc_threshold = 0.982
    prediction_probs = model.predict_proba(data["features"])
    nc_indicies = [index for index, prob in enumerate(prediction_probs) if np.amax(prob) < qc_threshold]

    # make prediction
    predictions = model.predict(data["features"]).tolist()
    predictions = [prediction + 1 if index not in nc_indicies else "NC" for index, prediction in enumerate(predictions)]

    # prepare for response
    results = []
    for pred, id, prob_list in zip(predictions, data["ids"], prediction_probs.tolist()):
        results.append({
            "sampleID": id,
            "prediction": pred,
            "probs": prob_list
        })

    return jsonify({
        "results": results
    })

@app.route("/probability", methods=["POST"])
def probaility():
    data = request.data

    # make prediction
    probs = model.predict_proba(data["features"]).tolist()

    # prepare for response
    results = []
    for pred, id in zip(probs, data["ids"]):
        results.append({
            "sampleID": id,
            "probs": pred
        })

    return jsonify({
        "results": results
    })

@app.route("/pca", methods=["POST"])
def pca():
    data = request.data

    pca_pipe = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])
    pc = pca_pipe.fit_transform(data["features"]).tolist()

    return jsonify({
        "results": pc
    })


@app.route("/tsne", methods=["POST"])
def tsne():
    data = request.data

    tsne_pipe = Pipeline(steps=[("scaler", MinMaxScaler()), ("dr", TSNE(n_components=3, perplexity=9))])
    tsne = tsne_pipe.fit_transform(data["features"]).tolist()

    return jsonify({
        "results": tsne
    })

@app.route("/confidence", methods=["POST"])
def confidence():
    data = request.data

    features = data["features"]
    sample_ids = data["ids"]

    all_classified = []
    results = []
    
    for model in bootstrap_models:
        all_probs = model.predict_proba(features)

        classified_probs = []
        for probs in all_probs:
            classified_prob = np.amax(probs)
            classified_probs.append(classified_prob)
        all_classified.append(classified_probs)

    all_classified = np.transpose(np.array(all_classified))

    for classified, id in zip(all_classified, sample_ids):
        interval = np.percentile(classified, [2.5, 50, 97.5])


        results.append({
            "sampleID": id,
            "confidence": {
                "upper": interval[2],
                "median": interval[1],
                "lower": interval[0],
                "max": max(classified),
                "min": min(classified)
            }
        })
    return jsonify({
        "results": results
    })

if __name__ == "__main__":
    app.run(port=3000, debug=True)