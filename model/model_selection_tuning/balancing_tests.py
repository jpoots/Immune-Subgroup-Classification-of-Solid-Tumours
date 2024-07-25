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
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import sys

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils.utils import (
    get_data,
    split_data,
    print_cv_results,
    predict_with_qc,
    analyse_prediction_results,
)

RANDOM_STATE = 42
# define potential models
MODELS = [
    HistGradientBoostingClassifier(
        max_iter=1000,
        learning_rate=0.1,
        max_depth=75,
        max_leaf_nodes=41,
        min_samples_leaf=20,
    ),
    svm.SVC(class_weight="balanced"),
    RandomForestClassifier(class_weight="balanced"),
    KNeighborsClassifier(),
    GaussianNB(),
    LogisticRegression(class_weight="balanced"),
]
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
RUS = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE)
SMT = SMOTE(sampling_strategy=OVER_SAMPLE)

SCORING = {
    "accuracy": "accuracy",
    "f1_macro": "f1_macro",
    "precision_macro": "precision_macro",
    "recall_macro": "recall_macro",
    "balanced_accuracy": "balanced_accuracy",
    "f1_group6": make_scorer(f1_score, average=None, labels=[5]),
    "recall_group6": make_scorer(recall_score, average=None, labels=[5]),
}
QC_THRESHOLD = 0.992


def main():
    np.random.seed(RANDOM_STATE)

    # import data using util
    data = get_data()
    idx, x, y, genes = split_data(data)

    fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))

    analyse_models(x, y, axs)

    plt.tight_layout()
    plt.show()


def analyse_models(x, y, axs):
    # remove the test set and create a training and validation set
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y
    )

    x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(
        x_train, y_train, test_size=TEST_SIZE, stratify=y_train
    )
    for model, ax in zip(MODELS, axs.flatten()):
        pipe = ImbPipeline(
            steps=[("rus", RUS), ("smt", SMT), ("scaler", SCALER), ("model", model)]
        )

        # run cv and evaluate
        cv = cross_validate(pipe, x_train, y_train, cv=10, n_jobs=-1, scoring=SCORING)
        print("Model Name: " + model.__class__.__name__)
        print_cv_results(cv)

        # fit and predict
        pipe.fit(x_train_val, y_train_val)

        predictions, y_test, num_removed = predict_with_qc(
            pipe, QC_THRESHOLD, x_test, y_test
        )

        disp = ConfusionMatrixDisplay.from_predictions(y_test, predictions, ax=ax)
        ax.set_title(model.__class__.__name__)

        print(f"Model Name: {pipe.named_steps['model'].__class__.__name__}")
        print(f"QC Threshold: {QC_THRESHOLD}")
        print("Removed: " + str(num_removed))
        analyse_prediction_results(predictions, y_test)


if __name__ == "__main__":
    main()
