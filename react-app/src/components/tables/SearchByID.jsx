/**
 * a searchbar for searching by ID on any table with column sampleID
 * @param {TableInstance} table - the table to be searched
 * @returns
 */

export function SearchByID({ table }) {
  return (
    <input
      type="text"
      className="input queens-textfield"
      onChange={(e) => {
        let column = table.getColumn("sampleID");
        column.setFilterValue(e.target.value.toUpperCase());
      }}
      placeholder="Search by sample ID"
    />
  );
}
