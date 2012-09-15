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
customDictionary = {"bredon":2, "homology":4, "homotopy":4, "functor":2, "functors":2, "finiteness":3, "organising":4, "homological":5, "quotients":2, "pointwise":2, "familiarised":4, "pro-finite":3}

class UnknownWordException(Exception):
       def __init__(self, value):
           self.word = value
       def __str__(self):
           return repr(self.word)

class LoopException(Exception): pass

debug_enabled = False
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

      """
def nsylBlock(block): #Splits blocks of words into a list of their syllable-lengths
    x = []
    for i, piece in enumerate(block.split("$")):
      if i % 2 == 0:
	x += [nsyl(word) for word in piece.split()]
      if i % 2 == 1:
	x += nsylMath(piece)
    return x

    
def splitAtPunctuation(block):  #Attempts to split paragraphs into sentances
    punctuation = [".","!","(",")",":"] #"," not needed
    
    for i in range(0,len(punctuation)):
      block = block.replace(punctuation[i],",")
    return block.split(",")

    """
    
def getHaikuList(raw_text):    
    haikuFound = []
    
    paragraphs = raw_text.split("\n\n")

    debug ("Paragraphs:" + str(paragraphs) + "\n---------------------------------------------------------\n")
    
    for paragraph in paragraphs:
      paragraphSplitAtPunctuation = splitAtPunctuation(paragraph)
      debug ("Paragraph Split at punctuation: " + str(paragraphSplitAtPunctuation))
      
      #TODO : new data for each paragraph!!!
      data = []
      try:
	for (i, block) in enumerate(paragraphSplitAtPunctuation):
	  if block.strip()!="":
	    try:
	      data.append( (sum(nsylBlock(block)), block) )
      	      debug("Appending data:" + str ((sum(nsylBlock(block)), block))  + "\n----------------------------------------------\n\n")
	    
	    except UnknownWordException as e:
	      #Throw away block with unknown word, regard that block as splitting paragraph into two new paragraphs
	      debug("Unknown word found: " + e.word + "\nAppending new blocks \n")
	      #TODO: appending at correct place would be cleaner?
	      
	      if paragraphSplitAtPunctuation[0:i]: paragraphs += [".".join(paragraphSplitAtPunctuation[0:i])]
	      if paragraphSplitAtPunctuation[i+1:]: paragraphs += [".".join(paragraphSplitAtPunctuation[i+1:])]
	      
	      debug("New Paragraphs: " + str(paragraphs) + "\n------------------------------------------\n\n")
	      
	      raise LoopException
	    
      except LoopException: continue
      
      #Search for Haiku
      if data:
	newHaikuList = [data[i:i+3] for i in range(0, len(zip(*data)[0])-2) if zip(*data)[0][i:i+3] == (5, 7, 5) ]
      else:
	newHaikuList = []
      
      if newHaikuList: 
	debug("Found Haiku(?): " + str(newHaikuList))
      else:
	debug("Found no Haiku in this block")
    
      haikuFound += newHaikuList
    return haikuFound    
    
   
#TODO: This has a horrible return value, fix it
def find_haiku(raw_tex):
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
  print nsyl("22")
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
  
  haiku_list = find_haiku(raw_tex)  
  if len(haiku_list)==0:
    print "Found no Haiku, sorry :("
  else:
    print "Found the following Haiku:"
    for haiku in haiku_list:
      print haiku


