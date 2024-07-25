import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import MinMaxScaler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    balanced_accuracy_score,
)
import sys

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils.utils import (
    get_data,
    split_data,
    analyse_prediction_results,
    predict_with_qc,
)

FILE_NAME = "./trained_models/model.pkl"
RANDOM_STATE = 42

# param for gb model
MODEL_PARAMS = {
    "max_iter": 1000,
    "learning_rate": 0.1,
    "max_depth": 75,
    "max_leaf_nodes": 41,
    "min_samples_leaf": 20,
}
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

QC_THRESHOLD = 0.989


def main():
    np.random.seed(RANDOM_STATE)

    data = get_data()
    _idx, x, y, _genes = split_data(data)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y
    )

    pipe = build_model(x_train, y_train)

    # get prediction probs for test
    predictions, true, num_removed = predict_with_qc(pipe, QC_THRESHOLD, x_test, y_test)

    print("TRAINING COMPLETE SAVING")

    # saving and testing save successful
    joblib.dump(pipe, FILE_NAME)
    print("SAVE SUCCESSFUL")

    # sanity check the save
    loaded_model = joblib.load(FILE_NAME)
    loaded_model.predict(x_test)

    print(f"Removed: {num_removed}")
    analyse_prediction_results(true, predictions)
    ConfusionMatrixDisplay.from_predictions(true, predictions)
    plt.show()


def build_model(x, y):
    # define model to train
    model = HistGradientBoostingClassifier(**MODEL_PARAMS)

    # data scaler and generic pipeleine
    scaler = MinMaxScaler()

    # set up samplers and fit
    rus = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE)
    smt = SMOTE(sampling_strategy=OVER_SAMPLE)

    # set up pipeline and fit
    pipe = ImbPipeline(
        steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", model)]
    )
    pipe.fit(x, y)

    return pipe


if __name__ == "__main__":
    main()
