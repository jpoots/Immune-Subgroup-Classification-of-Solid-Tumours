import { useState, useRef, useContext } from "react";
import uploadIcon from "/upload-solid.svg";
import { Tooltip } from "react-tooltip";
import SampleQC from "./SampleQC";
import Summary from "./Summary";
import { Link } from "react-router-dom";
import { CSVLink } from "react-csv";
import ErrorModal from "../../components/errors/ErrorModal";
import { callAsyncApi } from "../../../utils/asyncAPI";
import { API_ROOT } from "../../../utils/constants";
import { openWarningModal } from "../../../utils/openWarningModal";
import { ResultsContext } from "../../context/ResultsContext";

/**
 * constants for managing the allowed file types to upload
 */
const ALLOWED_FILES = ["csv", "txt"];
const ALLOWED_FILE_HTML = ALLOWED_FILES.map((file) => `.${file}`).join(",");
const MAX_FILE_SIZE_MB = 30;
const MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1048576;
const API_URL = `${API_ROOT}/analyse`;

/**
 *  This component renders a dynamic upload page for uploading sample data. It makes a request to the ML API, sets the results state and presents a dynamic summary and downloads
 * @param {function} setResults - setter fir results
 * @param {Object.<number, number>} [summary] - summary of results
 * @param {function} setSummary - setter for summary
 * @returns
 */
const Upload = ({
  summary,
  setSummary,
  filename,
  setFileName,
  setTsneGraph2D,
  setTsneGraph3D,
  setConfidenceGraphData,
}) => {
  // defining state for the component
  const [file, setFile] = useState();
  const [loading, setLoading] = useState(false);
  const fileInput = useRef();
  const [summaryDownload, setSummaryDownload] = useState([]);
  const [allDownload, setAllDownload] = useState([]);
  const [openModal, setOpenModal] = useState(false);
  const [modalMessage, setModalMessage] = useState();
  const cancelled = useRef();
  const [delimiter, setDelimiter] = useState();

  // pulling context
  const [results, setResults] = useContext(ResultsContext);

  /**
   * sets the filename and file for the component after reset the current ones
   * @param {event} event - the onChange event from the file input
   */
  const handleFile = (event) => {
    cancelled.current = true;
    const file = event.target.files[0];
    handleReset(file.name);
    setFile(file);
    setFileName(file.name);

    // if invlaid file type or too big, open warning modal

    if (!ALLOWED_FILES.includes(file.name.split(".").pop()))
      openWarningModal(setModalMessage, setOpenModal, "Invalid file type");
    if (file.size > MAX_FILE_SIZE)
      openWarningModal(
        setModalMessage,
        setOpenModal,
        `Files must be smaller than ${MAX_FILE_SIZE_MB} MB`
      );
  };

  /**
   * resets the state of the app and clears the file input. The use of filename allows the name to persist in the box if resetting for new immediate upload
   * @param {string} [fileName] - the name of the file to set, optional. If none is given, the filename is reset to default
   */
  const handleReset = (fileName) => {
    fileName = typeof fileName === "undefined" ? "Upload File..." : filename;
    // clear field
    fileInput.current.value = null;

    // reset the app elements
    setFile();
    setFileName(fileName);
    setLoading(false);
    setResults();
    setSummary();
    setConfidenceGraphData();
    setTsneGraph2D();
    setTsneGraph3D();
  };

  /**
   * Generates a summary of the results when called in an object for downloading
   */
  const handleSummaryDownload = () => {
    setSummaryDownload(
      Object.entries(summary).map(([sample, num_samples]) => ({
        subgroup: sample,
        num_samples: num_samples,
      }))
    );
  };

  /**
   * Generates an object from the results which can be given to csv link
   */
  const handleAllDownload = () => {
    const allDownload = [];
    results.samples.forEach((result) => {
      // initialising result dict for each result
      let resultDict = {
        sampleID: result.sampleID,
        classLabel: result.prediction,
        type: result.typeid,
      };

      // extracting probs results
      result.probs.forEach((prob, index) => {
        resultDict[`prob${index + 1}`] = prob;
      });

      // extracting pca results
      result.pca.forEach((pca, index) => {
        resultDict[`pca${index + 1}`] = pca;
      });

      // extracting genes
      Object.entries(result.genes).forEach(
        ([geneName, expression]) => (resultDict[geneName] = expression)
      );

      allDownload.push(resultDict);
    });

    setAllDownload(allDownload);
  };

  /**
   * handles the logic to reach out to the ML api and set results
   */
  const handlePredict = async () => {
    const formData = new FormData();
    let request = {
      method: "POST",
      body: formData,
    };

    // if the cancelled ref has been set to true it must be reset
    cancelled.current = false;
    // loading true to make button change
    setLoading(true);

    // create a form and hit the api for predictions
    formData.append("samples", file);
    formData.append("delimiter", delimiter);

    console.log(formData);

    let asyncResults = await callAsyncApi(
      API_URL,
      request,
      setModalMessage,
      setOpenModal,
      cancelled
    );

    if (asyncResults.success) {
      // set state
      setResults(asyncResults.results);
      setSummary(generateSummary(asyncResults.results));
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

  return (
    <div className="container">
      <div className="box">
        <div className="block">
          <h1 className="block has-text-weight-bold">
            RNA-Seq Upload{" "}
            <a
              className="queens-branding-text"
              data-tooltip-content={`ICST accepts FPKM normalised RNA-Seq data in CSV or TXT format up to ${MAX_FILE_SIZE_MB}MB. See help for more details.`}
              data-tooltip-id="icst-tooltip"
              data-tooltip-place="right"
            >
              ?
            </a>
          </h1>
        </div>
        <div className="file has-name">
          <label className="file-label">
            <input type="hidden" name="MAX_FILE_SIZE" value="1" />

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
            disabled={!file || loading || results || !delimiter}
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
        <div className="block is-flex is-align-content-center">
          <div className="select is-danger">
            <select onChange={(e) => setDelimiter(e.target.value)}>
              <option default value="">
                Select Delimiter
              </option>
              <option value=",">Comma</option>
              <option value=";">Semicolon</option>
              <option value="\t">Tab</option>
            </select>
          </div>
        </div>

        <div className="block">
          ICST is an open-access, open source software package which allows you
          to classify samples solid tumour samples into one of 6 immune
          subgroups using FPKM normalised RNA-Seq data. Please read the help
          section before use. By using the software you agree to be bound by the{" "}
          <Link to="/help" className="queens-branding-text">
            terms and conditions
          </Link>
          {""}.
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
