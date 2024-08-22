const SearchAndFilter = ({ table }) => {
  return (
    <div className="columns">
      <div className="column is-one-quarter">
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
      <div className="column is-half">
        <div className="select is-danger">
          <select
            name=""
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
            <option value="NC">Non-classifiable</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default SearchAndFilter;
