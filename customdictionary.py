#!/usr/bin/python

unknownWordsList = []
customDictionary = {"abelian":3, "bredon":2, "homology":4, "homotopy":4, "functor":2, "functors":2, "finiteness":3, "organising":4, "homological":5, "quotients":2, "pointwise":2, "familiarised":4, "pro-finite":3, "whitecaps":2, "signboard":2}

class UnknownWordException(Exception):
  def __init__(self, value):
   self.word = value
  def __str__(self):
    return repr(self.word)

def get_nsyl_from_custom_dict(word):
  global unknownWordsList 
  try:
    return customDictionary[word]
  except KeyError as e:	
    unknownWordsList += [word]
    raise UnknownWordException(word);
      
if __name__=="__main__":
  print "No tests here yet.."