import pandas as pd
import numpy as np
import os
from sklearn.metrics import (
    f1_score,
    balanced_accuracy_score,
    make_scorer,
    recall_score,
    precision_score,
    accuracy_score,
)
import time
from sklearn.model_selection import GridSearchCV
import datetime

"""
A number of utility functions that are used across the model development pipeline are kept here
"""

# The location of the data file
CURRENT = os.path.dirname(os.path.abspath(__file__))
FILE_LOCATION = os.path.join(CURRENT, "data.csv")

# how to score
SCORING = {
    "accuracy": "accuracy",
    "balanced_accuracy": "balanced_accuracy",
    "f1": make_scorer(f1_score, average="macro", zero_division=np.nan),
    "precision": make_scorer(precision_score, average="macro", zero_division=np.nan),
    "recall": make_scorer(recall_score, average="macro", zero_division=np.nan),
}
# the number of cross validation splits to use
CV = 10


def get_data():
    """
    loads the data into a panda dataframe and returns the transposed data fram
    """

    data = pd.read_csv(FILE_LOCATION, index_col=0)
    data = data.T
    return data


# splits the data into the components of ID, features, classification and gene names
def split_data(data):
    """Splits a gene expression data frame into its component parts
    Args:
    data: the dataframe to split

    Returns:
    idx: a list of sample ids
    features: a numpy array of features
    classification: a list of assigned classifications
    genes: a list of gene names in the file
    """
    idx = [sample_id for sample_id in data.index]
    genes = [gene for gene in data.columns.values]

    # extract last digit of name
    classification = np.array([int(sample[-1]) - 1 for sample in data.index.values])
    features = data.to_numpy()
    return idx, features, classification, genes


def print_tuning_results(pipe, grid_search, duration):
    """Prints the results of model tuning
    Args:
    pipe: the base moedl
    grid_search: the fitted GridSearchCV object
    duration: the time taken to tune
    """

    results = grid_search.cv_results_
    best_index = grid_search.best_index_

    # model scoring on accuracy
    print("CROSS VALIDATION ON BEST MODEL")
    print(f"Model Name: {pipe.named_steps['model'].__class__.__name__}")
    print(f"Tuning time: {duration}")
    print(f"Best Params: {grid_search.best_params_}")
    print(f"Accuracy: {results['mean_test_accuracy'][best_index]}")
    print(f"F1: {results['mean_test_f1'][best_index]}")
    print(f"Precision: {results['mean_test_precision'][best_index]}")
    print(f"Recall: {results['mean_test_recall'][best_index]}")
    print(f"Balanced accuracy: {results['mean_test_balanced_accuracy'][best_index]}")
    print()


def print_cv_results(cv):
    """Prints the results of cross validation
    Args:
    cv: the dictionary result of cross validation
    """
    # pulling out my performance metrics
    accuracy_cv = np.average(cv["test_accuracy"])
    f1_cv = np.average(cv["test_f1_macro"])
    precision_cv = np.average(cv["test_precision_macro"])
    recall_cv = np.average(cv["test_recall_macro"])
    bal_accuracy_cv = np.average(cv["test_balanced_accuracy"])
    f1_group6 = np.average(cv["test_f1_group6"])
    recall_group6 = np.average(cv["test_recall_group6"])

    print("CROSS VALIDATION SCORES")
    print_all_scores(
        accuracy_cv,
        f1_cv,
        precision_cv,
        recall_cv,
        bal_accuracy_cv,
        recall_group6,
        f1_group6,
    )


def analyse_prediction_results(predictions, target):
    """Analyses the results of a prediction run given predictions and target labels
    Args:
    predictions: the assigned predictions
    target: target labels
    """

    accuracy = accuracy_score(target, predictions)
    f1 = f1_score(target, predictions, average="macro")
    precision = precision_score(target, predictions, average="macro")
    recall = recall_score(target, predictions, average="macro")
    bal_ac = balanced_accuracy_score(target, predictions)
    recall_group_6 = recall_score(target, predictions, labels=[5], average="macro")
    f1_group_6 = f1_score(target, predictions, labels=[5], average="macro")
    print_all_scores(
        accuracy, f1, precision, recall, bal_ac, recall_group_6, f1_group_6
    )


def print_all_scores(
    accuracy, f1, precision, recall, bal_ac, recall_group_6, f1_group_6
):
    """Prints a list of standard scors
    Args:
    accuracy: accuracy score
    f1: f1 score
    precision: precision score
    recall: recall score
    bal_ac: balanced accuracy score
    recall_group_6: recall score for subgroup 6
    f1_group_6: f1 score for subgroup 6
    """
    print(f"Accuracy: {accuracy}")
    print(f"F1: {f1}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"Balanced accuracy: {bal_ac}")
    print(f"Group 6 F1: {f1_group_6}")
    print(f"Group 6 Recall: {recall_group_6}")
    print()


def predict_with_qc(pipe, threshold, x, y):
    """Performs predictions with a QC threshold given data and an estimarots
    Args:
    pipe: the estimator
    threshold: the QC threshold value
    x: the x features
    y: the y labels

    Returns:
    predictions: the predictions assigned with those below threshold removed
    filtered_true: the corresponding set of y true values with those below threshold removed
    num_nc: the number of samples belwo the QC threshold
    """
    # get prediction probs for train and test
    prediction_probs = pipe.predict_proba(x)

    max_probs = np.amax(prediction_probs, axis=1)
    nc_indicies = [i for i, prob in enumerate(max_probs) if prob < threshold]
    filtered_samples = np.delete(x, nc_indicies, axis=0)
    filtered_true = np.delete(y, nc_indicies)

    predictions = pipe.predict(filtered_samples)
    num_nc = len(nc_indicies)
    return predictions, filtered_true, num_nc


def tune_models(x_train, y_train, models):
    """Perform grid search on all models and evaluates performance
    Args:
    x_train: the training data
    y_train: the training data
    models: the models to tune
    """
    for model in models:
        start = time.time()

        # try except to prevent long training runs failing because of an issue
        try:
            pipe = model["model"]
            params = model["params"]

            # grid search to return results for a range of metrics and refit on accuracy
            grid_search = GridSearchCV(
                pipe, params, n_jobs=-1, scoring=SCORING, refit="accuracy", cv=CV
            )
            grid_search.fit(x_train, y_train)

            # model tuning time
            end = time.time()
            duration_seconds = end - start
            duration = datetime.timedelta(seconds=duration_seconds)

            print(f"Model Name: {pipe.named_steps['model'].__class__.__name__}")
            print_tuning_results(pipe, grid_search, duration)

        except Exception as e:
            print(e)
