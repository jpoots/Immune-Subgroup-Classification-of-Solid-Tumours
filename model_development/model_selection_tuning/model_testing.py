import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBClassifier
from imblearn.under_sampling import RandomUnderSampler

from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
)
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import sys

sys.path.append("..")
from utils import (
    get_data,
    split_data,
    print_cv_results,
    analyse_prediction_results,
    predict_with_qc,
    RANDOM_STATE,
    SCORING_CV,
    TEST_SIZE,
)

"""
This script is used for testing tuned models. While the current state reflects only two models, this contained many models throughout the development process.
This script cross validates models and valdiates on a train test split
"""

# the QC threshold to use in validation evaluation
QC_THRESHOLD = 0.915

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

# set up samples
RUS = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE, random_state=RANDOM_STATE)
SMT = SMOTE(sampling_strategy=OVER_SAMPLE, random_state=RANDOM_STATE)

# set up scaler
SCALER = MinMaxScaler()

# define candidate pipelines

# XGBoost tuned on accuracy
XGBOOST = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", SCALER),
        (
            "model",
            XGBClassifier(
                learning_rate=0.3,
                max_depth=3,
                min_child_weight=None,
                n_estimators=500,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)

# Histogram gradient boosting tuned on accuracy
GB_AC = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", SCALER),
        (
            "model",
            HistGradientBoostingClassifier(
                max_iter=500,
                learning_rate=0.1,
                max_depth=25,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)

MODELS = [GB_AC, XGBOOST]

# the number of cross validation splits to use
CV = 10


def main():
    """
    gets data, trains models on the test data and analyses the results
    """

    # import data using util
    data = get_data()
    _idx, x, y, _genes = split_data(data)

    # set up figures
    fig_test, axs_test = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))
    _fig_train, axs_train = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))
    fig_test.suptitle("Confusion Matrix - Test Data")
    fig_test.suptitle("Confusion Matrix - Training Data")

    analyse_models(x, y, axs_test, axs_train)

    # show matricies
    plt.tight_layout()
    plt.show()


def analyse_models(x, y, axs_test, axs_train):
    """Trains models, cross validates, fits on a validation split and evaulates performance, printing to console
    Args:
        x: the training data
        y: the training data
        axs_test: the axis of the test confusion matrix
        axs_test: the axis of the training confusion matrix
    """

    # split train test validate
    x_train, _, y_train, __ = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )
    x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(
        x_train,
        y_train,
        test_size=TEST_SIZE,
        stratify=y_train,
        random_state=RANDOM_STATE,
    )

    for pipe, ax_test, ax_train in zip(MODELS, axs_test.flatten(), axs_train.flatten()):

        # run cv on all data and evaluate
        cv = cross_validate(
            pipe, x_train, y_train, cv=CV, n_jobs=-1, scoring=SCORING_CV
        )
        # print scores
        print(f"Model Name: {pipe.named_steps['model'].__class__.__name__}")
        print_cv_results(cv)

        # fit on valdiation training data and predict
        pipe.fit(x_train_val, y_train_val)

        # predict on the val set
        predictions_test, labels_test, num_removed = predict_with_qc(
            pipe, QC_THRESHOLD, x_test_val, y_test_val
        )

        # predictions on the train set
        predictions_train = pipe.predict(x_train_val)

        # set up confusion matricies
        cf_test = ConfusionMatrixDisplay.from_predictions(
            labels_test, predictions_test, ax=ax_test
        )
        ax_test.set_title(pipe.named_steps["model"].__class__.__name__)

        cf_train = ConfusionMatrixDisplay.from_predictions(
            y_train_val, predictions_train, ax=ax_train
        )
        ax_train.set_title(pipe.named_steps["model"].__class__.__name__)

        print(f"QC Threshold: {QC_THRESHOLD}")

        # display evaluation metrics
        print("VALIDATION SCORES")
        analyse_prediction_results(predictions_test, labels_test)

        print("TRAIN SCORES")
        analyse_prediction_results(predictions_train, y_train_val)

        # display classification reports
        print("TRAIN CLASSIFICATION REPORT")
        print(classification_report(y_train_val, predictions_train))

        print("TEST CLASSIFICATION REPORT")
        print(classification_report(labels_test, predictions_test))


if __name__ == "__main__":
    main()
