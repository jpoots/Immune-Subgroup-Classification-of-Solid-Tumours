from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from utils import get_data, split_data
from imblearn.over_sampling import SMOTE, ADASYN
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import ConfusionMatrixDisplay, f1_score, balanced_accuracy_score, roc_auc_score,recall_score, precision_score, accuracy_score, make_scorer
from imblearn.pipeline import Pipeline as ImbPipeline
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime

# This script performs grid search hyperparameter tuning for a number of alogrithms and reports the cross validated results

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

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

# data scaler and generic pipeleine
scaler = MinMaxScaler()

"""
excluded from inital tests due to necessary compute
'model__min_samples_split': [3, 6, 9, None], 
'model__min_samples_leaf': [3, 6, 9, None],
"""

models = [
    # donzo
    {
        "model": Pipeline(steps=[("scaler", scaler), ("model", SVC(class_weight="balanced"))]),
        "params": {
            "model__C": [0.001, 0.01, 0.1, 1, 10, 100, 1000],
            "model__kernel": ["rbf", "poly","sigmoid"],
            "model__gamma": ["scale", "auto", 0.001, 0.01, 0.1, 1, 10, 100],
            "model__degree": [2, 3, 4, 5],
        },
    },
    {

        # donzo
        "model": ImbPipeline(steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", RandomForestClassifier(n_jobs=-1))]),
        "params": { # top two are the most important
            'model__n_estimators': [100, 500, 1000, 2000], 
            'model__max_features': ['sqrt', 'log2', None, 100, 220], 
            'model__max_depth': [10, 20, 50, 100, None]
        }
    },
    # donzo
    {
    "model": ImbPipeline(steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", HistGradientBoostingClassifier(early_stopping=True))]) ,
    "params": {
        "model__max_iter": [10, 100, 500, 1000],
        "model__learning_rate": [0.001, 0.01, 0.1, 1],
        "model__max_depth": [25, 50, 75, None],
    }
    },

    #donzo
    {
    "model": Pipeline(steps=[("scaler", scaler), ("model", LogisticRegression(n_jobs=-1, max_iter=1000, class_weight="balanced"))]) ,
    "params": {
        "model__C": np.logspace(-4, 4, 20),
        'model__solver': ['lbfgs','newton-cg','liblinear','sag','saga'],
        "model__penalty": ['l1', 'l2', 'elasticnet', 'none'],
    }
    },
    {
    "model": ImbPipeline(steps=[("rus", rus), ("smt", smt), ("scaler", scaler), ("model", MLPClassifier(max_iter=1000))]) ,
    "params": {
        'model__hidden_layer_sizes': [(300,), (300, 200), (300,200,100)],
        'model__activation': ['tanh', 'relu'],
        'model__solver': ['sgd', 'adam'],
        'model__alpha': [0.0001, 0.001, 0.01, 0.1],
        'model__learning_rate': ['constant','adaptive'],
    }
    }
]

# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# get rid of test data
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20, stratify=y)

total_start = time.time()


scoring = {"accuracy" : "accuracy",
           "balanced_accuracy": "balanced_accuracy",
            "f1": make_scorer(f1_score, average="macro", zero_division=np.nan), 
            "precision": make_scorer(precision_score, average="macro", zero_division=np.nan),
            "recall": make_scorer(recall_score, average="macro", zero_division=np.nan), 
        } # ROC_AUC is not included due to the computational cost

for model in models:
    start = time.time()

    # try except to prevent long training runs failing because of an issue
    try:
        pipe = model["model"]
        params = model["params"]
                
        # grid search to return results for a range of metrics and refit on accuracy
        grid_search = GridSearchCV(pipe, params, n_jobs=-1, scoring=scoring, refit="accuracy", cv=10)
        grid_search.fit(x_train, y_train)

        # model tuning time
        end = time.time()
        duration_seconds = end - start
        duration = datetime.timedelta(seconds=duration_seconds)

        results = grid_search.cv_results_
        best_index = grid_search.best_index_

        # model scoring on accuracy
        print("CROSS VALIDATION ON BEST MODEL")
        print(f"Model Name: {pipe.named_steps['model'].__class__.__name__}")
        print(f"Tuning time: {duration}")
        print(f"Best Params: {grid_search.best_params_}")
        print(f"Accuracy: {results['mean_test_accuracy'][best_index]}")
        print(f"F1: {results['mean_test_f1'][best_index]}")
        print(f"Precision: {results['mean_test_precision'][best_index]}")
        print(f"Recall: {results['mean_test_recall'][best_index]}")
        print(f"Balanced accuracy: {results['mean_test_balanced_accuracy'][best_index]}")
        print()


    except Exception as e:
        print(e)
try: 
    total_end = time.time()
    duration_seconds_total = total_end - total_start
    duration_total = datetime.timedelta(seconds=duration_seconds_total)
    print(f"Total tuning time: {duration_total}")
except Exception as e:
    print(e)




    