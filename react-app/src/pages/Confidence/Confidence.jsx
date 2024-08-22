import Plot from "react-plotly.js";
import { useContext, useEffect, useRef, useState } from "react";
import TitleSetter from "../../components/graphs/TitleSetter";
import { CSVLink } from "react-csv";
import { callAsyncApi } from "../../../utils/asyncAPI";
import ErrorModal from "../../components/errors/ErrorModal";
import { API_ROOT } from "../../../utils/constants";
import EmptyGraph from "../../components/graphs/EmptyGraph";
import { ResultsContext } from "../../context/ResultsContext";
import Box from "../../components/layout/Box";

const MIN_INTERVAL = 0;
const MAX_INTERVAL = 100;
const API_URL = `${API_ROOT}/confidence`;

/**
 * generates the confidence interval box plot from the results
 * @returns - the box plotted confidence interval
 */
const Confidence = ({ graphState }) => {
  const slider = useRef();
  const [download, setDownload] = useState([]);
  const [title, setTitle] = useState();
  const [interval, setInterval] = useState(95);
  const [disabled, setDisabled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [modalMessage, setModalMessage] = useState();
  const [openModal, setOpenModal] = useState(false);
  const results = useContext(ResultsContext)[0];
  const [graphData, setGraphData] = graphState;
  const cancelled = useRef();
  const confidenceResults = useRef();

  /**
   * useLayoutEffect returns a function which is performed on unmount to cancel analysis
   * https://stackoverflow.com/questions/55139386/componentwillunmount-with-react-useeffect-hook
   */
  useEffect(() => {
    const cancelAnalysis = () => {
      cancelled.current = true;
    };
    return cancelAnalysis;
  }, []);

  /**
   * handles the confidence interval download info
   */
  const handleDownload = () => {
    console.log(confidenceResults.current);
    let toDownload = confidenceResults.current.map((sample) => ({
      sampleID: sample.sampleID,
      max: sample.max,
      upper: sample.upper,
      median: sample.median,
      lower: sample.lower,
      min: sample.min,
    }));

    setDownload(toDownload);
  };

  /**
   * Generates plotly graph data from confidence
   * @param {object} confidenceResults  -  the results from the confidence API
   * @returns
   */
  const generateConfidenceData = (confidenceResults) => {
    let upper = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      7: [],
      NC: [],
    };
    let lower = structuredClone(upper);
    let median = structuredClone(upper);
    let max = structuredClone(upper);
    let min = structuredClone(upper);
    let preds = structuredClone(upper);
    let id = structuredClone(upper);

    // extracts relevant data from each sample and pushes it to relevant array
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

    // retunrns the data
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

  /**
   * calls the confidence api
   */
  const handleConfidenceInterval = async () => {
    // if the cancelled ref has been set to true it must be reset
    cancelled.current = false;

    setLoading(true);
    let request = {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        samples: results.samples,
        interval: parseInt(interval),
      }),
    };

    let confidenceAPIResults = await callAsyncApi(
      API_URL,
      request,
      setModalMessage,
      setOpenModal,
      cancelled
    );
    if (confidenceAPIResults.success) {
      setTitle(`${interval}% Confidence Interval`);
      setGraphData(generateConfidenceData(confidenceAPIResults.results));
      confidenceResults.current = confidenceAPIResults.results;
      setDisabled(true);
    }

    setLoading(false);
  };

  return (
    <>
      <div className="columns">
        <Box className="column is-one-quarter">
          <h1 className="mt-4 block has-text-weight-bold">
            {" "}
            Confidence Interval
          </h1>
          <TitleSetter setTitle={setTitle} />

          <div className="block">
            <h1 className="has-text-weight-bold mt-5">Interval</h1>
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
                "button queens-branding queens-button block mr-2 " +
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
        </Box>
        <div className="column">
          {graphData ? (
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
          ) : (
            <EmptyGraph />
          )}
        </div>
      </div>
      {openModal && (
        <ErrorModal modalMessage={modalMessage} setOpenModal={setOpenModal} />
      )}
    </>
  );
};

export default Confidence;
