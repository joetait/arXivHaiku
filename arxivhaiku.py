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

import arxivhaikulogger, logging
from twitter import post_status_to_twitter
from rssparser import rssparse
from findhaiku import find_haiku_in_tex
import getopt,sys

if __name__=="__main__":  
  printlicense()

  logger = arxivhaikulogger.setup_custom_logger('mainLogger')
  logger.info("Running arXivHaiku with __name__==__main__")
  
  no_dictionary_update = False
  try:
    opts, args = getopt.getopt(sys.argv[1:],"", ["no-dictionary-update", "input-xml="])
  except getopt.GetoptError, err:
    print str(err) # will print something like "option -a not recognized"
    logger.critical("Caught getopt.GetoptError")
    sys.exit(2)
  input_xml = None
  for o, a in opts:
    if o == "--no-dictionary-update":
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
    for (article_id, raw_tex) in rssparse(input_xml):
      logger.info("Attempting raw tex from article_id: "+ str(article_id))
      try:
	haiku_list = find_haiku_in_tex(raw_tex, no_dictionary_update=no_dictionary_update)  
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