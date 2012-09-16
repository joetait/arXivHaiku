#!/usr/bin/python
import pickle, getopt, sys

#TODO: deal with unknownwordsbetter

class UnknownWordException(Exception):
  def __init__(self, value):
   self.word = value
  def __str__(self):
    return repr(self.word)

class CustomDictionary(object):
  def __init__(self):
    object.__init__(self)
    try:
      dictionary_file = open("customdictionary", "r")
      self.__dictionary = pickle.load(dictionary_file)
      dictionary_file.close()
    except IOError as e:
      print "Failed to open/read from dictionary file: " + str(e) + "\nFatal"
      exit(1)
    except EOFError as e:  
      print "Failed to open/read from dictionary file: " + str(e) + "\nFatal"
      exit(1)
    try:  
      ignored_words_file = open("ignoredwords", "r")
      self.__ignored_words = pickle.load(ignored_words_file)
      ignored_words_file.close()
      
      unknownwords_file = open("unknownwords", "r")
      self.__unknown_words = pickle.load(unknownwords_file)
      unknownwords_file.close()
    except IOError as e:
      print "Failed to open/read from ignoredwords/unknownwords file: " + str(e) + "\nInitialising blank"
      self.__unknown_words = []
      self.__ignored_words = []
    except EOFError as e:
      print "Failed to open/read from ignoredwords/unknownwords file: " + str(e) + "\nInitialising blank"      
      self.__unknown_words = []
      self.__ignored_words = []
      
  def __del__(self):
    try:
      dictionary_file = open("customdictionary", "w")
      pickle.dump(self.__dictionary, dictionary_file)
      dictionary_file.close()
      
      unknownwords_file = open("unknownwords", "w")
      pickle.dump(self.__unknown_words, unknownwords_file)
      unknownwords_file.close()
      
      ignored_words_file = open("ignoredwords", "w")
      pickle.dump(self.__ignored_words, ignored_words_file)
      ignored_words_file.close()
    except IOError as e:
      debug("Failed to save to dictionary file: " + str(e))
      
  def get_nsyl(self, word):
    word = word.lower()
    try:
      return self.__dictionary[word]
    except KeyError as e:
      if word not in self.__ignored_words and word not in self.__unknown_words:
        self.__unknown_words += [word]
      raise UnknownWordException(word);

  def sort_out_unknown_words(self):
    print "Sorting unknown words!"
    print self.__unknown_words
    for word in self.__unknown_words:
      if word in self.__ignored_words or word in self.__dictionary:
        print "Word in ignored_words or dictionary, this shouldn't happen."
      
      x = raw_input("How many syllables in " + word + "?")
      if (x == "" or (not x.isdigit()) or int(x) < 1 or int(x) > 9):
        print "Adding word to ignore list - didn't get a number, or got a stupid number"
        self.__ignored_words += [word]
      else:
        print "Adding to dictionary: " + word + " - " + x
        self.__dictionary[word] = int(x)
        pass
    
    self.__unknown_words = []
    
if __name__=="__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:], ":tp", [])
  except getopt.GetoptError, err:
    print str(err) # will print something like "option -a not recognized"
    sys.exit(2)
  input_file = None
  for o, a in opts:
    if o == "-p":
      CustomDictionary().sort_out_unknown_words()
      exit(0)
    elif o == "-t":    
      customdictionary = CustomDictionary()
      try:
	print customdictionary.get_nsyl("bredon")
	print customdictionary.get_nsyl("bredons")
      except UnknownWordException as e:
	print "Unknown Word: " + str(e)
      exit(0)
    else:
      print "Unhandled Option\n"
      sys.exit(2)
  if not input_file:
    print "No input file set, use --input option."
    sys.exit(2)