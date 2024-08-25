import {
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useContext, useMemo, useState } from "react";
import { ResultsContext } from "../../context/ResultsContext";
import { PaginationBar } from "../../components/tables/PaginationBar";
import { Table } from "../../components/tables/Table";
import SearchAndFilter from "../../components/tables/SearchAndFilter";
import Title from "../../components/other/Title";
import Box from "../../components/layout/Box";

const PredictionReport = () => {
  // setting state for the component
  const [sorting, setSorting] = useState([]);
  const [download, setDownload] = useState([]);
  const results = useContext(ResultsContext)[0];
  const samples = results["samples"];

  // table state
  const [columnFilters, setColumnFilters] = useState([]);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
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

  // memo to build columns. Iterating over 440. Only do once. Table building helped by documentation and https://www.youtube.com/watch?v=CjqG277Hmgg
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

  // set up table
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
    <>
      <Box>
        <Title>Prediction Report</Title>
        <SearchAndFilter table={table}></SearchAndFilter>
        <Table table={table} />
      </Box>
      <PaginationBar
        table={table}
        download={download}
        handleDownload={handleDownload}
      />
    </>
  );
};

export default PredictionReport;
