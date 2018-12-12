import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint
import sys
import os
import pickle
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


def try_predict(prediction):
  x = prediction[0]
  rnd_index = np.random.choice(len(x), p=x)
  return rnd_index


class LanguageModel():
  """
        Neural network language model capable of generating text.
         
        Args:
             dumped_words (String): Name of pickle data file holding the cleaned file contents
        """

  def __init__(self, dumped_words):

    with open(dumped_words, 'rb') as file_handle:
      words = pickle.load(file_handle)

    self.word_map = sorted(list(set(words)))
    self.word_to_n = dict((word, n) for n, word in enumerate(self.word_map))
    self.n_to_word = dict((n, word) for n, word in enumerate(self.word_map))

    self.train_array = []
    self.target_array = []
    self.length = len(words)
    self.SEQUENCE_LENGTH = 10

    for i in range(0, self.length - self.SEQUENCE_LENGTH, 1):
      sequence = words[i:i + self.SEQUENCE_LENGTH]
      label = words[i + self.SEQUENCE_LENGTH]
      self.train_array.append([self.word_to_n[word] for word in sequence])
      self.target_array.append(self.word_to_n[label])

    self.train = np.reshape(self.train_array,
                            (len(self.train_array), self.SEQUENCE_LENGTH, 1))
    self.train = self.train / float(len(self.word_map))
    self.target = np_utils.to_categorical(self.target_array)

    self.model = Sequential()
    self.model.add(
        LSTM(
            256,
            input_shape=(self.train.shape[1], self.train.shape[2]),
            return_sequences=True))
    self.model.add(Dropout(0.2))
    self.model.add(LSTM(256))
    self.model.add(Dropout(0.2))
    self.model.add(Dense(self.target.shape[1], activation='softmax'))

  def train_model(self):
    """
                Iterates through the training process to build a language model.
                The best file is saved and the other epochs are destroyed.
                """
    self.model.compile(loss='categorical_crossentropy', optimizer='adam')
    filepath = "weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
    checkpoint = ModelCheckpoint(
        filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
    callback_list = [checkpoint]
    self.model.fit(
        self.train,
        self.target,
        epochs=50,
        batch_size=64,
        callbacks=callback_list)

  def predict_word(self, query_text, words_wanted=1):
    """
                Using the current model, makes a prediction as to what the next word should be.
                
                Args:
                        query_text (String): Accepts a string of text whose next word is missing.
                        words_wanted (int, optional): Defaults to 1. Allows for multiple words to be predicted,
                                should they be required - such as in generating a sentence.

                Returns:
                        String of one or more words that complete the query.
                """

    weight_file = "weights-improvement-02-6.3365.hdf5"  ##TODO: Need to pick

    self.model.load_weights(weight_file)
    self.model.compile(loss='categorical_crossentropy', optimizer='adam')
    output = ""

    query_text = query_text.lower()

    tokens = word_tokenize(query_text)

    # Stemming
    ps = PorterStemmer()
    stem_words = []

    for word in tokens:
      if (word.isalpha()):  #Remove punctuation
        stem_words.append(ps.stem(word))

    query_text = stem_words

    query_int = [self.word_to_n[word] for word in query_text]
    pattern = list(
        np.ones(self.SEQUENCE_LENGTH - len(query_int)).astype(int)) + query_int

    for i in range(words_wanted):
      x = np.reshape(pattern, (1, len(pattern), 1))
      x = x / float(len(self.word_map))
      prediction = self.model.predict(x, verbose=0)
      index = try_predict(prediction)
      output = output + self.n_to_word[index] + " "
      pattern.append(index)
      pattern = pattern[1:len(pattern)]

    return output
