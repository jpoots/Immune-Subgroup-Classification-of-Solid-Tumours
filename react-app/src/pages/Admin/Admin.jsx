import React, { useEffect, useState } from "react";
import { API_ROOT } from "../../../utils/constants";

const Admin = () => {
  const [geneList, setGeneList] = useState();

  useEffect(() => {
    const getGeneList = async () => {
      let result = await fetch(`${API_ROOT}/admin/genelist`);
      result = await result.json();
      setGeneList(result);
    };
    getGeneList();
  }, []);

  const handleUpdate = async () => {
    const request = {
      method: "PUT",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        newContent: geneList,
      }),
    };

    let result = await fetch(`${API_ROOT}/admin/genelist`, request);
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
            setGeneList(e.target.value);
          }}
        ></textarea>
        <button
          className="button queens-branding queens-button"
          onClick={handleUpdate}
        >
          Change List
        </button>
      </div>
    </div>
  );
};

export default Admin;
