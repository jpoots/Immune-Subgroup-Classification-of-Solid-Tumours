import { GraphControls } from "./GraphControls";
import { useRef, useState } from "react";
import Plot from "react-plotly.js";
import NothingToDisplay from "../errors/NothingToDisplay";
import { CSVLink } from "react-csv";
import { getPlotlyData, generateGraphData } from "/utils/graphHelpers.js";
import ErrorModal from "../errors/ErrorModal";
import { getData } from "../../../utils/asyncAPI";

// tnse api url and perplexity setting
const API_URL = "http://127.0.0.1:3000/tsneasync";
const MIN_PERPLEXITY = 1;

/**
 * this component contaisn the t-SNE visualisation page where analysis can be done with varying perplexities
 * @param {object} results
 * @returns the t-SNE visualisation page
 */
const Tsne = ({ results, graphData, setGraphData }) => {
  // setting up to hold dom element and graph points
  const slider = useRef();
  const max_perplexity = results.samples.length - 1;

  // set app state
  const [perplexity, setPerplexity] = useState(max_perplexity);
  const [loading, setLoading] = useState(false);
  const [dimension, setDimensions] = useState(2);
  const [disabled, setDisabled] = useState(false);
  const [title, setTitle] = useState("t-SNE");
  const [download, setDownload] = useState([]);
  const [openModal, setOpenModal] = useState(false);
  const [modalMessage, setModalMessage] = useState();

  /**
   * generates an object of the tsne results for each sample to be given to csv link
   */
  const handleDownload = () => {
    let toDownload = [];
    let id = [];
    let tsne1 = [];
    let tsne2 = [];
    let tsne3 = [];

    // for each subgroup
    Object.keys(graphData.x).forEach((key) => {
      id = graphData.ids[key];
      tsne1 = graphData.x[key];
      tsne2 = graphData.y[key];
      tsne3 = graphData.z[key];

      id.forEach((id, index) => {
        toDownload.push({
          sampleID: id,
          tsne1: tsne1[index],
          tsne2: tsne2[index],
          tsne3: tsne3[index],
        });
      });
    });
    setDownload(toDownload);
  };

  /**
   * reaches out to the data analysis endpoint, handles reponse
   */
  const handleTsne = async () => {
    setLoading(true);

    try {
      let tsneResponse = await fetch(API_URL, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          samples: results.samples,
          perplexity: parseInt(perplexity),
        }),
      });

      if (tsneResponse.ok) {
        tsneResponse = await tsneResponse.json();
        let taskID = tsneResponse.id;
        tsneResponse = await getData("tsne", taskID);
        console.log(tsneResponse.data);
      } else {
        // known error
        tsneResponse = await tsneResponse.json();
        openWarningModal(tsneResponse.error.description);
      }
      setGraphData(generateGraphData(results, tsneResponse.data, "tsne"));
      setDisabled(true);
    } catch (err) {
      openWarningModal("Something went wrong! Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * opens a warning modal with the given message
   * @param {string} message - the message to display in the warning modal
   */
  const openWarningModal = (message) => {
    setModalMessage(message);
    setOpenModal(true);
  };

  const pageTitle = "t-SNE Visualisation";
  const tooltip =
    " is an unsupervised non-linear dimensionality reduction technique for visualizing high-dimensional data.";
  const fullName = "t-distributed Stochastic Neighbor Embedding (t-SNE)";
  const tooltipLink = "https://www.datacamp.com/tutorial/introduction-t-sne";

  return (
    <div className="container">
      {results ? (
        <div className="columns">
          <div className="column is-one-quarter box">
            <GraphControls
              setDimensions={setDimensions}
              dimension={dimension}
              setTitle={setTitle}
              pageTitle={pageTitle}
              tooltipMessage={tooltip}
              fullName={fullName}
              tooltipLink={tooltipLink}
            />
            <div className="block">
              <h1 className="has-text-weight-bold mt-5">Perplexity</h1>
              <input
                type="range"
                min={MIN_PERPLEXITY}
                max={max_perplexity}
                ref={slider}
                value={perplexity}
                onChange={(e) => {
                  setPerplexity(e.target.value);
                  setDisabled(false);
                }}
                className="queens-slider"
              />
              <div className="has-text-weight-bold has-text-centered">
                {perplexity}
              </div>
            </div>
            <div className="has-text-centered">
              <button
                className={
                  "button queens-branding queens-button block " +
                  (loading ? "is-loading" : "")
                }
                onClick={handleTsne}
                disabled={loading || disabled}
              >
                Analyse
              </button>
              {graphData && (
                <CSVLink
                  data={download}
                  filename="data"
                  onClick={handleDownload}
                >
                  <button className="button is-dark">Download Report</button>
                </CSVLink>
              )}
            </div>
          </div>

          <div className="column">
            {graphData ? (
              <Plot
                data={getPlotlyData(graphData, dimension)}
                layout={{
                  title: {
                    text: title,
                  },
                  height: 700,
                  showlegend: true,
                  legend: {
                    title: { text: "Subgroup" },
                  },
                  xaxis: {
                    title: { text: "t-SNE Component 1" },
                  },
                  yaxis: {
                    title: { text: "t-SNE Component 2" },
                  },
                  scene: {
                    xaxis: { title: "Component 1" },
                    yaxis: { title: "Component 2" },
                    zaxis: { title: "Component 3" },
                    camera: {
                      eye: {
                        x: 1.25,
                        y: 1.25,
                        z: 2.25,
                      },
                    },
                  },
                }}
              />
            ) : (
              <div className="box has-text-centered">
                Your graph will appear here when analysis is complete
              </div>
            )}
          </div>
        </div>
      ) : (
        <NothingToDisplay />
      )}

      {openModal && (
        <ErrorModal modalMessage={modalMessage} setOpenModal={setOpenModal} />
      )}
    </div>
  );
};

export default Tsne;
