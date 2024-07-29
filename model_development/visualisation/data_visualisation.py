import numpy as np
import pandas as pd
import plotly.express as px
import os
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import sys

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils.utils import get_data, split_data

DATA_POINTS_TO_VISUALISE = 9000
PERPLEXITY = 1
OUTPUT_FOLDER = "data_plots/"
N_COMPONENTS_PCA = 3
N_COMPONENTS_TSNE = 3
RANDOM_STATE = 42


def main():
    np.random.seed(RANDOM_STATE)
    check_folder()
    data = get_data()
    id_list, features, classification_list, _genes = split_data(data)
    classification_list = [
        str(classification) for classification in classification_list
    ]

    pca_dataframe = perform_pca(features, id_list, classification_list)
    tsne_dataframe = perform_tsne(features, id_list, classification_list)
    generate_graphs(tsne_dataframe, pca_dataframe)


def perform_pca(features, id_list, classification_list):
    # normalise features for PCA and t-SNE
    features = StandardScaler().fit_transform(features)

    # high component PCA (because it's fast) and t-SNE
    pca_canc = PCA(n_components=N_COMPONENTS_PCA)
    principle_components = pca_canc.fit_transform(features)

    # load into pd dataframe
    pca_dataframe = pd.DataFrame(
        principle_components,
        columns=[f"PCA{component+1}" for component in range(N_COMPONENTS_PCA)],
        index=id_list,
    )
    pca_dataframe["label"] = classification_list
    return pca_dataframe


def perform_tsne(features, id_list, classification_list):
    # normalise features for PCA and t-SNE
    features = MinMaxScaler().fit_transform(features)

    # high component PCA (because it's fast) and t-SNE
    tsne_canc = TSNE(
        n_components=N_COMPONENTS_TSNE, perplexity=PERPLEXITY, random_state=42
    )
    tsne_components = tsne_canc.fit_transform(features)

    # load into pd dataframe
    tsne_dataframe = pd.DataFrame(
        tsne_components,
        columns=[f"tSNE{component+1}" for component in range(N_COMPONENTS_TSNE)],
        index=id_list,
    )
    tsne_dataframe["label"] = classification_list
    return tsne_dataframe


def generate_graphs(tsne_dataframe, pca_dataframe):
    # plot my interactive figures using plotly
    fig_tsne = px.scatter(
        tsne_dataframe.head(DATA_POINTS_TO_VISUALISE),
        x="tSNE1",
        y="tSNE2",
        color="label",
        title=f"t-SNE Perplexity: {PERPLEXITY} Data points: {DATA_POINTS_TO_VISUALISE}",
        color_discrete_sequence=px.colors.qualitative.G10,
    )
    fig_tsne.write_html(
        OUTPUT_FOLDER
        + f"tsne2d_perp_{PERPLEXITY}_points_{DATA_POINTS_TO_VISUALISE}.html"
    )

    fig_tsne_3d = px.scatter_3d(
        tsne_dataframe.head(DATA_POINTS_TO_VISUALISE),
        x="tSNE1",
        y="tSNE2",
        z="tSNE3",
        color="label",
        title=f"t-SNE Perplexity: {PERPLEXITY} Data points: {DATA_POINTS_TO_VISUALISE}",
        color_discrete_sequence=px.colors.qualitative.G10,
    )
    fig_tsne_3d.write_html(
        OUTPUT_FOLDER
        + f"tsne3d_perp_{PERPLEXITY}_points_{DATA_POINTS_TO_VISUALISE}.html"
    )

    fig_pca = px.scatter(
        pca_dataframe.head(DATA_POINTS_TO_VISUALISE),
        x="PCA1",
        y="PCA2",
        color="label",
        title=f"PCA Data points: {DATA_POINTS_TO_VISUALISE}",
        color_discrete_sequence=px.colors.qualitative.G10,
    )
    fig_pca.write_html(OUTPUT_FOLDER + f"pca2d_points_{DATA_POINTS_TO_VISUALISE}.html")

    fig_pca_3d = px.scatter_3d(
        pca_dataframe.head(DATA_POINTS_TO_VISUALISE),
        x="PCA1",
        y="PCA2",
        z="PCA3",
        color="label",
        title=f"PCA Data points: {DATA_POINTS_TO_VISUALISE}",
        color_discrete_sequence=px.colors.qualitative.G10,
    )
    fig_pca_3d.write_html(
        OUTPUT_FOLDER + f"pca3d_points_{DATA_POINTS_TO_VISUALISE}.html"
    )


def check_folder():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(current_dir, OUTPUT_FOLDER)
    if not os.path.exists(abs_path):
        os.makedirs(abs_path)


if __name__ == "__main__":
    main()
