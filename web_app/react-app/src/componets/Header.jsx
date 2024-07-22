import { BrowserRouter as Router, Link, Route, Routes } from "react-router-dom";
import queensLogo from "/logo.png";

const Header = () => {
  return (
    <nav className="navbar queens-branding is-dark">
      <div className="container">
        <div className="navbar-brand">
          <Link to="/" className="navbar-item">
            <img src={queensLogo} alt="Queens Logo" />
          </Link>
        </div>

        <div className="navbar-start">
          <Link to="/upload" className="navbar-item">
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

          <div className="navbar-item has-dropdown is-hoverable">
            <a className="navbar-link">PCA</a>

            <div className="navbar-dropdown">
              <Link to="/pca2d" className="navbar-item">
                2D
              </Link>

              <Link to="/pca3d" className="navbar-item">
                3D
              </Link>
            </div>
          </div>

          <div className="navbar-item has-dropdown is-hoverable">
            <a className="navbar-link">t-SNE</a>

            <div className="navbar-dropdown">
              <Link to="/tsne2d" className="navbar-item">
                2D
              </Link>

              <Link to="/tsne3d" className="navbar-item">
                3D
              </Link>
            </div>
          </div>
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
