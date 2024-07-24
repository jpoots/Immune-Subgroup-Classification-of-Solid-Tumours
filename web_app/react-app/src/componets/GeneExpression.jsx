import { useState, useRef, useMemo } from "react";
import {
  getCoreRowModel,
  useReactTable,
  flexRender,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";
import { Table } from "./Table";

import { CSVLink } from "react-csv";
import NothingToDisplay from "./NothingToDisplay";
import { PaginationBar } from "./PaginationBar";

const GeneExpression = ({ results }) => {
  let samples = [];
  const [sorting, setSorting] = useState([]);
  const geneNameList = useRef();
  const allSamples = useRef();
  const [download, setDownload] = useState([]);

  let table = [];

  if (typeof results !== "undefined") {
    allSamples.current = results["samples"];
    geneNameList.current = Object.keys(allSamples.current[0]["genes"]);

    const currentAllSamples = allSamples.current;
    const [columnFilters, setColumnFilters] = useState([]);

    samples = allSamples.current;

    let columns = useMemo(() => {
      let columns = [
        {
          accessorKey: "sampleID",
          header: "Sample ID",
          id: "sampleID",
          cell: (props) => <p>{props.getValue()}</p>,
        },
      ];

      let append = geneNameList.current.map((name) => ({
        accessorKey: `genes.${name}`,
        header: name,
        id: name,
        cell: (props) => <p>{props.getValue()}</p>,
        enableSorting: false,
      }));

      columns = columns.concat(append);

      return columns;
    }, []);

    const [pagination, setPagination] = useState({
      pageIndex: 0,
      pageSize: 5,
    });

    table = useReactTable({
      data: currentAllSamples,
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
  }

  const exportSamples = () => {
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
        <div className="box">
          <div className="columns">
            <div className="column is-half">
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

          <PaginationBar
            table={table}
            download={download}
            exportSamples={exportSamples}
          />
          <CSVLink
            data={download}
            filename="data"
            onClick={exportSamples}
            className="button is-dark"
          >
            <button>Download Report</button>
          </CSVLink>
        </div>
      ) : (
        <NothingToDisplay />
      )}
    </div>
  );
};

export default GeneExpression;
