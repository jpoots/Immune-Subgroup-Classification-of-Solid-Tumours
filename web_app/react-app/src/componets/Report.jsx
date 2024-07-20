import React from "react";

const Report = ({ results }) => {
  let samples = [];
  if (typeof results !== "undefined") samples = results["samples"];

  return (
    <div className="container">
      <div className="box">
        {samples.length > 0 ? (
          <table className="table is-bordered is-centered">
            <tbody>
              <tr>
                <th>Sample ID</th> <th>Subgroup Classification</th>
              </tr>
              {samples.map((prediction, index) => (
                <tr key={index}>
                  <td>{prediction.sampleID}</td>
                  <td>{prediction.prediction}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <h1>Nothing to display</h1>
        )}
      </div>
    </div>
  );
};

export default Report;
