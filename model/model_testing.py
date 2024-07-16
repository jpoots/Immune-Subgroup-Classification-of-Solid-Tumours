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
from sklearn.metrics import f1_score, balanced_accuracy_score, roc_auc_score,recall_score, precision_score, accuracy_score, ConfusionMatrixDisplay, classification_report, make_scorer
from utils import get_data, split_data
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from scipy.stats import beta

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)


# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# data scaler and generic pipeleine
scaler = MinMaxScaler()

# split train test
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, stratify=y)
x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(x, y, test_size=0.20, stratify=y)


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
bsmt = BorderlineSMOTE(sampling_strategy=over_sample)


# define candidate models wiht best hyperparams
gb_ac = ImbPipeline(steps=[("rus", rus), ("smt", smt), ("model", HistGradientBoostingClassifier(max_iter=1000, learning_rate=0.1, max_depth=None))])
gb_ac_fine = ImbPipeline(steps=[("rus", rus), ("smt", smt), ("model", HistGradientBoostingClassifier(max_iter=1000, learning_rate=0.1, max_depth=75, max_leaf_nodes=41, min_samples_leaf=20))])
gb_f1_fine = ImbPipeline(steps=[("rus", rus), ("smt", smt), ("model", HistGradientBoostingClassifier(max_iter=1500, learning_rate=0.05, max_depth=100, max_leaf_nodes=41, min_samples_leaf=20))])

gb_ba = ImbPipeline(steps=[("rus", rus), ("smt", smt), ("model", HistGradientBoostingClassifier(max_iter=1000, learning_rate=0.1, max_depth=75))])
gb_ba_fine = ImbPipeline(steps=[("rus", rus), ("smt", smt), ("model", HistGradientBoostingClassifier(max_iter=2000, learning_rate=0.1, max_depth=50, max_leaf_nodes=31, min_samples_leaf=30))])
gb_f1 = ImbPipeline(steps=[("rus", rus), ("smt", smt), ("model", HistGradientBoostingClassifier(max_iter=1000, learning_rate=0.1, max_depth=50))])

models = [
gb_ac_fine, gb_f1_fine # gb_ba, gb_ba_fine, gb_f1  #svc_bal, rfc_bal #svc_bal#knn, nb, mlp, lr, 
]

# set up figures
fig_test, axs_test = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))
fig_train, axs_train = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))
fig_test.suptitle("Confusion Matrix - Test Data")
fig_test.suptitle("Confusion Matrix - Training Data")

# set up scoring metrics to report
scoring = {
    "accuracy": "accuracy",
    "f1_macro": "f1_macro",
    "precision_macro": "precision_macro",
    "recall_macro": "recall_macro",
    "balanced_accuracy": "balanced_accuracy",
    "f1_group6": make_scorer(f1_score, average=None, labels=[5]),
    "recall_group6": make_scorer(recall_score, average=None, labels=[5]),
}

for pipe, ax_test, ax_train in zip(models, axs_test.flatten(), axs_train.flatten()):
    # run cv on all data and evaluate
    cv = cross_validate(pipe, x_train, y_train, cv=10, n_jobs=-1, scoring=scoring)

    # pulling out my performance metrics
    accuracy_cv = np.average(cv["test_accuracy"])
    f1_cv = np.average(cv["test_f1_macro"])
    precision_cv = np.average(cv["test_precision_macro"])
    recall_cv = np.average(cv["test_recall_macro"])
    bal_accuracy_cv = np.average(cv["test_balanced_accuracy"])
    f1_group6 = np.average(cv["test_f1_group6"])
    recall_group6 = np.average(cv["test_recall_group6"])

    # fit on all training data and predict
    pipe.fit(x_train_val, y_train_val)
    predictions_train = pipe.predict(x_train_val)
    probaility_train = pipe.predict_proba(x_train_val)

    max_prob = np.amax(probaility_train, axis=1)
        # Fit the beta distribution to the predicted probabilities
    
    #max_prob = np.clip(max_prob, 1e-10, 1 - 1e-10)
    a, b, loc, scale = beta.fit(max_prob, floc=0, fscale=1)

    # Create a function for the fitted beta distribution
    fitted_beta = beta(a, b, loc, scale)

    # Calculate the 5th percentile of the fitted beta distribution
    qc_threshold = fitted_beta.ppf(0.05)
    qc_threshold = 0.982
    print(f"QC Threshold: {qc_threshold}")

    # optional confidence threshold for test data, removed for the moment
    y_test_val_copy = y_test_val
    x_test_val_copy = x_test_val

    prediction_probs = pipe.predict_proba(x_test_val)    
    to_remove = [i for i, prob in enumerate(prediction_probs) if prob.max() < qc_threshold]

    print("Removed: " + str(len(to_remove)))
    #y_test_val_copy = np.delete(y_test_val_copy, to_remove)
    #x_test_val_copy = np.delete(x_test_val_copy, to_remove, axis=0)

    predictions_test = pipe.predict(x_test_val_copy)

    # set up confusion matricies
    cf_test = ConfusionMatrixDisplay.from_predictions(
        y_test_val_copy, predictions_test, ax=ax_test
    )
    ax_test.set_title(pipe.named_steps['model'].__class__.__name__)

    cf_train = ConfusionMatrixDisplay.from_predictions(
        y_train_val, predictions_train,  ax=ax_train
    )
    ax_train.set_title(pipe.named_steps['model'].__class__.__name__)

    # pulling out my test metrics
    accuracy_test = accuracy_score(y_test_val_copy, predictions_test)
    f1_test = f1_score(y_test_val_copy, predictions_test, average="macro")
    precision_test = precision_score(y_test_val_copy, predictions_test, average="macro")
    recall_test = recall_score(y_test_val_copy, predictions_test, average="macro")
    bal_accuracy_test = balanced_accuracy_score(y_test_val_copy, predictions_test)
    

    # pulling out my training metrics
    accuracy_train = accuracy_score(y_train_val, predictions_train)
    f1_train = f1_score(y_train_val, predictions_train, average="macro")
    precision_train = precision_score(y_train_val, predictions_train, average="macro")
    recall_train = recall_score(y_train_val, predictions_train, average="macro")
    bal_accuracy_train = balanced_accuracy_score(y_train_val, predictions_train)

    # print scores
    print(f"Model Name: {pipe.named_steps['model'].__class__.__name__}")

    print("CROSS VALIDATION SCORES")
    print(f"Accuracy: {accuracy_cv}")
    print(f"F1: {f1_cv}")
    print(f"Precision: {precision_cv}")
    print(f"Recall: {recall_cv}")
    print(f"Balanced accuracy: {bal_accuracy_cv}")
    print(f"Group 6 F1: {f1_group6}")
    print(f"Group 6 Recall: {recall_group6}")
    print()

    print("VALIDATION SCORES")
    print(f"Accuracy: {accuracy_test}")
    print(f"F1: {f1_test}")
    print(f"Precision: {precision_test}")
    print(f"Recall: {recall_test}")
    print(f"Balanced accuracy: {bal_accuracy_test}")
    print()
    print("TEST CLASSIFICATION REPORT")
    print(classification_report(y_test_val_copy, predictions_test))

    print("TRAIN SCORES")
    print(f"Accuracy: {accuracy_train}")
    print(f"F1: {f1_train}")
    print(f"Precision: {precision_train}")
    print(f"Recall: {recall_train}")
    print(f"Balanced accuracy: {bal_accuracy_train}")
    print()

    print("TRAIN CLASSIFICATION REPORT")
    print(classification_report(y_train_val, predictions_train))

# show matricies
plt.tight_layout()
plt.show()
