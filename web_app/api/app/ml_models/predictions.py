import joblib
import os
import numpy as np

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

MODEL_LOCATION = os.path.join(current_dir, "model.pkl")
BOOTSTRAP_LOCATION = os.path.join(current_dir, "bootstrap_models.pkl")

# load models
model = joblib.load(MODEL_LOCATION)
bootstrap_models = joblib.load(BOOTSTRAP_LOCATION)


def predict(features):

    # get probabilites and mark those below QC
    qc_threshold = 0.982
    prediction_probs = model.predict_proba(features)
    nc_indicies = [
        index
        for index, prob in enumerate(prediction_probs)
        if np.amax(prob) < qc_threshold
    ]

    # make prediction
    predictions = model.predict(features).tolist()
    predictions = [
        prediction + 1 if index not in nc_indicies else "NC"
        for index, prediction in enumerate(predictions)
    ]

    return predictions, prediction_probs.tolist(), len(nc_indicies)


def confidence_intervals(features):

    all_classified = []

    for model in bootstrap_models:
        all_probs = model.predict_proba(features)

        classified_probs = []
        for probs in all_probs:
            classified_prob = np.amax(probs)
            classified_probs.append(classified_prob)
        all_classified.append(classified_probs)

    all_classified = np.transpose(np.array(all_classified))
    intervals = [
        np.percentile(classified, [0, 2.5, 50, 97.5, 100])
        for classified in all_classified
    ]
    return intervals


def probability(features):
    return model.predict_proba(features).tolist
