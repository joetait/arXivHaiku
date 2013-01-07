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
      
#import os.path, subprocess, threading, StringIO, re, io, getopt, sys, logging
from curses.ascii import isdigit
from nltk.corpus import cmudict
d = cmudict.dict() 

class Iambic:
  def __init__(self):
    self.clause_dict = {}   # Should load this from file
    self.poem = []

  #Detects if sentance is iambic, this turns out to be quite hard
  #  for now just counts the syllables, up to 10
  def is_iambic(clause):
    #print [e for word in clause.lower().split() for e in d[word][0]]
    return sum ([nsyl(word) for word in clause.lower().split()]) == 10
   
  #Pulls last two syllables from clause
  def rhyming_end(clause):
    clause = clause.replace("-", " ")   #Do this is nysl too..  Could also probably remove the if statement
    try:
      return tuple([e for word in clause.lower().split() for e in d[word][0]][-2:])
    except KeyError as e:
      return False

  def process_clause(self, clause):

  ########### HAVEN'T EVEN PROOF READ THIS YET...

    if is_iambic(clause):
      end = rhyming_end(clause)
      if end == False: return
      
      if end in self.clause_dict:
        self.poem.append(self.clause_dict[end])
        self.poem.append(self.clause)
      else:
        self.clause_dict[end] = clause
  

#If __name__=="__main__" then we will define the logger
if __name__!="__main__":
  global logger
  logger = logging.getLogger('mainLogger')

def nsyl(word):  #Finds number of syllables in a word
    #If the word is hypenated then use the sum of the word on each side of the dash
    if "-" in word:
      return sum([nsyl(w) for w in word.split("-")])
    
    if word == "": return 0
    
    try:    
      #returns the syllable length of a word - d actually returns a list of phonetics, so by default choose first length
      return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]][0]
    except KeyError as e:
      print "KeyError in nsyl booo"
      #return custom_dictionary.get_nsyl(word)

if __name__=="__main__":
  print is_iambic("Now is the winter of our discontent")


