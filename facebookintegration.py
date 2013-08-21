#!/usr/bin/python

#Copyright 2013, Simon St. John-Green, Simon <dot> StJG <at> gmail <dot> com

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

import facebook, logging

def printlicense():
  print """
  findhaiku is part of arXivHaiku  Copyright 2012 Simon StJohn-Green
    This program comes with ABSOLUTELY NO WARRANTY; for details see gpl.txt
    This is free software, and you are welcome to redistribute it
    under certain conditions; see gpl.txt for details.
  """     

if __name__!="__main__":
  logger = logging.getLogger('mainLogger')

def get_arxivhaiku_graph(personal_access_token):
  logger.info("Attempting to get arxivhaiku graph from facebook...")
  try:
    personal_graph = facebook.GraphAPI(personal_access_token)
    arxivhaiku_access_token = personal_graph.get_object("Arxivhaiku", fields="access_token")["access_token"]
    arxivhaiku_graph = facebook.GraphAPI(arxivhaiku_access_token)
    logger.info("Successfully got arxivhaiku graph")
    return arxivhaiku_graph
  except facebook.GraphAPIError as e:
    logger.warning("post-to-facebook caught GraphAPIError: " + str(e))
    return False

def post_to_facebook(arxivhaiku_graph, message, backdated_time=None):
  logger.info("Attempting to post to facebook: " + message)
  try:
    if backdated_time==None:
      arxivhaiku_graph.put_object("Arxivhaiku", "feed", message=message)
    else:
      arxivhaiku_graph.put_object("Arxivhaiku", "feed", message=message, backdated_time=backdated_time)
    logger.info("Post successful.")
    return True
  except facebook.GraphAPIError as e:
    logger.warning("Post unsuccessful, caught GraphAPIError: " + str(e))
    return False
   
if __name__=="__main__":
  import arXivHaikulogger
  printlicense()
  logger = arXivHaikulogger.setup_custom_logger('mainLogger')  #No need for global here - already at global scope
  logger.info("Running facebookintegration with __name__==__main__: ")
  personal_access_token = 'CAACEdEose0cBAFz6OC0rVqQKhqowjVVVeQhOvCB1etQnPM5ddpxmr3oCoZARGZAzrHzR8ZClCKDmCZBLHcg0mONvvyt9BhQuN5P8C0VGOwioHhvXmoHBRcQOW0I0S4EC9U9vZB54OpO4nx6auYDguFAaz3i6xHZBbgZAHZCm5Ic9zAZDZD'
  arxivhaiku_graph = get_arxivhaiku_graph(personal_access_token)
  message = "That we shall discuss (very superficially) in the next chapter.  (1211.5627) #arXivHaiku"
  post_to_facebook(arxivhaiku_graph, message)

