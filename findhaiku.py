#!/usr/bin/python

#TODO: check all dependancies needed

import os.path, subprocess, StringIO, re, curses, nltk, re, io, getopt, sys
from curses.ascii import isdigit
from nltk.corpus import cmudict
d = cmudict.dict() 
import pprint
pp = pprint.PrettyPrinter(indent=4)

#TODO Check how it behaves with "-" used as a punctuation seperator..

#TODO:Rewrite this dictionary stuff
unknownWordsList = []
#unknownMathList = []
customDictionary = {"bredon":2, "homology":4, "homotopy":4, "functor":2, "functors":2, "finiteness":3, "organising":4, "homological":5, "quotients":2, "pointwise":2, "familiarised":4, "pro-finite":3, "whitecaps":2, "signboard":2}

class UnknownWordException(Exception):
       def __init__(self, value):
           self.word = value
       def __str__(self):
           return repr(self.word)

class LoopException(Exception): pass

debug_enabled = True
def debug(string):
  global debug_enabled
  if debug_enabled:
    print string  

def nsyl(word):  #Finds number of syllables in a word
    
    global unknownWordsList 
    
    def get_nsyl_from_custom_dict(word):
      global unknownWordsList 
      try:
	return customDictionary[word]
      except KeyError as e:	
	unknownWordsList += [word]
	raise UnknownWordException("Unknown Word: " + word);
      
    word = word.lower() 
    
    #If the word is hypenated then use the sum of the word on each side of the dash
    if "-" in word:
      return sum([nsyl(w) for w in word.split("-")])
    
    #check for word "type" - alphanumeric etc
    if re.match("^[a-z']+$", word):   #alphanumeric word
      try:
	#returns the syllable length of a word - d actually returns a list of phonetics, so by default choose first length
	return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]][0]
      except KeyError as e:
        return get_nsyl_from_custom_dict(word)
    else: 
      return get_nsyl_from_custom_dict(word)
    
#returns list of tuples of form (block,ending_punctuation)
def split_at_punctuation(paragraph):  
  punctuation = [".","!","(",")",":",",","?","[","]"] 
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
	debug("Unknown word found: " + e.word)
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
    for paragraph in paragraphs:
      blocks = split_at_punctuation(paragraph)
      haiku_found += find_haiku_in_blocks(blocks)
    return haiku_found
      
def find_haiku_in_tex(raw_tex):
  def usage():  print "Usage: --input\t<INPUT FILE>\n\t-d\tdebug mode"

  # PASS DATA THROUGH untex TO GET raw_text from raw_tex
  if not os.path.isfile("/usr/bin/untex"):
    print "untex doesn't exist, failing"
    exit(1) #Generic error code
  try:
    untex_process = subprocess.Popen(["untex","-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
    raw_text = untex_process.communicate(input=raw_tex)[0]
    debug("untex successfully replied with: " + raw_text + "\n\n")
  except subprocess.CalledProcessError as e:
    print "Failed to run untex, subprocess.CalledProcessError: " + str(e)
  untex_process.stdin.close()

  return getHaikuList(raw_text)

if __name__=="__main__":  
  print find_haiku_in_text("Whitecaps on the bay: A broken signboard banging, In the April wind.\n\n\n\nWhitecaps on the bay: A broken signboard banging, In the April wind.")
  exit(0)
  
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
      global debug_enabled
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