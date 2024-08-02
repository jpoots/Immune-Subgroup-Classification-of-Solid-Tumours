import React from "react";
import { Link } from "react-router-dom";

const NotFound = () => {
  return (
    <div className="container">
      <div className="box has-text-centered">
        <h1 className="has-text-weight-bold">Page not found!</h1>
        <h1>We can&apos;t seem to find the page your looking for</h1>
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

export default NotFound;
