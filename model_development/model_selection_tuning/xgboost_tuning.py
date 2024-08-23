from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
import numpy as np
import time
import datetime
import sys
from xgboost import XGBClassifier

sys.path.append("..")
from utils import (
    get_data,
    split_data,
    tune_models,
    RANDOM_STATE,
    TEST_SIZE,
)  # append the path of the parent (taken from chatGPT)


"""
This script tunes the XGBoost model over a hyperparameter grid usign grid search
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

# model to train and hyperparameter grid
MODELS = [
    {
        "model": ImbPipeline(
            steps=[
                ("rus", RUS),
                ("smt", SMT),
                ("scaler", SCALER),
                ("model", XGBClassifier(random_state=RANDOM_STATE)),
            ]
        ),
        "params": {
            "model__n_estimators": [100, 200, 500, 1000, 1500],
            "model__max_depth": [3, 5, 7, 10, None],
            "model__min_child_weight": [4, 6, 8, 10, 12, None],
            "model__learning_rate": [0.001, 0.01, 0.1, 0.3, 1],
        },
    },
]


def main():
    """
    takes all models, tunes them over a hyperparmeter grid and evaluates their performance
    """

    # import data using util
    data = get_data()
    _idx, x, y, _genes = split_data(data)

    # get rid of test data
    x_train, _x_test, y_train, _y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    # used to time the tuning
    total_start = time.time()

    # tune model
    tune_models(x_train, y_train, MODELS)

    total_end = time.time()

    # display time
    duration_seconds_total = total_end - total_start
    duration_total = datetime.timedelta(seconds=duration_seconds_total)

    print(f"Total tuning time: {duration_total}")


if __name__ == "__main__":
    main()
