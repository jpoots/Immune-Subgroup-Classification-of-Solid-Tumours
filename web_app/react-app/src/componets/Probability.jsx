import React from "react";

const Proability = ({ results }) => {
  let samples = results ? results["samples"] : [];

  return (
    <div className="container">
      <div className="box">
        {results ? (
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
                    {sample.probs.map((prob) => (
                      <td>{parseFloat(prob).toFixed(5)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <h1>Nothing to display</h1>
        )}
      </div>
    </div>
  );
};

export default Proability;
