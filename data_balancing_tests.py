from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import normalize, scale, MinMaxScaler
from sklearn.model_selection import cross_val_score, cross_validate
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import StandardScaler
from imblearn.under_sampling import RandomUnderSampler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score, balanced_accuracy_score, roc_auc_score,recall_score, precision_score, accuracy_score, classification_report, make_scorer
from utils import get_data, split_data
from imblearn.over_sampling import SMOTE
from collections import Counter
from imblearn.pipeline import Pipeline as ImbPipeline

# A script to experiment with various data balancing ratios and techniques

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# define potential models
gb = HistGradientBoostingClassifier(early_stopping=True)
mlp = MLPClassifier(max_iter=500)
svc = svm.SVC(probability=True, C=1, degree=4, gamma="scale", kernel="poly")
rfc = RandomForestClassifier(n_jobs=-1, max_features="sqrt", n_estimators=1000, max_leaf_nodes=None, max_depth=None)
knn = KNeighborsClassifier(n_jobs=-1, n_neighbors=21)
nb = GaussianNB()
lr = LogisticRegression(max_iter=100000, n_jobs=-1)

models = [
    mlp,#svc, gb, knn, nb, mlp, lr, 
]

# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# data scaler and generic pipeleine
scaler = MinMaxScaler()

print(Counter(y))
# remove the test set and create a training and validation set
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20, stratify=y)
print(Counter(y_train))


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
rus = RandomUnderSampler(sampling_strategy=under_sample)
smt = SMOTE(sampling_strategy=over_sample)
#x_train, y_train = smt.fit_resample(x_train, y_train)
#x_train, y_train = rus.fit_resample(x_train, y_train)

x_train_val, x_test_val, y_train_val, y_test_val = train_test_split(x_train, y_train, test_size=0.20, stratify=y_train)
print(Counter(y_train_val))

fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))
fig1, axs1 = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))

scoring = ["accuracy", "f1_macro", "precision_macro", "recall_macro", "balanced_accuracy", "roc_auc_ovr"]

for model, ax, ax1 in zip(models, axs.flatten(), axs1.flatten()):
    pipe = ImbPipeline(steps=[("RUS", rus), ("SMOTE", smt), 
                              ("scaler", scaler), ("model", model)])

    # run cv and evaluate
    cv = cross_validate(pipe, x_train, y_train, cv=10, n_jobs=-1, scoring=scoring)

    # pulling out my performance metrics
    accuracy = np.average(cv["test_accuracy"])
    f1 = np.average(cv["test_f1_macro"])
    precision = np.average(cv["test_precision_macro"])
    recall = np.average(cv["test_recall_macro"])
    bal_accuracy = np.average(cv["test_balanced_accuracy"])
    roc_auc = np.average(cv["test_roc_auc_ovr"])

    # print scores
    print("Model Name: " + model.__class__.__name__)
    print(f"Accuracy: {accuracy}")
    print(f"F1: {f1}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"Balanced accuracy: {bal_accuracy}")
    print(f"ROC AUC: {roc_auc}" )

    y_test_copy = y_test

    # fit and predict
    pipe.fit(x_train_val, y_train_val)
    predictions = pipe.predict(x_test)
    prediction_probs = pipe.predict_proba(x_test)
    
    to_remove = []
    for i, prob in enumerate(prediction_probs):
        if (prob.max() < 0.7):
            to_remove.append(i)

    #print("Removed: " + str(len(to_remove)))
    #y_test_copy = np.delete(y_test_copy, to_remove)
    #predictions = np.delete(predictions, to_remove, axis=0)
    disp = ConfusionMatrixDisplay.from_predictions(
        y_test_copy, predictions, ax=ax
    )
    ax.set_title(model.__class__.__name__)

    disp = ConfusionMatrixDisplay.from_predictions(y_test_copy, predictions,  ax=ax1)
    ax.set_title(model.__class__.__name__)
    print("Accuracy on test set: " + str(accuracy_score(y_test_copy, predictions)))
    print()


plt.tight_layout()
plt.show()
