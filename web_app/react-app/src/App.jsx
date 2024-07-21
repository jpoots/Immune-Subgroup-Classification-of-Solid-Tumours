import { useState } from "react";
import { BrowserRouter as Router, Link, Route, Routes } from "react-router-dom";
import "bulma/css/bulma.min.css";
import Header from "./componets/Header";
import Upload from "./componets/Upload";
import Report from "./componets/Report";
import "./index.css";
import GeneExpression from "./componets/GeneExpression";
import Probability from "./componets/Probability";
import Visualisation from "./componets/Visualisation";
import Confidence from "./componets/Confidence";
import Help from "./componets/Help";

function App() {
  const [predictions, setPredictions] = useState([]);
  const [file, setFile] = useState();
  const [genes, setGenes] = useState();
  const [pca, setPca] = useState();
  const [tsne, setTsne] = useState();
  const [confidence, setConfidence] = useState();
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
              setDataFile={setFile}
              setGenes={setGenes}
              setPca={setPca}
              setTsne={setTsne}
              setConfidence={setConfidence}
              setResults={setResults}
              results={results}
              summary={summary}
              setSummary={setSummary}
            />
          }
        />
        <Route
          exact
          path="/upload"
          element={
            <Upload
              setPredictions={setPredictions}
              setDataFile={setFile}
              setGenes={setGenes}
              setPca={setPca}
              setTsne={setTsne}
              setConfidence={setConfidence}
              setResults={setResults}
              results={results}
              summary={summary}
              setSummary={setSummary}
            />
          }
        />
        <Route
          path="/geneexpression"
          element={<GeneExpression results={results} />}
        />
        <Route
          path="/report"
          element={<Report predictions={predictions} results={results} />}
        />
        <Route
          path="/probability"
          element={<Probability samples={predictions} results={results} />}
        />
        <Route
          path="/pca2d"
          element={<Visualisation twoD={true} isPca={true} results={results} />}
        />
        <Route
          path="/pca3d"
          element={
            <Visualisation twoD={false} isPca={true} results={results} />
          }
        />
        <Route
          path="/tsne2d"
          element={
            <Visualisation twoD={true} isPca={false} results={results} />
          }
        />
        <Route
          path="/tsne3d"
          element={
            <Visualisation twoD={false} isPca={false} results={results} />
          }
        />
        <Route path="/confidence" element={<Confidence results={results} />} />
        <Route path="/help" element={<Help />} />
      </Routes>
    </Router>
  );
}

export default App;
