import { useState } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import "bulma/css/bulma.min.css";
import Header from "./componets/Header";
import AllRoutes from "./AllRoutes";
import { ErrorBoundary } from "react-error-boundary";
import FallbackError from "./pages/FallbackError/FallbackError";
import { ResultsContext } from "./context/ResultsContext";
import Footer from "./componets/Footer";
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
  const [tsneGrahData, setTsneGraphData] = useState();
  const [confidenceGraphData, setConfidenceGraphData] = useState();

  /**
   * reset function to reset whole app state on error
   */
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
          <AllRoutes
            tsneState={[tsneGrahData, setTsneGraphData]}
            confidenceState={[confidenceGraphData, setConfidenceGraphData]}
            summaryState={[summary, setSummary]}
            fileNameState={[fileName, setFileName]}
          />
        </ResultsContext.Provider>
      </ErrorBoundary>

      <Footer />
    </Router>
  );
}

export default App;
