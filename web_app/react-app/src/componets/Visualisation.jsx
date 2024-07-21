import Plot from "react-plotly.js";

const Visualisation = ({ results, twoD, isPca }) => {
  let samples = [];
  let x = [];
  let y = [];
  let z = [];
  let ids = [];
  let labels = [];

  let key = isPca ? "pca" : "tsne";

  if (results) {
    samples = results["samples"];
    samples.forEach((sample) => {
      x.push(sample[key][0]);
      y.push(sample[key][1]);
      z.push(sample[key][2]);
      ids.push(sample["sampleID"]);
      labels.push(sample["prediction"]);
    });
  }

  const type = twoD ? "scatter" : "scatter3d";
  const dimension = twoD ? "2" : "3";

  return (
    <div className="container">
      <div className="box">
        {results ? (
          <Plot
            data={[
              {
                x: x,
                y: y,
                z: z,
                type: type,
                mode: "markers",
                text: ids,
                marker: {
                  color: labels,
                  colorscale: "Viridis",
                },
                showlegend: false,
              },
            ]}
            layout={{ title: `${dimension}D ${key}` }}
          />
        ) : (
          <h1>Nothing to display</h1>
        )}
      </div>
    </div>
  );
};

export default Visualisation;
