/**
 * a componet which handles the dimensions viewed and the title of a visualisation graph
 * @param {function} setDimensions
 * @param {number} dimension
 * @param {function} setTitle
 * @returns - the graph controls
 */
export function GraphControls({ setDimensions, dimension, setTitle }) {
  return (
    <>
      <div
        className="control block"
        onChange={() => setDimensions(dimension === 2 ? 3 : 2)}
      >
        <h1 className="has-text-weight-bold">Dimensions</h1>
        <label className="radio">
          <input
            type="radio"
            name="dim"
            value="2"
            checked={dimension === 2}
            className="queens-radio mr-2"
          />
          2D
        </label>

        <label className="radio">
          <input
            type="radio"
            name="dim"
            value="3"
            checked={dimension === 3}
            className="queens-radio mr-2"
          />
          3D
        </label>
      </div>
      <div className="block">
        <h1 className="has-text-weight-bold">Title</h1>
        <input
          type="text"
          placeholder="Title"
          className="input queens-textfield"
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>
    </>
  );
}
