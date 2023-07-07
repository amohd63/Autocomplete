from keras.models import load_model
from flask import Flask, jsonify, request, send_from_directory, redirect, render_template
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from Levenshtein import distance as lev

app = Flask(__name__)

# Read the input file
file = open("dataset.txt", "r", encoding="utf8")

# store file in list
lines = []
for line in file:
    temp_line = line.replace('\n', '').replace('\r', '').replace('\ufeff', '').replace('“', '').replace('”', '')
    lines.append(temp_line)
file.close()

freq_file = open("freq.txt", "r", encoding="utf8")
quest_freq = {}
for line in freq_file:
    temp_line = line.replace('\n', '').replace('\r', '').replace('\ufeff', '').replace('“', '').replace('”', '')
    quest, freq = temp_line.split(',')
    quest_freq[quest] = int(freq)
freq_file.close()

# Preprocess the text
tokenizer = Tokenizer(filters=',.\n')
tokenizer.fit_on_texts([lines])
sequences = tokenizer.texts_to_sequences([lines])[0]

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

model = load_model('model.h5')


def calculate_distances(word, word_list):
    distances = []
    for w in word_list:
        distance = lev(word, w)
        distances.append((w, distance))
    return distances


@app.route('/', methods=['GET'])
def upload_form():
    return render_template('index.html')


@app.route('/script.js')
def script():
    return send_from_directory('static', 'script.js')


@app.route('/favicon.ico')
def favicon():
    return render_template('index.html')


@app.route('/search_char', methods=['POST'])
def search_char():
    term = request.form['q'].strip()
    print('term: ', term)
    filtered_dict = []

    # Generate predictions based on user input
    input_sequence = [word_to_index[word] for word in term.split() if word in word_to_index]
    input_sequence = pad_sequences([input_sequence], maxlen=max_sequence_len)

    predictions = model.predict(input_sequence)[0]
    predicted_indices = np.argsort(predictions)[::-1]  # Sort predictions in descending order

    for index in predicted_indices:
        for word, idx in word_to_index.items():
            if idx == index and word.startswith(term):
                filtered_dict.append(word)

    ranking = [(question, quest_freq[question]) for question in filtered_dict]
    ranking.sort(key=lambda x: x[1], reverse=True)
    distances = calculate_distances(term, filtered_dict)
    distances.sort(key=lambda x: x[1], reverse=False)  # Sort the distances in ascending order
    length = 5 if len(ranking) > 5 else len(ranking)
    filtered_dict = []
    for j in range(length):
        if ranking[j][1] == 1:
            for k in range(len(distances)):
                if distances[k][0] not in filtered_dict:
                    filtered_dict.append(distances[k][0])
                    break
        elif ranking[j][0] not in filtered_dict:
            filtered_dict.append(ranking[j][0])
    print('predicted: ', filtered_dict)
    response = jsonify(filtered_dict)
    response.status_code = 200
    return response


@app.route('/update_freq', methods=['POST'])
def update_freq():
    term = request.form['q'].strip()
    print('term: ', term)
    if quest_freq.get(term) is not None:
        quest_freq[term] = quest_freq.get(term) + 1
        update_file()
    response = jsonify("Updated")
    response.status_code = 200
    return response


def update_file():
    freq_file_inner = open('freq.txt', "w", encoding='utf8')
    for key, value in quest_freq.items():
        freq_file_inner.write(
            key + ',' + str(value) + '\n'
        )
    freq_file_inner.close()


if __name__ == "__main__":
    app.run()
