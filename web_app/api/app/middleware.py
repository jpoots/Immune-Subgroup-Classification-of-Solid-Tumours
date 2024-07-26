from flask import request
from functools import wraps
from werkzeug import exceptions
from fastjsonschema import compile, JsonSchemaValueException
import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import joblib
import os

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


# decorator for parsing the JSON object
def parse_json(f):
    @wraps(f)
    def _parse_json(*args, **kwargs):
        # handles error automatically if the request isn't JSON
        data = request.get_json()

        # validate jsona and raise exception if invalid
        try:
            VALIDATOR(data)
        except JsonSchemaValueException as e:
            raise exceptions.BadRequest(e.message)

        if "perplexity" in data:
            request.perplexity = data["perplexity"]
        if "interval" in data:
            request.interval = int(data["interval"])

        data = data["samples"]

        # extract data from JSON. List comp not used for efficieny with large data
        idx, features = [], []
        for sample in data:
            idx.append(sample["sampleID"])
            features.append(list(sample["genes"].values()))

        request.data = data
        request.idx = idx
        request.features = features

        return f(*args, **kwargs)

    return _parse_json


# decorator for parsing a CSV
def parse_csv(f):
    @wraps(f)
    def _parse_csv(*args, **kwargs):

        try:
            # is file in request and is it a valid CSV
            file = request.files["samples"]
            data = pd.read_csv(file, index_col=0)
            data = data.T
            data = data[ORDERED_GENE_DF.columns.intersection(data.columns)]
        except Exception as e:
            raise exceptions.BadRequest(
                'Sample files should be valid CSV or TXT files attached as "samples"'
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
            raise exceptions.BadRequest(
                "Sample files should contain 440 genes and at least 1 sample"
            )

        # impute missing values - note, imputation could've been done in pipeline but seperation allows us to keep the gene expression values
        features = data.values
        imp = IterativeImputer().set_output(transform="pandas")
        features = imp.fit_transform(data)

        request.features = features
        request.invalid = invalid
        request.typeids = type_ids
        return f(*args, **kwargs)

    return _parse_csv
