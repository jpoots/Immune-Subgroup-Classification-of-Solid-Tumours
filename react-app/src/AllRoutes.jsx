import ProtectedRoute from "./components/other/ProtectedRoute";
import { Route, Routes } from "react-router-dom";
import GeneExpression from "./pages/GeneExpression/GeneExpression";
import Prediction from "./pages/Predictions/Prediction";
import Probability from "./pages/Probability/Probability";
import Pca from "./pages/Pca/Pca";
import Tsne from "./pages/Tsne/Tsne";
import Confidence from "./pages/Confidence/Confidence";
import ClassificationByType from "./pages/ClassificationByType/ClassificationByType";
import Upload from "./pages/Upload/Upload";
import Help from "./pages/Help/Help";
import NothingToDisplay from "./pages/NothingToDisplay/NothingToDisplay";
import NotFound from "./pages/NotFound/NotFound";
import Admin from "./pages/Admin/Admin";
import Login from "./pages/Login/Login";
import AuthOutlet from "@auth-kit/react-router/AuthOutlet";
/**
 * contains all the routes for the SPA
 * @param {[Object, function]} tsneState - array containing tsneGraphData and its setter
 * @param {[Object, function]} confidenceState - array containing confidenceGraphData and its setter
 * @param {[Object, function]} summaryState - array containing summary object and its setter
 * @param {[string, function]} fileNameState - array containing fileName and its setter
 * @returns - the routes objects
 */
const AllRoutes = ({
  tsneGraph2DState,
  tsneGraph3DState,
  tsneGraphDimensions,
  confidenceState,
  summaryState,
  fileNameState,
}) => {
  // desctructure props
  const [tsneGraph2D, setTsneGraph2D] = tsneGraph2DState;
  const [tsneGraph3D, setTsneGraph3D] = tsneGraph3DState;
  const [tsneDimensions, setTsneDimensions] = tsneGraphDimensions;
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
          element={
            <Tsne
              graph2D={[tsneGraph2D, setTsneGraph2D]}
              graph3D={[tsneGraph3D, setTsneGraph3D]}
              graphDim={[tsneDimensions, setTsneDimensions]}
            />
          }
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
            setTsneGraph2D={setTsneGraph2D}
            setTsneGraph3D={setTsneGraph3D}
            setConfidenceGraphData={setConfidenceGraphData}
          />
        }
      />

      <Route path="/login" element={<Login />} />

      <Route element={<AuthOutlet fallbackPath="/login" />}>
        <Route path="/admin" element={<Admin />} />
      </Route>

      <Route path="/help" element={<Help />} />
      <Route path="/empty" element={<NothingToDisplay />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default AllRoutes;
