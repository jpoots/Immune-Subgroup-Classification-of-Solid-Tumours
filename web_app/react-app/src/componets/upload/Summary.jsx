import { v4 as uuidv4 } from "uuid";

/**
 * shows a summary from a given object
 * @param {Object.<number, number>} summary
 * @returns
 */
const Summary = ({ summary }) => {
  return (
    <div className="box">
      <h1 className="block has-text-weight-bold">Results Summary</h1>
      {Object.keys(summary).map((subgroup) => (
        <div key={uuidv4()} className="block">
          Subgroup {subgroup}: {summary[subgroup]} sample(s)
        </div>
      ))}
    </div>
  );
};

export default Summary;
