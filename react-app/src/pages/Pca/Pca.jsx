import { useRef, useMemo, useState, useContext } from "react";
import Plot from "react-plotly.js";
import { CSVLink } from "react-csv";
import { GraphControls } from "../../componets/graphs/GraphControls";
import { getPlotlyData, generateGraphData } from "/utils/graphHelpers.js";
import { ResultsContext } from "../../context/ResultsContext";

/**
 * the pca visualisation page for viewing results in 2D and 3D
 * @returns the pca visualisation page
 */
const Pca = () => {
  const graphData = useRef();
  const [dimension, setDimensions] = useState(2);
  const [title, setTitle] = useState("PCA");
  const [download, setDownload] = useState([]);
  const results = useContext(ResultsContext)[0];

  /**
   * generates the graph data object using the helper function from the results
   */
  useMemo(() => {
    graphData.current = generateGraphData(results, results.samples, "pca");
  }, [results]);

  const handleDownload = () => {
    let toDownload = [];
    console.log(results.samples);
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
    " is a dimensionality reduction technique which seeks to visualise high dimensional data to while maintaining maximum variance";
  const fullName = "Principle Component Analysis (PCA)";
  const tooltipLink =
    "https://builtin.com/data-science/step-step-explanation-principal-component-analysis#:~:text=necessary%20for%20context.-,What%20Is%20Principal%20Component%20Analysis%3F,information%20in%20the%20large%20set.";

  return (
    <div className="container">
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

          <CSVLink
            data={download}
            filename="data"
            onClick={handleDownload}
            className="button is-dark"
          >
            <button>Download Report</button>
          </CSVLink>
        </div>

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
    </div>
  );
};

export default Pca;
