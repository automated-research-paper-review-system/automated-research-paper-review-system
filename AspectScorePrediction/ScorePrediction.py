import pickle
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from preprocessor import *
import numpy as np
import random


class ScorePrediction:

    def __init__(self):
        self.MAX_SEQUENCE_LENGTH = 500

    def predict_aspect(self, review, aspect):

        # load vectorizer and prediction model
        modelPath = 'model/' + aspect + '_model.h5'
        tokenizerPath = 'model/' + aspect +'_vector.pickel'
        tokenizer = pickle.load(open(tokenizerPath, 'rb'))
        model = load_model(modelPath)

        #preprocess the input review
        processed_review = preprocess(str(review))
        seq = tokenizer.texts_to_sequences([processed_review])
        padded = pad_sequences(seq, maxlen=self.MAX_SEQUENCE_LENGTH)

        #predict the aspect score
        pred = model.predict(padded)
        labels = ['1', '2', '3']
        return labels[np.argmax(pred)]

    def predictions(self, all_response):
        all_response['clarity'] = self.predict_aspect(all_response['review'], 'clarity')
        all_response['Impact'] = self.predict_aspect(all_response['review'], 'impact')
        all_response['Technical Soundness'] = self.predict_aspect(all_response['review'], 'soundness')
        all_response['Originality'] = self.predict_aspect(all_response['review'], 'originality')
        del all_response['review']
        return all_response







