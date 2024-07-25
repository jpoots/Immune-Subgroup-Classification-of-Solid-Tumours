import { useState, useRef } from "react";
import uploadIcon from "/upload-solid.svg";
import { Tooltip } from "react-tooltip";
import SampleQC from "./SampleQC";
import Summary from "./Summary";
import { Link } from "react-router-dom";
import { CSVLink } from "react-csv";
import ErrorModal from "../general/ErrorModal";

/**
 * constants for managing the allowed file types to upload
 */
const ALLOWED_FILES = ["csv", "txt"];
const ALLOWED_FILE_HTML = ALLOWED_FILES.map((file) => `.${file}`).join(",");

/**
 *  This component renders a dynamic upload page for uploading sample data. It makes a request to the ML API, sets the results state and presents a dynamic summary and downloads
 * @param {function} setResults - setter fir results
 * @param {Object} [results] - results from analysis
 * @param {Object.<number, number>} [summary] - summary of results
 * @param {function} setSummary - setter for summary
 * @returns
 */
const Upload = ({ setResults, results, summary, setSummary }) => {
  // defining state for the component
  const [file, setFile] = useState();
  const [filename, setFileName] = useState("Upload File...");
  const [loading, setLoading] = useState(false);
  const fileInput = useRef();
  const [summaryDownload, setSummaryDownload] = useState([]);
  const [allDownload, setAllDownload] = useState([]);
  const [openModal, setOpenModal] = useState(false);
  const [modalMessage, setModalMessage] = useState();

  /**
   * sets the filename and file for the component after reset the current ones
   * @param {event} event - the onChange event
   */
  const handleFile = (event) => {
    let file = event.target.files[0];
    handleReset(file.name);
    setFile(file);
    setFileName(file.name);

    // if invlaid file type, open warning modal
    if (!ALLOWED_FILES.includes(file.name.split(".").pop()))
      openWarningModal("Invalid file type");
  };

  /**
   * resets the state of the app and clears the file input. The use of filename allows the name to persist in the box if resetting for new immediate upload
   * @param {string} [fileName] - the name of the file to set, optional. If none is given, the filename is reset to default
   */
  const handleReset = (fileName) => {
    fileName = typeof fileName === "undefined" ? "Upload File..." : filename;
    fileInput.current.value = null;
    setFile();
    setFileName(fileName);
    setLoading(false);
    setResults();
    setSummary();
  };

  /**
   * Generates a summary of the results when called in an object for downloading
   */
  const handleSummaryDownload = () => {
    setSummaryDownload(
      Object.keys(summary).map((sample) => ({
        subgroup: sample,
        num_samples: summary[sample],
      }))
    );
  };

  /**
   * Generates an object from the results which can be given to csv link
   */
  const handleAllDownload = () => {
    let allDownload = [];
    results.samples.forEach((result) => {
      // initialising result dict for each result
      let resultDict = {
        sampleID: result.sampleID,
        prediction: result.prediction,
        upperConfidence: result.confidence.upper,
        lowerConfidence: result.confidence.lower,
        maxConfidence: result.confidence.max,
        minConfidence: result.confidence.min,
        medianConfidence: result.confidence.median,
      };

      // extracting probs results
      result.probs.forEach((prob, index) => {
        resultDict[`prob${index + 1}`] = prob;
      });

      // extracting pca results
      result.pca.forEach((pca, index) => {
        resultDict[`pca${index + 1}`] = pca;
      });

      // extracting tsne results
      result.tsne.forEach((tsne, index) => {
        console.log(tsne);
        resultDict[`tsne${index + 1}`] = tsne;
      });

      // extracting genes
      Object.keys(result.genes).forEach(
        (gene) => (resultDict[gene] = result.genes[gene])
      );

      allDownload.push(resultDict);
    });

    setAllDownload(allDownload);
  };

  /**
   * handles the logic to reach out to the ML api and set results
   */
  const handlePredict = async () => {
    // loading true to make button change
    setLoading(true);

    // create a form and hit the api for predictions
    const formData = new FormData();
    formData.append("samples", file);

    let fullResultsResponse = [];
    try {
      fullResultsResponse = await fetch(
        "http://127.0.0.1:3000/performanalysis",
        {
          method: "POST",
          body: formData,
        }
      );

      if (fullResultsResponse.ok) {
        fullResultsResponse = await fullResultsResponse.json();
        fullResultsResponse = fullResultsResponse.data;

        // set state
        setResults(fullResultsResponse);
        setSummary(generateSummary(fullResultsResponse));
      } else {
        // known error
        fullResultsResponse = await fullResultsResponse.json();
        openWarningModal(fullResultsResponse.error.description);
      }
    } catch (err) {
      // unkown error
      openWarningModal("Something went wrong! Please try again later.");
    }
    setLoading(false);
  };

  /**
   * generate a summary given results
   * @param {object} results
   * @returns a summary object to be given to csv link
   */
  const generateSummary = (results) => {
    // generate summary
    let summaryToSet = {
      1: 0,
      2: 0,
      3: 0,
      4: 0,
      5: 0,
      6: 0,
      NC: 0,
    };
    results["samples"].forEach((result) => summaryToSet[result.prediction]++);
    return summaryToSet;
  };

  /**
   * opens a warning modal with the given message and resets the app
   * @param {string} message - the message to display in the warning modal
   */
  const openWarningModal = (message) => {
    setModalMessage(message);
    setOpenModal(true);
    handleReset();
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
              data-tooltip-id="icst-tooltip"
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
              accept={ALLOWED_FILE_HTML}
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
            className={`button queens-branding queens-button ml-2 mr-2 ${
              loading ? "is-loading" : ""
            }`}
            onClick={handlePredict}
            disabled={!file || loading || results}
          >
            Analyse
          </button>

          <button
            className="button is-dark"
            onClick={() => handleReset()}
            disabled={loading || !results}
          >
            Reset
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
      {results && <Summary summary={summary} />}

      {results && (
        <CSVLink
          data={summaryDownload}
          filename="data"
          onClick={handleSummaryDownload}
          className="button is-dark mr-2 mb-5"
        >
          <button>Download Summary</button>
        </CSVLink>
      )}

      {results && (
        <CSVLink
          data={allDownload}
          filename="data"
          onClick={handleAllDownload}
          className="button queens-branding queens-button mr-2 mb-5"
        >
          <button>Download All Info</button>
        </CSVLink>
      )}

      {openModal && (
        <ErrorModal modalMessage={modalMessage} setOpenModal={setOpenModal} />
      )}

      <Tooltip id="icst-tooltip" />
    </div>
  );
};

export default Upload;
