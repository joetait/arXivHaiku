#!/usr/bin/python

import os.path, subprocess, threading, StringIO, re, io, getopt, sys, logging
from curses.ascii import isdigit
from nltk.corpus import cmudict
d = cmudict.dict() 

from  customdictionary import CustomDictionary, UnknownWordException
custom_dictionary = CustomDictionary()

logger = logging.getLogger('mainLogger')
log = logger.debug

#TODO Check how it behaves with "-" used as a punctuation seperator..

global debug_enabled
debug_enabled = False

def debug(string): 
  if debug_enabled: print string  

#This class runs untex in a seperate thread with specified timeout - prevents untex from hanging entire program
# initialise with no arguments and then run_untex(raw_tex) returns either untexified tex or an empty string on failure
# Only need to initialise once, can then keep calling run
#Code adapted from http://stackoverflow.com/questions/1191374/subprocess-with-timeout
class UntexThreadClass(object):
  __timeout = 5 #default thread timeout of 5 seconds
  
  def __init__(self):
    self.process = None
    self.raw_text = ""
    
    #Kill everything if we don't have untex available
    if not os.path.isfile("/usr/bin/untex"):
      print "untex doesn't exist, failing (exit(1))"
      log( "untex doesn't exist, failing (exit(1))")
      exit(1) #Generic error code
    
  def run_untex(self, raw_tex):
    self.raw_text = ""
    def untex_thread_target(raw_tex):
      print "untex thread started"
      self.untex_process = subprocess.Popen(["untex","-m" ,"-uascii" ,"-gascii" ,"-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
      self.raw_text = self.untex_process.communicate(input=raw_tex.encode("ascii","ignore"))[0]
      self.untex_process.stdin.close()  # TODO: Do I need this?
      print "untex thread finished."
    
    untex_thread = threading.Thread(target=untex_thread_target, kwargs={"raw_tex":raw_tex})
    untex_thread.start()
    untex_thread.join(self.__timeout)
    if untex_thread.is_alive():
      print 'Process timeout, terminating process'
      self.untex_process.terminate()
      untex_thread.join()
    return self.raw_text

def nsyl(word):  #Finds number of syllables in a word
    word = word.lower().strip()
    
    if word == "": return 0
    
    #If the word is hypenated then use the sum of the word on each side of the dash
    if "-" in word:
      return sum([nsyl(w) for w in word.split("-")])
    
    #check for word "type" - alphanumeric etc
    if re.match("^[a-z']+$", word):   #alphanumeric word
      try:
        #returns the syllable length of a word - d actually returns a list of phonetics, so by default choose first length
        return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]][0]
      except KeyError as e:
        return custom_dictionary.get_nsyl(word)
    else: 
      return custom_dictionary.get_nsyl(word)
    
#returns list of tuples of form (block,ending_punctuation)
def split_at_punctuation(paragraph):  
  punctuation = [".","!","(",")",":",",","?","[","]", ";"] 
  blocks = [paragraph]
  for element in punctuation:
    newblocks = []
    for block in blocks:
      split_at_element = block.split(element)
      newblocks += [block + element for block in split_at_element[:-1]]+[split_at_element[-1]]
    blocks = newblocks
  return [(block[:-1],block[-1]) for block in blocks if block!=""]

#takes a list of blocks - tuples (words,punctuation) - and returns a list of Haiku with punctuation added back in
def find_haiku_in_blocks(blocks):
    data = []
    haiku_found = []
    
    for (i, (block, ending_punctuation)) in enumerate(blocks):
      try:
	data.append((sum([ nsyl(word) for word in block.split()]), block, ending_punctuation) )
	#debug("Appending data:" + str ((sum(nsylBlock(block)), block))  + "\n----------------------------------------------\n\n")    
      except UnknownWordException as e:  #Recurse if problem found
	#log("Unknown word found: " + e.word)
	if blocks[0:i]: 
	  haiku_found += find_haiku_in_blocks(blocks[0:i])
	if blocks[i+1:]: 
	  haiku_found += find_haiku_in_blocks(blocks[i+1:])
	return haiku_found
	
    if len(data) > 2:
      haiku_found = [data[i:i+3] for i in range(0, len(zip(*data)[0])-2) if zip(*data)[0][i:i+3] == (5, 7, 5) ]
      haiku_found = ["".join([words+punctuation+" " for (syllables, words, punctuation) in haiku]) for haiku in haiku_found]
      
    return haiku_found    
  
def find_haiku_in_text(raw_text):    
    haiku_found = []    
    paragraphs = raw_text.split("\n\n")
    #ignore single line breaks, tabs - replace with spaces
    paragraphs = [p.replace("\n", " ").replace("\t", " ") for p in paragraphs]
    
    for paragraph in paragraphs:
      blocks = split_at_punctuation(paragraph)
      haiku_found += find_haiku_in_blocks(blocks)
    return haiku_found
      
def find_haiku_in_tex(raw_tex):
  untex_thread_class = UntexThreadClass()
  raw_text = untex_thread_class.run_untex(raw_tex)
  return find_haiku_in_text(raw_text)

def usage():  print "Usage: --input\t<INPUT FILE>\n\t-d\tdebug mode"  
  
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
  log("Running findHaiku with __name__==__main__")

  global debug_enabled
  debug_enabled = False
  try:
    opts, args = getopt.getopt(sys.argv[1:], ":d", ["input="])
  except getopt.GetoptError, err:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
  input_file = None
  for o, a in opts:
    if o == "--input":
      input_file = a
    elif o == "-d":    
      debug_enabled = True
    else:
      print "Unhandled Option\n"
      usage()
      sys.exit(2)
  if not input_file:
    print "No input file set, use --input option."
    sys.exit(2)
      
  try:
    raw_tex = open(input_file, "r").read()
  except IOError as e:
    print "Can't find input file.\n"
    sys.exit(2)
  
  haiku_list = find_haiku_in_tex(raw_tex)  
  if len(haiku_list)==0:
    print "Found no Haiku, sorry :("
  else:
    print "Found the following Haiku:"
    for haiku in haiku_list:
      print haiku