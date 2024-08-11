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
    f1_score,
    recall_score,
    ConfusionMatrixDisplay,
    classification_report,
    make_scorer,
)
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import sys

sys.path.append("..")
from utils.utils import (
    get_data,
    split_data,
    print_cv_results,
    analyse_prediction_results,
    predict_with_qc,
    RANDOM_STATE,
)

# set up scoring metrics to report
SCORING = {
    "accuracy": "accuracy",
    "f1_macro": "f1_macro",
    "precision_macro": "precision_macro",
    "recall_macro": "recall_macro",
    "balanced_accuracy": "balanced_accuracy",
    "f1_group6": make_scorer(f1_score, average=None, labels=[5]),
    "recall_group6": make_scorer(recall_score, average=None, labels=[5]),
}

# the QC threshold to use in validation evaluation
QC_THRESHOLD = 0

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

RUS = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE, random_state=RANDOM_STATE)
SMT = SMOTE(sampling_strategy=OVER_SAMPLE, random_state=RANDOM_STATE)

# scaler and samplers
SCALER = MinMaxScaler()


# define models to test
RF = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", MinMaxScaler()),
        (
            "model",
            RandomForestClassifier(
                max_depth=50,
                max_features="sqrt",
                n_estimators=1000,
                n_jobs=-1,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)

# define candidate models wiht best hyperparams
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
                n_estimators=1000,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)

# define candidate models wiht best hyperparams
XGBOOST1 = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", SCALER),
        (
            "model",
            XGBClassifier(random_state=RANDOM_STATE),
        ),
    ]
)

# define candidate models wiht best hyperparams
XGBOOST2 = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", SCALER),
        (
            "model",
            XGBClassifier(
                learning_rate=0.1,
                max_depth=7,
                min_child_weight=12,
                n_estimators=1500,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)

GB_AC = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", SCALER),
        (
            "model",
            HistGradientBoostingClassifier(
                max_iter=1000,
                learning_rate=0.1,
                max_depth=None,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)
GB_AC_FINE = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", SCALER),
        (
            "model",
            HistGradientBoostingClassifier(
                max_iter=1000,
                learning_rate=0.1,
                max_depth=75,
                max_leaf_nodes=41,
                min_samples_leaf=20,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)
GB_F1_FINE = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", SCALER),
        (
            "model",
            HistGradientBoostingClassifier(
                max_iter=2000,
                learning_rate=0.1,
                max_depth=50,
                max_leaf_nodes=31,
                min_samples_leaf=30,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)

GB_BA = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", SCALER),
        (
            "model",
            HistGradientBoostingClassifier(
                max_iter=1000,
                learning_rate=0.1,
                max_depth=75,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)
GB_BA_FINE = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", SCALER),
        (
            "model",
            HistGradientBoostingClassifier(
                max_iter=2000,
                learning_rate=0.1,
                max_depth=50,
                max_leaf_nodes=31,
                min_samples_leaf=30,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)
GB_F1 = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", SCALER),
        (
            "model",
            HistGradientBoostingClassifier(
                max_iter=1000,
                learning_rate=0.1,
                max_depth=50,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)

MODELS = [
    GB_F1,
    GB_F1_FINE,
    GB_AC,
    GB_AC_FINE,
    GB_BA,
    GB_BA_FINE,
    XGBOOST,
    XGBOOST1,
    XGBOOST2,
    XGBOOST,
    RF,
]
# the number of cross validation splits
CV = 10


def main():
    """
    gets data, trains models on the test data and analyses the results
    """

    # import data using util
    data = get_data()
    idx, x, y, genes = split_data(data)

    # set up figures
    fig_test, axs_test = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))
    fig_train, axs_train = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))
    fig_test.suptitle("Confusion Matrix - Test Data")
    fig_test.suptitle("Confusion Matrix - Training Data")

    analyse_models(x, y, axs_test, axs_train)

    # show matricies
    plt.tight_layout()
    plt.show()


def analyse_models(x, y, axs_test, axs_train):
    """Trains models, cross validates, fits on a validation split and evaulates performance, printing to console
    Args:
    x_train: the training data
    y_train: the training data
    axs_test: the axis of the test confusion matrix
    axs_test: the axis of the training confusion matrix
    """

    # split train test
    x_train, _, y_train, __ = train_test_split(
        x,
        y,
        test_size=0.20,
        stratify=y,
        random_state=RANDOM_STATE,
    )
    x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(
        x_train,
        y_train,
        test_size=0.20,
        stratify=y_train,
        random_state=RANDOM_STATE,
    )

    for pipe, ax_test, ax_train in zip(MODELS, axs_test.flatten(), axs_train.flatten()):
        # run cv on all data and evaluate
        cv = cross_validate(pipe, x_train, y_train, cv=CV, n_jobs=-1, scoring=SCORING)
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
        print("VALIDATION SCORES")
        analyse_prediction_results(predictions_test, labels_test)

        print("TRAIN SCORES")
        analyse_prediction_results(predictions_train, y_train_val)

        print("TRAIN CLASSIFICATION REPORT")
        print(classification_report(y_train_val, predictions_train))

        print("TEST CLASSIFICATION REPORT")
        print(classification_report(labels_test, predictions_test))


if __name__ == "__main__":
    main()
