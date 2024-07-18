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
from imblearn.over_sampling import SMOTE
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
from sklearn.utils import resample

FILE_NAME = "bootstrap_models.pkl"
RANDOM_STATE = 42

np.random.seed(RANDOM_STATE)

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
n_bootstraps = 2
n_samples = y_test.shape
predictions = np.empty((n_bootstraps, n_samples[0]))

models = []
for i in range(n_bootstraps):
    model = HistGradientBoostingClassifier(
        max_iter=1000,
        learning_rate=0.1,
        max_depth=75,
        max_leaf_nodes=41,
        min_samples_leaf=20,
    )
    pipe = ImbPipeline(
        steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", model)]
    )

    invalid_sample = True
    while invalid_sample:
        try:
            x_boot, y_boot = resample(x_train, y_train, stratify=y_train)
            pipe.fit(x_boot, y_boot)
            invalid_sample = False
        except:
            print("INVALID SAMPLE CONTINUING")
            continue

    print(f"FIT {i + 1} COMPLETE")
    models.append(pipe)


print("TRAINING COMPLETE SAVING")
joblib.dump(models, FILE_NAME)

# saving and testing save successful
print("SAVE SUCCESSFUL")
