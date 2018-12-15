from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import sys
import os
from NLPWebPortal import app
from NLPWebPortal.model import db, User, TrainingFile, Dictionary
from NLPWebPortal.neuralNetwork import LanguageModel
import json
import pickle

##Loads the files for the user based on whether or not they wish to user their private database
##Will return an array of words or characters
##def open_files(userID, private_check):


def clean_file(text):
  """Performs preprocessing on text so that it can be more readily used for Natural Language Processing Tasks
        
        Args:
                text (String): String of words
        
        Returns:
                [String]: List of cleaned words ready for NLP use
        """

  text = text.lower()

  tokens = word_tokenize(text)

  # Stemming
  ps = PorterStemmer()
  stem_words = []
  for word in tokens:
    if (word.isalpha()):  #Remove punctuation
      stem_words.append(ps.stem(word))

  # Build a dictionary
  # TODO: Eval if should be before stemming
  for word in stem_words:
    wordDB = False
    wordDB = db.session.query(Dictionary).filter(
        Dictionary.word == word).first()
    if (wordDB):
      wordDB.increment()
    else:
      wordDB = Dictionary(word)
      db.session.add(wordDB)

  # Commit changes
  db.session.commit()
  return stem_words


##Scans the database for any files that haven't been processed and generates weights for them
##Should run periodically, save the best weight file with the same name as the text file it came from
def generate_weights():

    training

    file_text = file_contents.read()  #contents in memory
    file_contents.close()

    stemmed = clean_file(file_text)
    outName = '/fileServer/TrainingFiles/clean-' + str(i.get_id()) + '.data'

    # * Save to disk so don't have to keep cleaning
    with open(outName, 'wb') as fileOut:
      pickle.dump(stemmed, fileOut)

    language_model = LanguageModel(outName)
    language_model.train_model()

    # * Update DB
    i.processed = True

  db.session.commit()
