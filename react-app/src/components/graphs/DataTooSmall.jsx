import Box from "../layout/Box";

const DataTooSmall = () => {
  return (
    <Box className="has-text-centered">
      To use PCA or t-SNE you must be analysing at least 3 samples
    </Box>
  );
};

export default DataTooSmall;
