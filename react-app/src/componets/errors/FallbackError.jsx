import { useEffect } from "react";

/**
 * shows a fallbakc page when error boundary is triggered
 * @param {boolean} error - the error boolean
 * @param {function} resetErrorBoundary - the function to reset the error
 * @returns
 */
const FallbackError = ({ resetErrorBoundary }) => {
  useEffect(() => {
    resetErrorBoundary();
  });
  return (
    <div className="container">
      <div className="box has-text-centered">
        <h1 className="has-text-weight-bold">Sorry! Something went wrong.</h1>
        <h1>Please try again later</h1>
        <h1></h1>
      </div>
    </div>
  );
};

export default FallbackError;
