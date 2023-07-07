import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Embedding
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from keras.callbacks import ModelCheckpoint
from keras.optimizers import Adam
from matplotlib import pyplot as plt
from keras.models import load_model


def plot_graphs(history, string):
    plt.plot(history.history[string])
    plt.xlabel("Epochs")
    plt.ylabel(string)
    plt.show()


# Read the input file
with open('dataset.txt', 'r') as file:
    text = file.readlines()

# Preprocess the text
tokenizer = Tokenizer(filters=',.\n')
tokenizer.fit_on_texts([text])
sequences = tokenizer.texts_to_sequences([text])[0]
vocab_size = len(tokenizer.word_index) + 1
word_to_index = tokenizer.word_index

# Create input-output pairs for training
input_sequences = []
output_words = []
for i in range(1, len(sequences)):
    input_sequences.append(sequences[:i])
    output_words.append(sequences[i])

# Pad sequences for consistent input length
max_sequence_len = max([len(seq) for seq in input_sequences])
input_sequences = pad_sequences(input_sequences, maxlen=max_sequence_len)

# Convert the output to one-hot encoding
output_words = tf.keras.utils.to_categorical(output_words, num_classes=vocab_size)

# Create the LSTM model
model = Sequential()
model.add(Embedding(vocab_size, 50, input_length=max_sequence_len))
model.add(LSTM(128))
model.add(Dense(1000, activation="tanh"))
model.add(Dense(vocab_size, activation='softmax'))

checkpoint = ModelCheckpoint("next_words.h5", monitor='loss', verbose=1, save_best_only=True)
model.compile(loss="categorical_crossentropy", optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])
# Train the model
history = model.fit(input_sequences, output_words, epochs=350, batch_size=64, callbacks=[checkpoint])

# Plot accuracy
plot_graphs(history, 'accuracy')

# Plot loss
plot_graphs(history, 'loss')

# Load model
model = load_model('model.h5')
while True:
    # Take user input
    user_input = input("Enter the starting letters (or 'q' to quit): ")

    if user_input.lower() == 'q':
        break

    # Generate predictions based on user input
    input_sequence = [word_to_index[word] for word in user_input.split() if word in word_to_index]
    input_sequence = pad_sequences([input_sequence], maxlen=max_sequence_len)

    predictions = model.predict(input_sequence)[0]
    predicted_indices = np.argsort(predictions)[::-1]  # Sort predictions in descending order

    # Print the predicted words
    print("Predicted words:")
    for index in predicted_indices:
        for word, idx in word_to_index.items():
            if idx == index and word.startswith(user_input):
                print(word)
