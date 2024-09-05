import SearchByID from "./SearchByID";

/**
 * a combined search and filter by id for a table with columns prediction and sampleid
 * @param {TableInstance} table - the table to search and filter
 * @returns the seach and filter bar
 */
const SearchAndFilter = ({ table }) => {
  return (
    <div className="columns">
      <div className="column is-one-quarter">
        <SearchByID table={table} />
      </div>
      <div className="column is-half">
        <div className="select is-danger">
          <select
            name="filterSelect"
            onChange={(e) => {
              table.getColumn("prediction").setFilterValue(e.target.value);
            }}
            defaultValue={""}
          >
            <option value="">All</option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
            <option value="7">7</option>
            <option value="NC">Non-classifiable</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default SearchAndFilter;
