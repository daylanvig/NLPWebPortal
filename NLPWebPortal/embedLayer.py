import collections
import os
import pickle
import math
import random
from neuralNetwork import LanguageModel, try_predict
import numpy as np
import tensorflow as tf

dumped_words = 'clean-3.data'

with open(dumped_words, 'rb') as file_handle:
  data_file = pickle.load(file_handle)
data_index = 0

VOCAB_SIZE = 3000

NET_BATCH_SIZE = 128
NET_EMBED_SIZE = 300
NET_WINDOW = 2
NET_N_SKIPS = 2

VALID_SIZE = 16
VALID_WINDOW = 100
VALID_EXAMPLE = np.random.choice(VALID_WINDOW, VALID_SIZE, replace=False)
N_SAMPLED = 64


def create_dataset(words, n_words):

  count = [['UNK', -1]]
  count.extend(collections.Counter(words).most_common(n_words - 1))

  dictionary = dict()
  for w, _ in count:
    dictionary[w] = len(dictionary)

  dictionary_int = list()
  count_unknown = 0

  for w in words:
    if w in dictionary:
      index = dictionary[w]
    else:
      index = 0
      count_unknown += 1
    dictionary_int.append(index)
  count[0][1] = count_unknown
  dictionary_reversed = dict(zip(dictionary.values(), dictionary.keys()))

  return dictionary_int, count, dictionary, dictionary_reversed


def create_batch(dictionary_int, batch_size, n_skips, window):
  global data_index
  assert batch_size % n_skips == 0
  assert n_skips <= 2 * window
  batch = np.ndarray(shape=(batch_size), dtype=np.int32)
  context = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
  span = 2 * window + 1
  buffer = collections.deque(maxlen=span)

  for _ in range(span):
    buffer.append(dictionary_int[data_index])
    data_index = (data_index + 1) % len(dictionary_int)

  for n in range(batch_size // n_skips):
    target = window
    avoid = [window]

  for m in range(n_skips):
    while target in avoid:
      target = random.randint(0, span - 1)
    avoid.append(target)
    batch[n * n_skips + m] = buffer[window]
    context[n * n_skips + m, 0] = buffer[target]

    buffer.append(dictionary_int[data_index])
    data_index = (data_index + 1) % len(dictionary_int)

  data_index = (data_index + len(dictionary_int) - span) % len(dictionary_int)
  return batch, context


dictionary_int, count, dictionary, dictionary_reversed = create_dataset(
    data_file, VOCAB_SIZE)

graph = tf.Graph()
with graph.as_default():
  # * Input data
  train_inputs = tf.placeholder(tf.int32, shape=[NET_BATCH_SIZE])
  train_context = tf.placeholder(tf.int32, shape=[NET_BATCH_SIZE, 1])
  valid_dataset = tf.constant(VALID_EXAMPLE, dtype=tf.int32)

  # * Embedding lookup
  embeddings = tf.Variable(
      tf.random_uniform([VOCAB_SIZE, NET_EMBED_SIZE], -1.0, 1.0))
  embed = tf.nn.embedding_lookup(embeddings, train_inputs)

  # * For softmax
  weights = tf.Variable(
      tf.truncated_normal([VOCAB_SIZE, NET_EMBED_SIZE],
                          stddev=1.0 / math.sqrt(NET_EMBED_SIZE)))
  biases = tf.Variable(tf.zeros([VOCAB_SIZE]))

  loss = tf.reduce_mean(
      tf.nn.nce_loss(
          weights=weights,
          biases=biases,
          labels=train_context,
          inputs=embed,
          num_sampled=N_SAMPLED,
          num_classes=VOCAB_SIZE))

  # * Optimizer
  optimizer = tf.train.GradientDescentOptimizer(1.0).minimize(loss)

  # *
  normal = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
  embeddings_normal = embeddings / normal
  embeddings_valid = tf.nn.embedding_lookup(embeddings_normal, valid_dataset)

  similar = tf.matmul(embeddings_valid, embeddings_normal, transpose_b=True)

  # * init
  init = tf.global_variables_initializer()


def run(graph, n_steps):
  with tf.Session(graph=graph) as session:
    init.run()

    loss_avg = 0

    for n in range(n_steps):
      batch_inputs, batch_context = create_batch(dictionary_int, NET_BATCH_SIZE,
                                                 NET_N_SKIPS, NET_WINDOW)
      dictionary_feed = {
          train_context: batch_inputs,
          train_context: batch_context
      }

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


num_steps = 50000
print(run(graph, num_steps))
