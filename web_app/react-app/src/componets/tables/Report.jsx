import { SearchByID } from "./SearchByID";
import { Table } from "./Table";
import { PaginationBar } from "./PaginationBar";
import { useState, useMemo } from "react";
import NothingToDisplay from "../errors/NothingToDisplay";
import {
  getCoreRowModel,
  useReactTable,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";
import { CSVLink } from "react-csv";

/**
 * the report page showing the prediction table with confidence
 * @param {Object} results - the results of the analysis
 * @returns - a report on the predicitons
 */
const Report = ({ results }) => {
  let samples = results["samples"];
  //if (typeof results !== "undefined") samples = results["samples"]; used as extra validation

  // setting state for the component
  const [sorting, setSorting] = useState([]);
  const [download, setDownload] = useState([]);
  const [columnFilters, setColumnFilters] = useState([]);

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  // memo to build columns. Iterating over 440. Only do once
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
        header: "Class label",
        id: "prediction",
        cell: (props) => <p>{props.getValue()}</p>,
        enableSorting: false,
        filterFn: "equalsString",
      },
      {
        accessorFn: (row) => Math.max(...row.probs).toFixed(8),
        header: "Probability",
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

  /**
   * generate objects of the report to be downloaded
   */
  const handleDownload = () => {
    let toExport = table.getFilteredRowModel().rows.map((row) => ({
      sampleID: row.original.sampleID,
      prediction: row.original.prediction,
    }));

    setDownload(toExport);
  };

  return (
    <div className="container">
      {results ? (
        <>
          <div className="box">
            <h1 className="block has-text-weight-bold">Prediction Report</h1>

            <div className="columns">
              <div className="column is-one-quarter">
                <SearchByID table={table} />
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
          <PaginationBar table={table} />
          <CSVLink
            data={download}
            filename="data"
            onClick={handleDownload}
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
