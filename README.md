The project is still premature and under heavy construction
Goal is to have an automated tool for extracting news spread patterns (and in the long term be able to identify sites reproducing hoaxes).

Prerequisites:
* python 2 (some libraries are not supported in python 3)
* simplejson, urllib2, oauth2, bokeh. You can install them through pip.

In a file named serviceTokens.py you should declare a variable:
* readabilityToken, containing your Readability token
* yboss_oauth_key and yboss_oauth_secret, containing your yahoo boss credentials
