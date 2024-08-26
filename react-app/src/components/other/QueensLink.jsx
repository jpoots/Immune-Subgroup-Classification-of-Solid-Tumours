/**
 * A wrapper component to produce a Queen's styled link
 * @param {string} className - additional classes to add
 * @param {string} href - link location
 * @param {boolean} download - boolean to indicate if link is a download link
 * @param {string} target - target for the link
 * @param {function} onClick - function to perform on link click
 * @param {React.ReactElement} children - children of the link
 * @returns the Queens link
 */
const QueensLink = ({
  className,
  href,
  download,
  target,
  onClick,
  children,
}) => {
  if (!target) target = "_blank";

  return (
    <a
      href={href}
      className={`queens-branding-text ${className}`}
      target={target}
      download={download}
      onClick={onClick}
    >
      {children}
    </a>
  );
};

export default QueensLink;
