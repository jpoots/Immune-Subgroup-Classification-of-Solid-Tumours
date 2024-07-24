import { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "bulma/css/bulma.min.css";
import Header from "./componets/general/Header";
import Upload from "./componets/upload/Upload";
import Report from "./componets/tables/Report";
import "./index.css";
import GeneExpression from "./componets/tables/GeneExpression";
import Probability from "./componets/tables/Probability";
import Confidence from "./componets/tables/Confidence";
import Help from "./componets/general/Help";
import Tsne from "./componets/graphs/Tsne";
import Pca from "./componets/graphs/Pca";
import ProtectedRoute from "./componets/general/ProtectedRoute";
import NothingToDisplay from "./componets/general/NothingToDisplay";

function App() {
  const [predictions, setPredictions] = useState([]);

  const [results, setResults] = useState();
  const [summary, setSummary] = useState();

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
              <Tsne results={results} />
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
        <Route path="/help" element={<Help />} />
        <Route path="/empty" element={<NothingToDisplay />} />
      </Routes>
    </Router>
  );
}

export default App;
