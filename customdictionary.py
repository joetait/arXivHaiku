#!/usr/bin/python
import  getopt, sys, pickle, logging

#TODO: deal with unknownwordsbetter

logger = logging.getLogger('mainLogger')
log = logger.debug

class UnknownWordException(Exception):
  def __init__(self, value):
   self.word = value
  def __str__(self):
    return repr(self.word)

class CustomDictionary(object):
  
  def __init__(self):
    object.__init__(self)
    self.__mypickle = pickle #keep a ref for this to use in del, otherwise pickle is deleted too sooon
    log("Initialising customDictionary")
    try:
      dictionary_file = open("customdictionary", "r")
      self.__dictionary = pickle.load(dictionary_file)
      dictionary_file.close()
    except IOError as e:
      print "Failed to open/read from dictionary file: " + str(e) + "\nFatal"
      log("Failed to open/read from dictionary file: " + str(e) + "\nFatal")
      exit(1)
    except EOFError as e:  
      print "Failed to open/read from dictionary file: " + str(e) + "\nFatal"
      log("Failed to open/read from dictionary file: " + str(e) + "\nFatal")
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
      log( "Failed to open/read from ignoredwords/unknownwords file: " + str(e) + "\nInitialising blank")
      self.__unknown_words = []
      self.__ignored_words = []
    except EOFError as e:
      print "Failed to open/read from ignoredwords/unknownwords file: " + str(e) + "\nInitialising blank"      
      log( "Failed to open/read from ignoredwords/unknownwords file: " + str(e) + "\nInitialising blank")
      self.__unknown_words = []
      self.__ignored_words = []
      
  def __del__(self):
    try:
      
      dictionary_file = open("customdictionary", "w")
      self.__mypickle.dump(self.__dictionary, dictionary_file)
      dictionary_file.close()
      
      unknownwords_file = open("unknownwords", "w")
      self.__mypickle.dump(self.__unknown_words, unknownwords_file)
      unknownwords_file.close()
      
      ignored_words_file = open("ignoredwords", "w")
      self.__mypickle.dump(self.__ignored_words, ignored_words_file)
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
      
      #TODO: This is not ideal, shouldn't immediately break, should remove words from unknownwords
      x = raw_input("x to exit, or how many syllables in " + word + "?")
      if x == "x":
	break
      if (x == "" or (not x.isdigit()) or int(x) < 1 or int(x) > 9):
        print "Adding word to ignore list - didn't get a number, or got a stupid number"
        self.__ignored_words += [word]
      else:
        print "Adding to dictionary: " + word + " - " + x
        self.__dictionary[word] = int(x)
        pass
    
    self.__unknown_words = []
    
if __name__=="__main__":
  def setup_custom_logger(name):
    #formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    formatter = logging.Formatter(fmt='%(asctime)s - %(module)s - %(message)s')
    handler = logging.FileHandler("arXivHaiku.log")
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
    
  logger = setup_custom_logger('mainLogger')
  global log
  log = logger.debug
  log("Running customDictionary with __name__==__main__")
  
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