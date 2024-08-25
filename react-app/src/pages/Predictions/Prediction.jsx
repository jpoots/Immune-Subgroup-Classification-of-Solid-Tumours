import PredominanceReport from "./PredominanceReport";
import PredictionReport from "./PredictionReport";

/**
 * the report page showing the prediction table with confidence
 * @returns - a report on the predicitons
 */
const Prediction = () => {
  return (
    <>
      <PredictionReport />

      <PredominanceReport />
    </>
  );
};

export default Prediction;
