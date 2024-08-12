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
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import sys

sys.path.append("..")
from utils import get_data, split_data, RANDOM_STATE
from xgboost import XGBClassifier
from sklearn.metrics import ConfusionMatrixDisplay, classification_report


"""
This is a short script attempting to explore the possibility of using a second classifier 
to identify if a sample was class 6 or not. This was never complete and thus remains messy 
and with data leakage issues but reamins in the repo as evidence of the experiment
"""

# define potential models
gb = HistGradientBoostingClassifier(random_state=RANDOM_STATE)
mlp = MLPClassifier(random_state=RANDOM_STATE)
svc = svm.SVC(class_weight="balanced", random_state=RANDOM_STATE)
rfc = RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE)
knn = KNeighborsClassifier()
nb = GaussianNB()
lr = LogisticRegression(class_weight="balanced", random_state=RANDOM_STATE)

models = [XGBClassifier(random_state=RANDOM_STATE), mlp, gb, svc, rfc, knn, nb, lr]

# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# data scaler and generic pipeleine
scaler = MinMaxScaler()

# remove the test set and create a training and validation set
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE
)

x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(
    x_train, y_train, test_size=0.20, stratify=y_train, random_state=RANDOM_STATE
)

# define sample strategy
under_sample = {
    0: 100,
    1: 100,
    2: 100,
    3: 100,
    4: 100,
}

over_sample = {
    5: 1000,
}

# set up samplers and fit
rus = RandomUnderSampler(sampling_strategy=under_sample, random_state=RANDOM_STATE)
smt = SMOTE(sampling_strategy=over_sample, random_state=RANDOM_STATE)

# x_train, y_train = smt.fit_resample(x_train, y_train)
x_train, y_train = rus.fit_resample(x_train, y_train)

x_train_val, y_train_val = rus.fit_resample(x_train_val, y_train_val)

y_train_binary = [0 if y < 5 else 1 for y in y_train]
y_train_val_binary = [0 if y < 5 else 1 for y in y_train_val]
y_test_val_binary = [0 if y < 5 else 1 for y in y_test_val]


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
    cv = cross_validate(
        pipe, x_train, y_train_binary, cv=10, n_jobs=-1, scoring=scoring
    )

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

    pipe.fit(x_train_val, y_train_val_binary)

    ax = ConfusionMatrixDisplay.from_estimator(
        pipe, x_test_val, y_test_val_binary, ax=ax
    )


svc = svm.SVC(class_weight="balanced", random_state=RANDOM_STATE)
svc = ImbPipeline(steps=[("scaler", MinMaxScaler()), ("model", svc)])
svc.fit(x_train_val, y_train_val_binary)

six_or_not = svc.predict(x_test_val)
six_indicies = [i for i, value in enumerate(six_or_not) if value == 1]
print(six_indicies)

# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# data scaler and generic pipeleine
scaler = MinMaxScaler()

# remove the test set and create a training and validation set
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, stratify=y)

x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(
    x_train, y_train, test_size=0.20, stratify=y_train
)

# define sample strategy
under_sample = {
    0: 1000,
    1: 1000,
    2: 1000,
}

over_sample = {
    3: 1000,
    4: 1000,
    5: 1000,
}

# set up samplers and fit
rus = RandomUnderSampler(sampling_strategy=under_sample, random_state=RANDOM_STATE)
smt = SMOTE(sampling_strategy=over_sample, random_state=RANDOM_STATE)
scaler = MinMaxScaler()
booster = XGBClassifier(random_state=RANDOM_STATE)

booster = ImbPipeline(
    steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", booster)]
)

booster.fit(x_train_val, y_train_val)

booster_predictions = booster.predict(x_test_val)
# booster_predictions = [
# prediction if i not in six_indicies else 5
# for i, prediction in enumerate(booster_predictions)
# ]

print(classification_report(y_test_val, booster_predictions))
ConfusionMatrixDisplay.from_predictions(y_test_val, booster_predictions)

plt.show()
