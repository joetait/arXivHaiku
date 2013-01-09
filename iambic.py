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

import logging
from curses.ascii import isdigit
from nltk.corpus import cmudict
d = cmudict.dict() 

from  customdictionary import CustomDictionary, UnknownWordException

#If __name__=="__main__" then we will define the logger
if __name__!="__main__":
  global logger
  logger = logging.getLogger('mainLogger')

#Find Iambic Pentameters!  
class Iambic:
  def __init__(self, custom_dictionary):
    logger.debug("Initialising Iambic class")
    self.clause_dict = {}   # Should load this from file
    self.poem = []
    self.custom_dictionary = custom_dictionary

  def nsyl(self,word):  #Finds number of syllables in a word
    try:    
      #returns the syllable length of a word - d actually returns a list of phonetics, so by default choose first length
      return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]][0]
    except KeyError as e:
      return self.custom_dictionary.get_nsyl(word)

  #Detects if sentance is iambic, this turns out to be quite hard
  #  for now just counts the syllables, up to 10
  def is_iambic(self,clause):
    #print [e for word in clause.lower().split() for e in d[word][0]]
    try:
      logger.debug( sum ([self.nsyl(word) for word in clause.lower().split()]) )
      return sum ([self.nsyl(word) for word in clause.lower().split()]) == 10
    except UnknownWordException as e:
      return False
  
  def strip_emph(self, syllable):
    if isdigit(syllable[-1]):
      return syllable[:-1]
    else:
      return syllable
 
  #Pulls last two syllables from clause
  def rhyming_end(self, clause):
    try:
      return tuple([self.strip_emph(e) for word in clause.lower().split() 
                                  for e in d[word][0]][-2:])
    except KeyError as e:
      return False

  def process_clause(self, clause):
    logger.debug("processing: " + clause)
    if self.is_iambic(clause):
      end = self.rhyming_end(clause)
      if end == False: 
        logger.debug("Is iambic, failed to get rhyming end though")
        return
      
      if end in self.clause_dict:
        logger.debug("Is iambic, rhymes with: " + self.clause_dict[end])
        self.poem.append(self.clause_dict.pop(end))
        self.poem.append(clause)
      else:
        self.clause_dict[end] = clause
        logger.debug("Is iambic, added to clause_dict: " + repr(self.clause_dict))
    
    else: 
      logger.debug("Not iambic")

  def get_poem(self):
    return self.poem


if __name__=="__main__":
  import arXivHaikulogger, customdictionary, logging
  
  #No need for global here - already at global scope
  logger = arXivHaikulogger.setup_custom_logger('mainLogger') 
  logger.info("Running findHaiku with __name__==__main__")
  logger.setLevel(logging.DEBUG)

  custom_dictionary = CustomDictionary()
  iambic = Iambic(custom_dictionary)
  iambic.process_clause("Now the winter of our discontent")
  iambic.process_clause("winter of our discontent caring")
  iambic.process_clause("Now is the winter of our car wing")
  iambic.process_clause("winter of our discontent hammer")
  iambic.process_clause("Now is is the winter of the slammer")
  custom_dictionary.save_dict()

  print iambic.get_poem()
