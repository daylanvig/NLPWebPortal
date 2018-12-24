import os
import string
from numpy import array
from pickle import dump, load
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM, Embedding
from keras import backend as K
from nltk.tokenize import word_tokenize
from . import app


class LanguageModel():

  def __init__(self, clean_text):
    K.clear_session()

    # integer encoding
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(clean_text)
    sequences = tokenizer.texts_to_sequences(clean_text)
    # vocabulary size
    vocab_size = len(tokenizer.word_index) + 1

    # separate into input and output
    sequences = array(sequences)
    train, target = sequences[:, :-1], sequences[:, -1]
    target = to_categorical(target, num_classes=vocab_size)
    seq_length = train.shape[1]

    # define model
    model = Sequential()
    model.add(Embedding(vocab_size, 50, input_length=seq_length))
    model.add(LSTM(100, return_sequences=True))
    model.add(LSTM(100))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(vocab_size, activation='softmax'))
    print(model.summary())
    self.train = train
    self.target = target
    self.model = model
    self.tokenizer = tokenizer

  def train_model(self, user_id):
    model = self.model
    train = self.train
    target = self.target
    tokenizer = self.tokenizer
    model.compile(
        loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    filepath = os.path.join(app.config['MODEL_DIR'],
                            'weights-' + str(user_id) + '.h5')
    # Run, save
    model.fit(train, target, batch_size=128, epochs=20)
    model.save(filepath)

    # Save tokenizer
    tokenizer_file = os.path.join(app.config['MODEL_DIR'],
                                  'token-' + str(user_id) + '.pk1')
    dump(tokenizer, open(tokenizer_file, 'wb'))

  def predict_word(sequences, weights, tokenizer, query_text, words_wanted=1):

    with open(sequences, 'rb') as handle:
      sequence_list = load(handle)
    seq_len = len(sequence_list[0].split()) - 1
    model = load_model(weights)

    with open(tokenizer, 'rb') as handle:
      tokenizer = load(handle)

    text = query_text.lower()  # Lowercase to reduce vocab

    tokens = word_tokenize(text)  #Tokenize

    table = str.maketrans('', '', string.punctuation)  #Punctuation removal
    tokens = [w.translate(table) for w in tokens]
    tokens = [word for word in tokens if word.isalpha()]
    seed = ' '.join(tokens)

    output = list()

    for _ in range(words_wanted):  #How many words should be generated
      encoded_text = tokenizer.texts_to_sequences([seed])[0]
      encoded_text = pad_sequences([encoded_text],
                                   maxlen=seq_len,
                                   truncating='pre')
      predict = model.predict_classes(encoded_text, verbose=0)
      out = ''
      for w, i in tokenizer.word_index.items():
        if i == predict:
          out = w
          break
      seed += ' ' + out
      output.append(out)
    result = ' '.join(output)
    K.clear_session()
    return result
