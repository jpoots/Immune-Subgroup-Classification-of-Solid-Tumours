import { useRef, useState } from "react";
import Plot from "react-plotly.js";

const Tsne = ({ results }) => {
  const slider = useRef();
  const [perplexity, setPerplexity] = useState(50);
  const [loading, setLoading] = useState(false);

  const x = useRef();
  const z = useRef();
  const y = useRef();
  const ids = useRef();
  const predictions = useRef();
  const [dimension, setDimensions] = useState(2);
  const [disabled, setDisabled] = useState(false);
  const [title, setTitle] = useState("t-SNE");

  const handleDim = () => {
    if (dimension === 2) {
      setDimensions(3);
    } else {
      setDimensions(2);
    }
  };

  const handleTsne = async () => {
    let samples = results.samples;
    setLoading(true);

    let tsneResponse = await fetch("http://127.0.0.1:3000/tsne", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        samples: samples,
        perplexity: perplexity,
      }),
    });
    tsneResponse = await tsneResponse.json();

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

    tsneResponse.data.forEach((sample, index) => {
      let prediction = samples[index].prediction;
      xAdd[prediction].push(sample.tsne[0]);
      yAdd[prediction].push(sample.tsne[1]);
      zAdd[prediction].push(sample.tsne[2]);
      idAdd[prediction].push(sample.sampleID);
      predsAdd[prediction].push(prediction);
    });

    x.current = xAdd;
    y.current = yAdd;
    z.current = zAdd;
    ids.current = idAdd;
    predictions.current = predsAdd;

    setLoading(false);
    setDisabled(true);
    setTitlePerplexity(perplexity);
  };

  return (
    <div className="container">
      <div className="columns">
        <div className="column is-one-quarter box">
          <div>
            <h1>Perplexity</h1>
            <input
              type="range"
              min={1}
              max={50}
              ref={slider}
              onChange={(e) => {
                setPerplexity(e.target.value);
                setDisabled(false);
              }}
            />
            <div>{perplexity}</div>
          </div>
          <div className="control" onChange={handleDim}>
            <h1>Dimensions</h1>
            <label className="radio">
              <input
                type="radio"
                name="dim"
                value="2"
                checked={dimension === 2}
              />
              2D
            </label>

            <label className="radio">
              <input
                type="radio"
                name="dim"
                value="3"
                checked={dimension === 3}
              />
              3D
            </label>
          </div>
          <h1 className="has-text-weight-bold">Title</h1>
          <input
            type="text"
            placeholder="Title"
            value={title}
            className="input"
            onChange={(e) => setTitle(e.target.value)}
          />
          <button
            className={
              "button queens-branding queens-button " +
              (loading ? "is-loading" : "")
            }
            onClick={handleTsne}
            disabled={loading || disabled}
          >
            {" "}
            Analyse{" "}
          </button>{" "}
        </div>

        <div className="column">
          {x.current && (
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
                  title: { text: "t-SNE Component 1" },
                },
                yaxis: {
                  title: { text: "t-SNE Component 2" },
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
          )}
        </div>
      </div>
    </div>
  );
};

export default Tsne;
