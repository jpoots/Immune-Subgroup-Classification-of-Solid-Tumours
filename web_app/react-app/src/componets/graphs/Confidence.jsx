import Plot from "react-plotly.js";
import { useRef, useMemo } from "react";
import NothingToDisplay from "../errors/NothingToDisplay";

/**
 * generates the 95% confidence interval box plot from the results
 * @param {Object} results - the analysis results
 * @returns - the box plotted 95% confidence interval
 */
const Confidence = ({ results }) => {
  const graphData = useRef();

  // pull out the confidence interval from results and add to graphData
  useMemo(() => {
    let upper = {
      1: [],
      2: [],
      3: [],
      4: [],
      5: [],
      6: [],
      NC: [],
    };
    let lower = structuredClone(upper);
    let median = structuredClone(upper);
    let max = structuredClone(upper);
    let min = structuredClone(upper);
    let preds = structuredClone(upper);
    let id = structuredClone(upper);

    // could add protection here
    results.samples.forEach((sample) => {
      let prediction = sample.prediction;
      upper[prediction].push(sample.confidence.upper);
      lower[prediction].push(sample.confidence.lower);
      median[prediction].push(sample.confidence.median);

      max[prediction].push(sample.confidence.max);
      min[prediction].push(sample.confidence.min);

      id[prediction].push(sample.sampleID);
      preds[prediction].push(sample.prediction);
    });

    graphData.current = {
      upper: upper,
      lower: lower,
      median: median,
      max: max,
      min: min,
      predictions: preds,
      ids: id,
    };
  }, [results]);

  return (
    <div className="container">
      {results ? (
        <div className="box">
          <Plot
            data={Object.keys(graphData.current.upper).map((key) => ({
              q1: graphData.current.lower[key],
              median: graphData.current.median[key],
              q3: graphData.current.upper[key],
              lowerfence: graphData.current.min[key],
              upperfence: graphData.current.max[key],
              x: graphData.current.ids[key],
              // from docs
              hoverinfo: "y",
              type: "box",
              name: `${key}`,
              text: graphData.current.ids[key],
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
