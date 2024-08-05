import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "react-tooltip/dist/react-tooltip.css";
import AuthProvider from "react-auth-kit/AuthProvider";
import createStore from "react-auth-kit/createStore";

// https://authkit.arkadip.dev/getting_started/integration/react-app/#usage
const store = createStore({
  authName: "_auth",
  authType: "cookie",
  cookieDomain: window.location.hostname,
  cookieSecure: window.location.protocol === "https:",
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider store={store}>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
