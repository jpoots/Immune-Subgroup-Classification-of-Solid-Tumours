import numpy as np
import joblib
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
from utils import get_data, split_data
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    balanced_accuracy_score,
)
from scipy.stats import beta

FILE_NAME = "model.pkl"
RANDOM_STATE = 42

np.random.seed(RANDOM_STATE)

# define model to train
model = HistGradientBoostingClassifier(
    max_iter=1000,
    learning_rate=0.1,
    max_depth=75,
    max_leaf_nodes=41,
    min_samples_leaf=20,
)

# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# data scaler and generic pipeleine
scaler = MinMaxScaler()

# remove the test set
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, stratify=y)


# define sample strategy if necessary
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

# set up pipeline and fit
pipe = ImbPipeline(
    steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", model)]
)
pipe.fit(x_train, y_train)

prediction_probs = pipe.predict_proba(x_test)
prediction_probs_train = pipe.predict_proba(x_train)

max_probs = np.amax(prediction_probs_train, axis=1)
max_probs = np.clip(max_probs, 1e-10, 1 - 1e-10)
a, b, loc, scale = beta.fit(data=max_probs, floc=0, fscale=1)
fitted_beta = beta(a, b, loc=loc, scale=scale)
threshold = fitted_beta.ppf(0.116)
threshold = 0.989

print(y_test.shape)
max_probs_test = np.amax(prediction_probs, axis=1)

nc_indicies = [i for i, prob in enumerate(max_probs_test) if prob < threshold]
filtered_samples = np.delete(x_test, nc_indicies, axis=0)
filtered_true = np.delete(y_test, nc_indicies)

predictions = pipe.predict(filtered_samples)

cf = ConfusionMatrixDisplay.from_predictions(filtered_true, predictions)

print("TRAINING COMPLETE SAVING")

# saving and testing save successful
joblib.dump(pipe, FILE_NAME)
print("SAVE SUCCESSFUL")

# sanity check the save
loaded_model = joblib.load(FILE_NAME)
assert isinstance(
    loaded_model, Pipeline
)  # tell VS code that this is an instance of the classifier for developer convenience
print(loaded_model.predict(x_train))

print(f"Removed: {len(nc_indicies)}")
print(f"QC Threshold: {threshold}")
print(f"Accuracy: {accuracy_score(filtered_true, predictions)}")
print(f"Recall: {recall_score(filtered_true, predictions, average="macro")}")
print(f"Precision: {precision_score(filtered_true, predictions, average="macro")}")
print(f"F1: {f1_score(filtered_true, predictions, average="macro")}")
print(f"Balanced Accuracy: {balanced_accuracy_score(filtered_true, predictions)}")
print(
    f"Class 6 F1: {f1_score(filtered_true, predictions, labels=[5], average="macro")}"
)
print(
    f"Class 6 Recall: {recall_score(filtered_true, predictions, labels=[5], average="macro")}"
)

# show the generated confusion matrix
plt.show()
