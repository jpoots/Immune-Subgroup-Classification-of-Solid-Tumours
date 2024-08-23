import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
)
from xgboost import XGBClassifier
from sklearn.preprocessing import MinMaxScaler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import sys

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils import (
    get_data,
    split_data,
    RANDOM_STATE,
    TEST_SIZE,
)

"""
This script trains a final model and imputer and saves them to .pkl files.
"""

# define locations
MODEL_FILE_NAME = "./trained_models/model.pkl"
IMPUTER_FILE_NAME = "./trained_models/mice.pkl"

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


def main():
    """
    This script trains the defined model and imputer and saves it to a file
    """

    # load data
    data = get_data()
    _idx, x, y, _genes = split_data(data)

    # remove test set and get validtion set
    x_train, _x_test, y_train, _y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    x_train, _x_val, y_train, _y_val = train_test_split(
        x_train,
        y_train,
        test_size=TEST_SIZE,
        stratify=y_train,
        random_state=RANDOM_STATE,
    )

    # build models on training data
    print("FITTING MODEL....")
    pipe = build_model(x_train, y_train)
    print("DONE")

    # fit the imputer
    print("FITTING IMPUTER...")
    imp = IterativeImputer(max_iter=100).set_output(transform="pandas")
    imp.fit(x_train)
    print("DONE")

    # saving to file
    print("SAVING...")
    joblib.dump(pipe, MODEL_FILE_NAME)
    joblib.dump(imp, IMPUTER_FILE_NAME)
    print("SAVE SUCCESSFUL")


def build_model(x, y):
    """Trains a gradient boosting model on the data using sampling strategy
    Args:
        x: the training data
        y: the training data

    Returns:
        pipe: a trained model
    """

    # define model to train
    model = XGBClassifier(
        learning_rate=0.3,
        max_depth=3,
        min_child_weight=None,
        n_estimators=500,
        random_state=RANDOM_STATE,
        nthread=1,
    )

    # data scaler and generic pipeleine
    scaler = MinMaxScaler()

    # set up samplers
    rus = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE, random_state=RANDOM_STATE)
    smt = SMOTE(sampling_strategy=OVER_SAMPLE, random_state=RANDOM_STATE)

    # set up pipeline and fit
    pipe = ImbPipeline(
        steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", model)]
    )
    pipe = pipe.fit(x, y)
    return pipe


if __name__ == "__main__":
    main()
