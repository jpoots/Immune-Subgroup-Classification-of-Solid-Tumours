from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    HistGradientBoostingClassifier,
)
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    f1_score,
    recall_score,
    precision_score,
    make_scorer,
)
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime
import sys

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils.utils import get_data, split_data, tune_models, RANDOM_STATE

"""
Takes a range of models and tunes them on a hyperparameter grid on the unbalanced dataset
"""

# size of test split
TEST_SIZE = 0.2
# number of crossvalidation runs
CV = 10


# models to tune and parameters
MODELS = [
    {
        "model": HistGradientBoostingClassifier(random_state=RANDOM_STATE),
        "params": {
            "model__learning_rate": [0.001, 0.01, 0.1, 1],
            "model__max_depth": [25, 50, 75, None],
            "model__max_iter": [100, 500, 1000],
        },
    },
]


def main():
    """
    gets data, splits it into train and test and tunes all miodels
    """

    # import data using util
    data = get_data()
    _idx, x, y, _genes = split_data(data)

    # get rid of test data
    x_train, _x_test, y_train, _y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    # timer for model tuning
    total_start = time.time()

    tune_models(x_train, y_train, MODELS)

    # print timer
    total_end = time.time()
    duration_total = datetime.timedelta(seconds=(total_end - total_start))
    print(f"Total tuning time: {duration_total}")


if __name__ == "__main__":
    main()
