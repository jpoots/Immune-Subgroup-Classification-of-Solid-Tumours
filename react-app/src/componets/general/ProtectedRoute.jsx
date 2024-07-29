import { Navigate } from "react-router-dom";

//https://www.makeuseof.com/create-protected-route-in-react/
//https://stackoverflow.com/questions/48497510/simple-conditional-routing-in-reactjs

/**
 * protects components from being rendered without results where relvent. Redirects to an empty page
 * @param {Componet} children - the child to route to if results is available
 * @param {Object} results - the results of the analysis
 * @returns - the appropriate router - either naivgate or the original
 */
const ProtectedRoute = ({ results, children }) => {
  console.log(results);
  if (!results) {
    return <Navigate to="/empty" replace={true} />;
  } else {
    return children;
  }
};

export default ProtectedRoute;
