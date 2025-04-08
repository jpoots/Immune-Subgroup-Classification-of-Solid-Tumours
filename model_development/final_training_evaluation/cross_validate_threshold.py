import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
)
from xgboost import XGBClassifier
from sklearn.preprocessing import MinMaxScaler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    recall_score,
    f1_score,
    balanced_accuracy_score,
)

import sys

# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils import (
    get_data,
    split_data,
    predict_with_qc_and_predom,
    RANDOM_STATE,
    TEST_SIZE,
)

"""
This script cross validates a models class 6 recall and accuracy with a QC threshold in place
"""

# cross validation splits to create
CV = 10

# The QC threshold to use
QC_THRESHOLD = 0.92

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
    cross validates class 6 recall and accuracy with a QC threshold in place
    """
    data = get_data()
    _idx, x, y, _genes = split_data(data)

    # remove test set and get validtion set
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    x_train, _x_val, y_train, _y_val = train_test_split(
        x_train,
        y_train,
        test_size=TEST_SIZE,
        stratify=y_train,
        random_state=RANDOM_STATE,
    )

    # perform custom cross validation
    (
        accuracy,
        recall,
        f1,
        balanced_accuracy,
        predom_count,
        nc_count,
        predom_percent,
        nc_percent,
    ) = cross_validate(x_train, y_train)

    print(f"Accuracy: {accuracy}")
    print(f"Class 6 recall: {recall}")
    print(f"F1: {f1}")
    print(f"Balanced Accuracy: {balanced_accuracy}")
    print(f"Predominant class count: {predom_count}")
    print(f"Non-class count: {nc_count}")
    print(f"Predominant class percent: {predom_percent}")
    print(f"Non-class percent: {nc_percent}")


def build_model():
    """Builds a fresh untrained model pipeline
    Returns:
        pipe: a model pipeline
    """
    # define model to train
    model = XGBClassifier(
        learning_rate=0.3,
        max_depth=3,
        min_child_weight=None,
        n_estimators=500,
        random_state=RANDOM_STATE,
    )

    # data scaler
    scaler = MinMaxScaler()

    # set up samplers and fit
    rus = RandomUnderSampler(sampling_strategy=UNDER_SAMPLE, random_state=RANDOM_STATE)
    smt = SMOTE(sampling_strategy=OVER_SAMPLE, random_state=RANDOM_STATE)

    # set up pipeline
    pipe = ImbPipeline(
        steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", model)]
    )
    return pipe


def cross_validate(x_train, y_train):
    """Cross validates class 6 recall and accrucy with a QC threshold

    Args:
        x_train: x training data
        y_yest: y training data

    Returns:
        results: a tuple containing
            - avg_recall: average recall score
            - avg_acc: average accuracy
    """

    # produce stratified splits shuffled
    skf = StratifiedKFold(n_splits=CV, shuffle=True, random_state=RANDOM_STATE)
    accuracy_score_list = []
    class_6_recall_list = []
    f1_list = []
    balanced_accuracy_list = []
    predom_count = 0
    nc_count = 0
    predom_percent = 0
    nc_percent = 0

    # https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html
    # iterate over the training and test splits as per the documentation
    for i, (train, test) in enumerate(skf.split(x_train, y_train)):

        # create a model and fit on 9 splits
        pipe = build_model()
        pipe.fit(np.array(x_train)[train], np.array(y_train)[train])

        # precit on the left out split
        predictions, true, num_removed, num_predom = predict_with_qc_and_predom(
            pipe, QC_THRESHOLD, np.array(x_train)[test], np.array(y_train)[test]
        )

        predom_count += num_predom
        nc_count += num_removed

        predom_percent += num_predom / len(np.array(y_train)[test])
        nc_percent += num_removed / len(np.array(y_train)[test])

        # score and append for this run
        class_6_recall = recall_score(true, predictions, average="macro", labels=[5])
        f1 = f1_score(true, predictions, average="macro")
        balanced_accuracy = balanced_accuracy_score(true, predictions)

        f1_list.append(f1)
        balanced_accuracy_list.append(balanced_accuracy)
        class_6_recall_list.append(class_6_recall)

        accuracy = accuracy_score(true, predictions)
        accuracy_score_list.append(accuracy)
        print(f"Completed {i + 1}")

    # get average over 10 runs
    avg_recall = np.mean(class_6_recall_list)
    avg_acc = np.mean(accuracy_score_list)
    avg_f1 = np.mean(f1_list)
    avg_balanced_accuracy = np.mean(balanced_accuracy_list)

    predom_count /= CV
    nc_count /= CV

    predom_percent /= CV
    nc_percent /= CV

    return (
        avg_acc,
        avg_recall,
        avg_f1,
        avg_balanced_accuracy,
        predom_count,
        nc_count,
        predom_percent,
        nc_percent,
    )


if __name__ == "__main__":
    main()
