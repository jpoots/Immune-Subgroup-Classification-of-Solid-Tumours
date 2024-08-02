import { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "bulma/css/bulma.min.css";
import Header from "./componets/general/Header";
import Upload from "./componets/upload/Upload";
import Prediction from "./componets/tables/pages/Prediction";
import "./index.css";
import GeneExpression from "./componets/tables/pages/GeneExpression";
import Probability from "./componets/tables/pages/Probability";
import Confidence from "./componets/graphs/pages/Confidence";
import Help from "./componets/general/Help";
import Tsne from "./componets/graphs/pages/Tsne";
import Pca from "./componets/graphs/pages/Pca";
import ProtectedRoute from "./componets/general/ProtectedRoute";
import NothingToDisplay from "./componets/errors/NothingToDisplay";
import NotFound from "./componets/errors/NotFound";
import ClassificationByType from "./componets/graphs/pages/ClassificationByType";
import Footer from "./componets/general/Footer";
import { ErrorBoundary } from "react-error-boundary";
import FallbackError from "./componets/errors/FallbackError";
import { ResultsContext } from "./componets/context/ResultsContext";

/**
 * the main app component that contains shared app state and contains a SPA header with the below switched by a router
 * @returns the main app component
 */
function App() {
  // state for the app
  const [fileName, setFileName] = useState("Upload File...");
  const [results, setResults] = useState();
  const [summary, setSummary] = useState();
  const [tsneGrahData, setTsneGraphData] = useState();
  const [confidenceGraphData, setConfidenceGraphData] = useState();

  const resetApp = () => {
    setFileName("Upload files...");
    setResults();
    setSummary();
    setTsneGraphData();
    setConfidenceGraphData();
  };

  return (
    <Router>
      <Header />
      <ErrorBoundary FallbackComponent={FallbackError} onError={resetApp}>
        <ResultsContext.Provider value={[results, setResults]}>
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
            <Route path="/help" element={<Help />} />
            <Route path="/empty" element={<NothingToDisplay />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </ResultsContext.Provider>
      </ErrorBoundary>

      <Footer />
    </Router>
  );
}

export default App;
