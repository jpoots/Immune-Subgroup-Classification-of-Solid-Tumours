import { useState, useMemo, useContext } from "react";
import {
  getCoreRowModel,
  useReactTable,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";

import { CSVLink } from "react-csv";
import NothingToDisplay from "../NothingToDisplay/NothingToDisplay";
import { PaginationBar } from "../../components/tables/PaginationBar";
import { ResultsContext } from "../../context/ResultsContext";
import Box from "../../components/layout/Box";
import { TableWithBoldMax } from "./TableWithBoldMax";
import SearchAndFilter from "../../components/tables/SearchAndFilter";
import Title from "../../components/other/Title";

/**
 * generates the probability page showing the probabiltiy of all subgroups
 * @returns a probabiltiy page
 */
const Probability = () => {
  // grab results context
  const results = useContext(ResultsContext)[0];

  const samples = results["samples"];

  // state for the componet
  const [sorting, setSorting] = useState([]);
  const [download, setDownload] = useState([]);

  // graph state
  const [columnFilters, setColumnFilters] = useState([]);
  // prediction hidden by default, only used for filtering
  const [columnVisibility, setColumnVisibility] = useState({
    prediction: false,
  });
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

  // generates a list of columns helped by https://www.youtube.com/watch?v=CjqG277Hmgg&pp=ygUPdGFuc3RhY2sgdGFibGVz
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
      {
        accessorKey: "prediction",
        header: "Subgroup",
        id: "prediction",
        cell: (props) => <p>{props.getValue()}</p>,
        enableSorting: false,
        enableColumnVisibility: false,
        filterFn: "equalsString",
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
    onColumnVisibilityChange: setColumnVisibility,
    state: {
      columnFilters,
      pagination,
      sorting,
      columnVisibility,
    },
  });

  return (
    <>
      {results ? (
        <>
          <Box>
            <Title> Prediction Probability by Subgroup</Title>
            <SearchAndFilter table={table} />
            <TableWithBoldMax table={table} accessor="probs" />
          </Box>
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
    </>
  );
};

export default Probability;
