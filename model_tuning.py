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
from sklearn.metrics import ConfusionMatrixDisplay, f1_score, balanced_accuracy_score, roc_auc_score,recall_score, precision_score, accuracy_score
from imblearn.pipeline import Pipeline as ImbPipeline
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime

# This script performs grid search hyperparameter tuning for a number of alogrithms and reports the cross validated results

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

models = [
    {
        "model": RandomForestClassifier(),
        "params": { # needs looked at again
            'model__n_estimators': [10, 100, 500, 1000], 
            'model__max_features': ['sqrt', 'log2', None], 
            'model__max_depth': [3, 6, 9, None], # not included
            'model__max_leaf_nodes': [3, 6, 9, None], # not included
        }
    },
    {
    "model": HistGradientBoostingClassifier(early_stopping=True),
    "params": {
        "model__max_iter": [10, 100, 1000],
        "model__max_leaf_nodes": [2, 5, 10, 20, 50, 100],
        "model__learning_rate": [0.001, 0.01, 0.1, 1],
        "model__max_depth": [10, 20, 30, None],
    }
    },
    {
        "model": SVC(),
        "params": {
            "model__C": [0.001, 0.01, 0.1, 1, 10, 100, 1000],
            "model__kernel": ["rbf", "poly","sigmoid", "linear"],
            "model__gamma": ["scale", "auto", 0.001, 0.01, 0.1, 1, 10, 100],
            "model__degree": [2, 3, 4, 5],
        },
    },
]


""""

    "model": MLPClassifier(random_state=42),
    "params": {

    }
},
{
    "model": KNeighborsClassifier(),
    "params": { #done
        "model__n_neighbors" : range(1, 21, 2),
        "model__weights" : ['uniform','distance'],
        "metric" : ['minkowski','euclidean','manhattan']
    }
},
{
    "model": LogisticRegression(random_state=42),
    "params": {
        
    }
},
    {
    "model": GaussianNB(),
    "params": {
        
    }
}
"""


# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# data scaler and generic pipeleine
scaler = MinMaxScaler()

# get rid of test data
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

# set up samplers and fit
rus = RandomUnderSampler(sampling_strategy=under_sample)
smt = SMOTE(sampling_strategy=over_sample)

total_start = time.time()
scoring = ["accuracy", "f1_macro", "precision_macro", "recall_macro", "balanced_accuracy", "roc_auc_ovr"]
for model, ax in models:
    start = time.time()
    # try except to prevent long training runs failing because of an issue
    try:
        clf = model["model"]
        params = model["params"]
        
        pipe = ImbPipeline(steps=[("SMOTE", smt), ("RUS", rus), 
                                ("scaler", scaler), ("model", clf)])
        
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
        print(f"Model Name: {clf.__class__.__name__}")
        print(f"Tuning time: {duration}")
        print(f"Best Params: {grid_search.best_params_}")
        print(f"Accuracy: {grid_search.best_score_}")
        print(f"F1: {results["mean_test_f1_macro"][best_index]}")
        print(f"Precision: {results["mean_test_f1_precision_macro"][best_index]}")
        print(f"Recall: {results["mean_test_f1_recall_macro"][best_index]}")
        print(f"Balanced accuracy: {results["mean_test_balanced_accuracy"][best_index]}")
        print(f"ROC AUC: {results["mean_test_roc_auc_ovr"][best_index]}" )
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




    