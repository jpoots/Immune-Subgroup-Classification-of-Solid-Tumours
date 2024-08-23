import { v4 as uuidv4 } from "uuid";
import Box from "../../components/layout/Box";
import Title from "../../components/other/Title";

/**
 * shows a summary from a given results object
 * @param {Object.<number, number>} summary
 * @returns
 */
const Summary = ({ summary }) => {
  return (
    <Box>
      <Title>Results Summary</Title>
      {Object.keys(summary).map((subgroup) => (
        <div key={uuidv4()} className="block">
          Subgroup {subgroup}: {summary[subgroup]} sample(s)
        </div>
      ))}
    </Box>
  );
};

export default Summary;
