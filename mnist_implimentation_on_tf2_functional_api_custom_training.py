
import tensorflow as tf
from tensorflow.keras.datasets import mnist
import numpy as np
from random import sample 
import time

BATCH_SIZE = 128
num_classes = 10

# Read data
(x_train, y_train), (x_test, y_test) = mnist.load_data()

from tensorflow import keras
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D

# Preprocess data
x_train = np.expand_dims(x_train, axis=3)
x_test = np.expand_dims(x_test, axis=3)
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

input_layer = keras.Input(shape=(28, 28, 1))
ConvLayer1 = Conv2D(32, kernel_size=(3,3),activation='relu')(input_layer)
ConvLayer2 = Conv2D(64, (3,3), activation='relu')(ConvLayer1)
D1 = Dropout(0.25)(ConvLayer2)
Flatten_layer = Flatten()(D1)
Dense1 = Dense(128, activation='relu')(Flatten_layer)
D2 = Dropout(0.5)(Dense1)
Dense2 = Dense(10, activation='softmax')(D2)

complete_model = keras.Model(inputs=input_layer, outputs = Dense2)
complete_model.summary()

from tensorflow.keras.utils import plot_model
plot_model(complete_model, to_file='model.png')

# Create batches to feed to the model
# features are our inputs, targets are our labels
# By adding a 'dataset_size parameter, we can use this for both
# training and testing

import random
def pack_batch(features, targets, dataset_size, batch_size):
    x_batch = []
    y_batch = []
    for i in range(batch_size):
        index = random.randint(0, dataset_size-1)
        x_batch.append(features[index])
        y_batch.append(targets[index])
    return np.array(x_batch), np.array(y_batch)

# Test the function output shape with an example
x_batch, y_batch = pack_batch(x_train, y_train, 60000, BATCH_SIZE)
print("x_batch size: %s" %str(len(x_batch)))
print(x_batch.shape)

# Specify optimizer
optimizer = tf.keras.optimizers.Adadelta()

def loss(model, inputs, targets):
    y_ = model(inputs)
    return keras.losses.categorical_crossentropy(targets, y_, from_logits=False, label_smoothing=0)
    
def grad(model, inputs, targets): #Define gradients
  with tf.GradientTape() as tape:
    loss_value = loss(model, inputs, targets)
  return loss_value, tape.gradient(loss_value, model.trainable_variables)

loss(complete_model, x_batch, y_batch)

def validate_accuracy(model, features, targets):
    epoch_validation_accuracy = tf.keras.metrics.CategoricalAccuracy()
    epoch_validation_accuracy.update_state(targets, model(features))
    return epoch_validation_accuracy.result()

train_loss_results = []
train_accuracy_results = []
validation_accuracy = []

start_time = time.time()
epochs = 1500
for epoch in range(epochs):
    epoch_loss_avg = tf.keras.metrics.Mean()
    epoch_accuracy = tf.keras.metrics.CategoricalAccuracy()
    # Training loop - using batches of 32
    x,y = pack_batch(x_train, y_train, 60000, BATCH_SIZE)
    loss_value, grads = grad(complete_model, x, y)
    # print(loss_value)
    if (epoch%100==0):
        print("Running epoch %d, %d epochs left" %(epoch, epochs-epoch))
    optimizer.apply_gradients(zip(grads, complete_model.trainable_variables))
    x_validation, y_validation = pack_batch(x_test, y_test, 10000, 50)
    validation_accuracy.append(validate_accuracy(complete_model,x_validation,y_validation))
    # Track progress
    epoch_loss_avg.update_state(loss_value)  # Add current batch loss
    # Compare predicted label to actual label
    # training=True is needed only if there are layers with different
    # behavior during training versus inference (e.g. Dropout).
    epoch_accuracy.update_state(y, complete_model(x, training=True))

  # End epoch
    train_loss_results.append(epoch_loss_avg.result())
    train_accuracy_results.append(epoch_accuracy.result())

print("Time taken: %d" %(time.time() - start_time))

import matplotlib.pyplot as plt
fig, axes = plt.subplots(3, sharex=True, figsize=(12, 8))
fig.suptitle('Training Metrics')

axes[0].set_ylabel("Loss", fontsize=14)
axes[0].plot(train_loss_results)

axes[1].set_ylabel("Accuracy", fontsize=14)
axes[1].plot(train_accuracy_results)

axes[2].set_ylabel("Validation Accuracy", fontsize=14)
axes[2].set_xlabel("Epoch", fontsize=14)
axes[2].plot(validation_accuracy)

plt.show()

