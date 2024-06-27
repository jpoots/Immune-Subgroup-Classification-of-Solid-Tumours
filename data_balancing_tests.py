from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, BaggingClassifier, RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import normalize, scale, MinMaxScaler
from sklearn.model_selection import cross_val_score
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import StandardScaler
from imblearn.under_sampling import RandomUnderSampler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score, balanced_accuracy_score, roc_auc_score,recall_score, precision_score
from utils import get_data, split_data # type: ignore
from imblearn.over_sampling import SMOTE, ADASYN
from collections import Counter


# define potential models
model = HistGradientBoostingClassifier(max_iter=1000, random_state=42, verbose=1)
#model = BaggingClassifier(svm.SVC(max_iter=10000000, verbose=True, kernel="rbf"))
#model = MLPClassifier(max_iter=10000000, verbose=1)
#model = svm.SVC(max_iter=10000000, kernel="rbf", gamma='scale', C=10)
#model = RandomForestClassifier(n_jobs=-1)
#model = KNeighborsClassifier(n_neighbors=95, n_jobs=-1)
#model = GaussianNB()
#model = LassoCV(verbose=True, n_jobs=-1)
#model = tree.DecisionTreeClassifier()
#model = LogisticRegression(max_iter=1000)

# import data using util
data = get_data()
idx, x, y, genes = split_data(data)

# data scaler and generic pipeleine
scaler = StandardScaler()
model = Pipeline(steps=[("scaler", scaler), ("model", model)])

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20)
print(Counter(y_train))

# define sample strategy
under_sample = {
    0: 500,
    1: 500,
    2: 385,
    3: 385,
    4: 385,
    5: 180, 
}

over_sample = {
    0: 385,
    1: 385,
    2: 385,
    3: 385,
    4: 385,
    5: 250, 
}

# set up samplers and fit
rus = RandomUnderSampler(random_state=42, sampling_strategy=under_sample)
smt = SMOTE(random_state=42, sampling_strategy=over_sample)
x_train, y_train = rus.fit_resample(x_train, y_train)
x_train, y_train = smt.fit_resample(x_train, y_train)

# run cv and evaluate
scores = cross_val_score(model, x, y, cv=5, n_jobs=-1)
print(f"Accuracy Score: {np.average(scores)}")

# fit and predict
model.fit(x_train, y_train)
predictions = model.predict(x_test)

f1 = f1_score(y_test, predictions, average="micro")


# plot the confusion matrix for the prediction
cm = confusion_matrix(y_test, predictions, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                              display_labels=model.classes_)

disp.plot()
plt.show()
