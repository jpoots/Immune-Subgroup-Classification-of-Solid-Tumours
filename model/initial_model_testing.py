from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score, cross_validate
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    make_scorer,
    f1_score,
    recall_score,
)
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from utils import get_data, split_data
from sklearn.decomposition import NMF
from lightgbm import LGBMClassifier


RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# define potential models
gb = HistGradientBoostingClassifier(class_weight="balanced")
mlp = MLPClassifier(max_iter=1000)
svc = svm.SVC(class_weight="balanced")
rfc = RandomForestClassifier(n_jobs=-1, class_weight="balanced")
knn = KNeighborsClassifier(n_jobs=-1)
nb = GaussianNB()
lr = LogisticRegression(n_jobs=-1, max_iter=1000, class_weight="balanced")

models = [svc, knn, nb, rfc, mlp, lr, gb]

# data scaler and generic pipeleine
scaler = MinMaxScaler()

# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# remove test set
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, stratify=y)

# split data into train validate
x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(
    x_train, y_train, test_size=0.2, stratify=y_train
)

fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))

scoring = {
    "accuracy": "accuracy",
    "f1_macro": "f1_macro",
    "precision_macro": "precision_macro",
    "recall_macro": "recall_macro",
    "balanced_accuracy": "balanced_accuracy",
    "f1_group6": make_scorer(f1_score, average=None, labels=[5]),
    "recall_group6": make_scorer(recall_score, average=None, labels=[5]),
}


for model, ax in zip(models, axs.flatten()):

    pipe = Pipeline(steps=[("scaler", scaler), ("model", model)])

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

    # fit and predict
    pipe.fit(x_train_val, y_train_val)
    predictions = pipe.predict(x_test_val)

    disp = ConfusionMatrixDisplay.from_predictions(y_test_val, predictions, ax=ax)
    ax.set_title(model.__class__.__name__)

plt.tight_layout()
plt.show()
