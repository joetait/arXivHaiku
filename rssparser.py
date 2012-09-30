#!/usr/bin/python
import feedparser, re, urllib, tarfile, gzip, StringIO, logging
from lxml import html

logger = logging.getLogger('mainLogger')
log = logger.debug

debug_enabled = False
def debug(string):
  global debug_enabled
  if debug_enabled:
    print string  
  
#Yields tuples from parse_entry
def rssparse(feed_name="http://export.arxiv.org/rss/math?mirror=edu"):
  log("Attempting to parse feed: " + feed_name)
  feed = feedparser.parse(feed_name)
  for entry in feed.entries:
    parsed_entry = parse_entry(entry)
    if parsed_entry != False:
      log("Parsed entry associated to article_id: " + str(parsed_entry[0]))
      yield parsed_entry
    else:
      log("Failed to parse entry (ignoring): " + str(entry))
    
#Returns tuple (article_id, raw_tex) or False on failure, raw_tex is UTF8, article_id is xxxx.xxxx format
def parse_entry(entry):
    
    #Since this stuff is crucial, use utf8 ENCODE so as to catch ANY problems.  Rest uses decode with ignore.
    #TODO: Check that this encoding stuff is done right..
    try:
      #authors = html.document_fromstring(feed.entries[0].author).text_content().encode("utf8").split(",")
      #authors = ["".join(e for e in y if (e.isalnum() or e == " ")) for y in authors]
      link = entry.link.encode("utf8")
      #summary = html.document_fromstring(entry.summary.replace("\n", " ")).text_content().encode("utf8")
      #title = entry.title.encode("utf8")
      article_id = link[-9:]
    except UnicodeDecodeError as e:
      log("Caught UnicodeDecodeError while decoding article_id: " + str(e))
      
    src_link = "http://de.arxiv.org/e-print/"+article_id
    log("Downloading: "+src_link)
    (filename, headers) = urllib.urlretrieve(src_link)
    content_type, content_encoding = (headers.get("Content-Type"), headers.get("Content-Encoding"))
    if content_type == "application/x-eprint-tar":
      log("Recieved: application/x-eprint-tar, unpacking..")
      tar = tarfile.open(filename, "r:gz")
      try:
	for tarinfo in tar:
	  if tarinfo.isreg() and tarinfo.name[-3:] == "tex":
	    log("Extracting: "+tarinfo.name)
	    raw_tex = tar.extractfile(tarinfo).read().decode("utf8", "ignore")
	    return (article_id, raw_tex)
	tar.close()
      except IOError as e:
	log("Skipping to next entry, got IOError: " + str(e))
	return False
    elif content_type ==  "application/x-eprint" and content_encoding == "x-gzip":
      log("Recieved: application/x-eprint encoded with x-gzip, unpacking")
      raw_tex = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(open(filename).read())).read()
      return (article_id, raw_tex.decode("utf8", "ignore"))
    else:
      log("Recieved Content Type: " + content_type + "\n With Encoding: " + content_encoding + "\n Don't know what to do with this! Skipping to next entry\n\n")
      return False
	
if __name__=="__main__":
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
  global log
  log = logger.debug
  log("Running rssparser with __name__==__main__")
  
  print "Testing with rss17.09.2012.xml, entries up to 10:"
  feed = feedparser.parse("rss17.09.2012.xml")
  for i in range(0, 10):
    print str(parse_entry(feed.entries[i])) + "\n\n That was entry" + str(i) + ", press enter to continue"
    raw_input()