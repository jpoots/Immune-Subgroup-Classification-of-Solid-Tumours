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

const PAGE_SIZE = 5;

const GeneExpression = ({ results }) => {
  let samples = [];
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(0);
  const [sorting, setSorting] = useState([]);
  const [reverse, setReverse] = useState(false);
  const geneNameList = useRef();
  const allSamples = useRef();
  const [download, setDownload] = useState([]);

  if (typeof results !== "undefined") {
    allSamples.current = results["samples"];
    geneNameList.current = Object.keys(allSamples.current[0]["genes"]);

    samples = allSamples.current;
  }

  const currentAllSamples = allSamples.current;
  const [columnFilters, setColumnFilters] = useState([]);

  let columns = useMemo(() => {
    let columns = [
      {
        accessorKey: "sampleID",
        header: "Sample ID",
        id: "sampleID",
        cell: (props) => <p>{props.getValue()}</p>,
      },
    ];

    let append = geneNameList.current.map((name) => ({
      accessorKey: `genes.${name}`,
      header: name,
      id: name,
      cell: (props) => <p>{props.getValue()}</p>,
      enableSorting: false,
    }));

    columns = columns.concat(append);

    return columns;
  }, []);

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  const table = useReactTable({
    data: currentAllSamples,
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

  const exportSamples = () => {
    let toExport = table.getFilteredRowModel().rows.map((row) => {
      let sample = row.original;
      let sampleDict = { sampleID: sample.sampleID };

      Object.keys(sample["genes"]).forEach(
        (gene) => (sampleDict[gene] = sample["genes"][gene])
      );
      return sampleDict;
    });

    setDownload(toExport);
  };

  const tableComponent = (samples) => {
    return (
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
    );
  };

  return (
    <div className="container">
      <div className="box">
        <div className="columns">
          <div className="column is-half">
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

        {samples.length > 0 ? (
          [
            tableComponent(samples),
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
                <li>
                  <span>Go to page:</span>{" "}
                  <input
                    onChange={(e) => table.setPageIndex(e.target.value)}
                    type="number"
                  />
                </li>
              </ul>
            </nav>,
            <CSVLink
              data={download}
              filename="data"
              onClick={exportSamples}
              className="button is-dark"
            >
              <button>Download Report</button>
            </CSVLink>,
          ]
        ) : (
          <h1>Nothing to display</h1>
        )}
      </div>
    </div>
  );
};

export default GeneExpression;
