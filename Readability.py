#!/usr/bin/env python

from __future__ import print_function
import urllib2
from HTMLParser import HTMLParser

from ConfigBundle import *


class ReadabilityAccessError(Exception):
    pass



#http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class Readability:

    @staticmethod
    def GetPageContent(token, url):

        #fetch
        constructedURL = applicationConfig.readabilityBaseURL.format(url, token)
        try:
            page = urllib2.urlopen(constructedURL)
            json = simplejson.load(page)
        except:
            print("There was an error accessing Readability API:", exc)
            raise ReadabilityAccessError()

        content = json["content"]

        #now we have to prettify it: unescape it & strip tags
        h = HTMLParser()
        unescapedContent = h.unescape(content)
        strippedContent = strip_tags(unescapedContent)

        return strippedContent



if __name__ == "__main__":
    applicationEntry()
    #print("Nothing to run here! Execute the main application file instead!")
