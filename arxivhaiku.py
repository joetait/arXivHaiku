#!/usr/bin/python
#This is the main program

import arxivhaikulogger, logging
from twitter import post_status_to_twitter
from rssparser import rssparse
from findhaiku import find_haiku_in_tex
import getopt,sys

if __name__=="__main__":  
  logger = arxivhaikulogger.setup_custom_logger('mainLogger')
  logger.info("Running arXivHaiku with __name__==__main__")
  try:
    opts, args = getopt.getopt(sys.argv[1:],"", ["input-xml="])
  except getopt.GetoptError, err:
    print str(err) # will print something like "option -a not recognized"
    logger.critical("Caught getopt.GetoptError")
    sys.exit(2)
  input_xml = None
  for o, a in opts:
    if o == "--input-xml":
      input_xml = a
    else:
      print "Unhandled Option\n"
      logger.critical("Unhandled Option")
      sys.exit(2)
  if not input_xml:
    print "No input xml set, use --input-xml option."
    logger.critical("No input xml set")
    sys.exit(2)
  
  try:
    for (article_id, raw_tex) in rssparse(input_xml):
      logger.info("Attempting raw tex from article_id: "+ str(article_id))
      try:
	haiku_list = find_haiku_in_tex(raw_tex)  
      except RuntimeError as e:
	logger.warning("Caught RuntimeError: "+ str(e))
      if len(haiku_list)==0:
	logger.info("Found no Haiku in article_id: " + str(article_id))
      else:
	for haiku in haiku_list:
	  print haiku + " (" + str(article_id) + ") #arXivHaiku"
	  logger.info("Found haiku in article_id :" + str(article_id) + " : " + haiku)
	  
  except KeyboardInterrupt as e:
    print "Caught KeyboardInterrupt, Terminating"
    logger.critical("Caught KeyboardInterrupt, Terminating")    