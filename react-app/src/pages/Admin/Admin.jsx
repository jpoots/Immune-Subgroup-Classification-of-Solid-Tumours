import { useEffect, useRef, useState } from "react";
import { API_ROOT } from "../../../utils/constants";
import { openWarningModal } from "../../../utils/openWarningModal";
import ErrorModal from "../../components/errors/ErrorModal";
import useSignOut from "react-auth-kit/hooks/useSignOut";
import { useNavigate } from "react-router-dom";
import useAuthHeader from "react-auth-kit/hooks/useAuthHeader";
import { Tooltip } from "react-tooltip";
import { useAuth } from "react-auth-kit";

const Admin = () => {
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

  useEffect(() => {
    const getGeneList = async () => {
      try {
        let response = await fetch(`${API_ROOT}/genelist`, {
          headers: { Authorization: authHeader },
        });

        if (response.status == 401) {
          navigate("/login");
        } else if (!response.ok) throw new Error();
        else {
          response = await response.json();
          let gene_name_list = response.results;
          gene_name_list = gene_name_list.join("\n");
          geneNameList.current.value = gene_name_list;
        }
      } catch (err) {
        openWarningModal(
          setModalMessage,
          setOpenModal,
          "An error has occurred please try again later!"
        );
      }
    };
    openWarningModal(
      setModalMessage,
      setOpenModal,
      "WARNING: Editing the gene name list is a destructive action and should be performed with caution."
    );
    getGeneList();
  }, [authHeader, navigate]);

  const handleUpdate = async () => {
    setLoading(true);
    let errorMessage = "Invalid input";

    try {
      // https://stackoverflow.com/questions/3871816/is-there-a-javascript-regular-expression-to-remove-all-whitespace-except-newline regex taken from herer
      let geneList = geneNameList.current.value
        .replace(",", "")
        .replace(/[^\S\r\n]+/g, "")
        .split("\n");

      //https://stackoverflow.com/questions/281264/remove-empty-elements-from-an-array-in-javascript works because empty strings are false
      geneList.filter((name) => name);

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

      if (geneList.length == 0) throw Error();

      errorMessage = "Something went wrong!";
      let response = await fetch(`${API_ROOT}/genelist`, request);

      if (response.status == 401) {
        navigate("/login");
      } else if (response.ok) {
        openWarningModal(setModalMessage, setOpenModal, "Success!");
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

  const handleFirstClick = () => {
    setDisabled(true);
    setImsure(true);
  };

  const handleLogOut = () => {
    signOut();
    navigate("/login");
  };

  const handleNewAdmin = async () => {
    setCreateAdminLoading(true);
    try {
      const request = {
        method: "PUT",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          Authorization: authHeader,
        },
      };

      let response = await fetch(`${API_ROOT}/admin`, request);
      response = await response.json();

      console.log(response);
      let username = response.username;
      let password = response.password;
      let message = `A new account has been created with username ${username} and password ${password}\n Keep this safe. You will not have access to it again.`;
      openWarningModal(setModalMessage, setOpenModal, message);
    } catch (err) {
      openWarningModal(setModalMessage, setOpenModal, "Something went wrong!");
    } finally {
      setLoading(false);
      setDisabled(true);
      setCreateAdminLoading(false);
    }
  };

  return (
    <>
      <div className="container">
        <div className="box">
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
        </div>

        {openModal && (
          <ErrorModal modalMessage={modalMessage} setOpenModal={setOpenModal} />
        )}
      </div>
      <Tooltip id="visual-tooltip" place="right-end" className="tooltip" />
    </>
  );
};

export default Admin;
