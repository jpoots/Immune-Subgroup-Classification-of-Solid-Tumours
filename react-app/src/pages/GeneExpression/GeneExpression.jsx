import { useState, useMemo, useContext } from "react";
import {
  getCoreRowModel,
  useReactTable,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";
import { Table } from "../../components/tables/Table";
import { CSVLink } from "react-csv";
import { PaginationBar } from "../../components/tables/PaginationBar";
import { ResultsContext } from "../../context/ResultsContext";
import Box from "../../components/layout/Box";
import SearchAndFilter from "../../components/tables/SearchAndFilter";
import Title from "../../components/other/Title";

/**
 * the gene expression page where the extracted genes can be viewed
 * @returns - the gene expression results page
 */
const GeneExpression = () => {
  // defining state for the page
  const [download, setDownload] = useState([]);
  // table state
  const [sorting, setSorting] = useState([]);
  const [columnFilters, setColumnFilters] = useState([]);
  const [columnVisibility, setColumnVisibility] = useState({
    prediction: false,
  });
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 5,
  });

  // pull context
  const results = useContext(ResultsContext)[0];

  // pull out samples and gene list
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

      {
        accessorKey: "prediction",
        header: "Subgroup",
        id: "prediction",
        cell: (props) => <p>{props.getValue()}</p>,
        enableSorting: false,
        enableColumnVisibility: false,
        filterFn: "equalsString",
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

  // defining react table
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

  /**
   * generates an array of objects to be used with CSV link
   */
  const handleDownload = () => {
    let toExport = table.getFilteredRowModel().rows.map((row) => {
      // for each sapmple...
      let sample = row.original;

      // add sample id and gene for each gene
      let sampleDict = { sampleID: sample.sampleID };
      Object.keys(sample["genes"]).forEach(
        (gene) => (sampleDict[gene] = sample["genes"][gene])
      );
      return sampleDict;
    });

    // set download state
    setDownload(toExport);
  };

  return (
    <>
      <Box>
        <Title>Gene Expression Report</Title>
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
  );
};

export default GeneExpression;
