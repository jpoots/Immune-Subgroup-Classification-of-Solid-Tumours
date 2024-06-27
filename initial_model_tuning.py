import pandas as pd
import numpy as np
import os
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from utils import get_data # type: ignore

data  = get_data()

# defining models
svmModel = SVC()
randomForestModel = RandomForestClassifier()
gradBoostModel = HistGradientBoostingClassifier()
mlpModel = MLPClassifier()
kNeighbourModel = KNeighborsClassifier()
logRegressModel = LogisticRegression()
nbModel = GaussianNB()

scaler = StandardScaler()

# pipelines for scaling
svm = Pipeline(steps=[("scaler", scaler), ("smv", svmModel)])
randomForest = Pipeline(steps=[("scaler", scaler), ("randomForest", randomForestModel)])
gradBoost = Pipeline(steps=[("scaler", scaler), ("gradBoost", gradBoostModel)])
mlp = Pipeline(steps=[("scaler", scaler), ("mlp", mlpModel)])
kNeighbour = Pipeline(steps=[("scaler", scaler), ("kNeighbour", kNeighbourModel)])
logRegress = Pipeline(steps=[("scaler", scaler), ("logRegress", logRegressModel)])
nb = Pipeline(steps=[("scaler", scaler), ("nb", nbModel)])

models = [
    {
        "model": svm,
        "params": {
            "C": [0.001, 0.01, 0.1, 1, 10, 100, 1000],
            "kernel": ["rbf", "poly","sigmoid", "linear"],
            "gamma": ["scale", "auto", 0.001, 0.01, 0.1, 1, 10, 100],
            "degree": [2, 3, 4, 5],
            "class_weight": [None, "balance"]
        },
    },
    {
        "model": randomForest,
        "params": {
            'n_estimators': [25, 50, 100, 150], 
            'max_features': ['sqrt', 'log2', None], 
            'max_depth': [3, 6, 9], 
            'max_leaf_nodes': [3, 6, 9], 
        }
    },
    {
        "model": kNeighbour,
        "params": {
            
        }
    }
]