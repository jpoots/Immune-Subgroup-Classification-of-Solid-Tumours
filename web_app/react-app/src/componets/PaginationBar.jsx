import React from "react";
import { CSVLink, CSVDownload } from "react-csv";

export function PaginationBar({ table }) {
  return (
    <>
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
              onChange={(e) => table.setPageIndex(e.target.value)}
              type="number"
            />
          </li>
        </ul>
      </nav>
    </>
  );
}
