import pickle
# from tensorflow import keras
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from preprocessor import *
import numpy as np


class ScorePrediction:

    def __init__(self):

        # load vectorizer and prediction model
        self.tokenizer = pickle.load(open('model/score_token_vector.pickel', 'rb'))
        self.model = load_model('model/clarity_model.h5')
        self.MAX_SEQUENCE_LENGTH = 500

    def predict_clarity(self, review):
        processed_review = preprocess(str(review))
        # new_review = ['It is not clear to me how the presented approach works.']
        seq = self.tokenizer.texts_to_sequences([processed_review])
        padded = pad_sequences(seq, maxlen=self.MAX_SEQUENCE_LENGTH)
        pred = self.model.predict(padded)
        # print("\nprediction-", pred)
        labels = ['1', '2', '3']
        # print("\nargmax-", np.argmax(pred))

        return labels[np.argmax(pred)]







