from dash import Dash, html, dcc, dash_table, Input, Output, State, callback
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.pipeline import Pipeline
import plotly.express as px
import io
import base64

external_stylesheets = ["https://cdn.jsdelivr.net/npm/bootstrap@4.4.1/dist/css/bootstrap.min.css"]
app = Dash(__name__, external_stylesheets=external_stylesheets)
np.random.seed(42)

# splits the data into the components of ID, features, classification and gene names
def split_data(data):
    idx = [sample_id for sample_id in data.index]
    genes = [gene for gene in data.columns.values]
    classification = np.array([int(sample[-1]) - 1 for sample in data.index.values])
    features = data.to_numpy()
    return idx, features, classification, genes

# load model
model = joblib.load("model.pkl")
assert isinstance(model, Pipeline)

# load example data
df = pd.read_csv("data_small.csv", index_col=0)
df_t = df.T
id_list, features, classification_list, genes = split_data(df_t)
classification_list = [str(classification) for classification in classification_list]

predictions = model.predict(features)
prediction_probailites = model.predict_proba(features)

rounded_probs = np.round(prediction_probailites, decimals=4)
probabilities_df = pd.DataFrame(rounded_probs)

app.layout = [
    html.Div(children="ICST"),
    dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag and Drop or ',
        html.A('Select Files')
    ])),
    dcc.Graph(id="pca"),
    dcc.Graph(id="tsne"),
    dash_table.DataTable(id="uploaded", page_size=10),
    dash_table.DataTable(id="probabilities", page_size=10),
    dash_table.DataTable(id="predictions", page_size=10),
    dash_table.DataTable(id="all-input", page_size=10),
]

@callback (Output("all-input", "data"),
           Input("upload-data", "contents"))
def load_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
    df = df.T
    return df.to_dict("records")


@callback (Output("pca", "figure"),
           Input("upload-data", "contents"))
def perform_pca(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), index_col=0)
    df = df.T

    id_list, features, classification_list, genes = split_data(df)
    print(features)
    classification_list = [str(classification) for classification in classification_list]

    pca_pipe = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])
    pc = pca_pipe.fit_transform(features)

    # load into pd dataframe
    pca_dataframe = pd.DataFrame(pc, columns=["PCA1", "PCA2", "PCA3"], index=id_list)
    pca_dataframe["label"] = classification_list

    fig_pca = px.scatter(pca_dataframe, x="PCA1", y="PCA2", color="label", title=f"PCA Data points", color_discrete_sequence=px.colors.qualitative.G10)
    return fig_pca

@callback (Output("predictions", "data"),
           Input("upload-data", "contents"))
def perform_predictions(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), index_col=0)
    df = df.T
    id_list, features, classification_list, genes = split_data(df)
    predictions = model.predict(features)
    
    predictions_df = pd.DataFrame({
    "ID": id_list,
    "Prediction": predictions
    })

    return predictions_df.to_dict("records")


@callback (Output("probabilities", "data"),
           Input("upload-data", "contents"))
def probabilites(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), index_col=0)
    df = df.T

    
    id_list, features, classification_list, genes = split_data(df)
    prediction_probailites = model.predict_proba(features)

    rounded_probs = np.round(prediction_probailites, decimals=4)
    probabilities_df = pd.DataFrame(rounded_probs)

    return probabilities_df.to_dict("records")


@callback (Output("tsne", "figure"),
           Input("upload-data", "contents"))
def perform_tsne(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), index_col=0)
    df = df.T

    id_list, features, classification_list, genes = split_data(df)
    classification_list = [str(classification) for classification in classification_list]

    tsne_pipe = Pipeline(steps=[("scaler", MinMaxScaler()), ("dr", TSNE(n_components=3, perplexity=500))])
    tsne = tsne_pipe.fit_transform(features)

    tsne_dataframe = pd.DataFrame(tsne, columns=["tSNE1", "tSNE2", "tSNE3"], index=id_list)
    tsne_dataframe["label"] = classification_list
    fig_tsne = px.scatter(tsne_dataframe, x="tSNE1", y="tSNE2", color="label", title=f"t-SNE Perplexity", color_discrete_sequence=px.colors.qualitative.G10)
    return fig_tsne


if __name__ == "__main__":
    app.run(debug=True)
