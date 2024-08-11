import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from xgboost import XGBClassifier
from sklearn.preprocessing import MinMaxScaler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
from sklearn.calibration import CalibratedClassifierCV
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.metrics import ConfusionMatrixDisplay

import sys

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils.utils import (
    get_data,
    split_data,
    analyse_prediction_results,
    predict_with_qc,
    RANDOM_STATE,
)

FILE_NAME = "./trained_models/model.pkl"

TEST_SIZE = 0.2

# define sample strategy
UNDER_SAMPLE = {
    0: 1000,
    1: 1000,
    2: 1000,
}

OVER_SAMPLE = {
    3: 1000,
    4: 1000,
    5: 1000,
}


def main():
    data = get_data()
    _idx, x, y, _genes = split_data(data)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    x_train, x_test, y_train, y_test = train_test_split(
        x_train, y_train, test_size=0.2, stratify=y_train, random_state=RANDOM_STATE
    )

    pipe = build_model(x_train, y_train)

    # get prediction probs for test
    predictions, true, num_removed = predict_with_qc(pipe, 0, x_test, y_test)

    # saving and testing save successful
    joblib.dump(pipe, FILE_NAME)
    print("SAVE SUCCESSFUL")

    # sanity check the save
    loaded_model = joblib.load(FILE_NAME)
    loaded_model.predict(x_test)

    print(f"Removed: {num_removed}")
    analyse_prediction_results(predictions, true)
    ConfusionMatrixDisplay.from_predictions(true, predictions)


def build_model(x, y):
    """Trains a gradient boosting model on the data using sampling
    Args:
    x: the training data
    y: the training data

    Returns:
    pipe: a trained model
    """
    # define model to train
    model = HistGradientBoostingClassifier(
        max_iter=2000,
        learning_rate=0.1,
        max_depth=50,
        max_leaf_nodes=31,
        min_samples_leaf=30,
        random_state=RANDOM_STATE,
    )

    # data scaler and generic pipeleine
    scaler = MinMaxScaler()

    # set up samplers and fit
    rus = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE, random_state=RANDOM_STATE)
    smt = SMOTE(sampling_strategy=OVER_SAMPLE, random_state=RANDOM_STATE)

    # set up pipeline and fit
    pipe = ImbPipeline(
        steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", model)]
    )
    pipe = pipe.fit(x, y)
    return pipe


if __name__ == "__main__":
    main()
