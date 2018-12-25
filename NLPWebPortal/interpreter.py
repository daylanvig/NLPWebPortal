import os
import sys
from . import db, app, UserQuery, os, sys, LanguageModel, Dictionary
from bs4 import BeautifulSoup
import pickle
import random


def interpret_query_load(user_id, private_db):
  """
  Loader method to configure query settings, called by the word, char, and sentence specific functions


  Args:
  user_id (int/String): Identification number associated with the user's account. Will be an int if the user is logged in
    or otherwise will be None
  private_db (Boolean): Will be True if the user wishes to only use their own files in interpreting the query

  Returns:
  [String], String: A list of words used in the model, the path to the weights
  """

  if (private_db == False):
    file_name = 'shared'
  else:
    file_name = str(user_id)

  words_file_path = os.path.join(app.config['MODEL_DIR'],
                                 'user-' + file_name + '.data')
  weight_file_path = os.path.join(app.config['MODEL_DIR'],
                                  'weights-' + file_name + '.h5')
  tokenizer_file_path = os.path.join(app.config['MODEL_DIR'],
                                     'token-' + file_name + '.pk1')

  return words_file_path, weight_file_path, tokenizer_file_path


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

  words, weights, tokens = interpret_query_load(user_id, private_db)
  return LanguageModel.predict_word(words, weights, tokens, query_text)


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
  words_wanted = random.randint(5, 20)

  words, weights, tokens = interpret_query_load(user_id, private_db)
  sentence = LanguageModel.predict_word(words, weights, tokens, query_text,
                                        words_wanted)
  sentence = sentence.capitalize()
  return sentence


def interpret_query_character(user_id, private_db, query_text, partial_word):
  """
  Configures and calls the language model to predict a character. Called by interpret_query(...).


  Args:
    user_id (int/String): Identification number associated with the user's account. Will be an int if the user is logged in
      or otherwise will be None
    private_db (Boolean): Will be True if the user wishes to only use their own files in interpreting the query
    query_text (String): String of text that comes before the missing word
    parital_word (String): The fragmented word in full.

  Returns:
    String: The missing word as predicted by the model. Will fill with unknown otherwise.
  """
  partial_word = partial_word.lower()
  possible = db.session.query(Dictionary).filter(
      Dictionary.word.ilike(partial_word)).all()
  if possible:
    max = possible[0].count
    best = possible[0].word
    for i in range(len(possible)):
      if possible[i].count >= max:  #Return the most common match
        best = possible[i].word
        max = possible[i].count
    return best
  else:
    return partial_word.replace('_', '<UNK>')


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
  query_text = query_text.split()

  for c in query_text:
    if c == '_<W>_':  #Missing word
      result = interpret_query_word(curr_user, private_check, query_list)
      query_list += result + " "
      result_list.append(result)
    elif c == '_<S>_':  #Missing sentence
      result = interpret_query_sentence(curr_user, private_check, query_list)
      query_list += result + ". "
      result_list.append(result)
    elif '_<C>_' in c:  #Missing character(s)
      partial_word = c.replace('_<C>_', '_')
      result = interpret_query_character(curr_user, private_check, query_list,
                                         partial_word)
      query_list += result + " "
      result_list.append(result)
    else:
      query_list += c + " "

  if (curr_user):
    # If there's a current user the results should be stored for history
    result_list = ', '.join(result_list)
    db.session.add(UserQuery(query_text, curr_user, private_check, result_list))
    db.session.commit()
  return query_list