import { useState, useMemo } from "react";
import {
  getCoreRowModel,
  useReactTable,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";
import { Table } from "./Table";

import { CSVLink } from "react-csv";
import NothingToDisplay from "../general/NothingToDisplay";
import { PaginationBar } from "./PaginationBar";

/**
 * the gene expression page where the extracted genes can be viewed
 * @param {Object} results - the results of the analysis
 * @returns - the gene expression results page
 */
const GeneExpression = ({ results }) => {
  // defining state
  const [sorting, setSorting] = useState([]);
  const [download, setDownload] = useState([]);
  const [columnFilters, setColumnFilters] = useState([]);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 5,
  });

  const samples = results["samples"];
  const geneNameList = Object.keys(samples[0]["genes"]);

  // generating columns based on the gene names
  let columns = useMemo(() => {
    let columns = [
      {
        accessorKey: "sampleID",
        header: "Sample ID",
        id: "sampleID",
        cell: (props) => <p>{props.getValue()}</p>,
      },
    ];

    let append = geneNameList.map((name) => ({
      accessorKey: `genes.${name}`,
      header: name,
      id: name,
      cell: (props) => <p>{props.getValue()}</p>,
      enableSorting: false,
    }));

    columns = columns.concat(append);

    return columns;
  }, [geneNameList]);

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
   * generates an array of objects to be used with CSV link
   */
  const handleDownload = () => {
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

  return (
    <div className="container">
      {results ? (
        <>
          <Table table={table} />
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

export default GeneExpression;
