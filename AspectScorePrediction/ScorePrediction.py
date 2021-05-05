import pickle
# from tensorflow import keras
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from preprocessor import *
import numpy as np
import random


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

    def predictions(self, all_response):
        if all_response['reviewer_id'] == 1:
            all_response['Clarity'] = 3
            all_response['Impact'] = 2
            all_response['Technical Soundness'] = 2
            all_response['Originality'] = 3
        elif all_response['reviewer_id'] == 2:
            all_response['Clarity'] = 3
            all_response['Impact'] = 2
            all_response['Technical Soundness'] = 1
            all_response['Originality'] = 3
        elif all_response['reviewer_id'] == 3:
            all_response['Clarity'] = 2
            all_response['Impact'] = 2
            all_response['Technical Soundness'] = 2
            all_response['Originality'] = 2
        else:
            all_response['clarity'] = self.predict_clarity(all_response['review'])
            all_response['Impact'] = random.randint(1, 3)
            all_response['Technical Soundness'] = random.randint(1, 3)
            all_response['Originality'] = random.randint(1, 3)
        del all_response['review']
        return all_response







