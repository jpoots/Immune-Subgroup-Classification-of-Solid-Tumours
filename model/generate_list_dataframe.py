import pandas as pd
import numpy as np
from gene_list import GENE_LIST
import joblib

FILE_NAME = "ordered_gene_names.pkl"
gene_list_df = pd.DataFrame(columns=GENE_LIST)
joblib.dump(gene_list_df, filename=FILE_NAME)


"""
example usage
# https://stackoverflow.com/questions/43537166/select-columns-from-dataframe-on-condition-they-exist
data = data[gene_list_df.columns.intersection(data.columns)]
"""
