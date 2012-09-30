#!/usr/bin/python
#If __name__=="__main__" then we will define the logger

import logging, xml.dom.minidom

class UnknownWordException(Exception):
  def __init__(self, value):
   self.word = value
  def __str__(self):
    return repr(self.word)

if __name__!="__main__":
  global logger
  logger = logging.getLogger('mainLogger')

class CustomDictionary(object):
  __custom_dictionary_file = "test-customdictionary"
  __custom_dictionary_dom = None
  
  __unknown_words_dom = None
  
  __known_words = {}
  __ignored_words = []
  __unknown_words = []
  
  def __init__(self):
    try:
      self.__custom_dictionary_dom = xml.dom.minidom.parse(self.__custom_dictionary_file)
    except IOError as e:
      logger.critical("Failed to open custom dictionary file.")
      exit(2)    
    try:
      main_dom = self.__custom_dictionary_dom.getElementsByTagName("customdictionary")[0]
      self.__unknown_words_dom = main_dom.getElementsByTagName("unknownwords")[0].getElementsByTagName("entries")[0]
      for entry in main_dom.getElementsByTagName("knownwords")[0].getElementsByTagName("entries")[0].getElementsByTagName("entry"):
	#TODO handle encoding errors?
	word = str(entry.getElementsByTagName("word")[0].firstChild.nodeValue.encode("utf-8").lower())
	syllables = int(entry.getElementsByTagName("syllables")[0].firstChild.nodeValue)
	self.__known_words[word] = syllables
	
      for entry in main_dom.getElementsByTagName("ignoredwords")[0].getElementsByTagName("entries")[0].getElementsByTagName("entry"):
	#TODO handle encoding errors?
	word = str(entry.firstChild.nodeValue.encode("utf-8").lower())
	self.__ignored_words.append(word)
	
      for entry in main_dom.getElementsByTagName("unknownwords")[0].getElementsByTagName("entries")[0].getElementsByTagName("entry"):
	#TODO handle encoding errors?
	word = str(entry.firstChild.nodeValue.encode("utf-8").lower())
	self.__unknown_words.append(word)
	
    except IndexError as e:
      logger.critical("Failed to parse something.")
      
    print self.__known_words
    print self.__ignored_words
    print self.__unknown_words
    
  def __del__(self):
    self.__custom_dictionary_dom.writexml(open(self.__custom_dictionary_file, "w"))

  def get_nsyl(self, word):
    word = word.lower()
    try:
      return self.__known_words[word]
    except KeyError as e:
      if word not in self.__ignored_words and word not in self.__unknown_words:
        self.__unknown_words += [word]
        new_dom_element = self.__custom_dictionary_dom.createElement("entry") #.appendChild(self.__custom_dictionary_dom.createTextNode(word))
        self.__unknown_words_dom.appendChild(new_dom_element)
        new_dom_element.appendChild(self.__custom_dictionary_dom.createTextNode(word))
      raise UnknownWordException(word);
    
if __name__=="__main__":
  import arxivhaikulogger
  logger = arxivhaikulogger.setup_custom_logger('mainLogger')  #No need for global here - already at global scope
  logger.info("Running customDictionary (new testing one) with __name__==__main__")
  
  custom_dictionary = CustomDictionary()
  try:
    custom_dictionary.get_nsyl("homology")
  except UnknownWordException as e:
    print "Unknown word!"
  custom_dictionary.__del__()