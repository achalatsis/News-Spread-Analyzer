#!/usr/bin/env python

from __future__ import print_function
import urllib2
import simplejson
from HTMLParser import HTMLParser

#import global variable defined in ConfigBundle module
from ConfigBundle import *


##  @package Readability
#   Interface for Readability service
#
#   This package provides an easy to use implementation of the Readability API



##  Readability unavailable exception
#
#   Exception thrown when the Readability service is unreachable
#   due to network issues.
class ReadabilityAccessError(Exception):
    pass



##  URL submitted is malformed
#
#   Exception thrown when the URL passed is not valid, contains illegal characters, etc.
class ReadabilityURLError(Exception):
    pass



##  Class providing an HTML tag stripper
#
#   Wrapper around HTMLParser class
class MLStripper(HTMLParser):

    ##  Sets up a HTMLParser object and initializes required options
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []


    #used internally and as such is not documented.
    def handle_data(self, d):
        self.fed.append(d)


    ##  Returns data without HTML tags
    def get_data(self):
        return ''.join(self.fed)



##  Strips HTML tags
#
#   Takes HTML code as input, strips the HTML tags and returns it.
#   @param      html        The HTML content
#   @Returns    HTML-tags-free content
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()



##  Interface to Readability service
#
#   This is the main class of the module, and provides an interface to Readability service.
#   It uses the service's JSON API.
class Readability:

    ##  Submits the supplied URL to Readability and receives the extracted content.
    #   @param      token       The secret token provided for authentication
    #   @param      url         The URL to extract content from
    @staticmethod
    def GetPageContent(token, url):

        #first we try to construct a valid request URL by combining the Readability base URL
        #and the supplied arguments
        try:
            constructedURL = applicationConfig.readabilityBaseURL.format(url, token)
        #this may fail due to illegal characters in URL or malformed arguments
        except UnicodeEncodeError:
            print("There was an error constructing URL for accesing Readability")
            raise ReadabilityAccessError()

        #we have successfully constructed the request URL, so now submit the request and fetch the data
        try:
            #If we want debug output, print the URL of the page
            if applicationConfig.debugOutput is True:
                print("Getting pure content of:", url)
            page = urllib2.urlopen(constructedURL) #fetch contents
            json = simplejson.load(page) #parse into JSON
        #things that can go wrong here are network-related
        except (urllib2.HTTPError, urllib2.URLError):
            print("There was an error accessing Readability API")
            raise ReadabilityAccessError()

        #get the data from the JSON dictionary
        content = json["content"]

        #now we have to prettify it: unescape it & strip HTML tags
        h = HTMLParser()
        unescapedContent = h.unescape(content)
        strippedContent = strip_tags(unescapedContent)

        #return purified content
        return strippedContent



#there is nothing to run directly from here
if __name__ == "__main__":
    applicationEntry()
    #print("Nothing to run here! Execute the main application file instead!")
