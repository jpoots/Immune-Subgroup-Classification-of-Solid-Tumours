import React from "react";
import Plot from "react-plotly.js";

const Confidence = ({ data }) => {
  let upper = [];
  let median = [];
  let lower = [];
  let min = [];
  let max = [];
  let ids = [];

  data.forEach((sample) => {
    upper.push(sample.confidence.upper);
    median.push(sample.confidence.median);
    lower.push(sample.confidence.lower);
    min.push(sample.confidence.min);
    max.push(sample.confidence.max);
    ids.push(sample.sampleID);
  });

  console.log(ids);

  return (
    <div className="container">
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
    </div>
  );
};

export default Confidence;
