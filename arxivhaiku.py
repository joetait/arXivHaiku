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
  arXivHaiku  Copyright 2012 Simon StJohn-Green
    This program comes with ABSOLUTELY NO WARRANTY; for details see gpl.txt
    This is free software, and you are welcome to redistribute it
    under certain conditions; see gpl.txt for details.
  """       
        
def usage():
  print """
  Usage: 
  --no-dictionary-update \t Don't add new unknown words or increment unknown/ignored words count
  --input-xml= \t xml file from the arXiv to pull tex files from, defaults to http://export.arxiv.org/rss/math?mirror=edu
  """

import arxivhaikulogger, logging, getopt,sys, threading, Queue, re, StringIO
from lxml import etree
from lxml.builder import E
from twitter import post_status_to_twitter
from rssparser import rssparse
from findhaiku import find_haiku_in_tex
from gettextwithvi import get_text_with_vi

#This class maintains the list of articles already parsed
class AlreadyParsedList(object): 
  __already_parsed_list = None
  __xml_schema_regex = re.compile(r"^\d{4}\.\d{4}$")
  __schema_file = "alreadyparsedlist-schema.xsd"
  
  #If set to true then list won't be saved
  __no_update = False
  
  def __init__(self, filename="alreadyparsedlist.xml", no_update = False):   
    self.__filename = filename
    self.__no_update = no_update
    #--------------------
    #  Import and check against schema
    #--------------------
    try:
      schema_root = StringIO.StringIO(open(self.__schema_file).read())
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
      root = etree.parse(StringIO.StringIO( open(self.__filename, "r").read()),parser).getroot()
    except etree.XMLSyntaxError as e:
      logger.critical("Failed to parse alreadyparsed list: " + repr(e))
      exit(1)  
      
    try:
      self.__already_parsed_list = root.find("entries").getchildren()
      self.__already_parsed_list = [entry.text for entry in self.__already_parsed_list]
    except AttributeError as e:
      logger.critical("Failed to parse alreadyparsed list: " + repr(e) )
      exit(1)
   
    logger.info("Successfully loaded alreadyparsed list: " + str(len(self.__already_parsed_list)) + " elements in list")
  
  def save_list(self):
    if self.__no_update:
      logger.info("no alreadyparsedlist update flag set, not saving.")
      return
    already_parsed_root = E.entries( *[E.entry(article_id) for article_id in self.__already_parsed_list] )
    try:
      open(self.__filename, "w").write(etree.tostring(E.alreadyparsed( already_parsed_root), pretty_print=True))
    except IOError as e:
      logger.critical("Failed to save alreadyparsedlist to file: " + str(e))
      
    logger.info("Successfully saved alreadyparsedlist to file")
   
  #check for article_id in list - if it doesn't appear add to the list 
  def id_in_list(self, article_id):
    article_id = str(article_id)
    if not self.__xml_schema_regex.match(article_id):
      logger.warning("check_for_id caught id that doesn't match xml requirements: " + article_id)
      return False
    if article_id in self.__already_parsed_list:
      return True
    else:
      self.__already_parsed_list.append(article_id)
      return False

#This thread takes input xml and spits out string files containing the Haiku to be processed
class HaikuFindingThread(threading.Thread):
    def __init__(self, input_xml, no_dictionary_update, results_queue):
      self.input_xml = input_xml
      self.no_dictionary_update = no_dictionary_update
      self.results_queue = results_queue
      self.terminate_request_flag = False
      
      threading.Thread.__init__(self)
      
    def terminate_request(self):
      self.terminate_request_flag = True
      
    def run(self):
      already_parsed_list = AlreadyParsedList()
      for (article_id, raw_tex) in rssparse(input_xml):
	if self.terminate_request_flag:
	  logger.critical("Worker thread caught terminate_request_flag, terminating")
          already_parsed_list.save_list()
	  return
	  
        if already_parsed_list.id_in_list(article_id):
          logger.info("already parsed id: " + article_id)
          continue

	logger.info("Attempting raw tex from article_id: "+ str(article_id))
        haiku_list = []
	try:
	  haiku_list = find_haiku_in_tex(raw_tex, no_dictionary_update=no_dictionary_update)
	except RuntimeError as e:
	  logger.warning("Caught RuntimeError: "+ str(e))
	if len(haiku_list)==0:
	  logger.info("Found no Haiku in article_id: " + str(article_id))
	else:
	  for haiku in haiku_list:
	    self.results_queue.put(haiku + " (" + str(article_id) + ") #arXivHaiku")
	    logger.info("Found haiku in article_id :" + str(article_id) + " : " + haiku)
      already_parsed_list.save_list()  

if __name__=="__main__":  
  printlicense()

  logger = arxivhaikulogger.setup_custom_logger('mainLogger')
  logger.info("Running arXivHaiku with __name__==__main__")
  
  no_dictionary_update = False
  try:
    opts, args = getopt.getopt(sys.argv[1:],"", ["no-dictionary-update", "input-xml=", \
                                                 "log-level-critical", "log-level-warning", \
                                                 "log-level-info", "log-level-debug"])
  except getopt.GetoptError, err:
    print str(err) # will print something like "option -a not recognized"
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
    elif o == "--input-xml":
      input_xml = a
    else:
      print "Unhandled Option\n"
      logger.critical("Unhandled Option")
      sys.exit(2)
  if not input_xml:
    print "No input xml set, using default: http://export.arxiv.org/rss/math?mirror=edu"
    input_xml = "http://export.arxiv.org/rss/math?mirror=edu"
    
  try:
    results_queue = Queue.Queue()
    haiku_finding_thread = HaikuFindingThread(input_xml=input_xml,no_dictionary_update=no_dictionary_update, results_queue=results_queue)
    haiku_finding_thread.start()
    while(haiku_finding_thread.is_alive()):
      try:
        haiku = results_queue.get(block=True,timeout=1)  #Need such a timeout so KeyboardInterrupt works!
        
        successful_input_flag = False
        while not successful_input_flag:
          x = raw_input("Post the following to twitter after editing (Y/N)?\n" + haiku).strip().lower()
          if x == "y":
	    successful_input_flag = True
	    haiku = get_text_with_vi(haiku, "\n Edit Haiku to post to twitter.")
	    if post_status_to_twitter(haiku)[0]:    print "Tweet Successful!"
	    else:  print "Tweet Failed, see log"
	  elif x == "n":
	    successful_input_flag = True
	  else:
	    print "Didn't get Y or N"
	    pass
      except Queue.Empty as e:
	pass
      
  except KeyboardInterrupt as e:
    print "Caught KeyboardInterrupt, Attempting to terminate worker thread"
    logger.critical("Caught KeyboardInterrupt, Attempting to terminate worker thread")    
    haiku_finding_thread.terminate_request()
