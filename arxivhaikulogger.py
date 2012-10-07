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

def setup_custom_logger(name, log_file_name="arXivHaiku.log"):
    DEFAULT_LOG_LEVEL = logging.INFO #Change to debug for more messages
  
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.FileHandler(log_file_name)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(DEFAULT_LOG_LEVEL)
    logger.addHandler(handler)
    return logger

if __name__=="__main__":
  print "There are no tests here yet!"