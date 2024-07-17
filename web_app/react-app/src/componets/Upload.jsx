import React from "react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

const Upload = ({
  setPredictions,
  setDataFile,
  setGenes,
  setPca,
  setTsne,
  setConfidence,
}) => {
  const [file, setFile] = useState();
  const navigate = useNavigate();

  const handleFile = (event) => {
    setFile(event.target.files[0]);
  };

  const handlePredict = async () => {
    // set the file for the whole project
    setDataFile(file);

    // create a form and hit the api for predictions
    const formData = new FormData();
    formData.append("samples", file);

    let geneResponse = await fetch("http://127.0.0.1:3000/extractgenes", {
      method: "POST",
      body: formData,
    });
    geneResponse = await geneResponse.json();
    geneResponse = geneResponse.results;

    console.log(geneResponse);

    let predResponse = await fetch("http://127.0.0.1:3000/predict", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(geneResponse),
    });
    predResponse = await predResponse.json();

    console.log(predResponse.results);

    let pcaResponse = await fetch("http://127.0.0.1:3000/pca", {
      method: "POST",
      body: formData,
    });
    pcaResponse = await pcaResponse.json();

    let pca = predResponse.results;

    pca.forEach((sample, index) => {
      sample["pca"] = pcaResponse.results[index];
    });

    let tsneResponse = await fetch("http://127.0.0.1:3000/tsne", {
      method: "POST",
      body: formData,
    });
    tsneResponse = await tsneResponse.json();

    let tsne = predResponse.results;
    tsne.forEach((sample, index) => {
      sample["tsne"] = tsneResponse.results[index];
    });

    let confResponse = await fetch("http://127.0.0.1:3000/confidence", {
      method: "POST",
      body: formData,
    });
    confResponse = await confResponse.json();

    let conf = predResponse.results;
    conf.forEach((sample, index) => {
      sample["confidence"] = confResponse.results[index]["confidence"];
    });

    // set predictions and reroute
    setPredictions(predResponse.results);
    setGenes(geneResponse.results);
    setPca(pca);
    setTsne(tsne);
    setConfidence(conf);

    navigate("/report");
  };

  return (
    <div className="container">
      <div>
        <input type="file" onChange={handleFile}></input>
        <button className="button is-primary" onClick={handlePredict}>
          Predict
        </button>
        <div></div>
      </div>
    </div>
  );
};

export default Upload;
