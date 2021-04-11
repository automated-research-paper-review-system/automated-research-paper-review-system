import os

from pandas.errors import InvalidIndexError
from parsed_pdfs_to_dataframes import create_dataframe_from_parsed_pdfs
import pandas as pd
from reviews_to_dataframes import create_reviews_dataframe
from preprocess_text import *
from word_cloud import each_column_word_cloud
from classification_models import *
from word_embeddings import ELMoEmbedding

if __name__=="__main__":
    df = create_dataframe_from_parsed_pdfs()
    df = preprocess_dataframe(df)
    # print(ELMoEmbedding(df['abstractText']))
    # each_column_word_cloud(df)
    df = doc_to_vec(df)
    SVM_classifier(df)
    # df = hub_to_vec(df)
    df = tokenize_dataframe(df)

    df = create_vectors_dataframe(df)
    reviews_df = create_reviews_dataframe()
    merged_df = df.merge(reviews_df, left_on=['title', 'abstractText', 'accepted'], right_on=['title', 'abstractText', 'accepted'], how='outer')

    print(merged_df.accepted.value_counts())
    merged_df = merged_df[merged_df['accepted'].notna()]
    merged_df = merged_df.sort_values(by=['title'])

    final_df = merged_df[merged_df['accepted'].notna()]
    print(len(pd.unique(df['title'])))
    print()
    # model_elmo = build_model()
    # model_elmo.summary()
    # run_model_elmo(df, model_elmo)
