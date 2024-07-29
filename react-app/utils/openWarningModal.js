  /**
   * opens a warning modal with the given message
   * @param {string} message - the message to display in the warning modal
   * @param {function} setModalMessage - the function to set the mdoal message
   * @param {function} setOpenModal - the function to set the open modal boolean
   */
  const openWarningModal = (setModalMessage, setOpenModal, message) => {
    setModalMessage(message);
    setOpenModal(true);
};

export {openWarningModal}