import { Link } from "react-router-dom";
const NothingToDisplay = () => {
  return (
    <div className="box has-text-centered">
      <h1 className="has-text-weight-bold">Nothing to display!</h1>
      <h1>
        Begin your analysis{" "}
        <Link to="/upload" className="queens-branding-text">
          here
        </Link>
      </h1>
    </div>
  );
};

export default NothingToDisplay;
