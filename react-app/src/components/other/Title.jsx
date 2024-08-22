const Title = ({ classes, children }) => {
  return (
    <h1 className={`block has-text-weight-bold ${classes}`}>{children}</h1>
  );
};

export default Title;
