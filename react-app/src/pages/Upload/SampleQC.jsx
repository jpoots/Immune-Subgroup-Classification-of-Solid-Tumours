import { useContext } from "react";
import { ResultsContext } from "../../context/ResultsContext";
import Box from "../../components/layout/Box";
import Title from "../../components/other/Title";

/**
 * given a results object returns a summary of quality control
 * @returns - a summary of the QC results
 */
const SampleQC = () => {
  const results = useContext(ResultsContext)[0];
  return (
    <Box>
      <Title>Gene QC</Title>
      <div className="block">
        {results["samples"].length} sample(s) passed gene QC
      </div>

      <div className="block">
        {results["invalid"]} sample(s) could not be processed due to a large
        number of mising genes
      </div>

      <div className="block">
        {results["predominant"]} sample(s) could be assigned predominant
        subgroups (subgroup 7)
      </div>
      <div className="block">
        {results["nc"]} sample(s) were deemed non-classifiable due to a low
        confidence score
      </div>
    </Box>
  );
};

export default SampleQC;
