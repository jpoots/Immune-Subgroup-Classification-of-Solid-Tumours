// https://stackoverflow.com/questions/62520968/keep-calling-an-api-every-2-5-seconds-and-close-the-call-once-desired-result-is
const getData = (taskID) => {
return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
    let result = await fetch(`http://127.0.0.1:3000/getresults/${taskID}`);
    result = await result.json();
    if (result.status == "SUCCESS") {
        clearInterval(interval); // Clear the interval
        resolve(result); // Resolve with the data
    }
    }, 200);
});
};

export {getData}
