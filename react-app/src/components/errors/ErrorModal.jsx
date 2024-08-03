/**
 * an error modal that can be popped up with an error message and closed
 * @param {string} modalMessage - the pages model message variable
 * @param {function} setOpenModal - the function to set the
 * @returns an error modal with a message
 */
const ErrorModal = ({ modalMessage, setOpenModal }) => {
  return (
    <div className="modal is-active">
      <div className="modal-background"></div>
      <div className="modal-content">
        <div className="box has-text-centered"> {modalMessage}</div>
      </div>
      <button
        className="modal-close is-large"
        onClick={() => setOpenModal(false)}
      ></button>
    </div>
  );
};

export default ErrorModal;
