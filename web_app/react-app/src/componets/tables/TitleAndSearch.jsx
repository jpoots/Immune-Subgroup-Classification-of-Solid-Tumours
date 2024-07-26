import { SearchByID } from "./SearchByID";
/**
 * a search by ID bar for tables accompanied by the title
 * @param {TableInput} table - the table to be searched by ID
 * @param {string} title - the title to dsipaly on the page
 * @returns
 */
export function TitleAndSearch({ table, title }) {
  return (
    <div className="columns">
      <div className="column is-half">
        <h1 className="block has-text-weight-bold">{title}</h1>
        <SearchByID table={table} />
      </div>
    </div>
  );
}
