import joblib
import sklearn
import numpy as np
import matplotlib.pyplot as plt
import sys
from sklearn.calibration import CalibrationDisplay
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
)


# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils.utils import (
    get_data,
    split_data,
    predict_with_qc,
    analyse_prediction_results,
)

"""
A script for running the trained model with a variety of QC thresholds on a validation set
"""

RANDOM_STATE = 42
TEST_SIZE = 0.2
MODEL_FILE_NAME = "./trained_models/model.pkl"
QC_THRESHOLD = 0.87


def main():
    """
    Splits data, loads model, predicts and evaulates performance
    """
    np.random.seed(RANDOM_STATE)

    data = get_data()
    idx, x, y, _genes = split_data(data)

    # remove test set and get validtion set
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y
    )
    x_train, x_val, y_train, y_val = train_test_split(
        x_train, y_train, test_size=TEST_SIZE, stratify=y_train
    )

    # pulls the model in
    loaded_model = joblib.load(MODEL_FILE_NAME)

    # make predictiosn and evaluate
    predictions, true, num_removed = predict_with_qc(
        loaded_model, QC_THRESHOLD, x_val, y_val
    )
    evaluate_performance(predictions, true, num_removed)

    plt.show()


def evaluate_performance(true, predictions, num_removed):
    """Evaluates a models performance and displays a confusion matrix
    Args:
    true: The target labels
    predictions: the models predictions
    num_removed: the number of results removed by the QC threshold
    """
    print(f"Removed: {num_removed}")
    print(f"QC Threshold: {QC_THRESHOLD}")
    analyse_prediction_results(predictions, true)
    cf = ConfusionMatrixDisplay.from_predictions(true, predictions)


if __name__ == "__main__":
    main()
