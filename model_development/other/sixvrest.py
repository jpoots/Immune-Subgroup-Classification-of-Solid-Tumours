from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    GradientBoostingClassifier,
)

from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_validate
import numpy as np
import matplotlib.pyplot as plt
from imblearn.under_sampling import RandomUnderSampler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    f1_score,
    recall_score,
    make_scorer,
)
from utils.utils import get_data, split_data
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

"""
This is a short script attempting to explore the possibility of using a second classifier 
to identify if a sample was class 6 or not. This was never complete and thus remain messy 
but reamins in the repo as evidence of the experiment
"""

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# define potential models
gb = HistGradientBoostingClassifier()
mlp = MLPClassifier()
svc = svm.SVC(class_weight="balanced")
rfc = RandomForestClassifier(class_weight="balanced")
knn = KNeighborsClassifier()
nb = GaussianNB()
lr = LogisticRegression(class_weight="balanced")

models = [mlp, gb, svc, rfc, knn, nb, lr]

# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# data scaler and generic pipeleine
scaler = MinMaxScaler()

# remove the test set and create a training and validation set
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, stratify=y)

# define sample strategy
under_sample = {
    0: 50,
    1: 50,
    2: 50,
    3: 50,
    4: 50,
}

over_sample = {
    5: 250,
}

# set up samplers and fit
rus = RandomUnderSampler(sampling_strategy=under_sample)
smt = SMOTE(sampling_strategy=over_sample)
x_train, y_train = smt.fit_resample(x_train, y_train)
x_train, y_train = rus.fit_resample(x_train, y_train)

y[y < 5] = 0
y[y == 5] = 1

x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(
    x_train, y_train, test_size=0.20, stratify=y_train
)

y_train[y_train < 5] = 0
y_train[y_train == 5] = 1

fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))

scoring = {
    "accuracy": "accuracy",
    "f1_macro": "f1_macro",
    "precision_macro": "precision_macro",
    "recall_macro": "recall_macro",
    "balanced_accuracy": "balanced_accuracy",
    "f1_group6": make_scorer(f1_score, average=None, labels=[1]),
    "recall_group6": make_scorer(recall_score, average=None, labels=[1]),
}

for model, ax in zip(models, axs.flatten()):
    pipe = ImbPipeline(steps=[("scaler", scaler), ("model", model)])

    # run cv and evaluate
    cv = cross_validate(pipe, x_train, y_train, cv=10, n_jobs=-1, scoring=scoring)

    # pulling out my performance metrics
    accuracy = np.average(cv["test_accuracy"])
    f1 = np.average(cv["test_f1_macro"])
    precision = np.average(cv["test_precision_macro"])
    recall = np.average(cv["test_recall_macro"])
    bal_accuracy = np.average(cv["test_balanced_accuracy"])
    f1_group6 = np.average(cv["test_f1_group6"])
    recall_group6 = np.average(cv["test_recall_group6"])

    # print scores
    print("Model Name: " + model.__class__.__name__)
    print(f"Accuracy: {accuracy}")
    print(f"F1: {f1}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"Balanced accuracy: {bal_accuracy}")
    print(f"Group 6 F1: {f1_group6}")
    print(f"Group 6 Recall: {recall_group6}")
    print()

    y_test_copy = y_test
