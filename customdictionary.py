#!/usr/bin/python
import pickle
 
class UnknownWordException(Exception):
  def __init__(self, value):
   self.word = value
  def __str__(self):
    return repr(self.word)

class CustomDictionary(object):
  def __init__(self):
    object.__init__(self)
    self.__unknown_words = []
    try:
      dictionary_file = open("customdictionary", "r")
      self.__dictionary = pickle.load(dictionary_file)
      dictionary_file.close()
    except IOError as e:
      debug("Failed to open/read from dictionary file: " + str(e))
      #TODO: How to fail?
      
  def __del__(self):
    try:
      dictionary_file = open("customdictionary", "w")
      pickle.dump(self.__dictionary, dictionary_file)
      dictionary_file.close()
      
      unknownwords_file = open("unknownwords", "w")
      pickle.dump(self.__unknown_words, unknownwords_file)
      unknownwords_file.close()
    except IOError as e:
      debug("Failed to save to dictionary file: " + str(e))
      
  def get_nsyl(self, word):
    word = word.lower()
    try:
      return self.__dictionary[word]
    except KeyError as e:	
      self.__unknown_words += [word]
      raise UnknownWordException(word);

if __name__=="__main__":
  customdictionary = CustomDictionary()
  try:
    print customdictionary.get_nsyl("bredon")
    print customdictionary.get_nsyl("bredons")
  except UnknownWordException as e:
    print "Unknown Word: " + str(e)