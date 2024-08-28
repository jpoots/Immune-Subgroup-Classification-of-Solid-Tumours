import { openWarningModal } from "./openWarningModal";

/**
 * queries the given api every two seconds and checks for results
 * function adapted from https://stackoverflow.com/questions/62520968/keep-calling-an-api-every-2-5-seconds-and-close-the-call-once-desired-result-is
 * @param {string} resultURL - the API url to hit
 * @param {React.MutableRefObject} cancelled - the cancelled ref from the page requestion
 * @returns the result when the promise resolves
 */
const getData = (resultURL, cancelled) => {
  return new Promise((resolve, reject) => {
    // start every 2 seconds
    const interval = setInterval(async () => {
      try {
        // call API
        let result = await fetch(resultURL);

        // if cancelled exists and cancelled is true stop calls else if not still pending resovle promise
        if (cancelled && cancelled.current) {
          clearInterval(interval);
        } else if (result.status !== 201) {
          clearInterval(interval);
          resolve(result);
        }
      } catch (err) {
        reject();
      }
    }, 2000);
  });
};

/**
 * calls an async api, gets the task id and polls for a final result every two seconds. Returns the success status and results if valid. Validation is performed and an error modal opened with custom message on failure
 * @param {string} url - the async enpoint url to call
 * @param {Object} request - the request to send
 * @param {function} setModalMessage -  the function to set the modal message variable
 * @param {function} setOpenModal  - the function to set the openModal variable
 * @param {React.MutableRefObject} cancelled - the cancelled ref from the page requestion
 * @returns an object containing the results from the api and the success status
 */
const callAsyncApi = async (
  url,
  request,
  setModalMessage,
  setOpenModal,
  cancelled
) => {
  let apiResponse;
  let results;
  let resultURL;
  let errorMessage = "Sorry something went wrong! Please try again later.";

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
    resultURL = apiResponse.data.resultURL;
    results = await getData(resultURL, cancelled);

    // if results not ok
    if (!results.ok) {
      results = await results.json();
      errorMessage = results.error.description;
      throw new Error();
    }

    results = await results.json();
    results = results.data;

    return { results: results, success: true };
  } catch (err) {
    //  open error model on error
    openWarningModal(setModalMessage, setOpenModal, errorMessage);
    return { results: null, success: false };
  }
};

const cancelAnalysisFunctionDefiner = (cancelled) => {
  const cancelAnalysis = () => {
    cancelled.current = true;
  };
  return cancelAnalysis;
};

export { getData, callAsyncApi, cancelAnalysisFunctionDefiner };
