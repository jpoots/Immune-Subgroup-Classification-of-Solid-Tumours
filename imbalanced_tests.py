from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, BaggingClassifier, RandomForestClassifier, AdaBoostClassifier
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
from sklearn.metrics import f1_score, balanced_accuracy_score, roc_auc_score,recall_score, precision_score, accuracy_score, classification_report
from utils import get_data, split_data # type: ignore
from imblearn.over_sampling import SMOTE, ADASYN
from collections import Counter


# define potential models
#model = HistGradientBoostingClassifier(max_iter=100, random_state=42)
#model = AdaBoostClassifier(HistGradientBoostingClassifier())
#model = BaggingClassifier(svm.SVC(max_iter=10000000, verbose=True, kernel="rbf"))
#model = MLPClassifier(max_iter=10000000, verbose=1)
#model = RandomForestClassifier(n_jobs=-1)
model = svm.SVC(random_state=42, max_iter=10000)
#model = KNeighborsClassifier(n_neighbors=20, n_jobs=-1)
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

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20, random_state=42)

# run cv and evaluate
cv_scores = cross_val_score(model, x_train, y_train, cv=5, n_jobs=-1)
cv_avg = np.average(cv_scores)

# fit and predict
model.fit(x_train, y_train)
predictions = model.predict(x_test)
predictions_training = model.predict(x_train)

# scores
f1 = f1_score(y_test, predictions, average="micro")
accuracy = accuracy_score(y_test, predictions)
balanced_accuracy = balanced_accuracy_score(y_test, predictions)

# print scores
print("Model Name: " + model["model"].__class__.__name__)
print("Accuracy: " + str(accuracy))
print("Balanced Accuracy: " +  str(balanced_accuracy))
print("Cross fold: " + str(cv_avg))


""""
recall = recall_score(y_test, predictions, average="micro")
precision = precision_score(y_test, predictions, average="micro")
auc_roc = roc_auc_score(y_test, predictions, multi_class="ovr")
print("AUC-ROC: " + auc_roc)
print("Precision: " + precision)
print("Recall: " + recall)
print("Training Count: " + Counter(y_train))
print("Testing Count: " + Counter(y_test))
"""

# plot the confusion matrix for the prediction
cm = confusion_matrix(y_test, predictions, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                              display_labels=model.classes_)

# plot the confusion matrix for the prediction
cm_train = confusion_matrix(y_train, predictions_training, labels=model.classes_)
disp_train = ConfusionMatrixDisplay(confusion_matrix=cm_train,
                              display_labels=model.classes_)

print(classification_report(y_test, predictions, labels=range(0,6)))
print(classification_report(y_train, predictions_training, labels=model.classes_))

disp_train.plot()
disp.plot()
plt.show()
