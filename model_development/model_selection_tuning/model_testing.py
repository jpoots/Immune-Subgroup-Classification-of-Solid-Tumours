import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler
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

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils.utils import (
    get_data,
    split_data,
    print_cv_results,
    analyse_prediction_results,
    predict_with_qc,
)

RANDOM_STATE = 42

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

SCALER = MinMaxScaler()
RUS = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE)
SMT = SMOTE(sampling_strategy=OVER_SAMPLE)

# define candidate models wiht best hyperparams
GB_AC = ImbPipeline(
    steps=[
        ("rus", RUS),
        ("smt", SMT),
        ("scaler", SCALER),
        (
            "model",
            HistGradientBoostingClassifier(
                max_iter=1000, learning_rate=0.1, max_depth=None
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
                max_iter=1500,
                learning_rate=0.05,
                max_depth=100,
                max_leaf_nodes=41,
                min_samples_leaf=20,
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
                max_iter=1000, learning_rate=0.1, max_depth=75
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
                max_iter=1000, learning_rate=0.1, max_depth=50
            ),
        ),
    ]
)

MODELS = [GB_AC, GB_AC_FINE, GB_F1_FINE, GB_BA, GB_BA_FINE, GB_F1]


def main():
    np.random.seed(RANDOM_STATE)

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

    # split train test
    x_train, _, y_train, __ = train_test_split(x, y, test_size=0.20, stratify=y)
    x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(
        x, y, test_size=0.20, stratify=y
    )

    for pipe, ax_test, ax_train in zip(MODELS, axs_test.flatten(), axs_train.flatten()):
        # run cv on all data and evaluate
        cv = cross_validate(pipe, x_train, y_train, cv=10, n_jobs=-1, scoring=SCORING)
        # print scores
        print(f"Model Name: {pipe.named_steps['model'].__class__.__name__}")
        print_cv_results(cv)

        # fit on all training data and predict
        pipe.fit(x_train_val, y_train_val)

        qc_threshold = 0.982
        predictions_test, labels_test, num_removed = predict_with_qc(
            pipe, qc_threshold, x_test_val, y_test_val
        )

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

        print(f"QC Threshold: {qc_threshold}")
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
