import collections
import math
import os
import pickle
import random
import sys

import numpy as np
import tensorflow as tf
from keras.callbacks import ModelCheckpoint
from keras.layers import LSTM, Dense, Dropout, Embedding, Flatten
from keras.models import Sequential
from keras.utils import np_utils
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

data_index = 0

NET_BATCH_SIZE = 128
NET_EMBED_SIZE = 128
NET_WINDOW = 1
NET_N_SKIPS = 2

VALID_SIZE = 16
VALID_WINDOW = 100
VALID_EXAMPLE = np.random.choice(VALID_WINDOW, VALID_SIZE, replace=False)
N_SAMPLED = 64


class WordVecEmbed():

  def __init__(self, words, n_steps=50000):
    self.word_embeddings = WordVecEmbed.get_embed(words, n_steps)

  def create_dataset(words):
    """
    Encodes the dataset into dictionaries
    
    Converts a list of words into a dictionary containing words based on how common
    they are
    
    Args:
      words ([String]): List containing word tokens / strings
    """

    global VOCAB_SIZE
    global dictionary
    global dictionary_int
    global count
    global dictionary_reversed

    VOCAB_SIZE = len(set(words))

    count = [['UNK', -1]]
    count.extend(collections.Counter(words).most_common(VOCAB_SIZE - 1))

    dictionary = dict()
    for w, _ in count:
      dictionary[w] = len(dictionary)

    dictionary_int = list()
    count_unknown = 0

    for w in words:
      index = dictionary.get(w, 0)
      if index == 0:
        count_unknown += 1
      dictionary_int.append(index)
    count[0][1] = count_unknown
    dictionary_reversed = dict(zip(dictionary.values(), dictionary.keys()))

  def create_batch(batch_size, n_skips, window):
    global data_index
    global dictionary_int

    assert batch_size % n_skips == 0
    assert n_skips <= 2 * window
    batch = np.ndarray(shape=(batch_size), dtype=np.int32)
    context = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    span = 2 * window + 1
    buffer = collections.deque(maxlen=span)

    if data_index + span > len(dictionary_int):
      data_index = 0
    buffer.extend(dictionary_int[data_index:data_index + span])
    data_index += span

    for n in range(batch_size // n_skips):
      window_words = [w for w in range(span) if w != window]
      words_use = random.sample(window_words, n_skips)
      for m, context_word in enumerate(words_use):
        batch[n * n_skips + m] = buffer[window]
        context[n * n_skips + m, 0] = buffer[context_word]
      if data_index == len(dictionary_int):
        buffer.extend(dictionary_int[0:span])
        data_index = span
      else:
        buffer.append(dictionary_int[data_index])
        data_index += 1
    data_index = (data_index + len(dictionary_int) - span) % len(dictionary_int)
    return batch, context

  def create_graph():
    global graph
    global NET_BATCH_SIZE
    global VALID_EXAMPLE
    global VOCAB_SIZE
    global NET_EMBED_SIZE
    global N_SAMPLED
    global embeddings_normal
    global init
    global train_inputs
    global train_context
    global optimizer
    global merged
    global loss
    global similar
    graph = tf.Graph()

    with graph.as_default():
      with tf.name_scope('inputs'):
        # * Input data
        train_inputs = tf.placeholder(tf.int32, shape=[NET_BATCH_SIZE])
        train_context = tf.placeholder(tf.int32, shape=[NET_BATCH_SIZE, 1])
        valid_dataset = tf.constant(VALID_EXAMPLE, dtype=tf.int32)
      with tf.name_scope('embeddings'):
        # * Embedding lookup
        embeddings = tf.Variable(
            tf.random_uniform([VOCAB_SIZE, NET_EMBED_SIZE], -1.0, 1.0))
        embed = tf.nn.embedding_lookup(embeddings, train_inputs)

      with tf.name_scope('weights'):
        weights = tf.Variable(
            tf.truncated_normal([VOCAB_SIZE, NET_EMBED_SIZE],
                                stddev=1.0 / math.sqrt(NET_EMBED_SIZE)))

      with tf.name_scope('biases'):
        biases = tf.Variable(tf.zeros([VOCAB_SIZE]))

      with tf.name_scope('loss'):
        loss = tf.reduce_mean(
            tf.nn.nce_loss(
                weights=weights,
                biases=biases,
                labels=train_context,
                inputs=embed,
                num_sampled=N_SAMPLED,
                num_classes=VOCAB_SIZE))

      tf.summary.scalar('loss', loss)

      with tf.name_scope('optimizer'):
        optimizer = tf.train.GradientDescentOptimizer(1.0).minimize(loss)

      normal = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keepdims=True))
      embeddings_normal = embeddings / normal
      embeddings_valid = tf.nn.embedding_lookup(embeddings_normal,
                                                valid_dataset)

      similar = tf.matmul(embeddings_valid, embeddings_normal, transpose_b=True)

      merged = tf.summary.merge_all()

      # * init
      init = tf.global_variables_initializer()
      saver = tf.train.Saver()

  def train_model(n_steps):
    global dictionary_int
    global NET_BATCH_SIZE
    global NET_N_SKIPS
    global VALID_SIZE
    global NET_WINDOW
    global optimizer
    global merged
    global loss
    global similar
    global dictionary_reversed
    global VALID_EXAMPLE
    global embeddings_normal
    global train_inputs
    global train_context

    with tf.Session(graph=graph) as session:
      init.run()

      loss_avg = 0

      for n in range(n_steps):
        batch, context = WordVecEmbed.create_batch(NET_BATCH_SIZE, NET_N_SKIPS,
                                                   NET_WINDOW)
        dictionary_feed = {train_inputs: batch, train_context: context}
        run_metadata = tf.RunMetadata()

        _, summary, loss_val = session.run([optimizer, merged, loss],
                                           feed_dict=dictionary_feed)
        loss_avg += loss_val

        if n % 2000 == 0:
          if n > 0:
            loss_avg /= 2000
          loss_avg = 2000

        if n % 10000 == 0:
          sim = similar.eval()
          for n in range(VALID_SIZE):
            valid_word = dictionary_reversed[VALID_EXAMPLE[n]]
            top_k = 8
            near_word = (-sim[n, :]).argsort()[1:top_k + 1]
            log_str = 'Nearest to %s:' % valid_word
            for k in range(top_k):
              close_word = dictionary_reversed[near_word[k]]
              log_str = '%s %s,' % (log_str, close_word)
            print(log_str)
      final_embed = embeddings_normal.eval()
    return final_embed

  def get_embed(words, n_steps):
    WordVecEmbed.create_dataset(words)
    WordVecEmbed.create_graph()
    embed = WordVecEmbed.train_model(n_steps)
    return embed


class LanguageModel():
  """
        Neural network language model capable of generating text.
         
        Args:
             dumped_words (String): Name of pickle data file holding the cleaned file contents
        """

  def __init__(self, dumped_words):
    with open(dumped_words, 'rb') as file_handle:
      words = pickle.load(file_handle)
    wv = WordVecEmbed(words)
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

  def try_predict(prediction):
    x = prediction[0]
    rnd_index = np.random.choice(len(x), p=x)
    return rnd_index

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
      index = LanguageModel.try_predict(prediction)
      output = output + self.n_to_word[index] + " "
      pattern.append(index)
      pattern = pattern[1:len(pattern)]

    return output


lm = LanguageModel('clean-3.data')
