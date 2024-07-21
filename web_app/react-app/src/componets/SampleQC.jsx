const SampleQC = ({ results }) => {
  return (
    <div className="box">
      <h1 className="block">Gene QC</h1>
      <div className="block">
        {results["samples"].length} sample(s) passed gene QC
      </div>
      <div className="block">
        {results["nc"]} sample(s) were deemed non-classifiable due to a low
        confidence score
      </div>
      <div className="block">
        {results["invalid"]} sample(s) could not be processed due to a large
        number of mising genes
      </div>
    </div>
  );
};

export default SampleQC;
