#!/usr/bin/python

import os, sys
lib_path = os.path.abspath('brosner-python-oauth2-82a05f9/')
sys.path.append(lib_path)
import oauth2 as oauth
from cgi import escape as htmlescape

consumer_key = '7Hd1Rdux39Mn3WSGhDQSBw'
consumer_secret = '2CeE4fnVIgJZZ6UqNN5GM9r9LX6vKng4WBlh0WSNjrY'

app_token = '629275026-zWRdWREpX8Dqv2U1n4TQn8FmMaLl4bn3uEEtLGo'
app_token_secret = 'hpTHNzi6QMhzdAByjyHrmxiO9mJaT9B93TJbr0OItfM' 

debug_enabled = True
def debug(string):
  global debug_enabled
  if debug_enabled:
    print string  

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
  debug("Attempting to tweet: "+status)
  content = oauth_req(
    'https://api.twitter.com/1.1/statuses/update.json',
    app_token,
    app_token_secret,
    http_method="POST",
    post_body="status="+htmlescape(status),
    )
  if content[0]['status'] != '200':
    debug("Tweet unsuccessful.  Error message: " + str(content))
    return (False, content)
  debug("Tweet successful.")
  return (True, None)

if __name__ == "__main__":
  print "Testing by posting twice to twitter, the first should succeed and the second fail for posting same status twice.\n"
  (success1, error1) = post_status_to_twitter("Blah Blah Haiku")
  (success2, error2) = post_status_to_twitter("Blah Blah Haiku")
  if success1 and not success2: 
    print "Test Successful\n"
  else: 
    print "Test Unsuccessful\n"
  print "You need to delete the last post off twitter now..."