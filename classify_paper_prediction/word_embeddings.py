import keras.backend as K
import tensorflow_hub as hub
import tensorflow as tf
from simple_elmo import ElmoModel

elmo = hub.load("https://tfhub.dev/google/elmo/2")

embeddings = elmo.signatures["default"](tf.constant([
                "i like green eggs and ham",
                "i like green ham and eggs"
                ])
                )["elmo"]

print(embeddings.shape)

def ELMoEmbedding(x):
    return elmo.signatures["default"](tf.reshape(tf.cast(x, tf.string), [-1]))["default"]

def recall_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall


def precision_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision


def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2 * ((precision * recall) / (precision + recall + K.epsilon()))