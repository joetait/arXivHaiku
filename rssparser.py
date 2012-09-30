#!/usr/bin/python
import feedparser, re, urllib, tarfile, gzip, StringIO, logging
from lxml import html

#If __name__=="__main__" then we will define the logger
if __name__!="__main__":
  logger = logging.getLogger('mainLogger')
  
#Yields tuples from parse_entry
def rssparse(feed_name):
  logger.info("Attempting to parse feed: " + feed_name)
  feed = feedparser.parse(feed_name)
  for entry in feed.entries:
    parsed_entry = parse_entry(entry)
    if parsed_entry != False:
      logger.info("Parsed entry associated to article_id: " + str(parsed_entry[0]))
      yield parsed_entry
    else:
      logger.warning("Failed to parse entry (ignoring): " + str(entry))
    
#Returns tuple (article_id, raw_tex) or False on failure, raw_tex is UTF8, article_id is xxxx.xxxx format
def parse_entry(entry):
    
    #Since this stuff is crucial, use utf8 ENCODE so as to catch ANY problems.  Rest uses decode with ignore.
    #TODO: Check that this encoding stuff is done right..
    try:
      link = entry.link.encode("utf8")
      article_id = link[-9:]
    except UnicodeDecodeError as e:
      logger.warning("Caught UnicodeDecodeError while decoding article_id: " + str(e))
      
    src_link = "http://de.arxiv.org/e-print/"+article_id
    logger.info("Downloading: "+src_link)
    (filename, headers) = urllib.urlretrieve(src_link)
    content_type, content_encoding = (headers.get("Content-Type"), headers.get("Content-Encoding"))
    if content_type == "application/x-eprint-tar":
      logger.info("Recieved: application/x-eprint-tar, unpacking..")
      tar = tarfile.open(filename, "r:gz")
      try:
	for tarinfo in tar:
	  if tarinfo.isreg() and tarinfo.name[-3:] == "tex":
	    logger.info("Extracting: "+tarinfo.name)
	    raw_tex = tar.extractfile(tarinfo).read().decode("utf8", "ignore")
	    return (article_id, raw_tex)
	tar.close()
      except IOError as e:
	logger.warning("Skipping to next entry, got IOError: " + str(e))
	return False
    elif content_type ==  "application/x-eprint" and content_encoding == "x-gzip":
      logger.info("Recieved: application/x-eprint encoded with x-gzip, unpacking")
      raw_tex = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(open(filename).read())).read()
      return (article_id, raw_tex.decode("utf8", "ignore"))
    else:
      logger.warning("Recieved Content Type: " + str(content_type) + "\n With Encoding: " + str(content_encoding) + "\n Don't know what to do with this! Skipping to next entry\n\n")
      return False
	
if __name__=="__main__":
  import arxivhaikulogger
  logger = arxivhaikulogger.setup_custom_logger('mainLogger')  #No need for global here - already at global scope
  logger.info("Running rssparser with __name__==__main__")
  
  print "Testing with rss17.09.2012.xml, entries up to 10:"
  logger.info("Testing with rss17.09.2012.xml, entries up to 10.")
  feed = feedparser.parse("rss17.09.2012.xml")
  for i in range(0, 10):
    print str(parse_entry(feed.entries[i])) + "\n\n That was entry" + str(i) + ", press enter to continue"
    raw_input()