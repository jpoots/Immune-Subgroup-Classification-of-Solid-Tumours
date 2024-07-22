import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import uploadIcon from "/upload-solid.svg";
import { Tooltip } from "react-tooltip";
import SampleQC from "./SampleQC";
import Summary from "./Summary";
import { BrowserRouter as Router, Link, Route, Routes } from "react-router-dom";
import { CSVLink, CSVDownload } from "react-csv";

const Upload = ({
  setPredictions,
  setDataFile,
  setGenes,
  setPca,
  setTsne,
  setConfidence,
  setResults,
  results,
  summary,
  setSummary,
}) => {
  const [file, setFile] = useState();
  const [filename, setFileName] = useState("Upload File...");
  const [loading, setLoading] = useState(false);
  const fileInput = useRef();
  const [summaryDownload, setSummaryDownload] = useState([]);
  const [allDownload, setAllDownload] = useState([]);

  console.log(results.samples);

  const handleFile = (event) => {
    setFile(event.target.files[0]);
    setFileName(event.target.files[0].name);
    console.log("triggered");
  };

  const handleReset = () => {
    fileInput.current.value = null;
    setFile();
    setFileName("Upload File...");
    setDataFile();
    setLoading(false);
    setResults();
  };

  const handleSummaryDownload = () => {
    setSummaryDownload(
      Object.keys(summary).map((sample) => ({
        subgroup: sample,
        num_samples: summary[sample],
      }))
    );
  };

  const handleAllDownload = () => {
    let allDownload = [];
    results.samples.forEach((result) => {
      let resultDict = {
        sampleID: result.sampleID,
        prediction: result.prediction,
        upperConfidence: result.confidence.upper,
        lowerConfidence: result.confidence.lower,
        maxConfidence: result.confidence.max,
        minConfidence: result.confidence.min,
        medianConfidence: result.confidence.median,
      };

      result.probs.forEach((prob, index) => {
        resultDict[`prob${index + 1}`] = prob;
      });

      result.pca.forEach((pca, index) => {
        resultDict[`pca${index + 1}`] = pca;
      });

      result.tsne.forEach((tsne, index) => {
        console.log(tsne);
        resultDict[`tsne${index + 1}`] = tsne;
      });

      Object.keys(result.genes).forEach(
        (gene) => (resultDict[gene] = result.genes[gene])
      );

      allDownload.push(resultDict);
    });

    console.log(allDownload);
    setAllDownload(allDownload);
  };

  const handlePredict = async () => {
    setLoading(true);

    // set the file for the whole project
    setDataFile(file);

    // create a form and hit the api for predictions
    const formData = new FormData();
    formData.append("samples", file);

    let fullResultsResponse = await fetch(
      "http://127.0.0.1:3000/performanalysis",
      {
        method: "POST",
        body: formData,
      }
    );
    fullResultsResponse = await fullResultsResponse.json();
    fullResultsResponse = fullResultsResponse.data;
    setLoading(false);

    setResults(fullResultsResponse);

    //setSummary(summaryResults);

    /*
    let geneResponse = await fetch("http://127.0.0.1:3000/extractgenes", {
      method: "POST",
      body: formData,
    });
    geneResponse = await geneResponse.json();
    geneResponse = geneResponse.data;

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

    console.log(predResponse.data);

    let pcaResponse = await fetch("http://127.0.0.1:3000/pca", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(geneResponse),
    });
    pcaResponse = await pcaResponse.json();

    let pca = predResponse.data;
    pca.forEach((sample, index) => {
      sample["pca"] = pcaResponse.results[index];
    });

    let tsneResponse = await fetch("http://127.0.0.1:3000/tsne", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(geneResponse),
    });
    tsneResponse = await tsneResponse.json();

    let tsne = predResponse.data;
    tsne.forEach((sample, index) => {
      sample["tsne"] = tsneResponse.data[index];
    });

    let confResponse = await fetch("http://127.0.0.1:3000/confidence", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(geneResponse),
    });
    confResponse = await confResponse.json();

    let conf = predResponse.results;
    conf.forEach((sample, index) => {
      sample["confidence"] = confResponse.results[index]["confidence"];
    });

    console.log(conf);

    // set predictions and reroute
    setPredictions(predResponse.results);
    setGenes(geneResponse);
    setPca(pca);
    setTsne(tsne);
    setConfidence(conf);
    */
  };

  return (
    <div className="container">
      <div className="box">
        <div className="block">
          <h1 className="block has-text-weight-bold">
            RNA-Seq Upload{" "}
            <a
              className="queens-branding-text"
              data-tooltip-content={
                "ICST accepts FPKM normalised RNA-Seq data structured as shown in the test data. See help for more details."
              }
              data-tooltip-id="my-tooltip"
              data-tooltip-place="right"
            >
              ?
            </a>
          </h1>
        </div>

        <div className="file has-name">
          <label className="file-label">
            <input
              type="file"
              onChange={handleFile}
              className="file-input"
              ref={fileInput}
            />
            <span className="file-cta">
              <span className="file-icon">
                <img src={uploadIcon} alt="" />
              </span>
              <span className="file-label">Choose File</span>
            </span>
            <span className="file-name" id="filename">
              {filename}
            </span>
          </label>

          <button
            className={
              "button queens-branding queens-button " +
              (loading ? "is-loading" : "")
            }
            onClick={handlePredict}
            disabled={!file || loading || results}
          >
            {" "}
            Analyse{" "}
          </button>

          <button
            className="button is-dark"
            onClick={handleReset}
            disabled={loading || !results}
          >
            {" "}
            Reset{" "}
          </button>
        </div>

        <div className="block">
          ICST is an open-access, open source software package which allows you
          to classify samples into one of 6 immune subgroups. Please read the
          help section before use.
        </div>

        <div className="block">
          <a
            href="/test_data.csv"
            className="queens-branding-text mr-5"
            download={true}
          >
            Download Test Data
          </a>
          <Link to="/help" className="queens-branding-text">
            Help
          </Link>
        </div>
      </div>
      {results && <SampleQC results={results} />}
      {results && (
        <Summary results={results} setSummary={setSummary} summary={summary} />
      )}

      {results && (
        <CSVLink
          data={summaryDownload}
          filename="data"
          onClick={handleSummaryDownload}
          className="button is-dark"
        >
          <button>Download Report</button>
        </CSVLink>
      )}

      {results && (
        <CSVLink
          data={allDownload}
          filename="data"
          onClick={handleAllDownload}
          className="button queens-branding queens-button"
        >
          <button>Download All Info</button>
        </CSVLink>
      )}

      <Tooltip id="my-tooltip" />
    </div>
  );
};

export default Upload;
