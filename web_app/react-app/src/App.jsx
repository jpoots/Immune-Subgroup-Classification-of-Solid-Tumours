import { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "bulma/css/bulma.min.css";
import Header from "./componets/general/Header";
import Upload from "./componets/upload/Upload";
import Report from "./componets/tables/Report";
import "./index.css";
import GeneExpression from "./componets/tables/GeneExpression";
import Probability from "./componets/tables/Probability";
import Confidence from "./componets/graphs/Confidence";
import Help from "./componets/general/Help";
import Tsne from "./componets/graphs/Tsne";
import Pca from "./componets/graphs/Pca";
import ProtectedRoute from "./componets/general/ProtectedRoute";
import NothingToDisplay from "./componets/errors/NothingToDisplay";
import NotFound from "./componets/errors/NotFound";
import ClassificationByType from "./componets/graphs/ClassificationByType";
import Protected2 from "./componets/general/Protected2";

function App() {
  const [predictions, setPredictions] = useState([]);
  const [fileName, setFileName] = useState("Upload File...");
  const [results, setResults] = useState();
  const [summary, setSummary] = useState();
  const [tsneGrahData, setTsneGraphData] = useState();

  return (
    <Router>
      <Header></Header>
      <Routes>
        <Route
          exact
          path="/"
          element={
            <Upload
              setPredictions={setPredictions}
              setResults={setResults}
              results={results}
              summary={summary}
              setSummary={setSummary}
              filename={fileName}
              setFileName={setFileName}
            />
          }
        />
        <Route
          path="/geneexpression"
          element={
            <ProtectedRoute results={results}>
              <GeneExpression results={results} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/report"
          element={
            <ProtectedRoute results={results}>
              <Report predictions={predictions} results={results} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/probability"
          element={
            <ProtectedRoute results={results}>
              <Probability samples={predictions} results={results} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/pca"
          element={
            <ProtectedRoute results={results}>
              <Pca results={results} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tsne"
          element={
            <ProtectedRoute results={results}>
              <Tsne
                results={results}
                graphData={tsneGrahData}
                setGraphData={setTsneGraphData}
              />
            </ProtectedRoute>
          }
        />
        <Route
          path="/confidence"
          element={
            <ProtectedRoute results={results}>
              <Confidence results={results} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/bytype"
          element={
            <ProtectedRoute results={results}>
              <ClassificationByType results={results} />
            </ProtectedRoute>
          }
        />
        <Route path="/help" element={<Help />} />
        <Route path="/empty" element={<NothingToDisplay />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

export default App;
