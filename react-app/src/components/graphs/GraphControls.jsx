import { Tooltip } from "react-tooltip";
import { renderToStaticMarkup } from "react-dom/server";
import GraphTitleSetter from "./GraphTitleSetter";
import Title from "../other/Title";
import QueensLink from "../other/QueensLink";

/**
 * a componet which handles the dimensions viewed and the title of a visualisation graph
 * @param {function} setDimensions - the setter function for the number of dimensions on the current graph
 * @param {number} dimension - the dimensions of the grapg
 * @param {function} setTitle - settter function for the graph title state
 * @param {string} title - the graph title
 * @param {string} pageTitle - settter function for the graph title state
 * @param {string} tooltipMessage - the message to display beside the full name in the tool tip
 * @param {string} toooltipLink - the page that clicking the full name links to
 * @param {string} fullName - the full name of the graph being shown
 * @returns - the graph controls
 */

const GraphControls = ({
  setDimensions,
  dimension,
  setTitle,
  title,
  pageTitle,
  tooltipMessage,
  tooltipLink,
  fullName,
}) => {
  // converting tooltip to static html
  const tooltipHTML = () =>
    renderToStaticMarkup(
      <div>
        <QueensLink href={tooltipLink}> {fullName}</QueensLink>
        {tooltipMessage}
      </div>
    );

  return (
    <>
      <Title classes="mt-4">
        {pageTitle}{" "}
        <a
          className="queens-branding-text"
          data-tooltip-html={`${tooltipHTML()}`}
          data-tooltip-id="visual-tooltip"
        >
          ?
        </a>
      </Title>
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
            defaultChecked={dimension == 2}
            className="queens-radio mr-2"
          />
          2D
        </label>

        <label className="radio">
          <input
            type="radio"
            name="dim"
            value="3"
            defaultChecked={dimension == 3}
            className="queens-radio mr-2"
          />
          3D
        </label>
      </div>
      <GraphTitleSetter setTitle={setTitle} title={title} />
      <Tooltip
        id="visual-tooltip"
        place="right-end"
        className="tooltip"
        clickable={true}
      />
    </>
  );
};

export default GraphControls;
