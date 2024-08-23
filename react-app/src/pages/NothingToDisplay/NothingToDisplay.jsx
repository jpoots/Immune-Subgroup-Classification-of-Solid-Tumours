import { Link } from "react-router-dom";
import Box from "../../components/layout/Box";
import Title from "../../components/other/Title";

/**
 * a page to be returned when results are viewed but not set
 * @returns the empty page
 */
const NothingToDisplay = () => {
  return (
    <>
      <Box className="has-text-centered">
        <Title>Nothing to display!</Title>
        <h1>
          Begin your analysis{" "}
          <Link to="/" className="queens-branding-text">
            here
          </Link>
        </h1>
      </Box>
    </>
  );
};

export default NothingToDisplay;
