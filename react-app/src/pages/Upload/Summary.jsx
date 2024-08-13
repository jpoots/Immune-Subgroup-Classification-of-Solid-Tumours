import { v4 as uuidv4 } from "uuid";
import Box from "../../components/layout/Box";

/**
 * shows a summary from a given object
 * @param {Object.<number, number>} summary
 * @returns
 */
const Summary = ({ summary }) => {
  return (
    <Box>
      <h1 className="block has-text-weight-bold">Results Summary</h1>
      {Object.keys(summary).map((subgroup) => (
        <div key={uuidv4()} className="block">
          Subgroup {subgroup}: {summary[subgroup]} sample(s)
        </div>
      ))}
    </Box>
  );
};

export default Summary;
