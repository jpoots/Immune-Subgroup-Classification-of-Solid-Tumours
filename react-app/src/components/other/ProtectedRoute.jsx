import { useContext } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { ResultsContext } from "../../context/ResultsContext";

/**
 * https://medium.com/@dennisivy/creating-protected-routes-with-react-router-v6-2c4bbaf7bc1c
 * protects components from being rendered without results where relvent. Redirects to an empty page
 * @returns - the appropriate router - either naivgate or the original
 */
const ProtectedRoute = () => {
  const results = useContext(ResultsContext)[0];
  return results ? <Outlet /> : <Navigate to="/empty" replace={true} />;
};

export default ProtectedRoute;
