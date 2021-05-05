import pickle
# from tensorflow import keras
import re

import pandas as pd
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
import numpy as np


class AcceptancePrediction:

    def __init__(self):

        # load vectorizer and prediction model
        self.abstract_vectorizer = pickle.load(open('model/abstract_vectorizer.pickle', 'rb'))
        self.title_vectorizer = pickle.load(open('model/title_vectorizer.pickle', 'rb'))
        self.model = load_model('model/model_2.h5')
        self.MAX_SEQUENCE_LENGTH = 500

    def stemming_and_lemmatization(self, sentence):
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

    def predict_acceptance(self, df):
        df['abstractText'].iloc[0] = self.stemming_and_lemmatization(str(df['abstractText'].iloc[0]))
        df['title'].iloc[0] = self.stemming_and_lemmatization(str(df['title'].iloc[0]))
        df_references = pd.DataFrame([int(df['references'].iloc[0])], columns=['references'])
        # df_referenceMentions = pd.DataFrame([int(55)], columns=['referenceMentions'])
        df_referenceMentions = pd.DataFrame([int(df['referenceMentions'].iloc[0])], columns=['referenceMentions'])

        df_abstract = pd.DataFrame(self.abstract_vectorizer.transform((df['abstractText'].iloc[0]).split()).todense(),
                                              columns=self.abstract_vectorizer.get_feature_names())
        df_title = pd.DataFrame(self.title_vectorizer.transform((df['title'].iloc[0]).split()).todense(),
                                              columns=self.title_vectorizer.get_feature_names())


        df_test = pd.concat([df_abstract, df_title, df_references, df_referenceMentions], axis=1)
        pred = self.model.predict_classes(df_test)
        prob = self.model.predict(df_test)
        percentage = prob[0][1] * 100
        if pred[0] == 1:
            prediction = "True"
        else:
            prediction = "False"

        return {"accepted": prediction, "Acceptance_Probability": round(percentage,2)}
