import { useEffect, useState } from "react";
import { API_ROOT } from "../../../utils/constants";
import useSignIn from "react-auth-kit/hooks/useSignIn";
import { useNavigate } from "react-router-dom";
import useIsAuthenticated from "react-auth-kit/hooks/useIsAuthenticated";
import Box from "../../components/layout/Box";

/**
 * the login page for admin authentication
 * @returns the admin page
 */
const Login = () => {
  // settign app state
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const signIn = useSignIn();
  const isAuthenticated = useIsAuthenticated();
  const [loginFailed, setLoginFailed] = useState(false);
  const [errorMessage, setErrorMessage] = useState();
  const [loading, setLoading] = useState();

  // redirect to admin if already logged in
  useEffect(() => {
    if (isAuthenticated) {
      navigate("/admin");
    }
  });

  /**
   * handles the login process by reaching out to API and setting the access token
   */
  const handleLogin = async () => {
    // set loading for button
    setLoading(true);

    // http request
    let request = {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username: username, password: password }),
    };

    try {
      let response = await fetch(`${API_ROOT}/authenticate`, request);

      // if response ok set the token and navigate to admin. If not authorised, show the error message
      if (response.ok) {
        response = await response.json();
        console.log(response);
        signIn({
          auth: {
            token: response.data.accessToken,
            type: "Bearer",
          },
        });
        navigate("/admin");
      } else if (response.status === 401) {
        setErrorMessage("Invalid credentials");
        setLoginFailed(true);
      } else {
        throw new Error();
      }
    } catch (err) {
      // if unknown error, show general message
      setErrorMessage("Something went wrong!");
      setLoginFailed(true);
    } finally {
      // reset button loading
      setLoading(false);
    }
  };

  return (
    <>
      <Box>
        <div className="columns is-centered">
          <div className="column is-one-third has-text-centered">
            {loginFailed && (
              <h1 className="has-text-centered has-text-weight-bold has-text-danger">
                {errorMessage}
              </h1>
            )}
            <h1 className="has-text-centered has-text-weight-bold block">
              Admin Login
            </h1>
            <div className="field">
              <div className="control">
                <input
                  className="input queens-textfield"
                  type="text"
                  placeholder="Username"
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
            </div>

            <div className="field">
              <div className="control">
                <input
                  className="input queens-textfield"
                  type="password"
                  placeholder="Password"
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            <button
              className={`button queens-button queens-branding is-normal is-rounded block ${
                loading ? "is-loading" : ""
              }`}
              onClick={handleLogin}
              disabled={username.length == 0 || password.length == 0 || loading}
            >
              Log In
            </button>
          </div>
        </div>
      </Box>
    </>
  );
};

export default Login;
