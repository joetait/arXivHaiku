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

import os, sys, logging
lib_path = os.path.abspath('brosner-python-oauth2-82a05f9/')
sys.path.append(lib_path)
import oauth2 as oauth
from cgi import escape as htmlescape

if __name__!="__main__":
  logger = logging.getLogger('mainLogger')

consumer_key = '7Hd1Rdux39Mn3WSGhDQSBw'
consumer_secret = '2CeE4fnVIgJZZ6UqNN5GM9r9LX6vKng4WBlh0WSNjrY'

app_token = '629275026-zWRdWREpX8Dqv2U1n4TQn8FmMaLl4bn3uEEtLGo'
app_token_secret = 'hpTHNzi6QMhzdAByjyHrmxiO9mJaT9B93TJbr0OItfM' 

def oauth_req(url, key, secret, http_method="GET", post_body=None,
        http_headers=None):
    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    token = oauth.Token(key=key, secret=secret)
    client = oauth.Client(consumer, token)

    resp, content = client.request(
        url,
        method=http_method,
        body=post_body,
        headers=http_headers,
        #force_auth_header=True
    )
    return (resp,content)

#Post status to twitter, returns tuple of (success, error_message)
def post_status_to_twitter(status):
  logger.info("Attempting to tweet: "+status)
  content = oauth_req(
    'https://api.twitter.com/1.1/statuses/update.json',
    app_token,
    app_token_secret,
    http_method="POST",
    post_body="status="+htmlescape(status),
    )
  if content[0]['status'] != '200':
    logger.warning("Tweet unsuccessful.  Error message: " + str(content))
    return (False, content)
  logger.info("Tweet successful.")
  return (True, None)

if __name__ == "__main__":
  import arxivhaikulogger
  logger = arxivhaikulogger.setup_custom_logger('mainLogger')  #No need for global here - already at global scope
  logger.info("Running twitter with __name__==__main__")
  
  print "Testing by posting twice to twitter, the first should succeed and the second fail for posting same status twice.\n"
  (success1, error1) = post_status_to_twitter("Blah Blah Haiku")
  (success2, error2) = post_status_to_twitter("Blah Blah Haiku")
  if success1 and not success2: 
    print "Test Successful\n"
  else: 
    print "Test Unsuccessful\n"
  print "You need to delete the last post off twitter now..."