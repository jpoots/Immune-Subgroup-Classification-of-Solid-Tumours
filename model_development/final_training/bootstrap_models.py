import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import MinMaxScaler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.utils import resample
import sys

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils.utils import get_data, split_data

FILE_NAME = "./trained_models/bootstrap_models.pkl"
RANDOM_STATE = 42

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

# param for gb model
MODEL_PARAMS = {
    "max_iter": 1500,
    "learning_rate": 0.05,
    "max_depth": 100,
    "max_leaf_nodes": 41,
    "min_samples_leaf": 20,
}


def main():
    np.random.seed(RANDOM_STATE)

    # import data using util
    data = get_data()
    idx, x, y, genes = split_data(data)

    # data scaler and generic pipeleine
    scaler = MinMaxScaler()

    # remove the test set
    x_train, _x_test, y_train, _y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y
    )

    # set up samplers and fit
    rus = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE)
    smt = SMOTE(sampling_strategy=OVER_SAMPLE)

    # set up pipeline and fit
    models = []
    for bootstrap in range(N_BOOTSTRAPS):
        model = HistGradientBoostingClassifier(**MODEL_PARAMS)
        pipe = ImbPipeline(
            steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", model)]
        )

        # handles any sort of invalid sample
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

    print("TRAINING COMPLETE SAVING")
    joblib.dump(models, FILE_NAME)

    # saving and testing save successful
    print("SAVE SUCCESSFUL")


if __name__ == "__main__":
    main()
