from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_validate
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    ConfusionMatrixDisplay,
)
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import sys
import math
from xgboost import XGBClassifier

"""
The script takes a collection of models, trains them on the unbalanced dataset 
with default hyperparameters and evaluates
"""

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

# models to test
MODELS = [
    HistGradientBoostingClassifier(random_state=RANDOM_STATE),
    MLPClassifier(random_state=RANDOM_STATE),
    svm.SVC(random_state=RANDOM_STATE),
    RandomForestClassifier(n_jobs=-1, random_state=RANDOM_STATE),
    KNeighborsClassifier(n_jobs=-1),
    GaussianNB(),
    LogisticRegression(n_jobs=-1, random_state=RANDOM_STATE),
    XGBClassifier(n_jobs=-1, random_state=RANDOM_STATE),
]
# number of columns on confusion matrix
N_COLS = 4

# number of cross validation splits
CV = 10


def main():
    """
    splits data, trains all models and evaultes their performance, printing them to console.
    Confusion matricies are plotted.
    """

    # import data using util
    data = get_data()
    _idx, x, y, _genes = split_data(data)

    # remove test set
    x_train, _x_test, y_train, _y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    # split data into train validate
    x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(
        x_train,
        y_train,
        test_size=TEST_SIZE,
        stratify=y_train,
        random_state=RANDOM_STATE,
    )

    # create a plot
    fig, axs = plt.subplots(
        nrows=math.ceil(len(MODELS) / N_COLS), ncols=N_COLS, figsize=(15, 10)
    )

    # test models
    test_models(axs, x_train, y_train, x_train_val, x_test_val, y_train_val, y_test_val)

    # show plot
    plt.tight_layout()
    plt.show()


def test_models(
    axs, x_train, y_train, x_train_val, x_test_val, y_train_val, y_test_val
):
    """Cross validates all models, trains them on validation data and evaluates with confusion matrix
    Args:
        axs: Axs of the confusion amtric plot
        x_train: the training data
        y_train: the training data
        x_train_val: the validation training data
        x_test_val: the validation test data
        y_train_val: the validation trainign data
        y_test_val: the validation test data
    """

    # data scaler and generic pipeleine
    scaler = MinMaxScaler()

    for model, ax in zip(MODELS, axs.flatten()):

        # define a pipeline with the scaler and model
        pipe = Pipeline(steps=[("scaler", scaler), ("model", model)])

        # run cv and evaluate
        cv = cross_validate(
            pipe, x_train, y_train, cv=CV, n_jobs=-1, scoring=SCORING_CV
        )

        print("Model Name: " + model.__class__.__name__)
        print_cv_results(cv)

        # fit and predict
        pipe.fit(x_train_val, y_train_val)
        predictions = pipe.predict(x_test_val)

        # generate confusion matrix
        ConfusionMatrixDisplay.from_predictions(y_test_val, predictions, ax=ax)
        ax.set_title(model.__class__.__name__)


if __name__ == "__main__":
    main()
