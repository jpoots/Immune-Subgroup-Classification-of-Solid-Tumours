import React, { useState, useRef, useMemo } from "react";
import {
  getCoreRowModel,
  useReactTable,
  flexRender,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";

import sortArrows from "/sort-solid.svg";
import { CSVLink, CSVDownload } from "react-csv";

const Proability = ({ results }) => {
  let samples = results ? results["samples"] : [];

  const [query, setQuery] = useState("");
  const [page, setPage] = useState(0);
  const [sorting, setSorting] = useState([]);
  const [reverse, setReverse] = useState(false);
  const geneNameList = useRef();
  const allSamples = useRef();
  const [download, setDownload] = useState([]);
  const [columnFilters, setColumnFilters] = useState([]);

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  const exportSamples = () => {
    setDownload(
      table.getFilteredRowModel().rows.map((row) => ({
        sampleID: row.original.sampleID,
        prob1: row.original.probs[0],
        prob2: row.original.probs[1],
        prob3: row.original.probs[2],
        prob4: row.original.probs[3],
        prob5: row.original.probs[4],
        prob6: row.original.probs[5],
      }))
    );
  };

  let columns = useMemo(
    () => [
      {
        accessorKey: "sampleID",
        header: "Sample ID",
        id: "sampleID",
        cell: (props) => <p>{props.getValue()}</p>,
      },
      {
        accessorFn: (row) => row.probs[0].toFixed(5),
        header: "1",
        id: "prob1",
        cell: (props) => <p>{props.getValue()}</p>,
      },
      {
        accessorFn: (row) => row.probs[1].toFixed(5),
        header: "2",
        id: "prob2",
        cell: (props) => <p>{props.getValue()}</p>,
      },
      {
        accessorFn: (row) => row.probs[2].toFixed(5),
        header: "3",
        id: "prob3",
        cell: (props) => <p>{props.getValue()}</p>,
      },
      {
        accessorFn: (row) => row.probs[3].toFixed(5),
        header: "4",
        id: "prob4",
        cell: (props) => <p>{props.getValue()}</p>,
      },
      {
        accessorFn: (row) => row.probs[4].toFixed(5),
        header: "5",
        id: "prob5",
        cell: (props) => <p>{props.getValue()}</p>,
      },
      {
        accessorFn: (row) => row.probs[5].toFixed(5),
        header: "6",
        id: "prob6",
        cell: (props) => <p>{props.getValue()}</p>,
      },
    ],
    []
  );

  const table = useReactTable({
    data: samples,
    columns,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: setPagination,
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: {
      columnFilters,
      pagination,
      sorting,
    },
  });

  return (
    <div className="container">
      <div className="box">
        <div className="columns">
          <div className="column is-one-quarter">
            <input
              type="text"
              className="input queens-textfield"
              onChange={(e) => {
                let column = table.getColumn("sampleID");
                column.setFilterValue(e.target.value.toUpperCase());
              }}
              placeholder="Search by sample ID"
            />
          </div>
        </div>
        <div className="columns"></div>
        <div className="table-container">
          {
            <table className="table is-bordered">
              <thead>
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => {
                      return (
                        <th key={header.id}>
                          {header.column.columnDef.header}{" "}
                          {header.column.getCanSort() && (
                            <button
                              className="button is-small sort-button"
                              onClick={header.column.getToggleSortingHandler()}
                            >
                              <img src={sortArrows} width={10} />
                            </button>
                          )}
                        </th>
                      );
                    })}
                  </tr>
                ))}
              </thead>

              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id}>
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          }
        </div>
      </div>
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
            />
          </li>
        </ul>
      </nav>

      <CSVLink
        data={download}
        filename="data"
        onClick={exportSamples}
        className="button is-dark"
      >
        <button>Download Report</button>
      </CSVLink>
    </div>
  );
};

export default Proability;
