import { useState, useMemo, useContext } from "react";
import Plot from "react-plotly.js";
import GraphTitleSetter from "../../components/graphs/GraphTitleSetter";
import { CSVLink } from "react-csv";
import { ResultsContext } from "../../context/ResultsContext";
import Box from "../../components/layout/Box";
import Title from "../../components/other/Title";

const ClassificationByType = () => {
  const [title, setTitle] = useState("Class label by cancer type");
  const [download, setDownload] = useState([]);
  const results = useContext(ResultsContext)[0];

  // useMemo used for these calcualtions as could be expensive and rereun too much
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
    subgroups.forEach((subgroup) => {
      let y = [];
      typeids.forEach((typeid) => {
        let filtered = results.samples.filter(
          (sample) => sample.prediction == subgroup && sample.typeid == typeid
        );
        y.push(filtered.length);
      });

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

  const handleDownload = () => {
    let results = traces.map((trace) => {
      let traceResults = { subgroup: trace.name };

      trace.x.forEach((type, index) => {
        traceResults[type] = trace.y[index];
      });
      return traceResults;
    });

    setDownload(results);
  };

  return (
    <>
      <div className="columns">
        <Box className="column is-one-quarter">
          <Title classes="mt-4">Classification by Cancer Type</Title>
          <GraphTitleSetter setTitle={setTitle} />

          <CSVLink
            data={download}
            filename="data"
            onClick={handleDownload}
            className="button is-dark"
          >
            <button>Download Report</button>
          </CSVLink>
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
