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

import os, tempfile

def get_text(editable_text, displayed_text=""):
  (handle, filename) = tempfile.mkstemp()
  os.close(handle)
  open(filename, "w").write(editable_text+"\n"+displayed_text)
  os.system("vi " + filename)
  text = open(filename, "r").readline()
  os.remove(filename)
  return text.strip()  #Need strip to remove 

if __name__=="__main__":
  print get_text("This is a test run", "This should be underneath")