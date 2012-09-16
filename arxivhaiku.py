#!/usr/bin/python

#This is the main program

#Requirements:
#rssparser: feedparser, re, urllib, tarfile, gzip, StringIO, lxml
#twitter: os, sys, cgi, latest version of oauth2 in current dir
#findhaiku: os, subprocess, StringIO, [pprint]
#customdictionary

#TODO: Add check for previously parsed files, etc
#TODO: Rewrite customdictionary

from twitter import post_status_to_twitter
from rssparser import rssparse
from findhaiku import find_haiku_in_tex
import getopt,sys

def debug(string): 
  if debug_enabled: print string  

  """
if __name__=="__main__":
  for (article_id, raw_tex) in rssparse():
    print raw_tex
    exit(0)
  
    (success, error) = post_status_to_twitter("This is not really a test post")
    if not success:
      print "Error posting to twitter, content coming up...: \n\n" + str(error)
    exit(0)
  """
  
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
    try:
      haiku_list = find_haiku_in_tex(raw_tex)  
    except RuntimeError as e:
      print "OH SHIT.  Caught RuntimeError: " + str(e)
      
    if len(haiku_list)==0:
      print "Found no Haiku, sorry :("
    else:
      print "Found the following Haiku:"
      for haiku in haiku_list:
	print haiku
    
    x = raw_input("Press enter to continue, or x to quit")
    if x == "x": break
    