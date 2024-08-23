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
import matplotlib.pyplot as plt
from imblearn.under_sampling import RandomUnderSampler
from sklearn.linear_model import LogisticRegression
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
    SCORING_CV,
    TEST_SIZE,
)

"""
This script is for testing models with default hyperparameters on data balances
"""

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

# set up samplers
RUS = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE, random_state=RANDOM_STATE)
SMT = SMOTE(sampling_strategy=OVER_SAMPLE, random_state=RANDOM_STATE)

# QC threshold to use for predictions
QC_THRESHOLD = 0

# the number of cross validation splits
CV = 10


def main():
    """
    tests a range of models with default parameters with various data balances
    """

    # import data
    data = get_data()
    idx, x, y, genes = split_data(data)

    analyse_models(x, y)


def analyse_models(x, y):
    """Cross validates all models with the given sampling strategy, trains on a validation split and produces a confusion matrix.
    Args:
        x: all data
        y: all data
    """
    # remove the test set
    x_train, _x_test, y_train, _y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    for model in MODELS:
        # construct pipeline
        pipe = ImbPipeline(
            steps=[("rus", RUS), ("smt", SMT), ("scaler", SCALER), ("model", model)]
        )

        # run cv and evaluate
        cv = cross_validate(
            pipe, x_train, y_train, cv=CV, n_jobs=-1, scoring=SCORING_CV
        )

        print("Model Name: " + model.__class__.__name__)
        print_cv_results(cv)


if __name__ == "__main__":
    main()
