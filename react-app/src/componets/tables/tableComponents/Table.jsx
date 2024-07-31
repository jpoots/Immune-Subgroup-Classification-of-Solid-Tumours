import sortArrows from "/sort-solid.svg";
import { flexRender } from "@tanstack/react-table";
import NumEntriesSelector from "./NumEntriesSelector";

/**
 * takes a tanstack table and displays it in the appropriate format
 * @param {TableInstance} table - the tanstack table instance to display
 * @returns a table
 */
export function Table({ table }) {
  return (
    <div className="table-container">
      {
        <table className="table is-bordered is-striped is-fullwidth">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <th key={header.id} className="has-text-centered">
                      {header.column.columnDef.header}{" "}
                      {header.column.getCanSort() && (
                        <button
                          className="button is-small sort-button"
                          onClick={header.column.getToggleSortingHandler()}
                        >
                          <img src={sortArrows} width={10} />
                        </button>
                      )}
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>

          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="has-text-centered">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      }
      <NumEntriesSelector table={table} />
    </div>
  );
}
