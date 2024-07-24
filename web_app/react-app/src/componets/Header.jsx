import { BrowserRouter as Router, Link, Route, Routes } from "react-router-dom";
import queensLogo from "/logo.png";

const Header = () => {
  return (
    <nav className="navbar queens-branding is-dark">
      <div className="container">
        <Link to="/" className="navbar-brand">
          <div className="navbar-item">
            <img src={queensLogo} alt="Queens Logo" />
          </div>
        </Link>

        <div className="navbar-start">
          <Link to="/" className="navbar-item">
            Upload
          </Link>

          <Link to="/report" className="navbar-item">
            Report
          </Link>

          <Link to="/geneexpression" className="navbar-item">
            Gene Expression
          </Link>

          <Link to="/confidence" className="navbar-item">
            Confidence
          </Link>

          <Link to="/probability" className="navbar-item">
            Probability
          </Link>

          <Link to="/tsne" className="navbar-item">
            t-SNE
          </Link>

          <Link to="/pca" className="navbar-item">
            PCA
          </Link>
        </div>

        <div className="navbar-end">
          <Link to="/help" className="navbar-item">
            Help
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Header;
