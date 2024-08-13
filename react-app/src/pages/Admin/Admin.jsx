import { useEffect, useRef, useState } from "react";
import { API_ROOT } from "../../../utils/constants";
import { openWarningModal } from "../../../utils/openWarningModal";
import ErrorModal from "../../components/errors/ErrorModal";
import useSignOut from "react-auth-kit/hooks/useSignOut";
import { useNavigate } from "react-router-dom";
import useAuthHeader from "react-auth-kit/hooks/useAuthHeader";
import { Tooltip } from "react-tooltip";
import useIsAuthenticated from "react-auth-kit/hooks/useIsAuthenticated";
import Box from "../../components/layout/Box";

/**
 * the admin page where the admin can edit the gene list, create a new admin or log out
 * @returns
 */
const Admin = () => {
  // set page state
  const [loading, setLoading] = useState();
  const [modalMessage, setModalMessage] = useState();
  const [openModal, setOpenModal] = useState();
  const [disabled, setDisabled] = useState(true);
  const [imSure, setImsure] = useState(false);
  const geneNameList = useRef();
  const signOut = useSignOut();
  const navigate = useNavigate();
  const authHeader = useAuthHeader();
  const [createAdminLoading, setCreateAdminLoading] = useState();
  const isAuthenticated = useIsAuthenticated();

  // only do this on first render
  useEffect(() => {
    const getGeneList = async () => {
      // redirect to login if session has timed out
      if (!isAuthenticated) {
        navigate("/login");
        return;
      }

      try {
        let response = await fetch(`${API_ROOT}/genelist`);

        //  if unknown error throw error to be caught
        if (!response.ok) throw new Error();
        else {
          // if all is good display the gene list
          response = await response.json();
          let gene_name_list = response.data.results;
          gene_name_list = gene_name_list.join("\n");
          geneNameList.current.value = gene_name_list;
        }
      } catch (err) {
        // if an error has occured display
        openWarningModal(
          setModalMessage,
          setOpenModal,
          "An error has occurred please try again later!"
        );
      }
    };
    // open with warning modal about danger
    openWarningModal(
      setModalMessage,
      setOpenModal,
      "WARNING: Editing the gene name list is a destructive action and should be performed with caution."
    );
    getGeneList();
  }, [authHeader, isAuthenticated, navigate]);

  /**
   * handle the updating of the gene list
   */
  const handleUpdate = async () => {
    setLoading(true);

    // redirect to login if session has timed out
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    // init error message
    let errorMessage = "Invalid input";

    try {
      // https://stackoverflow.com/questions/3871816/is-there-a-javascript-regular-expression-to-remove-all-whitespace-except-newline regex taken from here
      // clean data
      let geneList = geneNameList.current.value
        .replace(",", "")
        .replace(/[^\S\r\n]+/g, "")
        .split("\n");

      //https://stackoverflow.com/questions/281264/remove-empty-elements-from-an-array-in-javascript works because empty strings are false
      // remove any empty token
      geneList.filter((name) => name);

      // convert to set and back to remove duplicates
      geneList = new Set(geneList);
      geneList = [...geneList];

      // request to sends
      const request = {
        method: "PUT",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          Authorization: authHeader,
        },
        body: JSON.stringify({
          geneList: geneList,
        }),
      };

      // validation
      if (geneList.length == 0) throw Error();

      // if validation has passed, change error message, these structures avoid try catch hell
      errorMessage = "Something went wrong!";
      let response = await fetch(`${API_ROOT}/genelist`, request);

      // if ok, notify user, otherwise get the error and display
      if (response.ok) {
        openWarningModal(setModalMessage, setOpenModal, "Success!");
        setImsure(false);
      } else {
        response = await response.json();
        errorMessage = response.error.description;
        throw new Error();
      }
    } catch (err) {
      openWarningModal(setModalMessage, setOpenModal, errorMessage);
    } finally {
      setLoading(false);
      setDisabled(true);
    }
  };

  /**
   * shows the I'm sure button if the first submission click has been performed
   */
  const handleFirstClick = () => {
    setDisabled(true);
    setImsure(true);
  };

  /**
   * logs the admin out
   */
  const handleLogOut = () => {
    signOut();
    navigate("/login");
  };

  /**
   * reaches to api to create a new admin
   */
  const handleNewAdmin = async () => {
    setCreateAdminLoading(true);
    try {
      // request to send
      const request = {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          Authorization: authHeader,
        },
      };

      // perform request
      let response = await fetch(`${API_ROOT}/admin`, request);

      if (response.ok) {
        response = await response.json();
        // get the details and display message
        let username = response.data.username;
        let password = response.data.password;
        let message = `A new account has been created with username: ${username} and password: ${password}. Keep this safe. You will not have access to it again.`;
        openWarningModal(setModalMessage, setOpenModal, message);
      } else {
        // if request not ok, throw error to be caught
        throw new Error();
      }
    } catch (err) {
      openWarningModal(setModalMessage, setOpenModal, "Something went wrong!");
    } finally {
      // always reset buttons
      setLoading(false);
      setDisabled(true);
      setCreateAdminLoading(false);
    }
  };

  return (
    <>
      <Box>
        <div className="columns">
          <div className="column is-half">
            <h1 className="has-text-weight-bold block">
              Edit accepted genes{" "}
              <a
                className="queens-branding-text"
                data-tooltip-id="visual-tooltip"
                data-tooltip-content="Gene aliases should be added on a new line above or below the current name. Whitespace and commas will be removed. Gene names are case sensitive."
              >
                ?
              </a>
            </h1>
          </div>

          <div className="column is-half has-text-right">
            <button
              className={`button queens-branding queens-button mr-5 ${
                createAdminLoading ? "is-loading" : ""
              }`}
              onClick={handleNewAdmin}
              disabled={createAdminLoading}
            >
              Create New Admin
            </button>
            <button className="button is-dark" onClick={handleLogOut}>
              Log Out
            </button>
          </div>
        </div>

        <textarea
          className="textarea block queens-textfield"
          rows="10"
          ref={geneNameList}
          onChange={() => {
            setDisabled(false);
            setImsure(false);
          }}
        ></textarea>
        <button
          className={`button queens-branding queens-button mr-5 ${
            loading ? "is-loading" : ""
          }`}
          disabled={disabled || loading}
          onClick={handleFirstClick}
        >
          Change List
        </button>
        <button
          className={`button is-dark ${loading ? "is-loading" : ""}`}
          disabled={!imSure || loading}
          onClick={handleUpdate}
        >
          I&apos;m sure
        </button>
      </Box>

      {openModal && (
        <ErrorModal modalMessage={modalMessage} setOpenModal={setOpenModal} />
      )}
      <Tooltip id="visual-tooltip" place="right-end" className="tooltip" />
    </>
  );
};

export default Admin;
