#!/usr/bin/python

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
  
  def __init__(self, custom_dictionary_file="customdictionary.xml"):   
    self.__custom_dictionary_file = custom_dictionary_file
  
    #--------------------
    #  Import and check against schema
    #--------------------
    try:
      schema_root = StringIO.StringIO(open(self.__custom_dictionary_schema_file).read())
    except IOError as e:
      logger.critical("Failed to open schema file: " + repr(e))
      exit(1)
    try:  
      schema = etree.XMLSchema(etree.parse(schema_root))
    except etree.XMLSyntaxError as e:
      logger.critical("Failed to parse XML schema: " + repr(e))
      exit(1)
      
    try:
      parser = etree.XMLParser(schema = schema, remove_blank_text=True)
      root = etree.parse(StringIO.StringIO( open(self.__custom_dictionary_file, "r").read()),parser).getroot()
    except etree.XMLSyntaxError as e:
      logger.critical("Failed to parse customdictionary: " + repr(e))
      exit(1)  
      
    try:
      self.__known_words = root.find("knownwords").find("entries").getchildren()
      self.__known_words = dict([(entry.find("word").text, int(entry.find("syllables").text)) for entry in self.__known_words])
      self.__ignored_words = root.find("ignoredwords").find("entries").getchildren()
      self.__ignored_words = dict([(entry.find("word").text, int(entry.find("count").text)) for entry in self.__ignored_words])
      self.__unknown_words = root.find("unknownwords").find("entries").getchildren()
      self.__unknown_words = dict([(entry.find("word").text, int(entry.find("count").text)) for entry in self.__unknown_words])
    except AttributeError as e:
      logger.critical("Failed to parse customdictionary: " + repr(e) )
      exit(1)
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
      logger.debug("get_nsyl caught word that doesn't match xml requirements: " + word)
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
      success_flag = False
      while not success_flag:
	response = raw_input("How many syllables in: " + unknown[0] + "?  \"p\" for pass (ignore word) and \"q\" to quit").strip()
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
  import arxivhaikulogger
  logger = arxivhaikulogger.setup_custom_logger('mainLogger')  #No need for global here - already at global scope
  logger.info("Running customDictionary (new testing one) with __name__==__main__")
  
  custom_dictionary_file = False
  
  try:
    opts, args = getopt.getopt(sys.argv[1:],":pt", ["dictionary-file="])
  except getopt.GetoptError, err:
    print str(err) # will print something like "option -a not recognized"
    logger.critical("Caught getopt.GetoptError")
    sys.exit(2)
  input_xml = None
  for o, a in opts:
    if o == "--dictionary-file":
      custom_dictionary_file = a
      
    elif o == "-p":
      try:
	logger.info("Running custom dictionary in prompt_user_for_new_words mode")
	if not custom_dictionary_file:
	  logger.warning("No dictionary file set, defaulting to customdictionary.xml")
	  print "No dictionary file set, defaulting to customdictionary.xml"
	  custom_dictionary_file = "customdictionary.xml"
	custom_dictionary = CustomDictionary(custom_dictionary_file=custom_dictionary_file)
	custom_dictionary.prompt_user_for_new_words()    
        custom_dictionary.save_dict()	

      except KeyboardInterrupt as e:
	logger.critical("Caught KeyboardInterrupt, terminating without saving dictionary: " + repr(e))
	print "Caught KeyboardInterrupt, terminating without saving dictionary: " + repr(e)

      exit(0)
      
    elif o == "-t":
      if not custom_dictionary_file:
	logger.warning("No dictionary file set, defaulting to customdictionary.xml")
        print "No dictionary file set, defaulting to customdictionary.xml"
        custom_dictionary_file = "customdictionary.xml"
      #Testing code
      logger.info("Running a test with custom dictionary")
      custom_dictionary = CustomDictionary(custom_dictionary_file=custom_dictionary_file)
      try:
	custom_dictionary.get_nsyl("snowdens")
      except UnknownWordException as e:
	print "Unknown word!"
      custom_dictionary.save_dict()
      
    else:
      print "Unhandled Option\n"
      logger.critical("Unhandled Option")
      sys.exit(2)
 
  print "You need to pass at least one option, -t to test, -p for prompt for user input.  Use --dictionary-file to specify dictionary file."