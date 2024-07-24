import { Table } from "./Table";
import { PaginationBar } from "./PaginationBar";
import { useState, useRef, useMemo } from "react";
import NothingToDisplay from "./NothingToDisplay";

import {
  getCoreRowModel,
  useReactTable,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";
import { CSVLink } from "react-csv";

const Report = ({ results }) => {
  let samples = [];
  if (typeof results !== "undefined") samples = results["samples"];

  const [sorting, setSorting] = useState([]);
  const [download, setDownload] = useState([]);
  const [columnFilters, setColumnFilters] = useState([]);

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  const exportSamples = () => {
    let toExport = table.getFilteredRowModel().rows.map((row) => ({
      sampleID: row.original.sampleID,
      prediction: row.original.prediction,
    }));

    setDownload(toExport);
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
        accessorKey: "prediction",
        header: "Classification",
        id: "prediction",
        cell: (props) => <p>{props.getValue()}</p>,
        enableSorting: false,
        filterFn: "equalsString",
      },
      {
        accessorFn: (row) => Math.max(...row.probs).toFixed(8),
        header: "Sample ID",
        id: "prob",
        cell: (props) => <p>{props.getValue()}</p>,
        enableSorting: false,
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

  console.log(table.getState().columnFilters);

  return (
    <div className="container">
      {results ? (
        <>
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
              <div className="column is-half">
                <div className="select is-danger">
                  <select
                    name=""
                    onChange={(e) => {
                      console.log(e.target.value);
                      table
                        .getColumn("prediction")
                        .setFilterValue(e.target.value);
                    }}
                    id=""
                  >
                    <option value="">All</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                    <option value="6">6</option>
                    <option value="NC">Non-classifiable</option>
                  </select>
                </div>
              </div>
            </div>

            <Table table={table} />
          </div>
          <PaginationBar
            table={table}
            download={download}
            exportSamples={exportSamples}
          />
          <CSVLink
            data={download}
            filename="data"
            onClick={exportSamples}
            className="button is-dark"
          >
            <button>Download Report</button>
          </CSVLink>
        </>
      ) : (
        <NothingToDisplay />
      )}
    </div>
  );
};

export default Report;
