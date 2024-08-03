import ProtectedRoute from "./components/ProtectedRoute";
import { Route, Routes } from "react-router-dom";
import GeneExpression from "./pages/GeneExpression/GeneExpression";
import Prediction from "./pages/Predictions/Prediction";
import Probability from "./pages/Probability/Probability";
import Pca from "./pages/Pca/Pca";
import Tsne from "./pages/Tsne/Tsne";
import Confidence from "./pages/Confidence/Confidence";
import ClassificationByType from "./pages/ConfidenceByType/ClassificationByType";
import Upload from "./pages/Upload/Upload";
import Help from "./pages/Help/Help";
import NothingToDisplay from "./pages/NothingToDisplay/NothingToDisplay";
import NotFound from "./pages/NotFound/NotFound";
import Admin from "./pages/Admin/Admin";

/**
 * contains all the routes for the SPA
 * @param {[Object, function]} tsneState - array containing tsneGraphData and its setter
 * @param {[Object, function]} confidenceState - array containing confidenceGraphData and its setter
 * @param {[Object, function]} summaryState - array containing summary object and its setter
 * @param {[string, function]} fileNameState - array containing fileName and its setter
 * @returns - the routes objects
 */
const AllRoutes = ({
  tsneState,
  confidenceState,
  summaryState,
  fileNameState,
}) => {
  // desctructure props
  const [tsneGrahData, setTsneGraphData] = tsneState;
  const [confidenceGraphData, setConfidenceGraphData] = confidenceState;
  const [summary, setSummary] = summaryState;
  const [fileName, setFileName] = fileNameState;

  return (
    <Routes>
      <Route element={<ProtectedRoute />}>
        <Route path="/geneexpression" element={<GeneExpression />} />
        <Route path="/prediction" element={<Prediction />} />
        <Route path="/probability" element={<Probability />} />
        <Route path="/pca" element={<Pca />} />
        <Route
          path="/tsne"
          element={<Tsne graphState={[tsneGrahData, setTsneGraphData]} />}
        />
        <Route
          path="/confidence"
          element={
            <Confidence
              graphState={[confidenceGraphData, setConfidenceGraphData]}
            />
          }
        />
        <Route path="/bytype" element={<ClassificationByType />} />
      </Route>

      <Route
        exact
        path="/"
        element={
          <Upload
            summary={summary}
            setSummary={setSummary}
            filename={fileName}
            setFileName={setFileName}
            setTsneGraphData={setTsneGraphData}
            setConfidenceGraphData={setConfidenceGraphData}
          />
        }
      />

      <Route path="/admin" element={<Admin />} />

      <Route path="/help" element={<Help />} />
      <Route path="/empty" element={<NothingToDisplay />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default AllRoutes;
