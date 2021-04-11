import re
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from gensim.models import KeyedVectors
from nltk.tokenize import word_tokenize
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
import tensorflow_hub as hub

def stemming_and_lemmatization(sentence):
    stemmer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    newSentence = re.sub(r'\W', ' ', sentence)
    newSentence = re.sub(r'\s+[a-zA-Z]\s+', ' ', newSentence)
    newSentence = re.sub(r'\^[a-zA-Z]\s+', ' ', newSentence)
    newSentence = re.sub(r'\s+', ' ', newSentence, flags=re.I)
    newSentence = newSentence.lower()
    newSentence = newSentence.split()
    newSentence = [w for w in newSentence if not w in stop_words]
    newSentence = [stemmer.lemmatize(word) for word in newSentence]
    newSentence = ' '.join(newSentence)
    return newSentence

def isNaN(string):
    return string != string

def create_vectors_dataframe(df):
    model = KeyedVectors.load_word2vec_format('/home/kapil/SJSU-Acad/MastersProject/codebase/data/GoogleNews-vectors-negative300.bin', binary=True)
    for index, row in df.iterrows():
        if not isNaN(df['title'][index]):
            df['title'] = model[df['title']]
        if not isNaN(df['abstractText'][index]):
            df['abstractText'] = model[df['abstractText']]
        if not isNaN(df[' Introduction'][index]):
            df[' Introduction'] = model[df[' Introduction']]
        if not isNaN(df[' Conclusion'][index]):
            df[' Conclusion'] = model[df[' Conclusion']]
    return df

def preprocess_reviews_dataframe(df):
    for index, row in df.iterrows():
        print(index)
        row['abstractText'] = stemming_and_lemmatization(str(row['abstractText']))
        row['title'] = stemming_and_lemmatization(str(row['title']))
    return df

def preprocess_dataframe(df):
    for index, row in df.iterrows():
        print(index)
        row['abstractText'] = stemming_and_lemmatization(str(row['abstractText']))
        row['title'] = stemming_and_lemmatization(str(row['title']))
        row[' Introduction'] = stemming_and_lemmatization(str(row[' Introduction']))
        row[' Related Work'] = stemming_and_lemmatization(str(row[' Related Work']))
        row[' Conclusion'] = stemming_and_lemmatization(str(row[' Conclusion']))
        row[' Experiments'] = stemming_and_lemmatization(str(row[' Experiments']))
        row[' Results'] = stemming_and_lemmatization(str(row[' Results']))
        row[' Discussion'] = stemming_and_lemmatization(str(row[' Discussion']))
    return df

def tokenize_dataframe(df):
    for index, row in df.iterrows():
        df['abstractText'][index] = word_tokenize(str(df['abstractText'][index]))
        df['title'][index] = word_tokenize(df['title'][index])
        df[' Introduction'][index] = word_tokenize(df[' Introduction'][index])
        df[' Conclusion'][index] = word_tokenize(df[' Conclusion'][index])
        df[' Experiments'][index] = word_tokenize(df[' Experiments'][index])
        df[' Related Work'][index] = word_tokenize(df[' Related Work'][index])
        df[' Discussion'][index] = word_tokenize(df[' Discussion'][index])
        df[' Results'][index] = word_tokenize(df[' Results'][index])

    return df

def doc_to_vec(df):
    for column in df:
        if column == 'abstractText' or column == 'title' or column == ' Introduction' or column == ' Related Work' or column == ' Experiments' or column == ' Results' or column == ' Conclusion' or column == ' Discussion':
            docs = [TaggedDocument(str(df[column][i]).split(' '), [i])
                         for i, doc in enumerate(df[column])]
            model = Doc2Vec(vector_size=64, window=2, min_count=1, workers=8, epochs=40)
            model.build_vocab(docs)
            model.train(docs, total_examples=model.corpus_count, epochs=model.epochs)

            vec = [model.infer_vector((df[column][i].split(' ')))
                        for i in range(0, len(df[column]))]

            df[column] = vec
    return df

# def hub_to_vec(df):
#     embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")
#     embeddings = embed(df['abstractText'])
#     use = np.array(embeddings).tolist()
#     df['use'] = use
#     return df


if __name__=="__main__":
    abstractText = "Cross lingual projection of linguistic annotation suffers from many sources of bias and noise, leading to unreliable annotations that cannot be used directly. In this paper, we introduce a novel approach to sequence tagging that learns to correct the errors from cross-lingual projection using an explicit noise layer. This is framed as joint learning over two corpora, one tagged with gold standard and the other with projected tags. We evaluated with only 1000 tokens tagged with gold standard tags, along with more plentiful parallel data. Our system equals or exceeds the state-of-the-art on eight simulated lowresource settings, as well as two real lowresource languages, Malagasy and Kinyarwanda."
    stemming_and_lemmatization(abstractText)