import pandas as pd
from flask import Flask, render_template, request, session, redirect, jsonify
from requests.exceptions import HTTPError
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import numpy as np

def read_data(): 
    file = request.files["samples"]
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
    request.data = data

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

def validate_data():
    try:
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

        data = {
            "ids": idx,
            "gene_names": genes,
            "features": features,
            "invalid": invalid
        }

        request.data = returnData

    except Exception as e:
        print(e)
        return ("Bad request", 400)



