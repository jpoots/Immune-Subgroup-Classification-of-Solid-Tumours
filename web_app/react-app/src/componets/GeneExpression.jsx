import React, { useState, useRef } from "react";
import {
  getCoreRowModel,
  useReactTable,
  flexRender,
  getFilteredRowModel,
} from "@tanstack/react-table";

import sortArrows from "/sort-solid.svg";
import { CSVLink, CSVDownload } from "react-csv";

const PAGE_SIZE = 5;

const GeneExpression = ({ results }) => {
  let samples = [];
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(0);
  const [reverse, setReverse] = useState(false);
  const geneNameList = useRef();
  const allSamples = useRef();
  const [download, setDownload] = useState([]);

  if (typeof results !== "undefined") {
    allSamples.current = results["samples"];
    geneNameList.current = Object.keys(allSamples.current[0]["genes"]);

    samples = allSamples.current.filter((sample) =>
      sample["sampleID"].toUpperCase().includes(query)
    );

    if (reverse) {
      samples.sort((a, b) => a.sampleID.localeCompare(b.sampleID));
    } else {
      samples.sort((b, a) => a.sampleID.localeCompare(b.sampleID));
    }
  }

  //const currentAllSamples = allSamples.current;
  const [columnFilters, setColumnFilters] = useState([]);

  let numPages = Math.ceil(samples.length / PAGE_SIZE);
  let firstOnPage = page * PAGE_SIZE;
  let lastOnPage = page * PAGE_SIZE + PAGE_SIZE;
  let data = [];

  if (lastOnPage > samples.length) lastOnPage = samples.length;

  samples = samples.slice(firstOnPage, lastOnPage);

  console.log(page);

  const handlePrev = () => {
    if (page > 0) setPage((p) => p - 1);
  };

  const handleNext = () => {
    if (page < numPages + 1) setPage((p) => p + 1);
  };

  const handlePageLink = (e) => {
    setPage(parseInt(e.target.text) - 1);
  };

  const exportSamples = () => {
    let toExport = allSamples.current.map((sample) => {
      let sampleDict = { sampleID: sample.sampleID };

      Object.keys(sample["genes"]).forEach(
        (gene) => (sampleDict[gene] = sample["genes"][gene])
      );
      return sampleDict;
    });

    setDownload(toExport);
  };

  /*
  experimenting with tan tables. Actually more efficient to handle manually
  const handleSearch = (e) => {
    setColumnFilters((c) => {
      return c
        .filter((filter) => filter.id != "sampleID")
        .concat({
          id: "sampleID",
          value: e.target.value,
        });
    });
  };

  let columns = [
    {
      accessorKey: "sampleID",
      header: "Sample ID",
      id: "sampleID",
      cell: (props) => <p>{props.getValue()}</p>,
    },
  ];

  columns = columns.concat(
    geneNameList.current.map((name) => ({
      accessorKey: `genes.${name}`,
      header: name,
      id: name,
      cell: (props) => <p>{props.getValue()}</p>,
    }))
  );


  const table = useReactTable({
    data: currentAllSamples,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      columnFilters,
    },
  });
  */

  const tableComponent = (samples) => {
    return (
      <div className="table-container">
        {/*
        <table className="table is-bordered">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id}>{header.column.columnDef.header}</th>
                ))}
              </tr>
            ))}
          </thead>

          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        */}
        <table className="table is-bordered">
          <tbody>
            <tr>
              <th>
                <span>Sample ID</span>{" "}
                <span>
                  <button
                    className="button is-small sort-button"
                    onClick={() => setReverse((s) => !s)}
                  >
                    <img src={sortArrows} width={10} />
                  </button>
                </span>
              </th>
              {geneNameList.current.map((geneName) => (
                <th key={geneName}>{geneName}</th>
              ))}
            </tr>
            {samples.map((sample) => (
              <tr key={sample.sampleID}>
                <th>{sample.sampleID}</th>
                {Object.keys(sample.genes).map((geneName) => (
                  <td key={`${sample.sampleID}_${geneName}`}>
                    {sample.genes[geneName].toFixed(2)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="container">
      <div className="box">
        <div className="columns">
          <div className="column is-half">
            <input
              type="text"
              className="input queens-textfield"
              onChange={(e) => {
                setQuery(e.target.value.toUpperCase());
                setPage(0);
              }}
              placeholder="Search by sample ID"
            />
          </div>
        </div>

        {samples.length > 0 ? (
          tableComponent(samples)
        ) : (
          <h1>Nothing to display</h1>
        )}
      </div>
      <nav className="pagination is-centered">
        <button
          onClick={handlePrev}
          className="pagination-previous queens-branding queens-button"
          disabled={page === 0}
        >
          Previous
        </button>

        <button
          onClick={handleNext}
          className="pagination-next queens-branding queens-button"
          disabled={page + 1 === numPages}
        >
          Next
        </button>

        <ul className="pagination-list">
          <li>
            <a className="pagination-link" onClick={handlePageLink}>
              1
            </a>
          </li>

          <li>
            <span className="pagination-ellipsis">&hellip;</span>
          </li>

          {page > 1 && (
            <li>
              <a className="pagination-link" onClick={handlePageLink}>
                {page}
              </a>
            </li>
          )}

          {page > 1 && (
            <li>
              <a className="pagination-link" onClick={handlePageLink}>
                {page + 1}
              </a>
            </li>
          )}

          {page + 2 < numPages && (
            <li>
              <a className="pagination-link" onClick={handlePageLink}>
                {page + 2}
              </a>
            </li>
          )}

          <li>
            <span className="pagination-ellipsis">&hellip;</span>
          </li>

          <li>
            <a className="pagination-link">{numPages}</a>
          </li>
        </ul>
      </nav>

      <CSVLink
        data={download}
        filename="data"
        onClick={exportSamples}
        className="button is-dark"
      >
        <button>Download Report</button>
      </CSVLink>
    </div>
  );
};

export default GeneExpression;
