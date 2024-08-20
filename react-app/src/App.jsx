import { useState } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import "bulma/css/bulma.min.css";
import Header from "./components/layout/Header";
import AllRoutes from "./AllRoutes";
import { ErrorBoundary } from "react-error-boundary";
import FallbackError from "./pages/FallbackError/FallbackError";
import { ResultsContext } from "./context/ResultsContext";
import Footer from "./components/layout/Footer";
import Container from "./components/layout/Container";
import "./index.css";

/**
 * the main app component that contains shared app state and contains a SPA header with the below switched by a router
 * @returns the main app component
 */
function App() {
  // state for the whole app
  const [fileName, setFileName] = useState("Upload File...");
  const [results, setResults] = useState();
  const [summary, setSummary] = useState();
  const [tsneGraph2D, setTsneGraph2D] = useState();
  const [tsneGraph3D, setTsneGraph3D] = useState();
  const [tsneGraphDimensions, setTsneGraphDimensions] = useState(2);
  const [confidenceGraphData, setConfidenceGraphData] = useState();

  /**
   * reset function to reset whole app state on error
   */
  const resetApp = () => {
    setFileName("Upload files...");
    setResults();
    setSummary();
    setTsneGraph2D();
    setTsneGraph3D();
    setTsneGraphDimensions(2);
    setConfidenceGraphData();
  };

  return (
    <Router basename="/icst">
      <Header />
      <ErrorBoundary FallbackComponent={FallbackError} onError={resetApp}>
        <ResultsContext.Provider value={[results, setResults]}>
          <Container>
            <AllRoutes
              tsneGraph2DState={[tsneGraph2D, setTsneGraph2D]}
              tsneGraph3DState={[tsneGraph3D, setTsneGraph3D]}
              tsneGraphDimensions={[
                tsneGraphDimensions,
                setTsneGraphDimensions,
              ]}
              confidenceState={[confidenceGraphData, setConfidenceGraphData]}
              summaryState={[summary, setSummary]}
              fileNameState={[fileName, setFileName]}
              resetApp={resetApp}
            />
          </Container>
        </ResultsContext.Provider>
      </ErrorBoundary>

      <Footer />
    </Router>
  );
}

export default App;
