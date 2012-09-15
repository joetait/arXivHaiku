#!/usr/bin/python

#This is the main program

#Requirements:
#rssparser: feedparser, re, urllib, tarfile, gzip, StringIO, lxml
#twitter: os, sys, cgi, latest version of oauth2 in current dir
#findhaiku: os, subprocess, StringIO, [pprint]

#TODO: Add check for previously parsed files, etc

from twitter import post_status_to_twitter
from rssparser import rssparse


if __name__=="__main__":
  print "Lets Go!"
  
  for (article_id, raw_tex) in rssparse():
    print raw_tex
    exit(0)
  
    (success, error) = post_status_to_twitter("This is not really a test post")
    if not success:
      print "Error posting to twitter, content coming up...: \n\n" + str(error)
    exit(0)
  
  