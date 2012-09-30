#!/usr/bin/python

import logging

def setup_custom_logger(name, log_file_name="arXivHaiku.log"):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    #formatter = logging.Formatter(fmt='%(asctime)s - %(module)s - %(message)s')
    handler = logging.FileHandler(log_file_name)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

if __name__=="__main__":
  print "There are no tests here yet!"