import sys
import os
import pickle
from NLPWebPortal import db, Dictionary

words = db.session.query(Dictionary).filter(Dictionary.word)
