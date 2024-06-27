import pandas as pd
import numpy as np
import os

FILE_LOCATION = "data.csv"

def get_data():
    data = pd.read_csv(FILE_LOCATION, index_col=0)
    data = data.T
    return data

def split_data(data):
    idx = [sample_id for sample_id in data.index]
    genes = [gene for gene in data.columns.values]
    classification = np.array([int(sample[-1]) - 1 for sample in data.index.values])
    features = data.to_numpy()
    return idx, features, classification, genes

