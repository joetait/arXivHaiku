#!/usr/bin/python

import logging

def setup_custom_logger(name, log_file_name="arXivHaiku.log"):
    DEFAULT_LOG_LEVEL = logging.DEBUG #Change to debug for more messages
  
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.FileHandler(log_file_name)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(DEFAULT_LOG_LEVEL)
    logger.addHandler(handler)
    return logger

if __name__=="__main__":
  print "There are no tests here yet!"