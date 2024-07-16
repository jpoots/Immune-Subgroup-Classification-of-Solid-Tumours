import React from "react";

const Proability = ({ samples }) => {
  console.log(samples);

  return (
    <div className="container">
      <div className="table-container">
        <table className="table is-bordered">
          <tbody>
            <tr>
              <th></th>
              <th>1</th>
              <th>2</th>
              <th>3</th>
              <th>4</th>
              <th>5</th>
              <th>6</th>
            </tr>
            {samples.map((sample) => (
              <tr>
                <th>{sample["sampleID"]}</th>
                {sample.prediction.map((pred) => (
                  <td>{parseFloat(pred).toFixed(5)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Proability;
