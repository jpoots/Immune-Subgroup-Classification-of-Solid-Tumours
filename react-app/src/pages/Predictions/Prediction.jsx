import { SearchByID } from "../../components/tables/SearchByID";
import { Table } from "../../components/tables/Table";
import { PaginationBar } from "../../components/tables/PaginationBar";
import { useState, useMemo, useContext } from "react";
import NothingToDisplay from "../NothingToDisplay/NothingToDisplay";
import {
  getCoreRowModel,
  useReactTable,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";
import { CSVLink } from "react-csv";
import { ResultsContext } from "../../context/ResultsContext";

/**
 * the report page showing the prediction table with confidence
 * @returns - a report on the predicitons
 */
const Prediction = () => {
  // setting state for the component
  const [sorting, setSorting] = useState([]);
  const [download, setDownload] = useState([]);
  const [columnFilters, setColumnFilters] = useState([]);
  const results = useContext(ResultsContext)[0];
  const samples = results["samples"];

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  // memo to build columns. Iterating over 440. Only do once. Table building helped by documentation and
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
        header: "Subgroup",
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
      classLabel: row.original.prediction,
      maxProbability: Math.max(...row.original.probs),
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
                      table
                        .getColumn("prediction")
                        .setFilterValue(e.target.value);
                    }}
                    defaultValue={""}
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

export default Prediction;
