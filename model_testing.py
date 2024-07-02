import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler
from imblearn.under_sampling import RandomUnderSampler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score, balanced_accuracy_score, roc_auc_score,recall_score, precision_score, accuracy_score, ConfusionMatrixDisplay
from utils import get_data, split_data
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# define candidate models wiht best hyperparams
gb_bal = HistGradientBoostingClassifier(early_stopping=True)
svc_bal = SVC(probability=True, C=1, degree=4, gamma="scale", kernel="poly")
rfc_bal = RandomForestClassifier(n_jobs=-1, max_features="sqrt", n_estimators=1000, max_leaf_nodes=None, max_depth=None)

models = [
    rfc_bal, svc_bal, gb_bal, #knn, nb, mlp, lr, 
]

# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# data scaler and generic pipeleine
scaler = MinMaxScaler()

# split train test
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20, stratify=y)

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

# set up data balancing
rus = RandomUnderSampler(sampling_strategy=under_sample)
smt = SMOTE(sampling_strategy=over_sample)

# set up figures
fig_test, axs_test = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))
fig_train, axs_train = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))
fig_test.suptitle("Confusion Matrix - Test Data")
fig_test.suptitle("Confusion Matrix - Training Data")

# set up scoring metrics to report
scoring = ["accuracy", "f1_macro", "precision_macro", "recall_macro", "balanced_accuracy", "roc_auc_ovr"]

for model, ax_test, ax_train in zip(models, axs_test.flatten(), axs_train.flatten()):
    pipe = ImbPipeline(steps=[("SMOTE", smt), ("RUS", rus), 
                              ("scaler", scaler), ("model", model)])

    # run cv on all data and evaluate
    cv = cross_validate(pipe, x_train, y_train, cv=10, n_jobs=-1, scoring=scoring)

    # pulling out my performance metrics
    accuracy_cv = np.average(cv["test_accuracy"])
    f1_cv = np.average(cv["test_f1_macro"])
    precision_cv = np.average(cv["test_precision_macro"])
    recall_cv = np.average(cv["test_recall_macro"])
    bal_accuracy_cv = np.average(cv["test_balanced_accuracy"])
    roc_auc_cv = np.average(cv["test_roc_auc_ovr"])

    # fit on all training data and predict
    pipe.fit(x_train, y_train)
    predictions_test = pipe.predict(x_test)
    predictions_train = pipe.predict(x_train)

    """
    # optional confidence threshold for test data, removed for the moment
    y_test_copy = y_test
    prediction_probs = pipe.predict_proba(x_test)    
    to_remove = []
    for i, prob in enumerate(prediction_probs):
        if (prob.max() < 0):
            to_remove.append(i)

    print("Removed: " + str(len(to_remove)))
    y_test_copy = np.delete(y_test_copy, to_remove)
    predictions = np.delete(predictions, to_remove, axis=0)
    """

    # set up confusion matricies
    cf_test = ConfusionMatrixDisplay.from_predictions(
        y_test, predictions_test, ax=ax_test
    )
    ax_test.set_title(model.__class__.__name__)

    cf_train = ConfusionMatrixDisplay.from_predictions(
        y_train, predictions_train,  ax=ax_train
    )
    ax_train.set_title(model.__class__.__name__)

    # pulling out my test metrics
    accuracy_test = accuracy_score(y_test, predictions_test)
    f1_test = f1_score(y_test, predictions_test, average="macro")
    precision_test = precision_score(y_test, predictions_test, average="macro")
    recall_test = recall_score(y_test, predictions_test, average="macro")
    bal_accuracy_test = balanced_accuracy_score(y_test, predictions_test)
    roc_auc_test = roc_auc_score(y_test, predictions_test, multi_class="ovr", average="macro")

    # pulling out my training metrics
    accuracy_train = accuracy_score(y_train, predictions_train)
    f1_train = f1_score(y_train, predictions_train, average="macro")
    precision_train = precision_score(y_train, predictions_train, average="macro")
    recall_train = recall_score(y_train, predictions_train, average="macro")
    bal_accuracy_train = balanced_accuracy_score(y_train, predictions_train)
    roc_auc_train = roc_auc_score(y_train, predictions_train, multi_class="ovr", average="macro")

    # print scores
    print("Model Name: " + model.__class__.__name__)

    print("CROSS VALIDATION SCORES")
    print(f"Accuracy: {accuracy_cv}")
    print(f"F1: {f1_cv}")
    print(f"Precision: {precision_cv}")
    print(f"Recall: {recall_cv}")
    print(f"Balanced accuracy: {bal_accuracy_cv}")
    print(f"ROC AUC: {roc_auc_cv}" )
    print()

    print("TEST SCORES")
    print(f"Accuracy: {accuracy_test}")
    print(f"F1: {f1_test}")
    print(f"Precision: {precision_test}")
    print(f"Recall: {recall_test}")
    print(f"Balanced accuracy: {bal_accuracy_test}")
    print(f"ROC AUC: {roc_auc_test}")
    print()

    print("TRAIN SCORES")
    print(f"Accuracy: {accuracy_train}")
    print(f"F1: {f1_train}")
    print(f"Precision: {precision_train}")
    print(f"Recall: {recall_train}")
    print(f"Balanced accuracy: {bal_accuracy_train}")
    print(f"ROC AUC: {roc_auc_train}")
    print()

# show matricies
plt.tight_layout()
plt.show()
