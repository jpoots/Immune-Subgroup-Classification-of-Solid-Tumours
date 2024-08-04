const Login = () => {
  return (
    <div className="container">
      <div className="box">
        <div className="columns is-centered">
          <div className="column is-one-third has-text-centered">
            <h1 className="has-text-centered has-text-weight-bold block">
              Admin Login
            </h1>
            <div className="field">
              <div className="control">
                <input
                  className="input queens-textfield"
                  type="text"
                  placeholder="Admin ID"
                />
              </div>
            </div>

            <div className="field">
              <div className="control">
                <input
                  className="input queens-textfield"
                  type="password"
                  placeholder="Password"
                />
              </div>
            </div>

            <button className="button queens-button queens-branding is-normal is-rounded block">
              Log In
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
