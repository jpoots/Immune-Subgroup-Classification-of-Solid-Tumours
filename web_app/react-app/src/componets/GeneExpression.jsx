import React from "react";

const GeneExpression = ({ samples }) => {
  let firstSample = samples[0];
  let geneNameList = Object.keys(firstSample.genes);

  console.log(samples);
  return (
    <div className="container">
      <div className="table-container">
        <table className="table is-bordered">
          <tbody>
            <tr>
              <th></th>
              {geneNameList.map((geneName) => (
                <th>{geneName}</th>
              ))}
            </tr>
            {samples.map((sample) => (
              <tr>
                <th>{sample.sampleID}</th>
                {Object.keys(sample.genes).map((geneName) => (
                  <td>{sample.genes[geneName]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default GeneExpression;
