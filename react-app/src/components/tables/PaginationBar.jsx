import { CSVLink } from "react-csv";

/**
 * a pagination bar componet for a results table
 * @param {TableInstance} table - the table to be paginated
 * @returns - the pagination bar for the table
 */
export function PaginationBar({ table, download, handleDownload }) {
  return (
    <nav className="pagination is-right">
      <button
        onClick={() => table.previousPage()}
        className="pagination-previous queens-branding queens-button"
        disabled={!table.getCanPreviousPage()}
      >
        Previous
      </button>

      <button
        onClick={() => table.nextPage()}
        className="pagination-next queens-branding queens-button"
        disabled={!table.getCanNextPage()}
      >
        Next
      </button>
      <ul className="pagination-list">
        <li className="mr-5">
          <span>Page </span>{" "}
          <span className="has-text-weight-bold	">
            {table.getState().pagination.pageIndex + 1}
          </span>{" "}
          <span>of</span>{" "}
          <span className="has-text-weight-bold	">{table.getPageCount()}</span>{" "}
        </li>

        <li>
          <span>Go to page:</span>{" "}
          <input
            onChange={(e) => table.setPageIndex(e.target.value - 1)}
            type="number"
            min={1}
            max={table.getPageCount()}
            value={table.getState().pagination.pageIndex + 1}
            className="queens-textfield mr-5"
          />
        </li>

        <li>
          <CSVLink
            data={download}
            filename="data"
            onClick={handleDownload}
            className="ml-5 button is-dark"
          >
            <button>Download Report</button>
          </CSVLink>
        </li>
      </ul>
    </nav>
  );
}
