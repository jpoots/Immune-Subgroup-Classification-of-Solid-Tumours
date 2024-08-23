import Box from "../layout/Box";

/**
 * a box to display on PCA or t-SNE page if the sample set is too small
 * @returns the box element
 */
const DataTooSmall = () => {
  return (
    <Box className="has-text-centered">
      To use PCA or t-SNE you must be analysing at least 3 samples
    </Box>
  );
};

export default DataTooSmall;
