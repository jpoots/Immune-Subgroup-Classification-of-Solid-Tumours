import Plot from "react-plotly.js";
import { useRef, useMemo, useState } from "react";
import TitleSetter from "./TitleSetter";
import { CSVLink } from "react-csv";

const MIN_INTERVAL = 0;
const MAX_INTERVAL = 100;
const API_URL = "http://127.0.0.1:3000/confidence";

/**
 * generates the 95% confidence interval box plot from the results
 * @param {Object} results - the analysis results
 * @returns - the box plotted 95% confidence interval
 */
const Confidence = ({ results, graphData, setGraphData }) => {
  const slider = useRef();
  const [download, setDownload] = useState([]);
  const [title, setTitle] = useState("Confidence Interval");
  const [interval, setInterval] = useState(MAX_INTERVAL);
  const [disabled, setDisabled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [modalMessage, setModalMessage] = useState();
  const [openModal, setOpenModal] = useState(false);

  /**
   * opens a warning modal with the given message
   * @param {string} message - the message to display in the warning modal
   */
  const openWarningModal = (message) => {
    setModalMessage(message);
    setOpenModal(true);
  };

  const handleDownload = () => {
    let toDownload = results.samples.map((sample) => ({
      sampleID: sample.sampleID,
      max: sample.confidence.max,
      upper: sample.confidence.upper,
      median: sample.confidence.median,
      lower: sample.confidence.lower,
      min: sample.confidence.min,
    }));

    setDownload(toDownload);
  };

  const generateConfidenceData = (confidenceResults) => {
    let upper = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      NC: [],
    };
    let lower = structuredClone(upper);
    let median = structuredClone(upper);
    let max = structuredClone(upper);
    let min = structuredClone(upper);
    let preds = structuredClone(upper);
    let id = structuredClone(upper);

    // could add protection here
    results.samples.forEach((sample, index) => {
      let prediction = sample.prediction;
      upper[prediction].push(confidenceResults[index].upper);
      lower[prediction].push(confidenceResults[index].lower);
      median[prediction].push(confidenceResults[index].median);

      max[prediction].push(confidenceResults[index].max);
      min[prediction].push(confidenceResults[index].min);

      id[prediction].push(sample.sampleID);
      preds[prediction].push(sample.prediction);
    });

    return {
      upper: upper,
      lower: lower,
      median: median,
      max: max,
      min: min,
      predictions: preds,
      ids: id,
    };
  };

  const handleConfidenceInterval = async () => {
    setLoading(true);

    try {
      let confidenceResponse = await fetch(API_URL, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          samples: results.samples,
          interval: parseInt(interval),
        }),
      });

      if (confidenceResponse.ok) {
        confidenceResponse = await confidenceResponse.json();
      } else {
        // known error
        confidenceResponse = await confidenceResponse.json();
        openWarningModal(confidenceResponse.error.description);
      }

      setGraphData(generateConfidenceData(confidenceResponse.data));
      setDisabled(true);
    } catch (err) {
      openWarningModal("Something went wrong! Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="columns">
        <div className="column is-one-quarter box">
          <h1 className="has-text-weight-bold"> Confidence Interval</h1>
          <TitleSetter setTitle={setTitle} />

          <div className="block">
            <h1 className="has-text-weight-bold mt-5">Confidence Interval</h1>
            <input
              type="range"
              min={MIN_INTERVAL}
              max={MAX_INTERVAL}
              ref={slider}
              value={interval}
              onChange={(e) => {
                setInterval(e.target.value);
                setDisabled(false);
              }}
              className="queens-slider"
            />
            <div className="has-text-weight-bold has-text-centered">
              {interval}%
            </div>
          </div>

          <div className="has-text-centered">
            <button
              className={
                "button queens-branding queens-button block " +
                (loading ? "is-loading" : "")
              }
              onClick={handleConfidenceInterval}
              disabled={loading || disabled}
            >
              Analyse
            </button>
            {graphData && (
              <CSVLink data={download} filename="data" onClick={handleDownload}>
                <button className="button is-dark">Download Report</button>
              </CSVLink>
            )}
          </div>
        </div>
        <div className="column">
          {graphData && (
            <Plot
              data={Object.keys(graphData.upper).map((key) => ({
                q1: graphData.lower[key],
                median: graphData.median[key],
                q3: graphData.upper[key],
                lowerfence: graphData.min[key],
                upperfence: graphData.max[key],
                x: graphData.ids[key],
                // from docs
                hoverinfo: "y",
                type: "box",
                name: `${key}`,
                text: graphData.ids[key],
              }))}
              layout={{
                title: {
                  text: title,
                },
                height: 700,
                showlegend: true,
                legend: {
                  title: { text: "Subgroup" },
                },
              }}
            />
          )}
        </div>
      </div>
      <button onClick={() => console.log(graphData)}>button</button>
    </div>
  );
};

export default Confidence;
