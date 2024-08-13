import { useEffect } from "react";
import Box from "../../components/layout/Box";

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
    <Box className="has-text-centered">
      <h1 className="has-text-weight-bold">Sorry! Something went wrong.</h1>
      <h1>Please try again later</h1>
      <h1></h1>
    </Box>
  );
};

export default FallbackError;
