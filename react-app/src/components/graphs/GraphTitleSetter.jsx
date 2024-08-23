/**
 * a box for altering the title on a page
 * @param {function} setTitle - the setter function for the graph title state
 * @param {function} title - the title state
 * @returns the graph title setter input box
 */
const GraphTitleSetter = ({ setTitle, title }) => {
  return (
    <div className="block mt-2">
      <h1 className="has-text-weight-bold">Title</h1>
      <input
        type="text"
        placeholder="Title"
        value={title}
        className="input queens-textfield"
        onChange={(e) => setTitle(e.target.value)}
      />
    </div>
  );
};

export default GraphTitleSetter;