"""
#http://www.onebloke.com/2011/06/counting-syllables-accurately-in-python-on-google-app-engine/


import curses, nltk, re, io, getopt, sys
from curses.ascii import isdigit
from nltk.corpus import cmudict
d = cmudict.dict() 

verbose = False
unknownWordsList = []
unknownMathList = []
customDictionary = {"bredon":2, "homology":4, "homotopy":4, "functor":2, "functors":2, "finiteness":3, "organising":4, "homological":5, "quotients":2, "pointwise":2, "familiarised":4, "pro-finite":3}

class UnknownWordException(Exception):
       def __init__(self, value):
           self.word = value
       def __str__(self):
           return repr(self.word)

class LoopException(Exception): pass

def debugPrint(string):
  if verbose: print string

def removeAnnoyingThings(block):
    #remove all inside $$
    block = "".join([block for i, block in enumerate(block.split("$$")) if i % 2 == 0])

    #remove cite etc
    removePattern = r"\\cite[\[\]\w1-9_\-]*{[\w1-9_\-]*}|\\label{[\w1-9_\-]*}|\\ref{[\w1-9_\-]*}"
    
    #remove \emph, \hbox, leaving a space
    emphPattern = r"\\emph|\\hbox"
    block = re.sub(emphPattern, ' ', block)
    
    #remove { and }
    block = re.sub(r'{|}',' ' , block)
    
    return re.sub(removePattern, ' ', block)
     
def nsylMath(word):
  global unknownMathList
  unknownMathList += [word]
  raise UnknownWordException("Unknown Math: " + word)
     
def nsyl(word): 
    global unknownWordsList 
    #check for word "type" - alphanumberic etc
    if re.match("^[a-z']+$", word.lower()):      
      try:
	#returns the syllable length of a word - d actually returns a list of phonetics, so by default choose first length
	return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]][0]
      except KeyError as e:
	#Try extra dictionary
	try:
	  return customDictionary[word.lower()]
	except KeyError as e:	
	  unknownWordsList += [word]
	  raise UnknownWordException("Unknown Word: " + word);
    elif word.strip() == "-":
      return 0
    elif re.match("^[1-9]+$", word.lower()):
      #TODO: make a less ugly ugly fix - just returns number of numbers...
      return len(word.strip())
    else: 
      unknownWordsList += [word]
      raise UnknownWordException("Unknown Word: " + word);
      
def nsylBlock(block): #Splits blocks of words into a list of their syllable-lengths
    x = []
    for i, piece in enumerate(block.split("$")):
      if i % 2 == 0:
	x += [nsyl(word) for word in piece.split()]
      if i % 2 == 1:
	x += nsylMath(piece)
    return x
    
def splitAtPunctuation(block):  #Attempts to split paragraphs into sentances
    punctuation = [".","!","(",")",":"] #"," not needed
    
    for i in range(0,len(punctuation)):
      block = block.replace(punctuation[i],",")
    return block.split(",")
    
def splitAtParagraph(block):    #Attempts to split out paragraphs from raw latex
    splitPattern = r"\\begin\**{[\w1-9_\-]+}|\\end\**{[\w1-9_\-]+}|\\section\**{[\w1-9_\-]+}|\\subsection\**{[\w1-9_\-]+}|\n+\s*\n+"  #word matched digits letters and underscores
    #removePattern = r"\\[\w1-9_]+"
    returnValue = [block.strip() for block in re.split(splitPattern, block) if block]
    return [x for x in returnValue if x!='']
    
def getHaikuList(rawString):    
    haikuFound = []
    
    paragraphs = splitAtParagraph(rawString)
    debugPrint ("Paragraphs:" + str(paragraphs) + "\n---------------------------------------------------------\n")
    
    for paragraph in paragraphs:
      paragraphSplitAtPunctuation = splitAtPunctuation(paragraph)
      debugPrint ("Paragraph Split at punctuation: " + str(paragraphSplitAtPunctuation))
      
      #TODO : new data for each paragraph!!!
      data = []
      try:
	for (i, block) in enumerate(paragraphSplitAtPunctuation):
	  if block.strip()!="":
	    try:
	      data.append( (sum(nsylBlock(block)), block) )
      	      debugPrint("Appending data:" + str ((sum(nsylBlock(block)), block))  + "\n----------------------------------------------\n\n")
	    
	    except UnknownWordException as e:
	      #Throw away block with unknown word, regard that block as splitting paragraph into two new paragraphs
	      debugPrint("Unknown word found: " + e.word + "\nAppending new blocks \n")
	      #TODO: appending at correct place would be cleaner?
	      
	      if paragraphSplitAtPunctuation[0:i]: paragraphs += [".".join(paragraphSplitAtPunctuation[0:i])]
	      if paragraphSplitAtPunctuation[i+1:]: paragraphs += [".".join(paragraphSplitAtPunctuation[i+1:])]
	      
	      debugPrint("New Paragraphs: " + str(paragraphs) + "\n------------------------------------------\n\n")
	      
	      raise LoopException
	    
      except LoopException: continue
      
      #Search for Haiku
      if data:
	newHaikuList = [data[i:i+3] for i in range(0, len(zip(*data)[0])-2) if zip(*data)[0][i:i+3] == (5, 7, 5) ]
      else:
	newHaikuList = []
      
      if newHaikuList: 
	debugPrint("Found Haiku(?): " + str(newHaikuList))
      else:
	debugPrint("Found no Haiku in this block")
    
      haikuFound += newHaikuList
    return haikuFound    
def usage():
    print "Usage: --input\t<INPUT FILE>\n\t-v\tdebug mode"
    
def main():
    try:
      opts, args = getopt.getopt(sys.argv[1:], ":v", ["input=", "output="])
    except getopt.GetoptError, err:
      # print help information and exit:
      print str(err) # will print something like "option -a not recognized"
      usage()
      sys.exit(2)
    inputfile = None
    outputfile = False
    for o, a in opts:
      print o,a
      if o == "--input":
        inputfile = a
      elif o == "--output":
	#TODO
	print "This isn't handled yet!"
        outputfile = a
      elif o == "-v":
	global verbose
	verbose = True
      else:
        print "Unhandled Option\n"
        usage()
        sys.exit(2)
    if not inputfile:
      print "No input file set!\n"
      usage()
      sys.exit(2)
      
    #TODO: Add error check properly
    try:
      rawTex = io.open(inputfile, "r").read()
    except IOError as e:
      print "Can't find file...\n"
      usage()
      sys.exit(2)
    
    #find between begin{document} and \end{document}
    beginDocPattern = r"\\begin{document}"
    endDocPattern = r"\\end{document}"
   
    try:
      rawTex = re.split(beginDocPattern, rawTex)[1]
      rawTex = re.split(endDocPattern, rawTex)[0]
    except IndexError as e:
      print "Can't find \\begin{document} and \\end{document} tags"
      usage()
      sys.exit(2)
      
    debugPrint(rawTex)
    rawTex = removeAnnoyingThings(rawTex)
    haikuList = getHaikuList(rawTex)
    
    if not haikuList:
      print "No haiku found :("
    else:
      for (i,haiku) in enumerate(haikuList):
	print "Haiku "+str(i) +":" + "\n".join(zip(*haiku)[1])
	
    print "Unknown Words: " + str(unknownWordsList)
    print "Unknown Math: " + str(unknownMathList)
    
if __name__ == "__main__":
    main()
    """