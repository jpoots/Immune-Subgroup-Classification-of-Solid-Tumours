from flask import request
from functools import wraps
from werkzeug import exceptions
from fastjsonschema import compile, JsonSchemaValueException
import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import joblib
import os
from .errors.BadRequest import BadRequest
import numpy as np

"""
utility functions to be used throughout the project
"""

# the number of genes
NUM_GENES = 440
# current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# gene list file
GENE_LIST_FILE_LOCATION = os.path.join(CURRENT_DIR, "gene_list.csv")

IMPUTER = joblib.load(os.path.join(CURRENT_DIR, "mice.pkl"))

gene_list_csv = pd.read_csv(GENE_LIST_FILE_LOCATION)
gene_list_csv.columns = [
    str(column).strip().upper() for column in gene_list_csv.columns
]

# defining as constants for json validation, much less code than manual validation
SCHEMA = {
    "type": "object",
    "properties": {
        "samples": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sampleID": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "genes": {
                        "type": "object",
                        "patternProperties": {
                            "^(?!\s*$).+": {"type": "number"},
                        },
                        "additionalProperties": False,
                        "minProperties": NUM_GENES,
                        "maxProperties": NUM_GENES,
                    },
                },
                "required": ["sampleID", "genes"],
            },
        },
        "interval": {"type": "integer", "minimum": 0, "maximum": 100},
        "perplexity": {"type": "integer"},
    },
    "required": ["samples"],
}
VALIDATOR = compile(SCHEMA)


def parse_csv(filepath, delimiter):
    """Parses a file from a file path and returns key info as a dict
    Args:
    filepath: The file path to read from
    delimiter: The files delimiter

    Returns:
        A dict including the features dataframe, type IDs and the number of invlaid samples

    Raises:
        BadRequest: The file is missing from the request or the sample file is invalid
    """
    try:
        # is file in request and is it a valid CSV
        data = pd.read_csv(filepath, index_col=0, delimiter=delimiter)

        data = data.T

        data.columns = data.columns.str.upper()
        data.columns = data.columns.str.strip()

        # extract valid data
        data = data[gene_list_csv.columns.intersection(data.columns)]

    except Exception as e:
        # if file could not be succesfully read
        raise BadRequest(
            body='Sample files should be valid CSV or TXT files attached as "samples" and a delimiter as "delimiter"'
        )

    # drop empty rows
    data.dropna(how="all", inplace=True)

    # extract type ids or set to none
    if "TYPEID" in data.columns:
        data = data.fillna({"TYPEID": "Unknown"})
    else:
        data["TYPEID"] = "None"
    type_ids = data.pop("TYPEID").values

    # drop rows with more than 10 empty genes, calculate diff
    original_size = data.shape[0]
    data.dropna(thresh=430, inplace=True)
    invalid = original_size - data.shape[0]

    # ensure all data is numeric, e.g no strings or the like in feature columns
    try:
        data = data.astype("float64")
    except Exception as e:
        raise BadRequest(body="Gene columns should contain only numeric data")

    # is data of valid shape
    n_col, n_row = data.shape[0], data.shape[1]
    print(n_row)
    if n_row != 440 or n_col == 0:
        raise BadRequest(
            body="Sample files should contain 440 genes and at least 1 sample"
        )

    gene_names = data.columns.tolist()

    # impute missing values - note, imputation could've been done in pipeline but seperation allows us to return the imputed gene expression values to the client
    data = IMPUTER.transform(data)

    ids = data.index.values.tolist()
    features = data.to_numpy()

    return {
        "ids": ids,
        "features": features,
        "invalid": invalid,
        "gene_names": gene_names,
        "type_ids": type_ids,
    }


def parse_json(data):
    """Parses a json request sent to the api for processing

    Args:
    data: The JSON data to process

    Returns:
        A dict including the features dataframe, type IDs and the number of invlaid samples

    Raises:
        BadRequest: The JSON is invalid or missing
    """
    # validate json and raise exception if invalid
    perplexity = False
    interval = False
    num_dimensions = False

    try:
        VALIDATOR(data)
    except JsonSchemaValueException as e:
        raise BadRequest(body=e.message)

    try:
        if "perplexity" in data:
            perplexity = int(data["perplexity"])
        if "interval" in data:
            interval = int(data["interval"])
        if "numDimensions" in data:
            num_dimensions = int(data["numDimensions"])
    except:
        raise BadRequest("Recieved invalid value for option")

    data = data["samples"]

    # extract data from JSON. List comp not used for efficieny with large data
    idx, features = [], []
    for sample in data:
        idx.append(sample["sampleID"])
        features.append(list(sample["genes"].values()))

    return {
        "features": features,
        "ids": idx,
        "data": data,
        "perplexity": perplexity,
        "interval": interval,
        "num_dimensions": num_dimensions,
    }


def validate_csv_upload(request):
    """
    Takes a request and validates for samples file and delimiter

    Args:
    request: the request object

    Returns:
    file: the samples file
    delimiter: the file delimiter
    """
    if "samples" not in request.files:
        raise exceptions.BadRequest("File missing")
    try:
        delimiter = request.form["delimiter"]
        if len(delimiter) == 0:
            raise Exception()
    except Exception as e:
        raise exceptions.BadRequest("Missing delimiter")

    file = request.files["samples"]
    return file, delimiter


def delete_file_on_failure(self, exc, task_id, args, kwargs, einfo):
    """
    Takes args from a celery task given a file name as input and deletes the file on return.

    Args:
    See the celery on_return documentation
    """
    os.remove(args[0])
    return


def reload_gene_list():
    """Reloads the in memory gene list from the CSV file"""
    global gene_list_csv
    gene_list_csv = pd.read_csv(GENE_LIST_FILE_LOCATION)
    gene_list_csv.columns = [
        str(column).strip().upper() for column in gene_list_csv.columns
    ]
    return
