from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from utils import get_data, split_data

# define potential models
gb = HistGradientBoostingClassifier(random_state=42)
mlp = MLPClassifier(random_state=42)
svc = svm.SVC(random_state=42)
rfc = RandomForestClassifier(n_jobs=-1)
knn = KNeighborsClassifier(n_jobs=-1)
nb = GaussianNB()
lr = LogisticRegression(random_state=42, n_jobs=-1)

models = [
    svc, knn, nb, rfc, mlp, lr, gb
]

# data scaler and generic pipeleine
scaler = MinMaxScaler()

# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# remove test set
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20, random_state=42)

fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(15, 10))

for model, ax in zip(models, axs.flatten()):

    pipe = Pipeline(steps=[("scaler", scaler), ("model", model)])
    
    # run cv and evaluate
    cv_scores = cross_val_score(pipe, x_train, y_train, cv=10, n_jobs=-1, scoring="f1_macro")
    cv_avg = np.average(cv_scores)
    
    # split data into train validate
    x_train, x_test, y_train, y_test = train_test_split(x_train, y_train, test_size=0.2, random_state=42)

    # fit and predict
    pipe.fit(x_train, y_train)
    predictions = pipe.predict(x_test)

    # print scores
    print("Model Name: " + model.__class__.__name__)
    print("Cross Fold: " + str(cv_avg))
    print(classification_report(y_test, predictions, labels=pipe.classes_))
    print()

    disp = ConfusionMatrixDisplay.from_predictions(
        y_test, predictions, ax=ax
    )
    ax.set_title(model.__class__.__name__)

plt.tight_layout()
plt.show()
