#!/usr/bin/env python

import sys
from Document import *
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from ConfigBundle import *
import simplejson
import time

global applicationConfig



class CrawlerError(Exception):
    def __init__(self, strerror):
        self.strerror = strerror



class Crawler:
    def __init__(self, keywords):
        self.keywords = keywords
        self.domains = []
        self.urls = []


    @staticmethod
    def FromFile(filename, parsingSettings):

        #load text
        doc = Document.FromFile(filename)
        topKeywords = doc.CalculateTF(parsingSettings, True, applicationConfig.termsToSearch)
        print("Most common terms in ", filename, "are:")
        for word in topKeywords:
            print(word[0], ":", word[1], end=", ")
        print("")

        spider = Crawler(topKeywords)
        return spider


    def SearchGoogle(self):
        #now we have to construct a search query from the returned terms
        searchTerms = ""
        for word in self.keywords:
            searchTerms += word[0] + "+"
        searchTerms = searchTerms[:-1] #strip last +
        searchURL = applicationConfig.baseSearchURL.format(applicationConfig.publicAddress, urllib.parse.quote(searchTerms), '/')
        print("Escaped search URL is: ", searchURL)

        #create HTTP client
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', applicationConfig.userAgent)]

        #startch fetching
        for start in range(0, applicationConfig.resultsToExamine):
            currentURL = searchURL + "&start=" + str(start*10)
            try: #fetching
                page = opener.open(currentURL, None, applicationConfig.crawlerFetchTimeout)
            except urllib.error.HTTPError as exc:
                print("There was an error fetching Google results:", exc)
                continue
            json = simplejson.load(page)

            responseStatus = json["responseStatus"]
            if responseStatus is not 200:
                raise CrawlerError("Error fetching results from Google: {0}".format(responseStatus))
                if applicationConfig.debugOutput is true:
                    print(page)

            results = json["responseData"]["results"]
            for result in results:
                #before saving the result, we have to open the page to verify it's subject
                #verification is done by comparing the first N (as configured) terms.


                

                unescapedURL = result["unescapedUrl"]
                self.urls.append(unescapedURL)

                try: #parsing domain
                    parsedURI = urllib.parse.urlparse(unescapedURL)
                    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsedURI)
                    self.domains.append(domain)
                except:
                    print("Error parsing URL:", unescapedURL, sys.exc_info()[0])

            time.sleep(applicationConfig.queryDelay) #try to make Google bot detection happy
            print("Fetching more results")





if __name__ == "__main__":
    print("Nothing to run here! Execute the main application file instead!")
