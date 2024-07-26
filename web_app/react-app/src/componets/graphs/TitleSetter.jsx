const TitleSetter = ({ setTitle }) => {
  return (
    <div className="block mt-2">
      <h1 className="has-text-weight-bold">Title</h1>
      <input
        type="text"
        placeholder="Title"
        className="input queens-textfield"
        onChange={(e) => setTitle(e.target.value)}
      />
    </div>
  );
};

export default TitleSetter;
