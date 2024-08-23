import { useState, useMemo, useContext } from "react";
import Plot from "react-plotly.js";
import GraphTitleSetter from "../../components/graphs/GraphTitleSetter";
import { CSVLink } from "react-csv";
import { ResultsContext } from "../../context/ResultsContext";
import Box from "../../components/layout/Box";
import Title from "../../components/other/Title";

/**
 * a page to display classification by cancer type in a stacked bar chart
 * @returns the classification by type page
 */
const ClassificationByType = () => {
  // set state for the app and pull context
  const [title, setTitle] = useState("Class label by cancer type");
  const [download, setDownload] = useState([]);
  const results = useContext(ResultsContext)[0];

  // useMemo used for these calcualtions as could be expensive
  // unique type ids extracted
  let typeids = useMemo(
    () => Array.from(new Set(results.samples.map((sample) => sample.typeid))),
    [results.samples]
  );

  // unique subgroups extracted
  let subgroups = useMemo(
    () =>
      Array.from(new Set(results.samples.map((sample) => sample.prediction)))
        .sort()
        .reverse(),
    [results.samples]
  );

  // traces built
  let traces = useMemo(() => {
    let traces = [];

    // for each subgroup
    subgroups.forEach((subgroup) => {
      let y = [];

      // for each type id get the samples which have the current subgroup
      typeids.forEach((typeid) => {
        let filtered = results.samples.filter(
          (sample) => sample.prediction == subgroup && sample.typeid == typeid
        );

        // add to list for the current trace
        y.push(filtered.length);
      });

      // define trace
      let trace = {
        name: subgroup,
        x: typeids,
        y: y,
        type: "bar",
      };
      traces.push(trace);
    });
    return traces;
  }, [results.samples, subgroups, typeids]);

  /**
   * handles the download of type info by CSV link. Sets data to download
   */
  const handleDownload = () => {
    // for each subgroup
    let results = traces.map((trace) => {
      let traceResults = { subgroup: trace.name };

      // get the count of each type
      trace.x.forEach((type, index) => {
        traceResults[type] = trace.y[index];
      });
      return traceResults;
    });

    // set data
    setDownload(results);
  };

  return (
    <>
      <div className="columns">
        <Box className="column is-one-quarter">
          <Title classes="mt-4">Classification by Cancer Type</Title>
          <GraphTitleSetter setTitle={setTitle} title={title} />

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
            data={traces}
            layout={{
              title: {
                text: title,
              },
              barmode: "stack",

              height: 700,
              showlegend: true,
              legend: {
                title: { text: "Subgroup" },
              },
              xaxis: {
                title: { text: "Cancer Type" },
              },
              yaxis: {
                title: { text: "Count" },
              },
            }}
          />
        </div>
      </div>
    </>
  );
};

export default ClassificationByType;
