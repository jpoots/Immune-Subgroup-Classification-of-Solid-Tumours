import { GraphControls } from "../../components/graphs/GraphControls";
import {
  useContext,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import Plot from "react-plotly.js";
import { CSVLink } from "react-csv";
import { getPlotlyData, generateGraphData } from "/utils/graphHelpers.js";
import ErrorModal from "../../components/errors/ErrorModal";
import {
  callAsyncApi,
  cancelAnalysisFunctionDefiner,
} from "../../../utils/asyncAPI";
import { API_ROOT } from "../../../utils/constants";
import EmptyGraph from "../../components/graphs/EmptyGraph";
import { ResultsContext } from "../../context/ResultsContext";
import Box from "../../components/layout/Box";
import DataTooSmall from "../../components/graphs/DataTooSmall";

// tnse api url and min perplexity setting
const API_URL = `${API_ROOT}/tsne`;
const MIN_PERPLEXITY = 1;

/**
 * this component contaisn the t-SNE visualisation page where analysis can be done with varying perplexities
 * @param {Array} graph2D - the state array for the 2D tsne graph
 * @param {Array} graph3D - the state array for the 3D tsne graph
 * @param {Array} graphDim - the state array for the tsne dimensions
 * @returns the t-SNE visualisation page. Only available is more than 3 samples
 */
const Tsne = ({ graph2D, graph3D, graphDim }) => {
  // setting up to hold dom element and graph points
  const slider = useRef();
  const results = useContext(ResultsContext)[0];

  // perplexity musn't ever be greater than 500
  const max_perplexity =
    results.samples.length - 1 < 500 ? results.samples.length - 1 : 500;

  // set app state
  const [perplexity, setPerplexity] = useState(max_perplexity);
  const [loading, setLoading] = useState(false);
  const [dimension, setDimensions] = graphDim;
  const [disabled, setDisabled] = useState(false);
  const [title, setTitle] = useState("t-SNE");
  const [download, setDownload] = useState([]);
  const [openModal, setOpenModal] = useState(false);
  const [modalMessage, setModalMessage] = useState();
  const [graphData2D, setGraphData2D] = graph2D;
  const [graphData3D, setGraphData3D] = graph3D;
  const [graphData, setGraphData] = useState();
  const cancelled = useRef();

  /**
   * useLayoutEffect returns a function which is performed on unmount
   * https://stackoverflow.com/questions/55139386/componentwillunmount-with-react-useeffect-hook
   */
  useLayoutEffect(() => cancelAnalysisFunctionDefiner(cancelled), []);

  useEffect(() => {}, [graphData]);

  /**
   * any time to graph dimension changes, on change of graphData2d or 3d and on first load, set graphData. If graph data not empty configure controls.
   */
  useLayoutEffect(() => {
    let dataToSet = dimension == 2 ? graphData2D : graphData3D;
    setGraphData(dataToSet);

    if (!dataToSet) {
      setDisabled(dataToSet ? true : false);
    } else {
      setPerplexity(dataToSet.metadata.perplexity);
      slider.current.value = dataToSet.metadata.perplexity;
      setDisabled(true);
      setTitle(`t-SNE Perplexity: ${dataToSet.metadata.perplexity}`);
    }
  }, [dimension, graphData2D, graphData3D]);

  // every time perplexity changes and on first load if graph data exists, set the disabled button appropriately
  useEffect(() => {
    if (graphData && graphData.metadata.perplexity === perplexity) {
      setDisabled(true);
    } else {
      setDisabled(false);
    }
  }, [graphData, perplexity]);

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
      // pull param lists
      id = graphData.ids[key];
      tsne1 = graphData.x[key];
      tsne2 = graphData.y[key];
      tsne3 = graphData.z[key];

      // pull out tsne
      id.forEach((id, index) => {
        let listToPush = {
          sampleID: id,
          tsne1: tsne1[index],
          tsne2: tsne2[index],
        };

        // if theres a 3 dimension push a third item
        if (dimension == 3) listToPush["tsne3"] = tsne3[index];
        toDownload.push(listToPush);
      });
    });
    setDownload(toDownload);
  };

  /**
   * reaches out to the data analysis endpoint, handles reponse
   */
  const handleTsne = async () => {
    // if the cancelled ref has been set to true it must be reset
    cancelled.current = false;

    // start loading button
    setLoading(true);

    let request = {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        samples: results.samples,
        perplexity: parseInt(perplexity),
        numDimensions: dimension,
      }),
    };

    // call api
    let tsneResults = await callAsyncApi(
      API_URL,
      request,
      setModalMessage,
      setOpenModal,
      cancelled
    );

    // if successful call set relvenant state
    if (tsneResults.success) {
      if (dimension == 2) {
        setGraphData2D(
          generateGraphData(results, tsneResults.results, "tsne", dimension, {
            perplexity: perplexity,
          })
        );
      } else {
        setGraphData3D(
          generateGraphData(results, tsneResults.results, "tsne", dimension, {
            perplexity: perplexity,
          })
        );
      }

      // disable current analyse button
      setDisabled(true);
    }

    // stop loading
    setLoading(false);
  };

  const pageTitle = "t-SNE Visualisation";
  const tooltip =
    " is an unsupervised non-linear dimensionality reduction technique for visualizing high-dimensional data.";
  const fullName = "t-distributed Stochastic Neighbor Embedding (t-SNE)";
  const tooltipLink = "https://www.datacamp.com/tutorial/introduction-t-sne";

  return (
    <>
      {results.samples.length >= 3 ? (
        <>
          <div className="columns">
            <Box className="column is-one-quarter">
              <GraphControls
                setDimensions={setDimensions}
                dimension={dimension}
                setTitle={setTitle}
                title={title}
                pageTitle={pageTitle}
                tooltipMessage={tooltip}
                fullName={fullName}
                tooltipLink={tooltipLink}
              />

              <div className="block">
                <h1 className="has-text-weight-bold">Perplexity</h1>
                <input
                  type="range"
                  min={MIN_PERPLEXITY}
                  max={max_perplexity}
                  ref={slider}
                  value={perplexity}
                  onChange={(e) => {
                    setPerplexity(e.target.value);
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
                    "button queens-branding queens-button block mr-2 " +
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
            </Box>

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
                <EmptyGraph />
              )}
            </div>
          </div>
          {openModal && (
            <ErrorModal
              modalMessage={modalMessage}
              setOpenModal={setOpenModal}
            />
          )}
        </>
      ) : (
        <DataTooSmall />
      )}
    </>
  );
};

export default Tsne;
