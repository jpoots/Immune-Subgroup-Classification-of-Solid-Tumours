/**
 * wrapper to contain the children within a bulma box element
 * @param {React.ReactElement} children - the items contained within the box
 * @param {string} className - additional css classes to add
 * @returns
 */
const Box = ({ children, className }) => {
  return <div className={`box ${className}`}>{children}</div>;
};

export default Box;
