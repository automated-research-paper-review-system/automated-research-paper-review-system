import pickle
import re
import pandas as pd
import scipy
import numpy as np
import sklearn.feature_extraction.text

class ReviewerRecommender:

    def __init__(self):
        # load vectorizer and prediction model
        self.fitted_vectorizer = pickle.load(open('fitted_vectorizer1.pickel', 'rb'))
        self.tfidf_train_vectors = pickle.load(open('tfidf_train_vectors1.pickel', 'rb'))


    def given_paperID_give_authours_id(self,paper_id, author_id_data):
        id_author_list = author_id_data[author_id_data['PaperId'] == paper_id]['AuthorId']
        return id_author_list

    def reviewer_recommender(self, df):
        #df['abstractText'].iloc[0] = self.stemming_and_lemmatization(str(df['abstractText'].iloc[0]))
        print(df['abstractText'].iloc[0])
        tfidf_search_query_vectors = self.fitted_vectorizer.transform([df['abstractText'].iloc[0]])
        #search_query = "Non-convex Statistical Optimization for Sparse Tensor Graphical Model."
        #tfidf_search_query_vectors = self.fitted_vectorizer.transform([search_query])
        # Calculate cosine similarity between search query vector and document vectors
        cosine_distance_between_search_query_and_doc_vectors = scipy.sparse.csr_matrix.dot(self.tfidf_train_vectors,
                                                                                           scipy.sparse.csr_matrix.transpose(
                                                                                               tfidf_search_query_vectors))
        top_n_docs = 2
        top_N_file_indices = np.squeeze(np.array((np.argsort(
            -cosine_distance_between_search_query_and_doc_vectors.todense().flatten(), axis=1)[0, :top_n_docs])))

        papers_data = pd.read_csv('Papers.csv')
        authors_data = pd.read_csv('Authors.csv')
        authorId_data = pd.read_csv('PaperAuthors.csv')

        doc_no = 0
        authors = []
        names = []
        for index in top_N_file_indices:
            # Show titles of top documents that match the search query the most
            doc_no += 1
            paper_id = papers_data.iloc[index]['Id']
            for authid in self.given_paperID_give_authours_id(paper_id, authorId_data):
                authors.append(authors_data[authors_data['Id'] == authid].index[0])

        for index in authors:
                names.append(authors_data.iloc[index]['Name'])
        print(names)
        return names



