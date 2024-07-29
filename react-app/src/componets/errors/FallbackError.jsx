import { Link } from "react-router-dom";

const FallbackError = () => {
  return (
    <div className="container">
      <div className="box has-text-centered">
        <h1 className="has-text-weight-bold">Sorry! Something went wrong.</h1>
        <h1>Please try again later</h1>
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

export default FallbackError;
