#!/usr/bin/python

#Copyright 2012, Simon St. John-Green, Simon <dot> StJG <at> gmail <dot> com

#This file is part of arXivHaiku.

#arXivHaiku is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#arXivHaiku is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with arXivHaiku.  If not, see <http://www.gnu.org/licenses/>.

def printlicense():
  print """
  customdictionary is part of arXivHaiku  Copyright 2012 Simon StJohn-Green
    This program comes with ABSOLUTELY NO WARRANTY; for details see gpl.txt
    This is free software, and you are welcome to redistribute it
    under certain conditions; see gpl.txt for details.
  """       
        
def usage():
  print """
  Usage: 
  --dictionary-file \t Use custom dictionary file, this option defaults to customdictionary.xml
  --no-dictionary-update \t Don't add new unknown words or increment unknown/ignored words count
  -p \t Prompt user to enter new words into dictionary
  -t \t Run some basic tests
  
  Using -p and -t together is not valid
  """

import logging, StringIO, re, getopt, sys
from lxml import etree
from lxml.builder import E

class UnknownWordException(Exception):
  def __init__(self, value, conforms_to_xml_requirements):
   self.word = value
   self.conforms_to_xml_requirements = conforms_to_xml_requirements
  def __str__(self):
    return repr(self.word) + "\n Conforms to XML requirements: "+repr(self.conforms_to_xml_requirements)

if __name__!="__main__":
  logger = logging.getLogger('mainLogger')

class CustomDictionary(object): 
  __known_words = None
  __ignored_words = None
  __unknown_words = None
  __xml_schema_word_regex = re.compile(r"^[a-z0-9]+$")
  __custom_dictionary_schema_file = "customdictionary-schema.xsd"
  
  #If set to true then counts for unknown/ignored words won't be incremented and new unknown words won't be added
  __no_dictionary_update = False
  
  def __init__(self, custom_dictionary_file="customdictionaryreduced.xml", no_dictionary_update = False):   
    self.__custom_dictionary_file = custom_dictionary_file
    self.__no_dictionary_update = no_dictionary_update
    #--------------------
    #  Import and check against schema
    #--------------------
    try:
      schema_root = StringIO.StringIO(open(self.__custom_dictionary_schema_file).read())
    except IOError as e:
      logger.critical("Failed to open schema file: " + repr(e))
      raise IOError("CustomDictionary - Failed to open schema file: " + repr(e))
    try:  
      schema = etree.XMLSchema(etree.parse(schema_root))
    except etree.XMLSyntaxError as e:
      logger.critical("Failed to parse XML schema: " + repr(e))
      raise IOError("Failed to parse XML schema: " + repr(e))
      
    try:
      parser = etree.XMLParser(schema = schema, remove_blank_text=True)
      root = etree.parse(StringIO.StringIO( open(self.__custom_dictionary_file, "r").read()),parser).getroot()
    except etree.XMLSyntaxError as e:
      logger.critical("Failed to parse customdictionary: " + repr(e))
      raise IOError("Failed to parse customdictionary: " + repr(e))
      
    try:
      self.__known_words = root.find("knownwords").find("entries").getchildren()
      self.__known_words = dict([(entry.find("word").text, int(entry.find("syllables").text)) for entry in self.__known_words])
      self.__ignored_words = root.find("ignoredwords").find("entries").getchildren()
      self.__ignored_words = dict([(entry.find("word").text, int(entry.find("count").text)) for entry in self.__ignored_words])
      self.__unknown_words = root.find("unknownwords").find("entries").getchildren()
      self.__unknown_words = dict([(entry.find("word").text, int(entry.find("count").text)) for entry in self.__unknown_words])
    except AttributeError as e:
      logger.critical("Failed to parse customdictionary: " + repr(e) )
      raise IOError("Failed to parse customdictionary: " + repr(e) )
    #--------------------
    #  Check that the same word doesn't appear in >1 list
    #--------------------
    def check_for_intersection_in_lists(list1, list2, list1name, list2name):
      intersection = set(list1).intersection(set(list2))
      if intersection: logger.critical("Words appear in both \"" + list1name + "\" and \"" + list2name + "\": " + str(intersection))
    
    for (list1,list2,list1name,list2name) in [   \
                                      (self.__known_words.keys(), self.__unknown_words.keys(), "known words", "unknown words"),   \
                                      (self.__unknown_words.keys(), self.__ignored_words.keys(), "unknown words", "ignored words"),   \
                                      (self.__ignored_words.keys(), self.__known_words.keys(), "ignored words", "known words")]:
      check_for_intersection_in_lists(list1,list2,list1name,list2name) 
       
    logger.info("Successfully loaded dictionary files: " + str(len(self.__known_words)) + " elements in known words, " + \
      str(len(self.__unknown_words)) + " elements in unknown words, and " + str(len(self.__ignored_words)) + 
      " elements in ignored words.")
  
  def save_dict(self):
    if self.__no_dictionary_update:
      logger.info("no dictionary update flag set, not saving dictionary")
      return
    knownwords_root = E.knownwords(E.entries( *[E.entry(E.word(word), E.syllables(str(syllables))) \
                                                for (word, syllables) in self.__known_words.items()] ))
    unknownwords_root = E.unknownwords(E.entries( *[E.entry(E.word(word), E.count(str(count))) \
                                                for (word, count) in self.__unknown_words.items()] ))
    ignoredwords_root = E.ignoredwords(E.entries( *[E.entry(E.word(word), E.count(str(count))) \
                                                for (word, count) in self.__ignored_words.items()] )) 
    try:
      open(self.__custom_dictionary_file, "w").write(etree.tostring(E.customdictionary( \
				  knownwords_root,unknownwords_root,ignoredwords_root), pretty_print=True))
    except IOError as e:
      logger.critical("Failed to save customdictionary to file: " + str(e))
      
    logger.info("Successfully saved customdictionary to file")
    
  def get_nsyl(self, word):
    word = word.lower().strip()
    
    #Check conforms to XML dict requirements
    if not self.__xml_schema_word_regex.match(word):
      logger.info("get_nsyl caught word that doesn't match xml requirements: " + word)
      raise UnknownWordException(value=word, conforms_to_xml_requirements=False)
    
    try:
      return self.__known_words[word]
    except KeyError as e:
      if word in self.__ignored_words:
	logger.debug("get_nsyl caught word already in ignored words: " + word)
	self.__ignored_words[word] += 1
      elif word in self.__unknown_words:
        logger.debug("get_nsyl caught word already in unknown words: " + word)
	self.__unknown_words[word] += 1
      else:
        logger.debug("get_nsyl caught new unknown word: " + word)
	self.__unknown_words[word] = 1
      raise UnknownWordException(value=word, conforms_to_xml_requirements=True)
  
  def prompt_user_for_new_words(self):
    unknowns = sorted(self.__unknown_words.items(),key=lambda x:-x[1])
    
    for unknown in unknowns:
      logger.debug("Prompting for " + repr(unknown))
      success_flag = False
      while not success_flag:
	response = raw_input(unknown[0] + " has count " + str(unknown[1]) + " how many syllables?  " + \
	                                  "Type \"p\" for pass (ignore word) and \"q\" to quit: ").strip()
	if response=="q":
	  return
	elif response=="p":
	  self.__ignored_words[unknown[0]] = unknown[1]
	  del self.__unknown_words[unknown[0]]
	  success_flag = True
	elif response.isdigit():
	  if int(response) > 0 and int(response) < 11:
	    self.__known_words[unknown[0]] = int(response)
	    del self.__unknown_words[unknown[0]]
	    success_flag = True
	  else:
	    print "Only numbers between 1 and 10 inclusive are valid."
        
        if not success_flag:print "Unknown input, repeating."
        
