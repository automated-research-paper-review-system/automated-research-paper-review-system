import os

from pandas.errors import InvalidIndexError
from parsed_pdfs_to_dataframes import create_dataframe_from_parsed_pdfs
import pandas as pd
from preprocess_text import preprocess_dataframe

if __name__=="__main__":
    df = create_dataframe_from_parsed_pdfs()
    df = preprocess_dataframe(df)
    print()
