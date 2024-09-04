import { useEffect, useRef, useState } from "react";
import { API_ROOT } from "../../../utils/constants";
import { CSVLink } from "react-csv";
import ErrorModal from "../../components/errors/ErrorModal";
import { openWarningModal } from "../../../utils/openWarningModal";
import Box from "../../components/layout/Box";
import QueensLink from "../../components/other/QueensLink";

/**
 * a help page for the app containing help text
 * @returns a help page for the ap
 */
const Help = () => {
  // setting state for the [age]
  const [download, setDownload] = useState([]);
  const [openModal, setOpenModal] = useState();
  const [modalMessage, setModalMessage] = useState();
  const csvLink = useRef();

  /**
   * use effect to trigger download once state is set for gene list
   */
  useEffect(() => {
    if (download.length != 0) {
      csvLink.current.link.click();
    }
  }, [download]);

  /**
   * gets the current gene name list and puts it into an array of arrays in down oad to be handled by CSVLink
   */
  const handleDownloadGeneList = async () => {
    try {
      let response = await fetch(`${API_ROOT}/genelist`);

      //  if unknown error throw error to be caught
      if (!response.ok) throw new Error();
      else {
        // if all is good set the gene lists to a array of arrays
        response = await response.json();
        let gene_name_list = response.data.results;
        gene_name_list = gene_name_list.map((name) => [name]);

        setDownload(gene_name_list);
      }
    } catch (err) {
      // if an error has occured display
      openWarningModal(
        setModalMessage,
        setOpenModal,
        "An error has occurred please try again later!"
      );
    }
  };

  return (
    <>
      <Box>
        <div className="block">
          <div className="columns">
            <div className="column block">
              {" "}
              <h1 className="block has-text-weight-bold">What is ICST?</h1>
              ICST (Immune Subgroup Classification of Solid Tumours) is a
              research tool for cancer researchers and immunotherapy
              practitioners developed as an MSc Software Development project by
              Jordan Poots in concert with research performed by Dr Reza Rafiee
              at Queen&apos;s University Belfast. It seeks to use FPKM
              normalised RNA-Seq data from 440 genes to group solid tumour
              samples into one of the six immune sugroups identified in the 2018
              publication{" "}
              <QueensLink href="https://pubmed.ncbi.nlm.nih.gov/29628290/">
                The Immune Landscape of Cancer
              </QueensLink>
              . In addition, a 7th subgroup is defined by Dr Rafiee for samples
              which fall between subgroups. Full sungroup names are listed
              below. More details about the characterists along with therapeutic
              inights can be found in the linked paper. The tool also provides
              useful visualisation tools for the data.
            </div>
          </div>

          <div className="columns is-centered">
            <div className="column is-half is-flex is-justify-content-center">
              <table className="table block">
                <thead>
                  <tr>
                    <th className="has-text-centered">Subgroup Label</th>
                    <th className="has-text-centered">Subgroup Name</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="has-text-centered">C1</td>
                    <td className="has-text-centered">Wound Healing</td>
                  </tr>
                  <tr>
                    <td className="has-text-centered">C2</td>
                    <td className="has-text-centered">IFN-&#947; Dominant</td>
                  </tr>
                  <tr>
                    <td className="has-text-centered">C3</td>
                    <td className="has-text-centered">Inflammatory</td>
                  </tr>
                  <tr>
                    <td className="has-text-centered">C4</td>
                    <td className="has-text-centered">Lymphocyte Depleted</td>
                  </tr>
                  <tr>
                    <td className="has-text-centered">C5</td>
                    <td className="has-text-centered">Immunologically Quiet</td>
                  </tr>
                  <tr>
                    <td className="has-text-centered">C6</td>
                    <td className="has-text-centered">TGF-β Dominant</td>
                  </tr>
                  <tr>
                    <td className="has-text-centered">C7</td>
                    <td className="has-text-centered">Predominant</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="block">
          <h1 className="block has-text-weight-bold	">How does it work?</h1>
          <div className="block">
            <p className="block">
              ICST accepts FPKM normalised RNA-Seq data and extracts 440 key
              genes for the subgroup classification. Any missing genes are
              imputed using MICE (Multivariate Imputation by Chained Equations).
              Note that the system will not accept missing gene rows. To ensure
              the quality of predictions all samples undergo Gene Quality
              Control and samples with 10 or more missing genes will be
              rejected. Gene expression values are then scaled between 0 and 1
              using a Minmax scaling algorithm. These &quot;features&quot; are
              fed to a supervised machine learning model trained on
              approximately 6000 samples from PanCanAtlas using the{" "}
              <QueensLink href="https://xgboost.readthedocs.io/en/stable/index.html">
                Extreme Gradient Boosting
              </QueensLink>{" "}
              algorthim to attain a classification along with the models
              probability of each subgroup.
            </p>

            <p className="block">
              The tool also uses the{" "}
              <QueensLink href="https://builtin.com/data-science/step-step-explanation-principal-component-analysis">
                {" "}
                PCA (Principle Component Analysis)
              </QueensLink>{" "}
              algorithm with standard scaling and the{" "}
              <QueensLink href="https://www.datacamp.com/tutorial/introduction-t-sne">
                t-SNE (t-distributed Stochastic Neighbor Embedding)
              </QueensLink>{" "}
              algorithm to visualise the sample data and identify clustering.
            </p>

            <p className="block">
              Confidence intervals are attained using models trained on 10
              random bootstraps of the training data. Note that this is for
              demonstration purposes only. A larger number of bootstraps should
              be used in production. Prediction probabilities are generated from
              each of these models and a confidence interval is extracted. This
              is shown via a box plot where the box indicates the true range of
              the probability with a confidence of the requested interval. For
              example, a box ranging from 0.95 - 0.9 for a 95% interval
              indicates the system is 95% sure that the true proability is in
              that range.
            </p>

            <p className="block">
              {" "}
              Visualisation of the classification by cancer type using a stacked
              bar chart is also avaialble where type IDs have been provided.
            </p>
          </div>
        </div>

        <div className="block">
          <h1 className="block has-text-weight-bold	">How do I use it?</h1>
          <div>
            ICST accepts RNA-Seq data from solid tumours in CSV or TXT files
            with a comma, semicolon or tab delimiter and assumes the data has
            already been FPKM normalised. This may be uploaded on the upload
            page. Data should be formatted as shown in the{" "}
            <QueensLink href="/icst/test_data.csv" download={true} target="">
              {" "}
              Test Data {}
            </QueensLink>
            with each column representing a sample and each row a gene. A list
            of the current accepted gene names can be found{" "}
            <QueensLink onClick={handleDownloadGeneList} target="">
              here
            </QueensLink>
            .{" "}
            <CSVLink
              data={download}
              filename="data"
              className="is-hidden"
              ref={csvLink}
            ></CSVLink>
            The genes may be in any order and a file may contain more than the
            440 required genes. A label row/column should be included for both
            axis. In addition, to maintain accuracy, any samples for which ICST
            cannot make a confident prediction will be deemed non-classifiable
            (NC). The current threshold for this is 92%. Where samples fall
            below this threshold but above a random guess (50%) and have a top
            two probabilities which sum to a value above the threshold, they are
            deemed to have two predominant subgroups and are labelled as
            subgroup 7 in the classification table. Results and visualisations
            can be viewed using the navigation bar at the top of the screen. All
            data including graphs is available to download.
          </div>
        </div>

        <div className="block">
          <h1 className="block has-text-weight-bold	">How good is it?</h1>
          <div className="block">
            While training and evaluation of a machine learning model is a
            complex process, some summary evaluation metrics from a holdout set
            of stratfified test data (approximately 2000 samples) are listed
            below for your confidence in the model&apos;s output. In addition,
            the model has underwent 10 fold cross validation prior to QC
            thresholding and final testing.
          </div>

          <div className="columns is-centered">
            <div className="column is-half is-flex is-justify-content-center">
              {" "}
              <table className="table block">
                <thead>
                  <tr>
                    <th className="has-text-centered">Metric</th>
                    <th className="has-text-centered">Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="has-text-centered">Accuracy</td>
                    <td className="has-text-centered">95.9%</td>
                  </tr>
                  <tr>
                    <td className="has-text-centered">F1</td>
                    <td className="has-text-centered">90.6%</td>
                  </tr>
                  <tr>
                    <td className="has-text-centered">Precision</td>
                    <td className="has-text-centered">89.0%</td>
                  </tr>
                  <tr>
                    <td className="has-text-centered">Recall</td>
                    <td className="has-text-centered">93.1%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="block">
          <h1 className="block has-text-weight-bold	">For developers</h1>
          <div className="block">
            In keeping with the open access nature of ICST, all APIs used to
            provide site functionality are open. In addition, other APIs are
            availble for conveience of development. Full Swagger documumentation
            for these can be found{" "}
            <QueensLink href={`${API_ROOT}/apidocs`}>here</QueensLink>. These
            can used to perform your own custom analysis.
          </div>
        </div>

        <div className="block">
          <h1 className="block has-text-weight-bold	">Terms and conditions</h1>
          <div className="block">
            All software including the API is provided on an &quot;as is&quot;
            basis without warranties of any kind, either express or implied.
            Software disclaims all warranties, express or implied, arising by
            law or otherwise, with respect to any error, defect, deficiency,
            infringement, or noncompliance in the services, technology, support,
            or any other items provided by, through, or on behalf of Software
            under this agreement. Data may be stored by the provider and used
            anonymously for research purposes. This data may be shared with 3rd
            parties. By using this software, including the API, you consent to
            these terms and conditions.
          </div>
        </div>
      </Box>
      {openModal && (
        <ErrorModal modalMessage={modalMessage} setOpenModal={setOpenModal} />
      )}
    </>
  );
};

export default Help;
