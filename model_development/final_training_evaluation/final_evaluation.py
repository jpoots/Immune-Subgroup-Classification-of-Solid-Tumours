import joblib
import numpy as np
import matplotlib.pyplot as plt
import sys
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
)

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils import (
    get_data,
    split_data,
    analyse_prediction_results,
    predict_with_qc,
    RANDOM_STATE,
    TEST_SIZE,
)

"""
Performs a final evaulation on the test set of the saved model. QC thresholding is applied and mismatch and nc analysis output to a csv
"""

# the location of the model
MODEL_FILE_NAME = "./trained_models/model.pkl"
# the location to store the probability analysis
PROBS_FOLDER_NAME = "./prob_analysis"
# the QC threshold to use
QC_THRESHOLD = 0.92


def main():
    """
    Loads the model and test data, splits it appropriately, performs predictiosn on the test set and analyses performance including NC and missmatch results
    """

    # load data
    data = get_data()
    idx, x, y, _genes = split_data(data)

    # get test set
    _x_train, x_test, _y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    # making and x and y with sample ID linked for analysis of probs
    y = [(sample_id, subgroup) for sample_id, subgroup in zip(idx, y)]
    x = [(sample_id, features) for sample_id, features in zip(idx, x)]

    # get test set labelled
    _x_train, x_test_labelled, _y_train, y_test_labelled = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        stratify=[label for _id, label in y],
        random_state=RANDOM_STATE,
    )

    # load model
    loaded_model = joblib.load(MODEL_FILE_NAME)

    # analyse nc results
    extract_nc_probs(loaded_model, QC_THRESHOLD, x_test_labelled)

    # analyse missmach results
    extract_missmatch_probs(loaded_model, x_test_labelled, y_test_labelled)

    # predict and evaluate
    predictions, true, num_removed = predict_with_qc(
        loaded_model, QC_THRESHOLD, x_test, y_test
    )
    evaluate_performance(true, predictions, num_removed)

    # show plot
    plt.show()


def extract_nc_probs(pipe, threshold, x):
    """Extracts NC samples, their classification and their max probs to a CSV
    Args:
        pipe: The model pipeline
        threshold: the models prediction threshold
        x: the features labelled
    """

    features = [features for _id, features in x]

    # predict
    prediction_probs = pipe.predict_proba(features)
    predictions = pipe.predict(features)

    # filter to max probs
    max_probs_test = np.amax(prediction_probs, axis=1)
    nc_indicies = [i for i, prob in enumerate(max_probs_test) if prob < threshold]

    # get the max probs that are nc
    nc_probabilities = max_probs_test[nc_indicies]

    # get the nc predictions and undo 0 index
    nc_predictions = predictions[nc_indicies]
    nc_predictions = [pred + 1 for pred in nc_predictions]

    # get nc ids
    nc_ids = [x[i][0] for i in nc_indicies]

    # build dataframe and write to file
    nc_df = pd.DataFrame(data=nc_probabilities, index=nc_ids, columns=["max_prob"])
    nc_df.index.name = "sampleID"
    nc_df.insert(loc=1, column="prediction", value=nc_predictions)
    nc_df.to_csv(f"{PROBS_FOLDER_NAME}/nc.csv")


def extract_missmatch_probs(pipe, x, y):
    """Extracts missmatched samples, their classification and their max probs to a CSV
    Args:
        pipe: The model
        x: the features labelled by sample id
        y: target labels labelled by sample id
    """

    # extract feautres and subgroup labels
    features = [features for _id, features in x]
    subgroups = [group for _id, group in y]

    # preditc
    prediction_probs = pipe.predict_proba(features)
    predictions = pipe.predict(features)

    # get mismatched indicies and max probs
    max_probs = np.amax(prediction_probs, axis=1)
    mismatched_indicies = [
        i
        for i, (prediction, subgroup) in enumerate(zip(predictions, subgroups))
        if prediction != subgroup
    ]

    # get data from mismatched indicies
    mismatched_probs = [max_probs[i] for i in mismatched_indicies]
    mismatched_ids = [y[i][0] for i in mismatched_indicies]
    mismatched_predictions = predictions[mismatched_indicies]
    mismatched_predictions = [pred + 1 for pred in mismatched_predictions]

    # build dataframe and write to file
    df = pd.DataFrame(data=mismatched_probs, index=mismatched_ids, columns=["max_prob"])
    df.index.name = "sampleID"
    df.insert(loc=1, column="prediction", value=mismatched_predictions)
    df.to_csv(f"{PROBS_FOLDER_NAME}/mismatch.csv")


def evaluate_performance(true, predictions, num_removed):
    """Evaluates performance
    Args:
        true: target labels
        predictions: model predictions
        num_removed: the number of sampels removed as NC
    """
    print(f"Removed: {num_removed}")
    print(f"QC Threshold: {QC_THRESHOLD}")
    analyse_prediction_results(predictions, true)
    cf = ConfusionMatrixDisplay.from_predictions(true, predictions)


if __name__ == "__main__":
    main()
