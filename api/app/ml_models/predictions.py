import joblib
import os
import numpy as np
import pandas

"""
Functions for using the trained ML model (and bootstrap models) to attain predictions, probabilties and confidence intervals
"""

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# the location of the trained mdeol
MODEL_LOCATION = os.path.join(current_dir, "model.pkl")
BOOTSTRAP_LOCATION = os.path.join(current_dir, "bootstrap_models.pkl")

# load models
MODEL = joblib.load(MODEL_LOCATION)
BOOTSTRAP_MODELS = joblib.load(BOOTSTRAP_LOCATION)

# the classification confident prediction limit
QC_THRESHOLD = 0.915


def predict(features):
    """
    Forms predictions and probailties given features as input
    Args:
    features: A 2D numpy array or list of the 440 relevant gene expression values FPKM normalised

    Returns:
        predictions: a list of predictions
        prediction_probs: a list of prediction probs for each sample
        invalid: the number of invalid samples
    """

    # get probabilites and mark those below QC
    prediction_probs = MODEL.predict_proba(features)
    nc_indicies = [
        index
        for index, prob in enumerate(prediction_probs)
        if np.amax(prob) < QC_THRESHOLD
    ]

    # make prediction
    predictions = MODEL.predict(features).tolist()

    # filter out NC probs
    predictions = [
        prediction + 1 if index not in nc_indicies else "NC"
        for index, prediction in enumerate(predictions)
    ]

    invalid = len(nc_indicies)
    return predictions, prediction_probs.tolist(), invalid


def confidence_intervals(features, interval):
    """
    Calculates prediction intervals given an interval and feature set
    Args:
    features: A 2D numpy array or list of the 440 relevant gene expression values FPKM normalised
    interval: the percentage confidence interval (e.g 95)

    Returns:
        intervals: a list as [min, lower percentile, median, upper percentile, max]
    """

    # calcuate upper and lower percentiel values
    bound = 100 - interval
    upper = 100 - bound / 2
    lower = bound / 2

    all_classified = []
    for model in BOOTSTRAP_MODELS:
        # predict
        all_probs = model.predict_proba(features)

        # extract max prob for each prediction
        classified_probs = []
        for probs in all_probs:
            classified_prob = np.amax(probs)
            classified_probs.append(classified_prob)
        all_classified.append(classified_probs)

    # transpose all classified as an array
    all_classified = np.transpose(np.array(all_classified))

    # pull out interval data and append to intervals
    intervals = [
        np.percentile(classified, [0, lower, 50, upper, 100])
        for classified in all_classified
    ]
    return intervals


def probability(features):
    """
    Calculates probabilites of each sub group given a list of featues
    Args:
    features: A 2D numpy array or list of the 440 relevant gene expression values FPKM normalised
    interval: the percentage confidence interval (e.g 95)

    Returns:
        intervals: a list as [min, lower percentile, median, upper percentile, max]
    """
    return MODEL.predict_proba(features).tolist
