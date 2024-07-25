import { useState, useMemo } from "react";
import {
  getCoreRowModel,
  useReactTable,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";

import { Table } from "../tables/Table";

import { CSVLink } from "react-csv";
import NothingToDisplay from "../general/NothingToDisplay";
import { PaginationBar } from "./PaginationBar";

/**
 * generates the probability page showing the probabiltiy of all subgroups
 * @param {Object} results - the results of the analysis
 * @returns a probabiltiy page
 */
const Proability = ({ results }) => {
  // could add extra layer of protection here
  let samples = results["samples"];

  // state for the componet
  const [sorting, setSorting] = useState([]);
  const [download, setDownload] = useState([]);
  const [columnFilters, setColumnFilters] = useState([]);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  /**
   * generates a list of objects to be downloaded by CSV link
   */
  const handleDownload = () => {
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

  // generates a list of columns
  const columns = useMemo(
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
      {results ? (
        <>
          <div className="box">
            {" "}
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
            <Table table={table} />
          </div>
          <PaginationBar
            table={table}
            download={download}
            exportSamples={handleDownload}
          />
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

export default Proability;
