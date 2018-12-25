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
  """
  Neural network language model capable of generating missing word values.

  After a text file has been processed by the preprocessor, it can be loaded into the constructor and then train_model can be called to create weights and store the language model.
  Later, the predict_word function can be called to access the model and predict the next word in a sequence.

  Args:
    clean_text ([String]): List of strings, each of which represents a sequence to be accessed for word embeddings.
  """

  def __init__(self, clean_text):
    K.clear_session()

    # Tokenize and encode the sequences into integers
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(clean_text)
    sequences = tokenizer.texts_to_sequences(clean_text)

    vocab_size = len(tokenizer.word_index) + 1

    # Splits the sequences into the training information and the target results
    sequences = array(sequences)
    train, target = sequences[:, :-1], sequences[:, -1]
    target = to_categorical(target, num_classes=vocab_size)
    seq_length = train.shape[1]

    # Create the model using the word embedding information.
    model = Sequential()
    model.add(Embedding(vocab_size, 50, input_length=seq_length))
    model.add(LSTM(100, return_sequences=True))
    model.add(LSTM(100))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(vocab_size, activation='softmax'))
    self.train = train
    self.target = target
    self.model = model
    self.tokenizer = tokenizer

  def train_model(self, user_id):
    """
    Trains the language model
    
    Calling train_model results in the model being compiled and trained. Results are saved as a model file associated with the owning user's ID
    
    Args:
      user_id (int): ID Number of the user whose data is training the model. This is used to save the file so that it can only be accessed by the owner.
    """

    model = self.model
    train = self.train
    target = self.target
    tokenizer = self.tokenizer

    #Compile model
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
    """
    Attempts to predict the next word in of a query.
    
    Loads the information of a model, including the raw sequences, the model itself, and a tokenizer, and uses that information to generate
    a specified number of words, based on a seed of query_text
    
    Args:
      sequences (String): A string representing the location of a pickle.dump file that stores a serialized list of sequences.
      weights (String): A string representing the location of the requested model
      tokenizer (String): String for the directory of the tokenizer used to create the model
      query_text (String): A string of words submitted by a user to serve as a seed. Attempts to predict the next word.
      words_wanted (int, optional): Defaults to 1. The amount of words wanted. If a sentence is wanted the number will change, otherwise the default is used.
    
    Returns:
      String: The next word(s) that best fit the sequence based on the model's weights.
    """

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
