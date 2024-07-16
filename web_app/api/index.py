
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

def read_data(file): 
    data = pd.read_csv(file, index_col=0)
    data = data.T

    idx = [sample_id for sample_id in data.index]
    genes = [gene for gene in data.columns.values]
    features = data.values.tolist()
    
    data = {
        "ids": idx,
        "gene_names": genes,
        "features": features
    }
    return data

def split_data(data):
    idx = [sample_id for sample_id in data.index]
    genes = [gene for gene in data.columns.values]
    features = data.values.tolist()

    data = {
        "ids": idx,
        "gene_names": genes,
        "features": features
    }
    return data

@app.route("/extractgenes", methods=["POST"])
def extract_genes():
    file = request.files["samples"]
    data = read_data(file)

    results = []
    for idx, features in zip(data["ids"], data["features"]):
        genes = {}
        for feature, gene_name in zip(features, data["gene_names"]):
            genes[gene_name] = feature
        
        results.append({
            "sampleID": idx,
            "genes": genes
        })
    return jsonify({
        "results": results
    })

@app.route("/predict", methods=["POST"])
def predict():
    file = request.files["samples"]
    data = read_data(file)

    # seperate features and sample IDs
    features, sample_ids = data["features"], data["ids"]

    # make prediction
    predictions = model.predict(features).tolist()

    # prepare for response
    results = []
    for pred, id in zip(predictions, sample_ids):
        results.append({
            "sampleID": id,
            "prediction": pred
        })

    return jsonify({
        "results": results
    })

@app.route("/probability", methods=["POST"])
def probaility():
    file = request.files["samples"]
    data = read_data(file)

    # make prediction
    probs = model.predict_proba(data["features"]).tolist()

    # prepare for response
    results = []
    for pred, id in zip(probs, data["ids"]):
        results.append({
            "sampleID": id,
            "prediction": pred
        })

    return jsonify({
        "results": results
    })

@app.route("/pca", methods=["POST"])
def pca():
    file = request.files["samples"]
    data = read_data(file)

    pca_pipe = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])
    pc = pca_pipe.fit_transform(data["features"]).tolist()

    return jsonify({
        "results": pc
    })


@app.route("/tsne", methods=["POST"])
def tsne():
    file = request.files["samples"]
    data = read_data(file)

    tsne_pipe = Pipeline(steps=[("scaler", MinMaxScaler()), ("dr", TSNE(n_components=3, perplexity=9))])
    tsne = tsne_pipe.fit_transform(data["features"]).tolist()

    return jsonify({
        "results": tsne
    })

@app.route("/confidence", methods=["POST"])
def confidence():
    file = request.files["samples"]
    data = read_data(file)

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