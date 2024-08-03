import { useEffect, useState } from "react";
import { API_ROOT } from "../../../utils/constants";
import { openWarningModal } from "../../../utils/openWarningModal";
import ErrorModal from "../../components/errors/ErrorModal";

const Admin = () => {
  const [geneList, setGeneList] = useState();
  const [loading, setLoading] = useState();
  const [modalMessage, setModalMessage] = useState();
  const [openModal, setOpenModal] = useState();
  const [disabled, setDisabled] = useState(true);

  useEffect(() => {
    const getGeneList = async () => {
      let response = await fetch(`${API_ROOT}/admin/genelist`);
      response = await response.json();
      let gene_name_list = response.results;
      gene_name_list = gene_name_list.join(",");
      setGeneList(gene_name_list);
    };
    getGeneList();
  }, []);

  const handleUpdate = async () => {
    setLoading(true);
    const request = {
      method: "PUT",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        geneList: geneList,
      }),
    };

    let response = await fetch(`${API_ROOT}/admin/genelist`, request);

    if (response.ok) {
      openWarningModal(setModalMessage, setOpenModal, "Success!");
    } else {
      response = await response.json();
      let errorMessage = response.error.description;
      setModalMessage(setModalMessage, setOpenModal, errorMessage);
    }

    setLoading(false);
    setDisabled(true);
  };

  return (
    <div className="container">
      <div className="box">
        <h1 className="has-text-weight-bold block">Edit accepted genes</h1>
        <textarea
          className="textarea block queens-textfield"
          rows="10"
          value={geneList}
          onChange={(e) => {
            setDisabled(false);
            setGeneList(e.target.value);
          }}
        ></textarea>
        <button
          className={`button queens-branding queens-button ${
            loading ? "is-loading" : ""
          }`}
          disabled={disabled || loading}
          onClick={handleUpdate}
        >
          Change List
        </button>
      </div>

      {openModal && (
        <ErrorModal modalMessage={modalMessage} setOpenModal={setOpenModal} />
      )}
    </div>
  );
};

export default Admin;
