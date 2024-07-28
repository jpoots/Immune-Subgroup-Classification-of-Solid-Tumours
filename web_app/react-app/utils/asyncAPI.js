import { openWarningModal } from "./openWarningModal";

/**
 * queries the given api every two seconds and checks for results
 * // function adapted from https://stackoverflow.com/questions/62520968/keep-calling-an-api-every-2-5-seconds-and-close-the-call-once-desired-result-is
 * @param {string} resultURL - the api to hit
 * @returns the result when the promise resolves
 */
const getData = (resultURL) => {
return new Promise((resolve) => {
    const interval = setInterval(async () => {
    let result = await fetch(resultURL);
    
    if (result.status !== 201) {
        clearInterval(interval);
        resolve(result);
    }

    }, 200);
});
};


/**
 * calls an async api, gets the task id and polls for a final result every two seconds. Returns the success status and results if valid. Validation is performed and an error modal opened with custom message on failure
 * @param {string} url - the async enpoint
 * @param {object} request - the request to send
 * @param {function} setModalMessage -  the function to set the modal message variable
 * @param {function} setOpenModal  - the function to set he openModal variable
 * @returns an object containing the results from the api and the success status
 */
const callAsyncApi = async (url, request, setModalMessage, setOpenModal) => {
    let apiResponse;
    let errorMessage;
    let results;
    let resultURL;

    try {
        apiResponse = await fetch(url, request);

        // if api response not ok
        if (!apiResponse.ok) {
            apiResponse = await apiResponse.json();
            errorMessage = apiResponse.error.description;
            throw new Error();
        }

        // use the async getData to poll for result
        apiResponse = await apiResponse.json();
        resultURL = apiResponse.resultURL;
        results = await getData(resultURL);

        // if results not ok
        if (!results.ok) {
            results = await results.json();
            errorMessage = results.error.description;
            throw new Error();
        }

        results = await results.json();
        results = results.data;

        return {"results": results, "success": true}

        } catch (err) {
        //  error
        openWarningModal(setModalMessage, setOpenModal, errorMessage);
        return {"results": null, "success": false}
        }
}

export {getData, callAsyncApi}
