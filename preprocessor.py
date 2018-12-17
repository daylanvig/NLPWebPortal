from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import sys
import os
import io
from NLPWebPortal import app, db
from NLPWebPortal.model import User, TrainingFile, Dictionary
from NLPWebPortal.neuralNetwork import LanguageModel
import json
import pickle


def clean_file(text):
  """Performs preprocessing on text so that it can be more readily used for Natural Language Processing Tasks
        
        Args:
                text (String): String of words
        
        Returns:
                [String]: List of cleaned words ready for NLP use
        """

  text = text.lower()

  tokens = word_tokenize(text)

  # Build a dictionary
  # TODO: Eval if should be before stemming
  for word in tokens:
    wordDB = False
    wordDB = db.session.query(Dictionary).filter(
        Dictionary.word == word).first()
    if (wordDB):
      wordDB.increment()
    else:
      wordDB = Dictionary(word)
      db.session.add(wordDB)

  # Stemming
  ps = WordNetLemmatizer()
  stem_words = []
  for word in tokens:
    if (word.isalpha()):  #Remove punctuation
      stem_words.append(ps.lemmatize(word))

  # Commit changes
  db.session.commit()
  return stem_words


def merge_files(user_id):

  if (user_id != 'shared'):
    files_owned = db.session.query(TrainingFile).filter(
        TrainingFile.user_id == user_id).all()
  else:
    files_owned = db.session.query(TrainingFile).all()

  complete_file = []

  for f in files_owned:  #For every file owned by the user, open the pickle(.data) file and extend to one list

    input_file = os.path.join(app.config['MODEL_DIR'],
                              str(f.get_id()) + '.data')

    with open(input_file, 'rb') as file_handle:
      words = pickle.load(file_handle)

    complete_file.extend(words)

  output_file = os.path.join(app.config['MODEL_DIR'],
                             "user-" + str(user_id) + '.data')

  with open(output_file, 'wb') as completeOut:
    pickle.dump(complete_file, completeOut)


def train_model(user_id):

  # Open the complete files
  input_file = os.path.join(app.config['MODEL_DIR'],
                            "user-" + str(user_id) + '.data')

  #If the input file doesnt exist
  try:
    with open(input_file, 'rb') as file_in_train:
      dumped_words = pickle.load(file_in_train)
      lm = LanguageModel(dumped_words)
      lm.train_language_model(user_id)
  except:
    # TODO: Error handling/create file
    print(0)


def check_files():
  """
  [summary]
  
  [description]
  
  Returns:
    [type]: [description]
  """

  # load complete processed file database
  shared_file = os.path.join(app.config['MODEL_DIR'], 'shared.data')

  try:
    with open(shared_file, 'rb') as file_handle:
      complete_content = pickle.load(file_handle)
  except:
    complete_content = []

  # Check new
  training_files = db.session.query(TrainingFile).all()
  users_added = []

  # Iterate through the unprocessed files
  for i in training_files:
    file_name = i.name()
    users_added.append(i.user_id)

    # TODO: Fix encoding issues using openFile method
    try:
      file_contents = open(
          os.path.join(app.config['UPLOAD_DIR'], file_name),
          'rt',
          encoding='utf-8')
    except:
      file_contents = open(
          os.path.join(app.config['UPLOAD_DIR'], file_name), 'rt')

    file_text = file_contents.read()  #contents in memory
    file_contents.close()

    stemmed = clean_file(file_text)
    complete_content.extend(stemmed)
    outName = os.path.join(app.config['MODEL_DIR'], str(i.get_id()) + '.data')

    # * Save stemmed words to disk so don't have to keep cleaning
    with open(outName, 'wb') as file_handle:
      pickle.dump(stemmed, file_handle)

    # * Update DB
    i.processed = True

  db.session.commit()
  users_added.append('shared')
  # Any users who added files should have the contents merged and models retrained
  users_added = list(set(users_added))

  for u in users_added:
    merge_files(u)
    train_model(u)

  # shared file write
  with open(shared_file, 'wb') as file_full_handle:
    pickle.dump(complete_content, file_full_handle)

  return users_added


def generate_weights():
  """
  Interface function that calls the functions necessary to clean files and generate weights for the neural network.

  """

  users_added = check_files()

  for user_id in users_added:
    # Open the complete files
    input_file = os.path.join(app.config['MODEL_DIR'],
                              "user-" + str(user_id) + '.data')
    with open(input_file, 'rb') as fh:
      content = pickle.load(fh)
    string_content = " ".join(str(e) for e in content)
    try:
      lm = LanguageModel(string_content)
      lm.train_language_model("char" + str(user_id))
      output_file = os.path.join(app.config['MODEL_DIR'],
                                 "user-char" + str(user_id) + '.data')
      with open(output_file, 'wb') as fh:
        pickle.dump(string_content, fh)
    except:
      print('No new files')


generate_weights()
