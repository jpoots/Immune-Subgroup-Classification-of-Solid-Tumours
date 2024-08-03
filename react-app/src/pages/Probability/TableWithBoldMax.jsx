import sortArrows from "/sort-solid.svg";
import { flexRender } from "@tanstack/react-table";
import NumEntriesSelector from "../../components/tables/NumEntriesSelector";
/**
 * takes a tanstack table and displays it in the appropriate format with bold row maxs
 * @param {TableInstance} table - the tanstack table instance to display
 * @param {string} accessor - the key to the original list of items to be maxed
 * @returns a table
 */
export function TableWithBoldMax({ table, accessor }) {
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
            {table.getRowModel().rows.map((row) => {
              let max = Math.max(...row.original[accessor]).toFixed(5);
              console.log(max);
              return (
                <tr key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <td
                      key={cell.id}
                      className={`has-text-centered ${
                        cell.getValue() === max ? "has-text-weight-bold	" : ""
                      }`}
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      }
      <NumEntriesSelector table={table} />
    </div>
  );
}
