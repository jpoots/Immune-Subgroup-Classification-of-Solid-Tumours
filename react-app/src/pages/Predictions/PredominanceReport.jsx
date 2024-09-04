import {
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useContext, useMemo, useState } from "react";
import { ResultsContext } from "../../context/ResultsContext";
import { Table } from "../../components/tables/Table";
import Box from "../../components/layout/Box";
import { PaginationBar } from "../../components/tables/PaginationBar";
import Title from "../../components/other/Title";
import SearchByID from "../../components/tables/SearchByID";

/**
 * the entire report on predominant classification
 * @returns a component containing the predominant report
 */
const PredominanceReport = () => {
  // setting state for the component
  const [sorting, setSorting] = useState([]);
  const [download, setDownload] = useState([]);
  const results = useContext(ResultsContext)[0];

  // table state
  const [columnFilters, setColumnFilters] = useState([]);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  /**
   * get the predominant samples
   */
  const predomSamples = useMemo(
    () => results.samples.filter((sample) => sample.prediction == 7),
    [results]
  );

  /**
   * generate objects of the report to be downloaded
   */
  const handleDownload = () => {
    let toExport = table.getFilteredRowModel().rows.map((row) => ({
      sampleID: row.original.sampleID,
      subgroup1: row.original.predomPrediction[0],
      subgroup2: row.original.predomPrediction[1],
      prob1: row.original.predomProbs[0],
      prob2: row.original.predomProbs[1],
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
        accessorFn: (row) => row.predomPrediction[0],
        header: "Subgroup 1",
        id: "prediction1",
        cell: (props) => <p>{props.getValue()}</p>,
        enableSorting: false,
      },
      {
        accessorFn: (row) => row.predomPrediction[1],
        header: "Subgroup 2",
        id: "prediction2",
        cell: (props) => <p>{props.getValue()}</p>,
        enableSorting: false,
      },
      {
        accessorFn: (row) => row.predomProbs[0].toFixed(8),
        header: "Probability 1",
        id: "prob1",
        cell: (props) => <p>{props.getValue()}</p>,
        enableSorting: false,
      },
      {
        accessorFn: (row) => row.predomProbs[1].toFixed(8),
        header: "Probability 2",
        id: "prob2",
        cell: (props) => <p>{props.getValue()}</p>,
        enableSorting: false,
      },
    ],
    []
  );

  // set up table
  const table = useReactTable({
    data: predomSamples,
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
    predomSamples.length > 0 && (
      <>
        <Box className="block">
          <Title>Predominance Report</Title>

          <div className="columns">
            <div className="column is-one-quarter">
              <SearchByID table={table} />
            </div>
          </div>

          <Table table={table} />
        </Box>
        <PaginationBar
          table={table}
          download={download}
          handleDownload={handleDownload}
        />
      </>
    )
  );
};

export default PredominanceReport;
