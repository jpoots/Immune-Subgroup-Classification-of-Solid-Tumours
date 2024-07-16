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

function App() {
  const [predictions, setPredictions] = useState([]);
  const [file, setFile] = useState();
  const [genes, setGenes] = useState();
  const [probs, setProbs] = useState();
  const [pca, setPca] = useState();
  const [tsne, setTsne] = useState();
  const [confidence, setConfidence] = useState();

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
              setProbs={setProbs}
              setPca={setPca}
              setTsne={setTsne}
              setConfidence={setConfidence}
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
              setProbs={setProbs}
              setPca={setPca}
              setTsne={setTsne}
              setConfidence={setConfidence}
            />
          }
        />
        <Route
          path="/geneexpression"
          element={<GeneExpression samples={genes} />}
        />
        <Route path="/report" element={<Report predictions={predictions} />} />
        <Route path="/probability" element={<Probability samples={probs} />} />
        <Route
          path="/pca2d"
          element={<Visualisation data={pca} twoD={true} isPca={true} />}
        />
        <Route
          path="/pca3d"
          element={<Visualisation data={pca} twoD={false} isPca={true} />}
        />
        <Route
          path="/tsne2d"
          element={<Visualisation data={tsne} twoD={true} isPca={false} />}
        />
        <Route
          path="/tsne3d"
          element={<Visualisation data={tsne} twoD={false} isPca={false} />}
        />
        <Route path="/confidence" element={<Confidence data={confidence} />} />
      </Routes>
    </Router>
  );
}

export default App;
