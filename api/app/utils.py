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

"""
utility functions to be used throughout the project
"""

# the number of genes
NUM_GENES = 440
# current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# the path to the pickle file containing the gene names
ORDERED_GENE_DF = joblib.load(os.path.join(CURRENT_DIR, "ordered_gene_names.pkl"))

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


def parse_csv(filepath):
    """Parses a csv from a file path and returns key info as a dict
    Args:
    filepath: The file path to read from

    Returns:
        A dict including the features dataframe, type IDs and the number of invlaid samples

    Raises:
        BadRequest: The file is missing from the request or the sample file is invalid
    """
    try:
        # is file in request and is it a valid CSV
        data = pd.read_csv(filepath, index_col=0)
        data = data.T
        # extract valid data
        data = data[ORDERED_GENE_DF.columns.intersection(data.columns)]
    except Exception as e:
        # if file could not be succesfully read
        raise BadRequest(
            body='Sample files should be valid CSV or TXT files attached as "samples"'
        )

    # drop empty rows
    data.dropna(how="all", inplace=True)

    # extract type ids or set to none
    if "TYPEID" in data.columns:
        data = data.fillna({"TYPEID": "None"})
    else:
        data["TYPEID"] = "None"
    type_ids = data.pop("TYPEID").values

    # drop rows with more than 2 empty genes, calculate diff
    original_size = data.shape[0]
    data.dropna(thresh=438, inplace=True)
    invalid = original_size - data.shape[0]

    # is data of valid shape
    n_col, n_row = data.shape[0], data.shape[1]
    if n_row != 440 or n_col == 0:
        raise BadRequest(
            body="Sample files should contain 440 genes and at least 1 sample"
        )

    # impute missing values - note, imputation could've been done in pipeline but seperation allows us to return the imputed gene expression values to the client
    imp = IterativeImputer().set_output(transform="pandas")
    data = imp.fit_transform(data)

    gene_names = data.columns.tolist()
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
        BadRequest: The JSON is invalid
    """
    # validate jsona and raise exception if invalid
    perplexity = None
    interval = None

    try:
        VALIDATOR(data)
    except JsonSchemaValueException as e:
        raise BadRequest(body=e.message)

    try:
        if "perplexity" in data:
            perplexity = int(data["perplexity"])
        if "interval" in data:
            interval = int(data["interval"])
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
    }


"""TSNE_SCHEMA = {
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sampleID": {"type": "string"},
                    "tsne": {
                        "type": "array",
                        "items": [
                            {"type": "number"},
                        ],
                        "example": [1, 2, 3],
                    },
                },
            },
        },
        "status": {"type": "string"},
    },
}


CONFIDENCE_SCHEMA = {
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "lower": {"type": "number"},
                    "max": {"type": "number"},
                    "median": {"type": "number"},
                    "min": {"type": "number"},
                    "sampleID": {"type": "string"},
                    "upper": {"type": "number"},
                },
            },
        },
        "status": {"type": "string"},
    },
}

ANALYSIS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "data": {
            "type": "object",
            "properties": {
                "invalid": {"type": "integer"},
                "nc": {"type": "integer"},
                "samples": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "genes": {
                                "type": "object",
                                "properties": {
                                    "gene_name": {"type": "number"},
                                },
                            },
                            "pca": {
                                "type": "array",
                                "items": {"type": "number", "example": [1, 2, 3]},
                            },
                            "prediction": {"type": "integer"},
                            "probs": {
                                "type": "array",
                                "items": {
                                    "type": "number",
                                    "example": [1, 2, 3, 4, 5, 6],
                                },
                            },
                            "sampleID": {"type": "string"},
                            "typeid": {"type": "string"},
                        },
                    },
                },
            },
        },
        "status": {"type": "string"},
    },
}

INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "samples": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sampleID": {
                        "type": "string",
                    },
                    "genes": {
                        "type": "object",
                        "properties": {
                            "gene_name": {"type": "number"},
                        },
                    },
                },
            },
        },
        "interval": {"type": "integer", "minimum": 0, "maximum": 100},
        "perplexity": {"type": "integer"},
    },
    "required": ["samples"],
}
"""

"""def generate_get_results_schema(return_schema):
    return {
        "tags": ["Get results"],
        "summary": "Get analysis results",
        "produces": ["application/json"],
        "responses": {
            200: {
                "description": "The current request is ongoing",
                "schema": {
                    "type": "object",
                    "properties": {"status": {"type": "string", "example": "PENDING"}},
                },
            },
            201: {
                "description": "Analysis successfully completed",
                "schema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "lower": {"type": "number"},
                                    "max": {"type": "number"},
                                    "median": {"type": "number"},
                                    "min": {"type": "number"},
                                    "sampleID": {"type": "string"},
                                    "upper": {"type": "number"},
                                },
                            },
                        },
                        "status": {"type": "string"},
                    },
                },
            },
            400: {
                "description": "Task failed due to an issue with client input",
            },
            500: {"description": "An interval server error has occured"},
        },
        http://python-tool.net/transform/to-yaml/
    }"""
