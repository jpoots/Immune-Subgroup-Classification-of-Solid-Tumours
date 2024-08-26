import { useRef, useMemo, useState, useContext } from "react";
import Plot from "react-plotly.js";
import { CSVLink } from "react-csv";
import { GraphControls } from "../../components/graphs/GraphControls";
import { getPlotlyData, generateGraphData } from "/utils/graphHelpers.js";
import { ResultsContext } from "../../context/ResultsContext";
import Box from "../../components/layout/Box";
import DataTooSmall from "../../components/graphs/DataTooSmall";

/**
 * the pca visualisation page for viewing results in 2D and 3D. Only available if more than 3 samples
 * @returns the pca visualisation page
 */
const Pca = () => {
  // set up app state
  const [dimension, setDimensions] = useState(2);
  const [title, setTitle] = useState("PCA");
  const [download, setDownload] = useState([]);
  const results = useContext(ResultsContext)[0];
  const graphData = useRef();

  /**
   * generates the graph data object using the helper function from the results
   */
  useMemo(() => {
    if (results.samples.length >= 3) {
      graphData.current = generateGraphData(results, results.samples, "pca");
    }
  }, [results]);

  /**
   * set up download object for download by CSV link
   */
  const handleDownload = () => {
    let toDownload = [];
    results.samples.forEach((sample) => {
      toDownload.push({
        sampleID: sample.sampleID,
        pc1: sample.pca[0],
        pc2: sample.pca[1],
        pc3: sample.pca[2],
      });
    });
    setDownload(toDownload);
  };

  // constants for the tooltip
  const pageTitle = "PCA Visualisation";
  const tooltip =
    " is a dimensionality reduction technique which seeks to visualise high dimensional data while maintaining maximum variance";
  const fullName = "Principle Component Analysis (PCA)";
  const tooltipLink =
    "https://builtin.com/data-science/step-step-explanation-principal-component-analysis";

  return (
    <>
      {results.samples.length >= 3 ? (
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
            <div className="has-text-centered">
              <CSVLink
                data={download}
                filename="data"
                onClick={handleDownload}
                className="button is-dark"
              >
                <button>Download Report</button>
              </CSVLink>
            </div>
          </Box>
          <div className="column is-fullheight">
            <Plot
              data={getPlotlyData(graphData.current, dimension)}
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
                  title: { text: "Principle Component 1" },
                },
                yaxis: {
                  title: { text: "Principle Component 2" },
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
          </div>
        </div>
      ) : (
        <DataTooSmall />
      )}
    </>
  );
};

export default Pca;
