const Help = () => {
  return (
    <div className="container">
      <div className="box">
        <div className="block">
          <h1 className="block has-text-weight-bold">What is ICST?</h1>
          ICST (Immune Subgroup Classification of Solid Tumours) is a research
          tool for cancer researchers and immunotherapy practitioners developed
          as an MSc Software Development project by Jordan Poots in concert with
          research performed by Dr Reza Rafiee at Queen's University Belfast. It
          seeks to use FPKM normalised RNA-Seq data from 440 genes to group
          solid tumour samples into one of the six immune sugroups identified in
          the 2018 publication{" "}
          <a
            href="https://pubmed.ncbi.nlm.nih.gov/29628290/"
            className="queens-branding-text"
          >
            The Immune Landscape of Cancer
          </a>
          . The tool also provides useful visualisation tools for sample data.
        </div>

        <div className="block">
          <h1 className="block has-text-weight-bold	">How does it work?</h1>
          <div className="block">
            <p className="block">
              ICST accepts RNA-Seq data and extracts 440 key genes for the
              subgroup classification. Any missing genes are imputed using the
              MICE algorithm and genes are then scaled betwen -1 and 1 using a
              Minmax scaling algorithm. They are then fed to a supervised
              machine learning model trained on over 9000 samples from
              PanCanAtlas using the gradient boosting algorthim in order the
              attain a classification along with the models probability of each
              subgroup.
            </p>

            <p className="block">
              The tool also uses the PCA algorithm with standard scaling and the
              t-SNE algorithm to visualise the sample data and identify
              clustering.
            </p>

            <p className="block">
              Confidence intervals are attained using models trained on X random
              bootstraps of the training data. Prediction probabilities are
              generated from each of these models and a 95% confidence interval
              is extracted from these. This is shown via a box plot where the
              box contains the 95%.
            </p>
          </div>
        </div>

        <div className="block">
          <h1 className="block has-text-weight-bold	">How do I use it?</h1>
          <div>
            ICST accepts RNA-Seq data from solid tumours in CSV or TXT files and
            assumes the data has already been FPKM normalised. This may be
            uploaded on the upload page. Data should be formatted as shown in
            the{" "}
            <a
              href="/test_data.csv"
              className="queens-branding-text"
              download={true}
            >
              Test Data
            </a>{" "}
            with each column representing a sample and each row a gene. A label
            row/column should be included for both axis. While ICST can impute
            genes, for quality reasons samples with more than Y missing genes
            will be rejected. In addition, to maintain accuracy, any samples for
            which ICST cannot make a confident prediction will be deemed
            non-classifiable (NC). Results can be viewed using the navigation
            bar at the top of the screen.
          </div>
        </div>

        <div className="block">
          <h1 className="block has-text-weight-bold	">How good is it?</h1>
          <div className="block">
            While training and evaluation of a machine learning model is a
            complicated process, some evaluation statistics are listed below for
            your confidence in the models output. All values have been attained
            using 10 fold cross validation.
          </div>

          <div className="block">
            <ul>
              <li>Accuracy: X</li>
              <li>F1: Y</li>
              <li>Precision: Z</li>
              <li>Recall: O</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Help;
