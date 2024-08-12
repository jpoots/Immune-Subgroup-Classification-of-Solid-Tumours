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
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    f1_score,
    recall_score,
    precision_score,
    make_scorer,
)
from imblearn.pipeline import Pipeline as ImbPipeline
import numpy as np
import time
import datetime
import sys

sys.path.append("..")
from utils import (
    get_data,
    split_data,
    tune_models,
    RANDOM_STATE,
)  # append the path of the parent (taken from chatGPT)


"""
Tuning hyperparamets of models on their best data balance as attained in balancing_tests.py
"""

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

# set up samplers and scaler
RUS = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE, random_state=RANDOM_STATE)
SMT = SMOTE(sampling_strategy=OVER_SAMPLE, random_state=RANDOM_STATE)
SCALER = MinMaxScaler()

# models to train
MODELS = [
    {
        "model": ImbPipeline(
            steps=[
                ("rus", RUS),
                ("smt", SMT),
                ("scaler", SCALER),
                ("model", RandomForestClassifier(n_jobs=-1, random_state=RANDOM_STATE)),
            ]
        ),
        "params": {
            "model__n_estimators": [100, 500, 1000, 2000],
            "model__max_features": ["sqrt", "log2", None, 100, 220],
            "model__max_depth": [10, 20, 50, 100, None],
        },
    },
]

# scoring metrics to use
SCORING = {
    "accuracy": "accuracy",
    "balanced_accuracy": "balanced_accuracy",
    "f1": make_scorer(f1_score, average="macro", zero_division=np.nan),
    "precision": make_scorer(precision_score, average="macro", zero_division=np.nan),
    "recall": make_scorer(recall_score, average="macro", zero_division=np.nan),
}
# size of test set
TEST_SIZE = 0.2
# number of cross validation splits to do
CV = 10


def main():
    """
    takes all models, tunes them over a hyperparmeter grid and evaluates their performance
    """

    # import data using util
    data = get_data()
    idx, x, y, genes = split_data(data)

    # get rid of test data
    x_train, _x_test, y_train, _y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    total_start = time.time()
    tune_models(x_train, y_train, MODELS)

    total_end = time.time()
    duration_seconds_total = total_end - total_start
    duration_total = datetime.timedelta(seconds=duration_seconds_total)
    print(f"Total tuning time: {duration_total}")


if __name__ == "__main__":
    main()
