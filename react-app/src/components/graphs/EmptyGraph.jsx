import Box from "../layout/Box";

/**
 * an element to display with a graph has not yet been produced
 * @returns - graph element
 */
const EmptyGraph = () => {
  return (
    <Box className="has-text-centered">
      Your graph will appear here when analysis is complete
    </Box>
  );
};

export default EmptyGraph;
