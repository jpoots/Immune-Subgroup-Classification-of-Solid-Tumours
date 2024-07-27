""""
@views.route("/tsne", methods=["POST"])
@parse_json
def tsne():

    idx = request.idx
    features = request.features
    perplexity = request.perplexity

    print(perplexity)
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

    return jsonify({"data": results})


@views.route("/confidence", methods=["POST"])
@parse_json
def confidence():
    features = request.features
    sample_ids = request.idx
    interval = request.interval

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
    return jsonify({"data": results})



@views.route("/performanalysis", methods=["POST"])
@parse_csv
def perform_analysis():
    data = gene_preprocessing(full_analysis=True, features=request.features)

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
        request.typeids,
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

    return jsonify(
        {"data": {"samples": results, "invalid": request.invalid, "nc": num_nc}}
    )
"""
