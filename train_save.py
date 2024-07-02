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

FILE_NAME = "trained_model.pkl"
RANDOM_STATE = 42

np.random.seed(RANDOM_STATE)
# define model to train
model = HistGradientBoostingClassifier(learning_rate=0.1, max_depth=10, max_iter=1000, max_leaf_nodes=10, verbose=1)

# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# data scaler and generic pipeleine
scaler = MinMaxScaler()

# remove the test set
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20, stratify=y)

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
x_train, y_train = smt.fit_resample(x_train, y_train)
x_train, y_train = rus.fit_resample(x_train, y_train)

# set up pipeline and fit
pipe = Pipeline(steps=[("scaler", scaler), ("model", model)])
pipe.fit(x_train, y_train)
print("TRAINING COMPLETE SAVING")

# saving and testing save successful
joblib.dump(pipe, FILE_NAME)
print("SAVE SUCCESSFUL")

loaded_model = joblib.load(FILE_NAME)
assert isinstance(loaded_model, Pipeline) # tell VS code that this is an instance of the classifier for developer convenience
print(loaded_model.predict(x_test))