import React from "react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

const Upload = ({
  setPredictions,
  setDataFile,
  setGenes,
  setProbs,
  setPca,
  setTsne,
  setConfidence,
}) => {
  const [file, setFile] = useState();
  const navigate = useNavigate();

  const handleFile = (event) => {
    setFile(event.target.files[0]);
  };

  const makeAPICall = async (endpoint, formData) => {
    const response = await fetch(endpoint, {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    const results = data.results;

    return results;
  };

  const handlePredict = async (event) => {
    // set the file for the whole project
    setDataFile(file);

    // create a form and hit the api for predictions
    const formData = new FormData();
    formData.append("samples", file);

    let predResponse = await fetch("http://127.0.0.1:3000/predict", {
      method: "POST",
      body: formData,
    });
    predResponse = await predResponse.json();

    let geneResponse = await fetch("http://127.0.0.1:3000/extractgenes", {
      method: "POST",
      body: formData,
    });
    geneResponse = await geneResponse.json();

    let probResponse = await fetch("http://127.0.0.1:3000/probability", {
      method: "POST",
      body: formData,
    });
    probResponse = await probResponse.json();

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
    setProbs(probResponse.results);
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
