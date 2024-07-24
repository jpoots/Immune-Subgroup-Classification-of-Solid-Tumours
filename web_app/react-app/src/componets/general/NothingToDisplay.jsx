import { Link } from "react-router-dom";

/**
 * a page to be returned when results are viewed but not set
 * @returns the empty page
 */
const NothingToDisplay = () => {
  return (
    <div className="container">
      <div className="box has-text-centered">
        <h1 className="has-text-weight-bold">Nothing to display!</h1>
        <h1>
          Begin your analysis{" "}
          <Link to="/" className="queens-branding-text">
            here
          </Link>
        </h1>
      </div>
    </div>
  );
};

export default NothingToDisplay;
