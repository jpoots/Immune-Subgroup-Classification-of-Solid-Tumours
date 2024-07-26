import { NavLink } from "react-router-dom";
import queensLogo from "/logo.png";

/**
 * the header navbar for the app
 * @returns the header
 */
const Header = () => {
  const navbarClassName = ({ isActive }) =>
    ["navbar-item", isActive ? "is-current-page" : ""].join(" ");

  return (
    <nav className="navbar queens-branding is-dark">
      <div className="container">
        <NavLink to="/" className="navbar-brand">
          <div className="navbar-item">
            <img src={queensLogo} alt="Queens Logo" />
          </div>
        </NavLink>

        <div className="navbar-start">
          <NavLink to="/" className={navbarClassName}>
            Upload
          </NavLink>

          <NavLink to="/report" className={navbarClassName}>
            Report
          </NavLink>

          <NavLink to="/geneexpression" className={navbarClassName}>
            Gene Expression
          </NavLink>

          <NavLink to="/confidence" className={navbarClassName}>
            Confidence
          </NavLink>

          <NavLink to="/probability" className={navbarClassName}>
            Probability
          </NavLink>

          <NavLink to="/tsne" className={navbarClassName}>
            t-SNE
          </NavLink>

          <NavLink to="/pca" className={navbarClassName}>
            PCA
          </NavLink>
          <NavLink to="/bytype" className={navbarClassName}>
            Type
          </NavLink>
        </div>

        <div className="navbar-end">
          <NavLink to="/help" className={navbarClassName}>
            Help
          </NavLink>
        </div>
      </div>
    </nav>
  );
};

export default Header;
