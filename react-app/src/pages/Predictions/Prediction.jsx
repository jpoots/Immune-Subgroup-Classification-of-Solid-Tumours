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
import Box from "../../components/layout/Box";
import Title from "../../components/other/Title";
import SearchAndFilter from "../../components/tables/SearchAndFilter";

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
    <>
      {results ? (
        <>
          <Box>
            <Title>Prediction Report</Title>
            <SearchAndFilter table={table}></SearchAndFilter>
            <Table table={table} />
          </Box>
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
    </>
  );
};

export default Prediction;
