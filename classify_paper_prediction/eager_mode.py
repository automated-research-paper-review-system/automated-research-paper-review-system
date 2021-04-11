import numpy as np
import tensorflow as tf
from tqdm import tqdm
from tensorflow import keras
from tensorflow.keras.layers import Input, Dense, Flatten, Conv2D
from tensorflow.keras import Model
from tensorflow.keras.optimizers import Adam


def loss_compute(y_true, y_pred):
    return tf.square(y_true - y_pred)

def train_model(model, train_samples, test_samples, train_targets, test_targets):
    # Training loop
    epochs = 10
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

    for epoch in range(epochs):

        # Fancy progress bar
        pbar = tqdm(range(len(train_samples)))

        # Metrics
        loss_metric = keras.metrics.Mean()

        # Batches iteration, batch_size = 1
        for batch_id in pbar:
            # Getting sample target pair
            sample = train_samples[batch_id]
            target = train_targets[batch_id]

            # Adding batch dim since batch=1
            sample = tf.expand_dims(sample, axis=0)
            target = tf.expand_dims(target, axis=0)

            # Forward pass: needs to be recorded by gradient tape
            with tf.GradientTape() as tape:
                target_pred = model(sample)
                loss = loss_compute(target, target_pred)

            # Backward pass:
            # compute gradients w.r.t. the loss
            # update trainable weights of the model
            gradients = tape.gradient(loss, model.trainable_weights)
            optimizer.apply_gradients(zip(gradients, model.trainable_weights))

            # Tracking progress
            loss_metric(loss)
            pbar.set_description('Training Loss: %.3f' %
                                 loss_metric.result().numpy())

        # At the end of the epoch test the model
        test_targets_pred = model(test_samples)
        test_loss = loss_compute(test_targets, test_targets_pred)
        test_loss_avg = tf.reduce_mean(test_loss)
        print('Validation Loss: %.3f' % test_loss_avg)

if __name__ == '__main__':

    # Learn to sum 20 nums
    train_samples = tf.random.normal(shape=(10000, 20)) #X_train
    train_targets = tf.reduce_sum(train_samples, axis=-1) #Y_train
    test_samples = tf.random.normal(shape=(100, 20)) #X_test
    test_targets = tf.reduce_sum(test_samples, axis=-1) #Y_test

    # Model building: Keras functional API
    x = Input(shape=[20])
    h = Dense(units=20, activation='relu')(x)
    h = Dense(units=10, activation='relu')(h)
    y = Dense(units=1)(h)
    model = Model(x, y)

    train_model(model, train_samples, test_samples, train_targets, test_targets)

