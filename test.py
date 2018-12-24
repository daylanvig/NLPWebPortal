import sys
import os
import pickle
from NLPWebPortal import app

fn = os.path.join(app.config['MODEL_DIR'], 'user-1.data')
with open(fn, 'rb') as handle:
  text = pickle.load(handle)

s = text[0].split()
print(len(s) - 1)
