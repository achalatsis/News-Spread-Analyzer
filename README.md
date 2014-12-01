The project is still premature and under heavy construction

Goal is to have an automated tool for extracting news spread patterns (and in the long term be able to identify sites reproducing hoaxes).

Prerequisites:
* python 2 (some libraries are not supported in python 3)
* simplejson, urllib2, oauth2, matplotlib. You can install them through pip.

In a file named serviceTokens.py you should declare a variable:
* readabilityToken, containing your Readability token
* yboss_oauth_key and yboss_oauth_secret, containing your yahoo boss credentials

You need 3 files to run the application:
* a file with punctuation marks to strip
* a file with common words to ignore
* a file with a list of article links to start crawling from, and a title for the output chart.

You run the application with switch -h for running options.
