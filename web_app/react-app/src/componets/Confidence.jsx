import Plot from "react-plotly.js";
import { useRef, useMemo } from "react";
import NothingToDisplay from "./NothingToDisplay";

const Confidence = ({ results }) => {
  let samples = [];

  const upper = useRef();
  const lower = useRef();
  const max = useRef();
  const min = useRef();
  const median = useRef();
  const ids = useRef();
  const predictions = useRef();

  console.log(results);

  useMemo(() => {
    let upperAdd = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      NC: [],
    };

    let lowerAdd = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      NC: [],
    };

    let medianAdd = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      NC: [],
    };
    let maxAdd = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      NC: [],
    };
    let minAdd = {
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
        upperAdd[prediction].push(sample.confidence.upper);
        lowerAdd[prediction].push(sample.confidence.lower);
        medianAdd[prediction].push(sample.confidence.median);

        maxAdd[prediction].push(sample.confidence.max);
        minAdd[prediction].push(sample.confidence.min);

        idAdd[prediction].push(sample.sampleID);
        predsAdd[prediction].push(sample.prediction);
      });

      upper.current = upperAdd;
      lower.current = lowerAdd;
      median.current = medianAdd;
      max.current = maxAdd;
      min.current = minAdd;
      ids.current = idAdd;
      predictions.current = predsAdd;
    }
  });

  return (
    <div className="container">
      {results ? (
        <div className="box">
          <Plot
            data={Object.keys(lower.current).map((key) => ({
              q1: lower.current[key],
              median: median.current[key],
              q3: upper.current[key],
              lowerfence: min.current[key],
              upperfence: max.current[key],
              x: ids.current[key],
              // from docs
              hoverinfo: "y",
              type: "box",
              name: `${key}`,
              text: ids.current[key],
            }))}
            layout={{
              title: {
                text: "95% Confidence Interval",
              },
              height: 700,
              showlegend: true,
              legend: {
                title: { text: "Subgroup" },
              },
            }}
          />
        </div>
      ) : (
        <NothingToDisplay />
      )}
    </div>
  );
};

export default Confidence;
