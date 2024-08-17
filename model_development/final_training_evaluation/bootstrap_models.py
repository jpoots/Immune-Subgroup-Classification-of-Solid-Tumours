import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import MinMaxScaler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.utils import resample
from xgboost import XGBClassifier
import sys

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils import get_data, split_data, RANDOM_STATE

"""
Trains N_BOOSTRAPS number of models on a bootstrap resample of the dataset and saves to a file to be used for confidence predictions
"""

# location to save
FILE_NAME = "./trained_models/bootstrap_models.pkl"

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

# training params
TEST_SIZE = 0.2
N_BOOTSTRAPS = 10


def main():
    """
    Splits data, trains the bootstrap models and saves to disk
    """
    # import data using util
    data = get_data()
    idx, x, y, genes = split_data(data)

    # remove the test set
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    # remove the validation
    x_train, x_test, y_train, y_test = train_test_split(
        x_train,
        y_train,
        test_size=TEST_SIZE,
        stratify=y_train,
        random_state=RANDOM_STATE,
    )

    models = train_bootstraps(x_train, y_train)
    print("TRAINING COMPLETE SAVING")
    joblib.dump(models, FILE_NAME)

    # saving and testing save successful
    print("SAVE SUCCESSFUL")


def train_bootstraps(x_train, y_train):
    """Trains N_BOOTSRAPS models on a bootstrap resample of the training data
    Args:
    axs: Axs of the confusion amtric plot
    x_train: the training data
    y_train: the training data

    Returns:
    models: a list of trained models
    """
    # data scaler
    scaler = MinMaxScaler()

    # set up samplers and fit
    rus = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE, random_state=RANDOM_STATE)
    smt = SMOTE(sampling_strategy=OVER_SAMPLE, random_state=RANDOM_STATE)

    # set up pipeline and fit
    models = []
    for bootstrap in range(N_BOOTSTRAPS):
        model = XGBClassifier(
            learning_rate=0.3,
            max_depth=3,
            min_child_weight=None,
            n_estimators=500,
            random_state=RANDOM_STATE,
            nthread=1,
        )
        pipe = ImbPipeline(
            steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", model)]
        )

        # handles any sort of invalid sample by ignoring and resampling
        invalid_sample = True
        while invalid_sample:
            try:
                x_boot, y_boot = resample(x_train, y_train, stratify=y_train)
                pipe.fit(x_boot, y_boot)
                invalid_sample = False
            except:
                print("INVALID SAMPLE CONTINUING")
                continue

        print(f"FIT {bootstrap + 1} COMPLETE")
        models.append(pipe)
    return models


if __name__ == "__main__":
    main()
