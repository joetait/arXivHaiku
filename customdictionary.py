#!/usr/bin/python
 
import pickle
 
class UnknownWordException(Exception):
  def __init__(self, value):
   self.word = value
  def __str__(self):
    return repr(self.word)

class CustomDictionary(object):
  def __init__(self):
    try:
      dictionary_file = open("customdictionary", "r")
      self.dictionary = pickle.load(dictionary_file)
      dictionary_file.close()
    except IOError as e:
      debug("Failed to open/read from dictionary file: " + str(e))
      #TODO: How to fail?
      
  def __del__(self):
    try:
      dictionary_file = open("customdictionary", "w")
      pickle.dump(self.dictionary, dictionary_file)
      dictionary_file.close()
    except IOError as e:
      debug("Failed to save to dictionary file: " + str(e))
      
  def get_nsyl(self, word):
    word = word.lower()
    try:
      return self.dictionary[word]
    except KeyError as e:	
      #unknownWordsList += [word]
      raise UnknownWordException(word);

if __name__=="__main__":
  customdictionary = CustomDictionary()
  print customdictionary.get_nsyl("bredon")