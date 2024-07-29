from ..ml_models.predictions import predict, confidence_intervals, probability
from .. import celery
from ..errors.BadRequest import BadRequest
from ..utils import json_func, csv_func
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from app.utils import gene_preprocessing
import os

TSNE_PIPE = Pipeline(
    steps=[("scaler", MinMaxScaler()), ("dr", TSNE(n_components=3, perplexity=4))]
)

PCA_PIPE = Pipeline(steps=[("scaler", StandardScaler()), ("dr", PCA(n_components=3))])


@celery.task(
    throws=(BadRequest,),
)
def confidence_celery(data):
    data = json_func(data)

    features = data["features"]
    sample_ids = data["ids"]
    interval = data["interval"]

    results = []
    for interval, id in zip(confidence_intervals(features, interval), sample_ids):

        results.append(
            {
                "sampleID": id,
                "min": interval[0],
                "lower": interval[1],
                "median": interval[2],
                "upper": interval[3],
                "max": interval[4],
            }
        )
    return results


@celery.task(
    throws=(BadRequest,),
)
def tsne_celery(data):
    data = json_func(data)

    idx = data["ids"]
    features = data["features"]
    perplexity = data["perplexity"]

    Pipeline(
        steps=[
            ("scaler", MinMaxScaler()),
            ("dr", TSNE(n_components=3, perplexity=perplexity)),
        ]
    )

    results = []
    tsne = TSNE_PIPE.fit_transform(features).tolist()
    for id, tsne_result in zip(idx, tsne):
        results.append({"sampleID": id, "tsne": tsne_result})

    return results


def celery_return(self, status, retval, task_id, args, kwargs, einfo):
    os.remove(args[0])
    return


@celery.task(
    throws=(BadRequest,),
    after_return=celery_return,
)
def analyse(filepath):
    parsed_results = csv_func(filepath)
    data = gene_preprocessing(full_analysis=True, features=parsed_results["features"])

    predictions, prediction_probs, num_nc = predict(data["features"])
    pc = PCA_PIPE.fit_transform(data["features"]).tolist()

    results = []

    for (
        sample_id,
        feature_list,
        prediction,
        prob_list,
        pc_comps,
        type_id,
    ) in zip(
        data["ids"],
        data["features"],
        predictions,
        prediction_probs,
        pc,
        parsed_results["type_ids"],
    ):
        genes = {
            gene_name: expression
            for gene_name, expression in zip(data["gene_names"], feature_list)
        }

        results.append(
            {
                "sampleID": sample_id,
                "genes": genes,
                "prediction": prediction,
                "probs": prob_list,
                "pca": pc_comps,
                "typeid": type_id,
            }
        )

    return {"samples": results, "invalid": parsed_results["invalid"], "nc": num_nc}
