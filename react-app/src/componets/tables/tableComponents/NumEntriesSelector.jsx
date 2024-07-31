/**
 * A component for changing the number of records displayed on a table
 * @param {TableInstance} table - the tanstack table instance to display for
 * @returns - the changer component
 */
const NumEntriesSelector = ({ table }) => {
  const pageSize = table.getState().pagination.pageSize;

  return (
    <div className="is-flex">
      <div>
        <label className="mr-2"> Per page:</label>
      </div>

      <div className="block mb-5 select is-danger is-small is-rounded ">
        <select onChange={(e) => table.setPageSize(e.target.value)}>
          <option value="5" selected={pageSize === 5}>
            5
          </option>
          <option value="10" selected={pageSize === 10}>
            10
          </option>
          <option value="20" selected={pageSize === 20}>
            20
          </option>
        </select>
      </div>
    </div>
  );
};

export default NumEntriesSelector;
