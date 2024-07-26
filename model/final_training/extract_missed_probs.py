import joblib
import sklearn
import numpy as np
import matplotlib.pyplot as plt
import sys
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    balanced_accuracy_score,
)


# append the path of the parent (taken from chatGPT)
sys.path.append("..")
from utils.utils import get_data, split_data

RANDOM_STATE = 42
TEST_SIZE = 0.2
MODEL_FILE_NAME = "./trained_models/model.pkl"
PROBS_FOLDER_NAME = "./prob_analysis/"
QC_THRESHOLD = 0.98


def main():
    np.random.seed(RANDOM_STATE)

    data = get_data()
    idx, x, y, _genes = split_data(data)

    _x_train1, x_test1, _y_train1, y_test1 = train_test_split(
    x, y, test_size=TEST_SIZE, stratify=y)

    y = [(sample_id, subgroup) for sample_id, subgroup in zip(idx, y)]

    x = [(sample_id, features) for sample_id, features in zip(idx, x)]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, stratify=[label for _id, label in y]
    )

    # sanity check the save
    loaded_model = joblib.load(MODEL_FILE_NAME)
    extract_nc_probs(loaded_model, QC_THRESHOLD, x_test)
    extract_missmatch_probs(loaded_model, x_test, y_test)

    predictions, true, num_removed = predict(loaded_model, QC_THRESHOLD, x_test1, y_test1)
    evaluate_performance(true, predictions, num_removed)
    plt.show()




def extract_nc_probs(pipe, threshold, x):
    # get prediction probs for train and test
    features = [features for _id, features in x]

    prediction_probs = pipe.predict_proba(features)
    predictions = pipe.predict(features)

    max_probs_test = np.amax(prediction_probs, axis=1)
    nc_indicies = [i for i, prob in enumerate(max_probs_test) if prob < threshold]

    nc_probabilities = max_probs_test[nc_indicies]
    nc_predictions = predictions[nc_indicies]
    nc_predictions = [pred + 1 for pred in nc_predictions]
    nc_ids = [x[i][0] for i in nc_indicies]

    nc_df = pd.DataFrame(data=nc_probabilities, index=nc_ids, columns=["max_prob"])
    nc_df.index.name = "sampleID"
    nc_df.insert(loc=1, column="prediction", value=nc_predictions)
    nc_df.to_csv(f"{PROBS_FOLDER_NAME}nc.csv")


def extract_missmatch_probs(pipe, x, y):
    features = [features for _id, features in x]
    subgroups = [group for _id, group in y]

    prediction_probs = pipe.predict_proba(features)
    predictions = pipe.predict(features)

    max_probs = np.amax(prediction_probs, axis=1)
    mismatched_indicies = [
        i
        for i, (prediction, subgroup) in enumerate(zip(predictions, subgroups))
        if prediction != subgroup
    ]
    mismatched_probs = [max_probs[i] for i in mismatched_indicies]
    mismatched_ids = [y[i][0] for i in mismatched_indicies]
    mismatched_predictions = predictions[mismatched_indicies]
    mismatched_predictions = [pred + 1 for pred in mismatched_predictions]


    df = pd.DataFrame(data=mismatched_probs, index=mismatched_ids, columns=["max_prob"])
    df.index.name = "sampleID"
    df.insert(loc=1, column="prediction", value=mismatched_predictions)
    df.to_csv(f"{PROBS_FOLDER_NAME}mismatch.csv")


def evaluate_performance(true, predictions, num_removed):
    print(f"Removed: {num_removed}")
    print(f"QC Threshold: {QC_THRESHOLD}")
    print(f"Accuracy: {accuracy_score(true, predictions)}")
    print(f"Recall: {recall_score(true, predictions, average="macro")}")
    print(f"Precision: {precision_score(true, predictions, average="macro")}")
    print(f"F1: {f1_score(true, predictions, average="macro")}")
    print(f"Balanced Accuracy: {balanced_accuracy_score(true, predictions)}")
    print(
        f"Class 6 F1: {f1_score(true, predictions, labels=[5], average="macro")}"
    )
    print(
        f"Class 6 Recall: {recall_score(true, predictions, labels=[5], average="macro")}"
    )
    cf = ConfusionMatrixDisplay.from_predictions(true, predictions)

def predict(pipe, threshold, x, y):
    
    # get prediction probs for train and test
    prediction_probs = pipe.predict_proba(x)

    max_probs_test = np.amax(prediction_probs, axis=1)
    nc_indicies = [i for i, prob in enumerate(max_probs_test) if prob < threshold]
    filtered_samples = np.delete(x, nc_indicies, axis=0)
    filtered_true = np.delete(y, nc_indicies)

    predictions = pipe.predict(filtered_samples)
    return predictions, filtered_true, len(nc_indicies)



if __name__ == "__main__":
    main()
