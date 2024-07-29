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
from imblearn.over_sampling import SMOTE, ADASYN
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    f1_score,
    recall_score,
    precision_score,
    make_scorer,
)
from imblearn.pipeline import Pipeline as ImbPipeline
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime
import sys

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils.utils import get_data, split_data, print_tuning_results

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV = 10


MODELS = [
    {
        "model": SVC(),
        "params": {
            "model__C": [0.001, 0.01, 0.1, 1, 10, 100, 1000],
            "model__kernel": ["rbf", "poly", "sigmoid"],
            "model__gamma": ["scale", "auto", 0.001, 0.01, 0.1, 1, 10, 100],
            "model__degree": [2, 3, 4, 5],
        },
    },
    {
        "model": RandomForestClassifier(n_jobs=-1),
        "params": {  # top two are the most important
            "model__n_estimators": [100, 500, 1000, 2000],
            "model__max_features": ["sqrt", "log2", None, 100, 220],
            "model__max_depth": [10, 20, 50, 100, None],
        },
    },
    {
        "model": HistGradientBoostingClassifier(),
        "params": {
            "model__learning_rate": [0.001, 0.01, 0.1, 1],
            "model__max_depth": [25, 50, 75, None],
            "model__max_iter": [100, 500, 1000],
        },
    },
    {
        "model": LogisticRegression(n_jobs=-1),
        "params": {
            "model__C": np.logspace(-4, 4, 20),
            "model__solver": ["lbfgs", "newton-cg", "liblinear", "sag", "saga"],
            "model__penalty": ["l1", "l2", "elasticnet", "None"],
            "model__max_iter": [100, 500, 1000],
        },
    },
    {
        "model": MLPClassifier(),
        "params": {
            "model__hidden_layer_sizes": [
                (100,),
                (300,),
                (
                    300,
                    200,
                ),
            ],
            "model__alpha": [0.0001, 0.001, 0.01, 0.1],
            "model__learning_rate": ["constant", "adaptive"],
            "model__max_iter": [200, 500, 1000],
        },
    },
]

SCORING = {
    "accuracy": "accuracy",
    "balanced_accuracy": "balanced_accuracy",
    "f1": make_scorer(f1_score, average="macro", zero_division=np.nan),
    "precision": make_scorer(precision_score, average="macro", zero_division=np.nan),
    "recall": make_scorer(recall_score, average="macro", zero_division=np.nan),
}  # ROC_AUC is not included due to the computational cost


def main():
    np.random.seed(RANDOM_STATE)

    # import data using util
    data = get_data()
    _idx, x, y, _genes = split_data(data)

    # get rid of test data
    x_train, _x_test, y_train, _y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y
    )

    total_start = time.time()

    tune_models(x_train, y_train)

    total_end = time.time()
    duration_seconds_total = total_end - total_start
    duration_total = datetime.timedelta(seconds=duration_seconds_total)
    print(f"Total tuning time: {duration_total}")


def tune_models(x_train, y_train):
    # data scaler and generic pipeleine
    scaler = MinMaxScaler()
    for model in MODELS:
        start = time.time()
        # try except to prevent long training runs failing because of an issue
        try:
            clf = model["model"]
            params = model["params"]

            pipe = Pipeline(steps=[("scaler", scaler), ("model", clf)])

            # grid search to return results for a range of metrics and refit on accuracy
            grid_search = GridSearchCV(
                pipe, params, n_jobs=-1, scoring=SCORING, refit="accuracy", cv=CV
            )
            grid_search.fit(x_train, y_train)

            # model tuning time
            end = time.time()
            duration_seconds = end - start
            duration = datetime.timedelta(seconds=duration_seconds)

            print(f"Model Name: {pipe.named_steps["model"].__class__.__name__}")
            print_tuning_results(grid_search, duration)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
