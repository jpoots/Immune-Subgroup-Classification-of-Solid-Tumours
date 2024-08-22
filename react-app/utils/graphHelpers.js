/**
 * helpers for generating and displaying the tsne and pca graphs
 */


/**
 * 
 * @param {Object} graphData - the graph object structred by point and then sample
 * @param {number} dimension - the number of dimennsions to render 
 * @returns a list of plotly data traces
 */
const getPlotlyData = (graphData, dimension) => {
    return Object.keys(graphData.x).map((key) => {
      return {
        x: graphData.x[key],
        y: graphData.y[key],
        z: graphData.z[key],
        name: `${key}`,
        type: dimension === 2 ? "scatter" : "scatter3d",
        mode: "markers",
        text: graphData.ids[key],
        marker: {
          color: graphData.predictions,
        },
      };
    });
};

/**
 * generates a graph data dictionary containing all lists required to build a plotly trace for each subgroup
 * @param {Object} results - the generic prediction results
 * @param {Object} graphResponse - the data attained from the api call to data analysis api
 * @param {string} accessorKey - the key to access the required array in graphResponse
 * @returns 
 */
const generateGraphData = (results, graphResponse, accessorKey, dimensions) => {
    let x  = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [],
        7: [],
        NC: [],
      };
  
      // there are other ways of doing this but this seemed clear
      let y = structuredClone(x);
      let z = structuredClone(x);
      let preds = structuredClone(x);
      let idx = structuredClone(x);
  
      // create an array of numbers for each grpah value and subgroup
      graphResponse.forEach((sample, index) => {
        let prediction = results.samples[index].prediction;
        x[prediction].push(sample[accessorKey][0]);
        y[prediction].push(sample[accessorKey][1]);
        z[prediction].push(sample[accessorKey][2]);
        idx[prediction].push(sample.sampleID);
        preds[prediction].push(prediction);
      });
  
      // set graph data
      return ({
        x: x,
        y: y,
        z: z,
        ids: idx,
        predictions: preds,
        dim: dimensions
      });
}

export {getPlotlyData, generateGraphData}