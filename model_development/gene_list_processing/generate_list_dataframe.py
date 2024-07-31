import pandas as pd
from gene_list import GENE_LIST
import joblib

"""
Generates a pandas data frame with columns being gene list which
can then be used to extract genes from a given dataframe
"""

# the location to save the object
FILE_NAME = "ordered_gene_names.pkl"


def main():
    gene_list_df = pd.DataFrame(columns=GENE_LIST)
    joblib.dump(gene_list_df, filename=FILE_NAME)


if __name__ == "__main__":
    main()


"""
example usage
# https://stackoverflow.com/questions/43537166/select-columns-from-dataframe-on-condition-they-exist
data = data[gene_list_df.columns.intersection(data.columns)]
"""
