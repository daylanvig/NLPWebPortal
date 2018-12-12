import pickle
from neuralNetwork import LanguageModel

lm = LanguageModel('clean-3.data')
print(lm.predict_word("Where is Elbert Huntington, which "))
