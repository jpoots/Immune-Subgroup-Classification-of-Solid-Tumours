from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_validate
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from imblearn.under_sampling import RandomUnderSampler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    f1_score,
    recall_score,
    make_scorer,
)
from sklearn.neural_network import MLPClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from xgboost import XGBClassifier
import sys

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils import (
    get_data,
    split_data,
    print_cv_results,
    RANDOM_STATE,
)

# define potential models
MODELS = [
    XGBClassifier(random_state=RANDOM_STATE),
    HistGradientBoostingClassifier(random_state=RANDOM_STATE),
    MLPClassifier(random_state=RANDOM_STATE),
    svm.SVC(random_state=RANDOM_STATE),
    RandomForestClassifier(n_jobs=-1, random_state=RANDOM_STATE),
    KNeighborsClassifier(n_jobs=-1),
    GaussianNB(),
    LogisticRegression(n_jobs=-1, random_state=RANDOM_STATE),
]
# scaler to use
SCALER = MinMaxScaler()
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

# set up samplers and fit
RUS = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE, random_state=RANDOM_STATE)
SMT = SMOTE(sampling_strategy=OVER_SAMPLE, random_state=RANDOM_STATE)

SCORING = {
    "accuracy": "accuracy",
    "f1_macro": "f1_macro",
    "precision_macro": "precision_macro",
    "recall_macro": "recall_macro",
    "balanced_accuracy": "balanced_accuracy",
    "f1_group6": make_scorer(f1_score, average=None, labels=[5]),
    "recall_group6": make_scorer(recall_score, average=None, labels=[5]),
}
QC_THRESHOLD = 0.989
# the number of cross validation splits
CV = 10


def main():
    """
    tests a range of models with default parameters with various data balances
    """

    # import data using util
    data = get_data()
    idx, x, y, genes = split_data(data)

    fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))

    analyse_models(x, y, axs)

    plt.tight_layout()
    plt.show()


def analyse_models(x, y, axs):
    """Cross validates all models with the given sampling strategy, trains on a validation split and produces a confusion matrix.
    Args:
    x_train: the training data
    y_train: the training data
    axs: the axis of the confusion matrix
    """
    # remove the test set and create a training and validation set
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(
        x_train,
        y_train,
        test_size=TEST_SIZE,
        stratify=y_train,
        random_state=RANDOM_STATE,
    )
    for model, ax in zip(MODELS, axs.flatten()):
        pipe = ImbPipeline(
            steps=[("rus", RUS), ("smt", SMT), ("scaler", SCALER), ("model", model)]
        )

        # run cv and evaluate
        cv = cross_validate(pipe, x_train, y_train, cv=CV, n_jobs=-1, scoring=SCORING)
        print("Model Name: " + model.__class__.__name__)
        print_cv_results(cv)

        """"
        # fit and predict
        pipe.fit(x_train_val, y_train_val)

        predictions, y_test_val, num_removed = predict_with_qc(
            pipe, QC_THRESHOLD, x_test_val, y_test_val
        )

        disp = ConfusionMatrixDisplay.from_predictions(y_test_val, predictions, ax=ax)
        ax.set_title(model.__class__.__name__)

        print(f"Model Name: {pipe.named_steps['model'].__class__.__name__}")
        print(f"QC Threshold: {QC_THRESHOLD}")
        print("Removed: " + str(num_removed))
        analyse_prediction_results(predictions, y_test_val)
        """


if __name__ == "__main__":
    main()
