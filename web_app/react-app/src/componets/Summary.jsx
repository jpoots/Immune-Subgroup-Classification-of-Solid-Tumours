import { v4 as uuidv4 } from "uuid";

const Summary = ({ results, setSummary, summary }) => {
  if (typeof summary === "undefined") {
    summary = {
      1: 0,
      2: 0,
      3: 0,
      4: 0,
      5: 0,
      6: 0,
      NC: 0,
    };
    results["samples"].forEach((result) => summary[result.prediction]++);
    setSummary(summary);
  }

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
