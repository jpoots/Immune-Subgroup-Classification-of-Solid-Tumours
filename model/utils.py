import pandas as pd
import numpy as np

# utility functions for use throughout the project

FILE_LOCATION = "data.csv"

# loads the data into a panda dataframe and returns the transposed data fram
def get_data():
    data = pd.read_csv(FILE_LOCATION, index_col=0)
    data = data.T
    return data

# splits the data into the components of ID, features, classification and gene names
def split_data(data):
    idx = [sample_id for sample_id in data.index]
    genes = [gene for gene in data.columns.values]
    classification = np.array([int(sample[-1]) - 1 for sample in data.index.values])
    features = data.to_numpy()
    return idx, features, classification, genes
