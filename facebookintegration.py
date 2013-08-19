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

import facebook

def get_arxivhaiku_graph(personal_access_token):
  try:
    personal_graph = facebook.GraphAPI(personal_access_token)
    arxivhaiku_access_token = personal_graph.get_object("Arxivhaiku", fields="access_token")["access_token"]
    return facebook.GraphAPI(arxivhaiku_access_token)
  except facebook.GraphAPIError as e:
    print "post-to-facebook caught GraphAPIError: " + str(e)
    return False

def post_to_facebook(arxivhaiku_graph, message, backdated_time=None):
  try:
    if backdated_time==None:
      arxivhaiku_graph.put_object("Arxivhaiku", "feed", message=message)
    else:
      arxivhaiku_graph.put_object("Arxivhaiku", "feed", message=message, backdated_time=backdated_time)
    return True
  except facebook.GraphAPIError as e:
    print "post-to-facebook caught GraphAPIError: " + str(e)
    return False
   
if __name__=="__main__":
  personal_access_token = 'CAACEdEose0cBAFz6OC0rVqQKhqowjVVVeQhOvCB1etQnPM5ddpxmr3oCoZARGZAzrHzR8ZClCKDmCZBLHcg0mONvvyt9BhQuN5P8C0VGOwioHhvXmoHBRcQOW0I0S4EC9U9vZB54OpO4nx6auYDguFAaz3i6xHZBbgZAHZCm5Ic9zAZDZD'
  arxivhaiku_graph = get_arxivhaiku_graph(personal_access_token)
  message = "That we shall discuss (very superficially) in the next chapter.  (1211.5627) #arXivHaiku"
  post_to_facebook(arxivhaiku_graph, message)

