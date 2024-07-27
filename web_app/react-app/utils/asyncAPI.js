const RESULTS_ENDPOINT = "http://127.0.0.1:3000/getresults/"

// function adapted from https://stackoverflow.com/questions/62520968/keep-calling-an-api-every-2-5-seconds-and-close-the-call-once-desired-result-is helped me learn about making my own promise funcitons :)
const getData = (resultType, taskID) => {
return new Promise((resolve) => {
    const interval = setInterval(async () => {
    let result = await fetch(`${RESULTS_ENDPOINT}${resultType}/${taskID}`);
    result = await result.json();
    if (result.status == "SUCCESS" || result.status === "FAILURE") {
        clearInterval(interval);
        resolve(result);
    }
    }, 200);
});
};

export {getData}
