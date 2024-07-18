from flask import request
from functools import wraps
from werkzeug import exceptions
from fastjsonschema import compile, JsonSchemaValueException

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
                        "minProperties": 440,
                        "maxProperties": 440,
                    },
                },
                "required": ["sampleID", "genes"],
            },
        },
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
