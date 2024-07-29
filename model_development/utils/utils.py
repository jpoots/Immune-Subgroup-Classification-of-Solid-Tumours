import pandas as pd
import numpy as np
import os
from sklearn.metrics import (
    f1_score,
    balanced_accuracy_score,

    recall_score,
    precision_score,
    accuracy_score,
)

# utility functions for use throughout the project

# current taken from chatGPT
CURRENT = os.path.dirname(os.path.abspath(__file__))
FILE_LOCATION = os.path.join(CURRENT, "data.csv")


# loads the data into a panda dataframe and returns the transposed data fram
def get_data():
    data = pd.read_csv(FILE_LOCATION, index_col=0)
    data = data.T
    return data


# splits the data into the components of ID, features, classification and gene names
def split_data(data):
    idx = [sample_id for sample_id in data.index]
    genes = [gene for gene in data.columns.values]
    classification = np.array([int(sample[-1]) - 1 for sample in data.index.values])
    features = data.to_numpy()
    return idx, features, classification, genes

def print_tuning_results(pipe, grid_search, duration):
    results = grid_search.cv_results_
    best_index = grid_search.best_index_

    # model scoring on accuracy
    print("CROSS VALIDATION ON BEST MODEL")
    print(f"Model Name: {pipe.named_steps["model"].__class__.__name__}")
    print(f"Tuning time: {duration}")
    print(f"Best Params: {grid_search.best_params_}")
    print(f"Accuracy: {results["mean_test_accuracy"][best_index]}")
    print(f"F1: {results["mean_test_f1"][best_index]}")
    print(f"Precision: {results["mean_test_precision"][best_index]}")
    print(f"Recall: {results["mean_test_recall"][best_index]}")
    print(
        f"Balanced accuracy: {results["mean_test_balanced_accuracy"][best_index]}"
    )
    print()

def print_cv_results(cv):
    # pulling out my performance metrics
    accuracy_cv = np.average(cv["test_accuracy"])
    f1_cv = np.average(cv["test_f1_macro"])
    precision_cv = np.average(cv["test_precision_macro"])
    recall_cv = np.average(cv["test_recall_macro"])
    bal_accuracy_cv = np.average(cv["test_balanced_accuracy"])
    f1_group6 = np.average(cv["test_f1_group6"])
    recall_group6 = np.average(cv["test_recall_group6"])

    print("CROSS VALIDATION SCORES")
    print_all_scores(accuracy_cv, f1_cv, precision_cv, recall_cv, bal_accuracy_cv, recall_group6, f1_group6)

def analyse_prediction_results(predictions, target):
    accuracy = accuracy_score(target, predictions)
    f1 = f1_score(target, predictions, average="macro")
    precision = precision_score(target, predictions, average="macro")
    recall = recall_score(target, predictions, average="macro")
    bal_ac = balanced_accuracy_score(target, predictions)
    recall_group_6 = recall_score(target, predictions, labels=[5], average="macro")
    f1_group_6 = f1_score(target, predictions, labels=[5], average="macro")
    print_all_scores(accuracy, f1, precision, recall, bal_ac, recall_group_6, f1_group_6)


def print_all_scores(accuracy, f1, precision, recall, bal_ac, recall_group_6, f1_group_6):
    print(f"Accuracy: {accuracy}")
    print(f"F1: {f1}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"Balanced accuracy: {bal_ac}")
    print(f"Group 6 F1: {f1_group_6}")
    print(f"Group 6 Recall: {recall_group_6}")
    print()

def predict_with_qc(pipe, threshold, x, y):
    # get prediction probs for train and test
    prediction_probs = pipe.predict_proba(x)

    max_probs = np.amax(prediction_probs, axis=1)
    nc_indicies = [i for i, prob in enumerate(max_probs) if prob < threshold]
    filtered_samples = np.delete(x, nc_indicies, axis=0)
    filtered_true = np.delete(y, nc_indicies)

    predictions = pipe.predict(filtered_samples)
    return predictions, filtered_true, len(nc_indicies)
