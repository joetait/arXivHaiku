#!/usr/bin/python
#If __name__=="__main__" then we will define the logger

import logging, StringIO, re, pprint, getopt, sys
from lxml import etree
from lxml.builder import E

pp = pprint.PrettyPrinter(indent=2)

class UnknownWordException(Exception):
  def __init__(self, value, conforms_to_xml_requirements):
   self.word = value
   self.conforms_to_xml_requirements = conforms_to_xml_requirements
  def __str__(self):
    return repr(self.word)

if __name__!="__main__":
  global logger
  logger = logging.getLogger('mainLogger')

class CustomDictionary(object):
  __custom_dictionary_file = "schematest.xml"
  __root = None
  
  __known_words = None
  __ignored_words = None
  __unknown_words = None
  
  __xml_schema_word_regex = re.compile(r"^[a-z0-9]+$")
  
  def __init__(self):    
    #--------------------
    #  Import and check against schema
    #--------------------
    schema_root = StringIO.StringIO(open("customdictionary-schema.xsd").read())
    schema = etree.XMLSchema(etree.parse(schema_root))
    try:
      parser = etree.XMLParser(schema = schema, remove_blank_text=True)
      self.__root = etree.parse(StringIO.StringIO( open(self.__custom_dictionary_file, "r").read()),parser).getroot()
    except etree.XMLSyntaxError as e:
      logger.critical("Failed to parse customdictionary: " + str(e))
      exit(1)  
      
    def parse(element):
      d=[]
      d.append((element.tag, element.text or map(parse, element.getchildren()) or {}))
      return d
    try:
      self.__known_words = self.__root.find("knownwords").find("entries").getchildren()
      self.__known_words = dict([(entry.find("word").text, int(entry.find("syllables").text)) for entry in self.__known_words])
      self.__ignored_words = self.__root.find("ignoredwords").find("entries").getchildren()
      self.__ignored_words = dict([(entry.find("word").text, int(entry.find("count").text)) for entry in self.__ignored_words])
      self.__unknown_words = self.__root.find("unknownwords").find("entries").getchildren()
      self.__unknown_words = dict([(entry.find("word").text, int(entry.find("count").text)) for entry in self.__unknown_words])
    except AttributeError as e:
      logger.critical("Failed to parse customdictionary: " + str(e) )
       
    #--------------------
    #  Check that the same word doesn't appear in >1 list
    #--------------------
    intersection = set(self.__known_words.keys()).intersection(set(self.__unknown_words.keys()))
    if intersection:
      logger.critical("Words appear in both \"known words\" and \"unknown words\": " + str(intersection))
    
    intersection = set(self.__unknown_words.keys()).intersection(set(self.__ignored_words.keys()))
    if intersection:
      logger.critical("Words appear in both \"unknown words\" and \"ignored words\": " + str(intersection))
    
    intersection = set(self.__ignored_words.keys()).intersection(set(self.__known_words.keys()))
    if intersection:
      logger.critical("Words appear in both \"ignored words\" and \"known words\": " + str(intersection))
 
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
          
    print self.__unknown_words.items()
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

if __name__=="__main__":
  import arxivhaikulogger
  logger = arxivhaikulogger.setup_custom_logger('mainLogger')  #No need for global here - already at global scope
  logger.info("Running customDictionary (new testing one) with __name__==__main__")
  
  try:
    opts, args = getopt.getopt(sys.argv[1:],":pt", [])
  except getopt.GetoptError, err:
    print str(err) # will print something like "option -a not recognized"
    logger.critical("Caught getopt.GetoptError")
    sys.exit(2)
  input_xml = None
  for o, a in opts:
    if o == "-p":
      custom_dictionary = CustomDictionary()
      custom_dictionary.prompt_user_for_new_words()    
      custom_dictionary.save_dict()
    elif o == "-t":
      #Testing code
      logger.info("Running a test with custom dictionary")
      custom_dictionary = CustomDictionary()
      try:
	custom_dictionary.get_nsyl("snowdens")
      except UnknownWordException as e:
	print "Unknown word!"
      custom_dictionary.save_dict()
    else:
      print "Unhandled Option\n"
      logger.critical("Unhandled Option")
      sys.exit(2)
  