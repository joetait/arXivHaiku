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

base_html = r"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head> 
<title>Poems from the arXiv</title>
<style type="text/css">
  body { 
    background-color:#EAEAEA;
  }
  div#contact{
    position:absolute;
    right:0;
    top:0;
    padding:10px;
  }
  div#titlebar {
    padding:5px;
    font-size:350%;
    text-align:center;
    color:#404040;
  }
  div#main {
    font-size:150%;
    text-align:center;
  }
  p.poem {
    padding:0px;
    margin:8px;
  }
  p>a:visited, p>a:link, p>a:active {
    color:#A0A0A0;
    font-size:70%;
  }
  
  p>a:hover {
    color:black;
  }
</style>
</head>

<body>
<div id="contact">
  <!-- AddThis Button BEGIN -->
  <div class="addthis_toolbox addthis_default_style ">
    <a class="addthis_button_preferred_1"></a>
    <a class="addthis_button_preferred_2"></a>
    <a class="addthis_button_preferred_3"></a>
    <a class="addthis_button_preferred_4"></a>
    <a class="addthis_button_compact"></a>
    <a class="addthis_counter addthis_bubble_style"></a>
  </div>
  <script type="text/javascript">var addthis_config = {"data_track_addressbar":true};</script>
  <script type="text/javascript" src="//s7.addthis.com/js/300/addthis_widget.js#pubid=ra-50ede3ed1ac3434b"></script>
  <!-- AddThis Button END -->

  <a href="http://www.personal.soton.ac.uk/~ssg1g11/index.html">Why?</a>
</div>
<div id="titlebar">
  <p>Poems from the arXiv</p>
</div>
<div id="main">
$POEM_SECTION$
</div>
</body>
</html>
"""

import logging

#If __name__=="__main__" then we will define the logger
if __name__!="__main__":
  global logger
  logger = logging.getLogger('mainLogger')

def build_html(poem):
  poem_html = "\n".join(["<p class=\"poem\">" + line + "</p>" for line in poem])
  html = base_html.replace("$POEM_SECTION$", poem_html)
  return html

def post_to_server(poem):
  html = build_html(poem)
  print "At this point, the following should be posted to server: "
  print html

  return True
