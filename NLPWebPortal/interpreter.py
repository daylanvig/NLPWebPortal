import os
import sys
from NLPWebPortal import app
from NLPWebPortal.model import db, UserQuery
from NLPWebPortal.neuralNetwork import LanguageModel
from bs4 import BeautifulSoup
import pickle
import random


def interpret_query_load(user_id, private_db, char=""):
  """
  Loader method to configure query settings, called by the word, char, and sentence specific functions


  Args:
  user_id (int/String): Identification number associated with the user's account. Will be an int if the user is logged in
    or otherwise will be None
  private_db (Boolean): Will be True if the user wishes to only use their own files in interpreting the query
  char (str, optional): Defaults to "". Will be 'char' if interpreting a character value to load different weights (character model specific)

  Returns:
  [String], String: A list of words used in the model, the path to the weights
  """

  if (private_db == False):
    file_name = 'shared'
  else:
    file_name = str(user_id)

  words_file_path = os.path.join(app.config['MODEL_DIR'],
                                 'user-' + char + file_name + '.data')
  weight_file_path = os.path.join(app.config['MODEL_DIR'],
                                  'weights.' + char + file_name + '.hdf5')

  with open(words_file_path, 'rb') as fh:
    dumped_words = pickle.load(fh)

  return dumped_words, weight_file_path


def interpret_query_word(user_id, private_db, query_text):
  """
  Configures and calls the language model to predict a word. Called by interpret_query(...).


  Args:
    user_id (int/String): Identification number associated with the user's account. Will be an int if the user is logged in
      or otherwise will be None
    private_db (Boolean): Will be True if the user wishes to only use their own files in interpreting the query
    query_text (String): String of text that comes before the missing word

  Returns:
    String: The missing word as predicted by the model 
  """

  dumped_words, weights = interpret_query_load(user_id, private_db)

  lm = LanguageModel(dumped_words)
  return (lm.predict_word(weights, query_text))


def interpret_query_sentence(user_id, private_db, query_text):
  """
  Configures and calls the language model to predict a sentence. Called by interpret_query(...).

  Creates a sentence based on a random number of words (5-20)

  Args:
    user_id (int/String): Identification number associated with the user's account. Will be an int if the user is logged in
      or otherwise will be None
    private_db (Boolean): Will be True if the user wishes to only use their own files in interpreting the query
    query_text (String): String of text that comes before the missing sentence

  Returns:
    String: The missing sentence as predicted by the model 

  """
  dumped_words, weights = interpret_query_load(user_id, private_db)
  words_wanted = random.randint(5, 20)

  lm = LanguageModel(dumped_words)
  sentence = lm.predict_word(weights, query_text, words_wanted).capitalize()
  return sentence


def interpret_query_character(user_id, private_db, query_text):
  """
  Configures and calls the language model to predict a character. Called by interpret_query(...).


  Args:
    user_id (int/String): Identification number associated with the user's account. Will be an int if the user is logged in
      or otherwise will be None
    private_db (Boolean): Will be True if the user wishes to only use their own files in interpreting the query
    query_text (String): String of text that comes before the missing word

  Returns:
    String: The missing word as predicted by the model 
  """
  dumped_words, weights = interpret_query_load(user_id, private_db, 'char')

  lm = LanguageModel(dumped_words)
  return (lm.predict_word(weights, query_text, 1, True)[0])


def interpret_query(curr_user, query_text, private_check):
  """
  Interprets a fragmented text query to attempt to determine the correct values for missing words, sentences, or characters.

  This function acts as the interface to direct to type specific functions
  
  Args:
    curr_user (int): The ID of the currently logged in user. If no user is logged in, will be 'None'
    query_text (String): A string of text submitted by a user, containing _<*>_ to symbolize missing information
    private_check (Boolean): Will be True if the user requested to use their private database, otherwise will False.
      Must be 'False' if curr_user is 'None'
  
  Returns:
    String: The text with fragments removed / replaced with valid details.
  """
  query_list = ""
  result_list = []

  position = 0
  pause_for = 0
  for c in query_text:
    if pause_for == 0:  # If _< is detected, a pause must be taken to not copy the rest of the expression
      if c == '_':
        if (len(query_text) >=  #error handling
            position + 2) and query_text[position + 1] == '<':
          pause_for = 4
          if query_text[position + 2] == 'C':
            result = interpret_query_character(curr_user, private_check,
                                               query_list)
            query_list += result
            result_list.append(result)
          elif query_text[position + 2] == 'W':
            result = interpret_query_word(curr_user, private_check, query_list)
            query_list += result + " "
            result_list.append(result)
          elif query_text[position + 2] == 'S':
            result = interpret_query_sentence(curr_user, private_check,
                                              query_list)
            query_list += result + ". "
            result_list.append(result)
      else:
        query_list += c
    position += 1
    if pause_for > 0:
      pause_for -= 1

  if (curr_user):
    result_list = ', '.join(result_list)
    db.session.add(UserQuery(query_text, curr_user, private_check, result_list))
    db.session.commit()
  return query_list