import { Tooltip } from "react-tooltip";
import { renderToStaticMarkup } from "react-dom/server";
import TitleSetter from "./TitleSetter";

/**
 * a componet which handles the dimensions viewed and the title of a visualisation graph
 * @param {function} setDimensions
 * @param {number} dimension
 * @param {function} setTitle
 * @returns - the graph controls
 */

export function GraphControls({
  setDimensions,
  dimension,
  setTitle,
  pageTitle,
  tooltipMessage,
  tooltipLink,
  fullName,
}) {
  const tooltipHTML = () =>
    renderToStaticMarkup(
      <div>
        <a className="queens-branding-text" href={tooltipLink} target="_blank">
          {fullName}
        </a>
        {tooltipMessage}
      </div>
    );

  return (
    <>
      <h1 className="has-text-weight-bold block mt-4">
        <a
          className="queens-branding-text"
          data-tooltip-html={`${tooltipHTML()}`}
          data-tooltip-id="visual-tooltip"
        >
          ?
        </a>
      </h1>
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
            defaultChecked={dimension}
            className="queens-radio mr-2"
          />
          2D
        </label>

        <label className="radio">
          <input
            type="radio"
            name="dim"
            value="3"
            className="queens-radio mr-2"
          />
          3D
        </label>
      </div>
      <TitleSetter setTitle={setTitle} />
      <Tooltip
        id="visual-tooltip"
        place="right-end"
        className="tooltip"
        clickable={true}
      />
    </>
  );
}
