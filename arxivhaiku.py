#!/usr/bin/python

#This is the main program

#Requirements:
#rssparser: feedparser, re, urllib, tarfile, gzip, StringIO, lxml
#twitter: os, sys, cgi, latest version of oauth2 in current dir
#findhaiku: os, subprocess, StringIO, [pprint]
#customdictionary

#TODO: Add check for previously parsed files, etc

import logging

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
log = logger.debug
    
from twitter import post_status_to_twitter
from rssparser import rssparse
from findhaiku import find_haiku_in_tex
import getopt,sys

def debug(string): 
  if debug_enabled: print string  
 
if __name__=="__main__":  
  global debug_enabled
  debug_enabled = False
  try:
    opts, args = getopt.getopt(sys.argv[1:], ":d", ["input-xml="])
  except getopt.GetoptError, err:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
  input_xml = None
  for o, a in opts:
    if o == "--input-xml":
      input_xml = a
    elif o == "-d":    
      debug_enabled = True
    else:
      print "Unhandled Option\n"
      usage()
      sys.exit(2)
  if not input_xml:
    print "No input xml set, use --input-xml option."
    sys.exit(2)
  
  for (article_id, raw_tex) in rssparse(input_xml):
    log("Attempting raw tex from article_id: "+ str(article_id))
    try:
      haiku_list = find_haiku_in_tex(raw_tex)  
    except RuntimeError as e:
      print "OH SHIT.  Caught RuntimeError: " + str(e)
      log("Caught RuntimeError: "+ str(e))
    if len(haiku_list)==0:
      print "Found no Haiku in " + str(article_id) + ", sorry :("
      log("Found no Haiku in article_id: " + str(article_id))
    else:
      print "Found the following Haiku in " + str(article_id) + ":"
      for haiku in haiku_list:
	print haiku
      log("Found haiku in article_id: " + str(article_id) + " : " + str(haiku_list))
    """
    x = raw_input("Press enter to continue, or x to quit")
    if x == "x": break"""
    
    