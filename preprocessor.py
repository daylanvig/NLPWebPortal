import string
import pickle
import os
import collections
from NLPWebPortal import app, db, TrainingFile, Dictionary, User, LanguageModel
from nltk.tokenize import word_tokenize

model = app.config['MODEL_DIR']
upload = app.config['UPLOAD_DIR']


def load_text(filename):

  file = open(os.path.join(upload, filename), 'r', encoding='utf-8')
  text = file.read()

  file.close()
  return text


def clean_text(text):

  text = text.lower()  # Lowercase to reduce vocab

  tokens = word_tokenize(text)  #Tokenize

  table = str.maketrans('', '', string.punctuation)  #Punctuation removal
  tokens = [w.translate(table) for w in tokens]
  tokens = [word for word in tokens if word.isalpha()]

  # To save querying db many times store in dict
  word_dict = dict()
  for word in tokens:
    if word in word_dict:
      word_dict[word] += 1
    else:
      word_dict[word] = 1

  for word, count in word_dict.items():
    wordDB = db.session.query(Dictionary).filter(
        Dictionary.word == word).first()
    if wordDB:
      wordDB.increment(count)  #If word exists, increment count
    else:
      db.session.add(Dictionary(word, count))  #Else create it
  db.session.commit()

  return tokens


def create_sequences(tokens):

  length = 26
  sequences = list()
  for n in range(length, len(tokens)):
    sequence = tokens[n - length:n]
    line = ' '.join(sequence)
    sequences.append(line)

  return sequences


def merge_sequences(user_id):

  if user_id != 'shared':
    file_list = db.session.query(TrainingFile).filter(
        TrainingFile.user_id == user_id).all()
  else:
    file_list = db.session.query(TrainingFile).all()

  sequence_list = []

  for f in file_list:
    in_file = os.path.join(model, str(f.get_id()) + '.data')  #load file
    with open(in_file, 'rb') as handle:
      sequence = pickle.load(handle)

    sequence_list.extend(sequence)

  #Store complete file

  out_file = os.path.join(model, 'user-' + str(user_id) + '.data')
  with open(out_file, 'wb') as handle:
    pickle.dump(sequence_list, handle)

  return sequence_list


def run():

  # Find new files
  new_files = db.session.query(TrainingFile).filter(
      TrainingFile.processed == False)

  users_added = []

  for f in new_files:
    users_added.append(f.user_id)
    # Load and create tokens
    tokens = clean_text(load_text(f.name()))

    # Convert to sequences
    content = create_sequences(tokens)

    #Save sequences in a dump as '/UPLOAD/<FILE_ID>.data'
    fn = os.path.join(model, str(f.get_id()) + '.data')
    with open(fn, 'wb') as handle:
      pickle.dump(content, handle)

    #Mark as processed to stop repeats
    #f.processed = True
    db.session.commit()

  if users_added:
    users_added.append('shared')
    users_added = list(set(users_added))
    for u in users_added:
      #Any user who has added a file, merge
      clean_sequence = merge_sequences(u)
      # Train model
      lm = LanguageModel(clean_sequence)
      lm.train_model(u)

  else:
    print('No new files')


if __name__ == "__main__":
  run()