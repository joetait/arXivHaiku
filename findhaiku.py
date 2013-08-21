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
  findhaiku is part of arXivHaiku  Copyright 2012 Simon StJohn-Green
    This program comes with ABSOLUTELY NO WARRANTY; for details see gpl.txt
    This is free software, and you are welcome to redistribute it
    under certain conditions; see gpl.txt for details.
  """       
        
def usage():
  print """
  Usage: 
  --no-dictionary-update \t Don't add new unknown words or increment unknown/ignored words count
  --input= \t tex file to search for haiku in
  --log-level-critical
  --log-level-warning
  --log-level-info
  --log-level-debug
  """

import os.path, subprocess, threading, StringIO, re, io, getopt, sys, logging
from curses.ascii import isdigit
from nltk.corpus import cmudict
d = cmudict.dict() 

from  customdictionary import CustomDictionary, UnknownWordException
custom_dictionary = None

if __name__!="__main__":
  global logger
  logger = logging.getLogger('mainLogger')

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
      logger.critical( "untex doesn't exist, failing (exit(1))")
      exit(1) #Generic error code
    
  def run_untex(self, raw_tex):
    self.raw_text = ""
    def untex_thread_target(raw_tex):
      logger.info("untex thread started")
      
      #Add -m to remove all math mode stuff below
      
      self.untex_process = subprocess.Popen(["untex" ,"-uascii" ,"-gascii" ,"-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
      self.raw_text = self.untex_process.communicate(input=raw_tex.encode("ascii","ignore"))[0]
      self.untex_process.stdin.close()  # TODO: Do I need this?
      logger.info("untex thread finished.")
    
    untex_thread = threading.Thread(target=untex_thread_target, kwargs={"raw_tex":raw_tex})
    untex_thread.start()
    untex_thread.join(self.__timeout)
    if untex_thread.is_alive():
      logger.warning('Process timeout, terminating process')
      self.untex_process.terminate()
      untex_thread.join()
    return self.raw_text

#Finds number of syllables in a word
#If the word is hypenated then use the sum of the word on each side of the dash
def nsyl(word):  
    if "-" in word:
      return sum([nsyl(w) for w in word.split("-")])
    
    if word == "": return 0
    
    try:    
      #returns the syllable length of a word - d actually returns a list of phonetics, so by default choose first length
      return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]][0]
    except KeyError as e:
      return custom_dictionary.get_nsyl(word)
    
#returns list of tuples of form (block,ending_punctuation)
#   No extra processing, lots of empty and horrible blocks exist at this point
def split_at_punctuation(paragraph):  
  punctuation = [".","!","(",")",":",",","?",";"] 
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
    haiku_found = []    
    stack = [blocks]
    while len(stack)!=0:
      data = []
      #logger.debug("entering loop of find_haiku_in_blocks with stack:\n" + pp.pformat(stack) )
      current_blocks = stack.pop()
      for (i, (block, ending_punctuation)) in enumerate(current_blocks):
        #logger.debug("Attempting block:" + pp.pformat(block) )
	try:
	  data.append((sum([ nsyl(word) for word in block.split()]), block, ending_punctuation) )
	except UnknownWordException as e:  #Recurse if problem found
	  #logger.debug("Unknown word found: " + e.word)
	  if len(current_blocks)-1-(i+1) >= 2:  #If not then there aren't enough blocks for haiku anyway
	    stack.append(current_blocks[i+1:])
	  if i >= 2:  #If not then there aren't enough blocks for haiku anyway
	    stack.append(current_blocks[0:i])
	  break

    if len(data) > 2:
      h = [data[i:i+3] for i in range(0, len(zip(*data)[0])-2) if zip(*data)[0][i:i+3] == (5, 7, 5) ]
      haiku_found += ["".join([words+punctuation+" " for (syllables, words, punctuation) in haiku]) for haiku in h]

    return haiku_found    
  
def find_haiku_in_text(raw_text):    
    haiku_found = []    
    
    #Split at double line breaks
    paragraphs = raw_text.split("\n\n")
    
    #ignore single line breaks, tabs - replace with spaces
    #remove all non-alphanumeric characters/non-punctuation characters   
    #   Remove all but:  [^ stuff ]
    #   \w  = word
    #   \d  = digit
    #   \s  = whitespace
    #   \.!\(\):,?;  =  . ! ( ) ; , ? ;
    #   Then remove:
    #   _ \t \n
    nonalphanumeric_pattern = re.compile(r'([^\w\d\s\.!\(\):,\?;]+|_+|\t+|\n+)')
    paragraphs = [nonalphanumeric_pattern.sub(' ',p).strip() for p in paragraphs]

    for paragraph in paragraphs:
      # split at punctuation, nothing else
      blocks = split_at_punctuation(paragraph)

      #Throwaway paragraphs with <3 blocks
      #   Strictly this is not necessary, but will speed things up a bit
      if len(blocks) < 3: continue

      haiku_found += find_haiku_in_blocks(blocks)
    return haiku_found
      
def find_haiku_in_tex(raw_tex, the_custom_dictionary):
  global custom_dictionary
  custom_dictionary = the_custom_dictionary
  untex_thread_class = UntexThreadClass()
  raw_text = untex_thread_class.run_untex(raw_tex)
  haiku_found = find_haiku_in_text(raw_text)
  return haiku_found
  
if __name__=="__main__":  
  printlicense()
  import arXivHaikulogger
  logger = arXivHaikulogger.setup_custom_logger('mainLogger')  #No need for global here - already at global scope
  logger.info("Running findHaiku with __name__==__main__")
  no_dictionary_update = False
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["no-dictionary-update", "input=", \
                                                 "log-level-critical", "log-level-warning", \
                                                 "log-level-info", "log-level-debug" ])
  except getopt.GetoptError, err:
    print str(err) # will print something like "option -a not recognized"
    logger.critical("Caught getopt.GetoptError")
    usage()
    sys.exit(2)
  input_file = None
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
    elif o == "--input":
      input_file = a
    else:
      print "Unhandled Option\n"
      logger.critical("Unhandled Option")
      usage()
      sys.exit(2)
  if not input_file:
    print "No input file set, use --input option."
    usage()
    logger.critical("No input file set")
    sys.exit(2)
      
  try:
    raw_tex = open(input_file, "r").read()
  except IOError as e:
    print "Can't read input file:" + str(e) + "\n"
    logger.critical("Can't read input file : " + str(e))
    sys.exit(2)
  
  custom_dictionary = CustomDictionary(no_dictionary_update=no_dictionary_update)
  haiku_list = find_haiku_in_tex(raw_tex, custom_dictionary) 
  custom_dictionary.save_dict()
  logger.info("Found the following haiku: " + str(haiku_list))
  if len(haiku_list)==0:
    print "Found no Haiku, sorry :("
  else:
    print "Found the following Haiku:"
    for haiku in haiku_list:
      print haiku
