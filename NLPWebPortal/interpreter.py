import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint
from nltk.tokenize import word_tokenize
import sys

file_name = r'C:\ResearchProject\Flask\NLPWebPortal\NLPWebPortal\29763.txt'
file_selected = open(file_name)
text = file_selected.read()
text = text.lower()
file_selected.close()
words = word_tokenize(text)

#mapping, word level
word_map = sorted(list(set(words)))
word_to_n = dict((word, n) for n, word in enumerate(word_map))
n_to_word = dict((n, word) for n, word in enumerate(word_map))


train_array = []
target_array = []
length = len(words)

SEQUENCE_LENGTH = 5 #How long before predicting

for i in range(0, length-SEQUENCE_LENGTH, 1):
    sequence = words[i : i + SEQUENCE_LENGTH]
    label = words[i + SEQUENCE_LENGTH]
    train_array.append([word_to_n[word] for word in sequence])
    target_array.append(word_to_n[label])


train = np.reshape(train_array, (len(train_array), SEQUENCE_LENGTH, 1))
train = train/float(len(word_map))
target = np_utils.to_categorical(target_array)

model = Sequential()
model.add(LSTM(256, input_shape=(train.shape[1], train.shape[2])))
model.add(Dropout(0.2))
model.add(Dense(target.shape[1], activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam')


filepath="weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
callback_list = [checkpoint]

model.fit(train, target, epochs=20, batch_size=128, callbacks=callback_list)

#if predicting input here


def predict():
    weight_file = "weights-improvement-05-5.7929.hdf5"
    model.load_weights(weight_file)
    start = np.random.randint(0, len(train_array)-1)
    pattern = train_array[start]
    print ([n_to_word[value] for value in pattern])

    for i in range(10):
        x = np.reshape(pattern, (1, len(pattern), 1))
        x = x/float(len(word_map))
        prediction = model.predict(x, verbose=0)
        index = np.argmax(prediction)
        result = n_to_word[index]
        seq_in = [n_to_word[value] for value in pattern]
        print(result)
        pattern.append(index)
        pattern = pattern[1:len(pattern)]

#Checkpoints
def modelMake():
    filepath="weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
    checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
    callback_list = [checkpoint]

    model.fit(train, target, epochs=20, batch_size=128, callbacks=callback_list)