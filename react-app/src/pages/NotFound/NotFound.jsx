import { Link } from "react-router-dom";
import Box from "../../components/layout/Box";
import Title from "../../components/other/Title";

/**
 * the error page to display when the requested page cannot be found
 * @returns the not found error page
 */
const NotFound = () => {
  return (
    <>
      <Box className="has-text-centered">
        <Title>Page not found!</Title>
        <h1>We can&apos;t seem to find the page your looking for</h1>
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

export default NotFound;
