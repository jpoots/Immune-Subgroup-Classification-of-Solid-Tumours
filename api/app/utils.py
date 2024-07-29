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


def gene_preprocessing(full_analysis, features):
    # if being sent back in JSON or if part of full analysis
    if not full_analysis:
        features = features.T.to_dict()
        returnData = []
        for sample in features.keys():
            returnData.append({"sampleID": sample, "genes": features[sample]})
    else:
        # split data for further processing
        idx = [sample_id for sample_id in features.index]
        genes = [gene for gene in features.columns.values]
        features = features.values.tolist()

        returnData = {
            "ids": idx,
            "gene_names": genes,
            "features": features,
        }
    return returnData


NUM_GENES = 440
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
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


def csv_func(filepath):
    try:
        # is file in request and is it a valid CSV
        data = pd.read_csv(filepath, index_col=0)
        data = data.T
        data = data[ORDERED_GENE_DF.columns.intersection(data.columns)]
    except Exception as e:
        raise BadRequest(
            body='Sample files should be valid CSV or TXT files attached as "samples"'
        )

    # drop empty rows
    data.dropna(how="all", inplace=True)
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
    if n_row != 440 or n_row == 0:
        raise BadRequest(
            body="Sample files should contain 440 genes and at least 1 sample"
        )

    # impute missing values - note, imputation could've been done in pipeline but seperation allows us to keep the gene expression values
    features = data.values
    imp = IterativeImputer().set_output(transform="pandas")
    features = imp.fit_transform(data)

    return {"features": features, "invalid": invalid, "type_ids": type_ids}


def json_func(data):
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
