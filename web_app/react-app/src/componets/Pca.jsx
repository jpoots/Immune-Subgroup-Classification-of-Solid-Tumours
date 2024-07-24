import { useEffect, useRef, useMemo, useState } from "react";
import Plot from "react-plotly.js";
import NothingToDisplay from "./NothingToDisplay";
import { CSVLink, CSVDownload } from "react-csv";

const Pca = ({ results }) => {
  const slider = useRef();
  const [perplexity, setPerplexity] = useState(50);
  const [loading, setLoading] = useState(false);
  const x = useRef();
  const y = useRef();
  const z = useRef();
  const ids = useRef();
  const predictions = useRef();
  const [dimension, setDimensions] = useState(2);
  const [disabled, setDisabled] = useState(false);
  const [title, setTitle] = useState("PCA");
  const [download, setDownload] = useState([]);

  useMemo(() => {
    let xAdd = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      NC: [],
    };

    let yAdd = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      NC: [],
    };

    let zAdd = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      NC: [],
    };

    let predsAdd = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      NC: [],
    };

    let idAdd = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      NC: [],
    };

    if (typeof results !== "undefined") {
      results.samples.forEach((sample) => {
        let prediction = sample.prediction;
        xAdd[prediction].push(sample.pca[0]);
        yAdd[prediction].push(sample.pca[1]);
        zAdd[prediction].push(sample.pca[2]);
        idAdd[prediction].push(sample.sampleID);
        predsAdd[prediction].push(sample.prediction);
      });

      x.current = xAdd;
      y.current = yAdd;
      z.current = zAdd;
      ids.current = idAdd;
      predictions.current = predsAdd;
    }
  });

  const handleDim = () => {
    if (dimension === 2) {
      setDimensions(3);
    } else {
      setDimensions(2);
    }
  };

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

  return (
    <div className="container">
      {results ? (
        <div className="columns">
          <div className="column is-one-quarter box">
            <div className="control block" onChange={handleDim}>
              <h1 className="has-text-weight-bold	mt-5">Dimensions</h1>
              <label className="radio">
                <input
                  type="radio"
                  name="dim"
                  value="2"
                  className="queens-radio mr-2"
                  checked={dimension === 2}
                />
                2D
              </label>

              <label className="radio">
                <input
                  type="radio"
                  name="dim"
                  value="3"
                  className="queens-radio mr-2"
                  checked={dimension === 3}
                />
                3D
              </label>
            </div>
            <h1 className="has-text-weight-bold">Title</h1>
            <input
              type="text"
              placeholder="Title"
              className="input queens-textfield block"
              onChange={(e) => setTitle(e.target.value)}
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
              data={Object.keys(x.current).map((key) => ({
                x: x.current[key],
                y: y.current[key],
                z: z.current[key],
                name: `${key}`,
                type: dimension === 2 ? "scatter" : "scatter3d",
                mode: "markers",
                text: ids.current[key],
                marker: {
                  color: predictions.current,
                },
              }))}
              layout={{
                title: {
                  text: title,
                  pad: {
                    b: -200,
                  },
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
                  height: 800,
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
        <NothingToDisplay />
      )}
    </div>
  );
};

export default Pca;
