from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
import requests
import pandas as pd
import plotly.express as px
import joblib
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.pipeline import Pipeline
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import json

app = Flask(__name__)
app.secret_key = "SECRET"

app.config['SESSION_TYPE'] = "filesystem"
Session(app)
#app.config['SESSION_PERMANENT'] = False
#app.config['SESSION_USE_SIGNER'] = True
#app.config['SESSION_REDIS'] = redis.from_url('redis://127.0.0.1:6379')

model = joblib.load("model.pkl")
bootstrap_models = joblib.load("bootstrap_models.pkl")

def predict(features, qc_threshold):

    prediction_probs = model.predict_proba(features).tolist()
    nc_list = [i for i, prob in enumerate(prediction_probs) if max(prob) < qc_threshold]

    prediction_probs = np.round(prediction_probs, 4)
    predictions = model.predict(features) + 1
    predictions = [str(prediction) for prediction in predictions]

    for index in nc_list:
        predictions[index] = "NC"

    session["data"]["predictions"] = predictions
    session["data"]["probs"] = prediction_probs

def read_data(file): 
    data = pd.read_csv(file, index_col=0)
    data = data.T
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

@app.route("/upload", methods=["POST"])
def upload():
    raw_data = request.files["genedata"]
    data = read_data(raw_data)
    data_dict = split_data(data)
    session["data"] = data_dict

    """
    to_send = []
    for id, feature in zip(data_dict["ids"], data_dict["features"]):
        to_send.append({
            "sampleID": id,
            "features": feature
        })
    # Create the headers for the request
    headers = {
        "Content-Type": "application/json"
    }
    response =requests.post("http://127.0.0.1:3000/probability", headers=headers, data=json.dumps({
        "samples": to_send
    }))
    print(response.text)
    """

    predict(data_dict["features"], 0.85)
    return redirect("/report")

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/pca", methods=["GET"])
def pca():
    data_dict = session["data"]
    dimensions = request.args.get("dim")
    classification_list = data_dict["predictions"]

    pca_pipe = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])
    pc = pca_pipe.fit_transform(data_dict["features"])

    # load into pd dataframe
    pca_dataframe = pd.DataFrame(pc, columns=["PCA1", "PCA2", "PCA3"], index=data_dict["ids"])
    pca_dataframe["prediction"] = classification_list

    if (int(dimensions)) == 2:
        fig = px.scatter(pca_dataframe, x="PCA1", y="PCA2", color="prediction", color_discrete_sequence=px.colors.qualitative.G10)
    else:
        fig = px.scatter_3d(pca_dataframe, x="PCA1", y="PCA2", z="PCA3", color="prediction", color_discrete_sequence=px.colors.qualitative.G10)

    
    return render_template("visualisation.html", fig=fig.to_html(full_html=False)) 

@app.route("/tsne", methods=["GET"])
def tsne():
    data_dict = session["data"]
    dimensions = request.args.get("dim")

    classification_list = data_dict["predictions"]

    tsne_pipe = Pipeline(steps=[("scaler", MinMaxScaler()), ("dr", TSNE(n_components=3, perplexity=4))])
    tsne = tsne_pipe.fit_transform(data_dict["features"])

    # load into pd dataframe
    tsne_dataframe = pd.DataFrame(tsne, columns=["tsne1", "tsne2", "tsne3"], index=data_dict["ids"])
    tsne_dataframe["prediction"] = classification_list

    if (int(dimensions)) == 2:
        fig = px.scatter(tsne_dataframe, x="tsne1", y="tsne2", color="prediction", color_discrete_sequence=px.colors.qualitative.G10)
    else:
        fig = px.scatter_3d(tsne_dataframe, x="tsne1", y="tsne2", z="tsne3", color="prediction", color_discrete_sequence=px.colors.qualitative.G10)
    
    return render_template("visualisation.html", fig=fig.to_html(full_html=False))

@app.route("/report", methods=["GET"])
def report():
    data_dict = session["data"]

    return render_template("report.html", predictions=data_dict["predictions"], ids=data_dict["ids"])

@app.route("/geneexpression", methods=["GET"])
def gene_expression():
    data = session["data"]

    return render_template("gene_expression.html", feature_lists=data["features"], genes=data["gene_names"], ids=data["ids"])

@app.route("/probability", methods=["GET"])
def probabilty():
    data = session["data"]
    return render_template("probability.html", probs=data["probs"], ids=data["ids"])

@app.route("/confidence", methods=["GET"])
def confidence():
    data = session["data"]
    predictions_unclean = data["predictions"]
    features_unclean = data["features"]
    sample_unclean = data["ids"]
    to_remove = [i for i, prediction in enumerate(predictions_unclean) if prediction == "NC"]

    features = [feature for i, feature in enumerate(features_unclean) if i not in to_remove]
    predictions = [int(prediction) - 1 for i, prediction in enumerate(predictions_unclean) if i not in to_remove]
    sample_ids = [sample for i, sample in enumerate(sample_unclean) if i not in to_remove]

    results = []
    q1 = []
    median = []
    q3 = []

    for model in bootstrap_models:
        all_probs = model.predict_proba(features)

        classified_probs = []
        for prediction, probs in zip(predictions, all_probs):
            classified_prob = probs[prediction]
            classified_probs.append(classified_prob)
        results.append(classified_probs)

    results = np.transpose(np.array(results))

    for result in results:
        interval = np.percentile(result, [2.5, 50, 97.5])
        q1.append(interval[0])
        median.append(interval[1])
        q3.append(interval[2])
    
    # documentation
    fig = go.Figure()

    fig.add_trace(go.Box(y=results, hoverinfo="none", boxpoints="outliers", x=sample_ids))

    fig.update_traces(q1=q1, median=median,
                  q3=q3, )

    return render_template("visualisation.html", fig=fig.to_html(full_html=False))


if __name__ == "__main__":
    app.run(port=4000, debug=True)