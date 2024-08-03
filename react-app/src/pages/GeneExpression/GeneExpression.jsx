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
import { TitleAndSearch } from "../../components/tables/TitleAndSearch";

/**
 * the gene expression page where the extracted genes can be viewed
 * @returns - the gene expression results page
 */
const GeneExpression = () => {
  // defining state
  const [sorting, setSorting] = useState([]);
  const [download, setDownload] = useState([]);
  const [columnFilters, setColumnFilters] = useState([]);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 5,
  });

  const results = useContext(ResultsContext)[0];
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

  const title = "Gene Expression Report";

  return (
    <div className="container">
      <div className="box">
        <TitleAndSearch title={title} table={table} />
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
    </div>
  );
};

export default GeneExpression;
