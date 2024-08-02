import { useState, useMemo, useContext } from "react";
import Plot from "react-plotly.js";
import TitleSetter from "../../componets/graphs/TitleSetter";
import { CSVLink } from "react-csv";
import { ResultsContext } from "../../context/ResultsContext";

const ClassificationByType = () => {
  const [title, setTitle] = useState("Class label by type");
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
      return results;
    });

    setDownload(results);
  };

  return (
    <div className="container">
      <div className="columns">
        <div className="column is-one-quarter box">
          <h1 className="mt-4 block has-text-weight-bold">
            Classification by Type
          </h1>

          <TitleSetter setTitle={setTitle} />

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
    </div>
  );
};

export default ClassificationByType;
