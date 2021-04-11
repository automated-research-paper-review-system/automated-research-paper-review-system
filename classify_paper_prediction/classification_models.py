from nltk.corpus import stopwords
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.python.keras import Input, Model
from tensorflow.python.keras.layers import Lambda, Dense
import keras
import keras.backend as K
from word_embeddings import ELMoEmbedding, f1_m
from eager_mode import train_model
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import svm, datasets

def SVM_classifier(df):
    y = df.pop('accepted')
    df.pop('name')
    df.pop('creator')
    df.pop('authors')
    df.pop('emails')
    X = df
    xtrain, xtest, ytrain, ytest = train_test_split(X, y, test_size=0.2)
    svc = svm.SVC(kernel='linear', C=1, gamma='auto')
    svc.fit(xtrain, ytrain)
    score = svc.score(xtrain, ytrain)
    print(score)

def tfidf_on_dataframe(df):
    vectorizer = CountVectorizer(max_features=1500, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))

def build_model():
    input_comment = Input(shape=(1,), dtype="string", name='input_comment')
    embedding = Lambda(ELMoEmbedding, output_shape=(1024, ))(input_comment)
    dense = Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001))(embedding)
    pred = Dense(1, activation='sigmoid')(dense)
    model = Model(inputs=[input_comment], outputs=pred)
    model.compile(keras.optimizers.Adam(lr=1e-4), loss='binary_crossentropy', metrics=['accuracy', f1_m])
    # model.run_eagerly = True
    return model

def run_model_elmo(df, model_elmo):
    y = df.pop('accepted')
    X = df
    xtrain, xtest, ytrain, ytest = train_test_split(X.index, y, test_size=0.2)

    # with tf.compat.v1.Session() as session:
    #     tf.compat.v1.keras.backend.set_session(session)
    #     session.run(tf.compat.v1.global_variables_initializer())
    #     session.run(tf.compat.v1.tables_initializer())
    #
    #     history = model_elmo.fit(xtrain, ytrain,validation_data=(xtest, ytest), epochs=10, batch_size=16)
    #     model_elmo.save_weights('./model_elmo_weights.h5')
    #     scores={}
    #     score_gl_test = model_elmo.evaluate([xtest], ytest, verbose=0)
    #     print('Test acc:', score_gl_test[1])
    #     print('Test fscore:', score_gl_test[2])

    with tf.compat.v1.Session() as session:
        tf.compat.v1.keras.backend.set_session(session)
        session.run(tf.compat.v1.global_variables_initializer())
        session.run(tf.compat.v1.tables_initializer())

        train_model(model_elmo, xtrain, xtest, ytrain, ytest)
        # history = model_elmo.fit(xtrain, ytrain,validation_data=(xtest, ytest), epochs=10, batch_size=16)
        model_elmo.save_weights('./model_elmo_weights.h5')
        scores={}
        score_gl_test = model_elmo.evaluate([xtest], ytest, verbose=0)
        print('Test acc:', score_gl_test[1])
        print('Test fscore:', score_gl_test[2])