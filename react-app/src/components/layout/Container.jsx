/**
 * a container element to encapsualte the whole app to avoid repetition and ease change
 * @param {React.ReactElement} children - the child components to render
 * @returns - a properly containerised page with the children contained
 */
const Container = ({ children }) => {
  return <div className="container">{children}</div>;
};

export default Container;
