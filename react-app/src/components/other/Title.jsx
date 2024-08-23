/**
 * A wrapper for elemetns to format them as a generic title
 * @param {string} classes - additional css classess to add
 * @param {React.ReactElement} children - the children of the title
 * @returns - the children of the element formatted as a title
 */
const Title = ({ classes, children }) => {
  return (
    <h1 className={`block has-text-weight-bold ${classes}`}>{children}</h1>
  );
};

export default Title;
