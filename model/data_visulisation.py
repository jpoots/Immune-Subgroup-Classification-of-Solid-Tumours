import numpy as np
import pandas as pd
import plotly.express as px
import os
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from utils import get_data, split_data

DATA_POINTS_TO_VISUALISE = 9000
PERPLEXITY = 500
OUTPUT_FOLDER = "./data_plots/"

data = get_data()
id_list, features, classification_list, genes = split_data(data)

classification_list = [str(classification) for classification in classification_list]

# normalise features for PCA and t-SNE
features = StandardScaler().fit_transform(features)

# high component PCA (because it's fast) and t-SNE
pca_canc = PCA(n_components=3,random_state=42)
tsne_canc = TSNE(n_components=3, perplexity=PERPLEXITY,random_state=42)

# perform analysis
principle_components = pca_canc.fit_transform(features)
tsne_components = tsne_canc.fit_transform(features)

# note how well the PCA axis explain variance
print(pca_canc.explained_variance_ratio_)

# load into pd dataframe
pca_dataframe = pd.DataFrame(principle_components, columns=["PCA1", "PCA2", "PCA3", "PCA4", "PCA5", "PCA6", "PCA7", "PCA8", "PCA9", "PCA10"], index=id_list)
pca_dataframe["label"] = classification_list

tsne_dataframe = pd.DataFrame(tsne_components, columns=["tSNE1", "tSNE2", "tSNE3"], index=id_list)
tsne_dataframe["label"] = classification_list

print(tsne_dataframe.tail())

# plot my interactive figures using plotly
fig_tsne = px.scatter(tsne_dataframe.head(DATA_POINTS_TO_VISUALISE), x="tSNE1", y="tSNE2", color="label", title=f"t-SNE Perplexity: {PERPLEXITY} Data points: {DATA_POINTS_TO_VISUALISE}", color_discrete_sequence=px.colors.qualitative.G10)
fig_tsne.show()
fig_tsne.write_html(OUTPUT_FOLDER + f"tsne2d_perp_{PERPLEXITY}_points_{DATA_POINTS_TO_VISUALISE}.html")

fig_tsne_3d= px.scatter_3d(tsne_dataframe.head(DATA_POINTS_TO_VISUALISE), x="tSNE1", y="tSNE2", z="tSNE3", color="label", title=f"t-SNE Perplexity: {PERPLEXITY} Data points: {DATA_POINTS_TO_VISUALISE}", color_discrete_sequence=px.colors.qualitative.G10)
fig_tsne_3d.show()
fig_tsne_3d.write_html(OUTPUT_FOLDER + f"tsne3d_perp_{PERPLEXITY}_points_{DATA_POINTS_TO_VISUALISE}.html")

fig_pca = px.scatter(pca_dataframe.head(DATA_POINTS_TO_VISUALISE), x="PCA1", y="PCA2", color="label", title=f"PCA Data points: {DATA_POINTS_TO_VISUALISE}", color_discrete_sequence=px.colors.qualitative.G10)
fig_pca.show()
fig_pca.write_html(OUTPUT_FOLDER + f"pca2d_points_{DATA_POINTS_TO_VISUALISE}.html")

fig_pca_3d = px.scatter_3d(pca_dataframe.head(DATA_POINTS_TO_VISUALISE), x="PCA1", y="PCA2", z="PCA3",  color="label", title=f"PCA Data points: {DATA_POINTS_TO_VISUALISE}", color_discrete_sequence=px.colors.qualitative.G10)
fig_pca_3d.show()
fig_pca_3d.write_html(OUTPUT_FOLDER + f"pca3d_points_{DATA_POINTS_TO_VISUALISE}.html")

