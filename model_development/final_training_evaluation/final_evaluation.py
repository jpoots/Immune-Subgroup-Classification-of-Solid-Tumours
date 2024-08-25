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
    predict_with_qc_and_predom,
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
    predictions, true, num_removed, num_predom = predict_with_qc_and_predom(
        loaded_model, QC_THRESHOLD, x_test, y_test
    )
    evaluate_performance(true, predictions, num_removed, num_predom)

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

    prediction_probs = pipe.predict_proba(features)
    predictions = pipe.predict(features)

    # filter to max probs
    nc_indicies, predom_indicies = [], []
    nc_probabilities, predom_prob1, predom_prob2, predom_class1, predom_class2 = (
        [],
        [],
        [],
        [],
        [],
    )

    # for each probability
    for index, prob in enumerate(prediction_probs):
        # get max
        max_prob = np.amax(prob)

        # if nc
        if max_prob < threshold:

            # if below thresh but sum of two highest above thresh and max above 0.5 (random guess)
            if (max_prob + np.sort(prob)[-2]) > threshold and max_prob > 0.5:
                predom_indicies.append(index)

                # sort indicies
                sorted_indicies = np.argsort(prob)

                # get the two highest classes
                predom_class1.append(sorted_indicies[-1] + 1)
                predom_class2.append(sorted_indicies[-2] + 1)

                # get the two highest probs
                predom_prob1.append(max_prob)
                predom_prob2.append(np.sort(prob)[-2])

            else:
                # note indicies and max prob
                nc_indicies.append(index)
                nc_probabilities.append(max_prob)

    # get the nc predictions and undo 0 index
    nc_predictions = predictions[nc_indicies]
    nc_predictions = [pred + 1 for pred in nc_predictions]

    # get nc ids
    nc_ids = [x[i][0] for i in nc_indicies]
    predom_ids = [x[i][0] for i in predom_indicies]

    # build dataframe and write to file
    nc_df = pd.DataFrame(data=nc_probabilities, index=nc_ids, columns=["max_prob"])
    nc_df.index.name = "sampleID"
    nc_df.insert(loc=1, column="prediction", value=nc_predictions)
    nc_df.to_csv(f"{PROBS_FOLDER_NAME}/nc.csv")

    # build dataframe and write to file
    predom_df = pd.DataFrame(index=predom_ids)
    predom_df.index.name = "sampleID"
    predom_df.insert(loc=0, column="prob1", value=predom_prob1)
    predom_df.insert(loc=1, column="prob2", value=predom_prob2)
    predom_df.insert(loc=2, column="class1", value=predom_class1)
    predom_df.insert(loc=3, column="class2", value=predom_class2)
    predom_df.to_csv(f"{PROBS_FOLDER_NAME}/predom.csv")


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


def evaluate_performance(true, predictions, num_removed, num_predom):
    """Evaluates performance
    Args:
        true: target labels
        predictions: model predictions
        num_removed: the number of sampels removed as NC
        num_predom : the number of predominant samples
    """
    print(f"Removed: {num_removed}")
    print(f"Predominant: {num_predom}")
    print(f"QC Threshold: {QC_THRESHOLD}")
    analyse_prediction_results(predictions, true)
    cf = ConfusionMatrixDisplay.from_predictions(true, predictions)


if __name__ == "__main__":
    main()
