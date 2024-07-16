import React from "react";

const Report = ({ predictions }) => {
  return (
    <div className="container">
      <table className="table">
        <tbody>
          <tr>
            <th>Sample ID</th> <th>Subgroup Classification</th>
          </tr>
          {predictions.map((prediction, index) => (
            <tr key={index}>
              <td>{prediction.sampleID}</td>
              <td>{prediction.prediction}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Report;
