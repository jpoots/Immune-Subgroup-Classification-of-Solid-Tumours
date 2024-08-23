import { useEffect } from "react";
import Box from "../../components/layout/Box";
import Title from "../../components/other/Title";

/**
 * shows a fallback page when error boundary is triggered
 * @param {function} resetErrorBoundary - the function to reset the error
 * @returns
 */
const FallbackError = ({ resetErrorBoundary }) => {
  // reset app
  useEffect(() => {
    resetErrorBoundary();
  });

  return (
    <Box className="has-text-centered">
      <Title>Sorry! Something went wrong.</Title>
      <h1>Please try again later</h1>
      <h1></h1>
    </Box>
  );
};

export default FallbackError;
