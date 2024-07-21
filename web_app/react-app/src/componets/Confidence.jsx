import Plot from "react-plotly.js";

const Confidence = ({ results }) => {
  let samples = [];

  let upper = [];
  let median = [];
  let lower = [];
  let min = [];
  let max = [];
  let ids = [];

  if (results) {
    samples = results["samples"];
    samples.forEach((sample) => {
      upper.push(sample.confidence.upper);
      median.push(sample.confidence.median);
      lower.push(sample.confidence.lower);
      min.push(sample.confidence.min);
      max.push(sample.confidence.max);
      ids.push(sample.sampleID);
    });
  }

  return (
    <div className="container">
      <div className="box">
        {results ? (
          <Plot
            data={[
              {
                q1: lower,
                median: median,
                q3: upper,
                lowerfence: min,
                upperfence: max,
                x: ids,
                type: "box",
              },
            ]}
            layout={{ title: `Confidence` }}
          />
        ) : (
          <h1>Nothing to display</h1>
        )}
      </div>
    </div>
  );
};

export default Confidence;