if __name__=="__main__":
  printlicense()
  
  import arXivHaikulogger
  logger = arxivhaikulogger.setup_custom_logger('mainLogger')  #No need for global here - already at global scope
  logger.info("Running customDictionary (new testing one) with __name__==__main__")
  
  custom_dictionary_file = False
  no_dictionary_update = False  #If this flag is set, it won't save the dictionary
  mode_prompt = False
  mode_test = False
  
  try:
    opts, args = getopt.getopt(sys.argv[1:],":pt", ["no-dictionary-update", "dictionary-file=", \
                                                 "log-level-critical", "log-level-warning", \
                                                 "log-level-info", "log-level-debug" ])
  except getopt.GetoptError, err:
    print str(err) # will print something like "option -a not recognized"
    usage()
    logger.critical("Caught getopt.GetoptError")
    sys.exit(2)
  input_xml = None
  for o, a in opts:
    if o == "--log-level-critical":
      logger.setLevel(logging.CRITICAL)
    elif o == "--log-level-warning":
      logger.setLevel(logging.WARNING)
    elif o == "--log-level-info":
      logger.setLevel(logging.INFO)
    elif o == "--log-level-debug":
      logger.setLevel(logging.DEBUG)
    elif o == "--no-dictionary-update":
      no_dictionary_update = True
    elif o == "--dictionary-file":
      custom_dictionary_file = a
    elif o == "-p":
      mode_prompt = True
    elif o == "-t":
      mode_test = True
    else:
      print "Unhandled Option.\n"
      usage()
      logger.critical("Unhandled Option")
      sys.exit(2)
 
  if (not mode_prompt and not mode_test) or (mode_prompt and mode_test):
    usage()
    exit(1) 
  
  if mode_test:
    if not custom_dictionary_file:
      logger.warning("No dictionary file set, defaulting to customdictionary.xml")
      print "No dictionary file set, defaulting to customdictionary.xml"
      custom_dictionary_file = "customdictionary.xml"
    #Testing code
    logger.info("Running a test with custom dictionary")
    custom_dictionary = CustomDictionary(custom_dictionary_file=custom_dictionary_file,no_dictionary_update=no_dictionary_update)
    try:
      custom_dictionary.get_nsyl("homomorphism")
    except UnknownWordException as e:
      print "Unknown word!"
    custom_dictionary.save_dict()
    exit(0)

  if mode_prompt:
    try:
      logger.info("Running custom dictionary in prompt_user_for_new_words mode")
      if not custom_dictionary_file:
        logger.warning("No dictionary file set, defaulting to customdictionary.xml")
        print "No dictionary file set, defaulting to customdictionary.xml"
	custom_dictionary_file = "customdictionary.xml"
      custom_dictionary = CustomDictionary(custom_dictionary_file=custom_dictionary_file, no_dictionary_update=no_dictionary_update)
      custom_dictionary.prompt_user_for_new_words()    
      custom_dictionary.save_dict()	

    except KeyboardInterrupt as e:
      logger.critical("Caught KeyboardInterrupt, terminating without saving dictionary: " + repr(e))
      print "Caught KeyboardInterrupt, terminating without saving dictionary: " + repr(e)
