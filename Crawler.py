#!/usr/bin/env python

from __future__ import print_function
import sys
import urllib2
import simplejson
import time
import urlparse
import oauth2 as oauth

from Readability import *
from Document import *
from ConfigBundle import *


global applicationConfig



class CrawlerError(Exception):
    def __init__(self, strerror):
        self.strerror = strerror



class Crawler:
    def __init__(self, keywords):
        self.keywords = keywords
        self.domains = []
        self.urls = []
        self.parsingSettings = None

    @staticmethod
    def oauth_request(url, params, method, oauth_key, oauth_secret):
        params['oauth_version'] = "1.0"
        params['oauth_nonce'] = oauth.generate_nonce()
        params['oauth_timestamp'] = int(time.time())

        consumer = oauth.Consumer(key=oauth_key,
                                  secret=oauth_secret)
        params['oauth_consumer_key'] = consumer.key
        req = oauth.Request(method=method, url=url, parameters=params)
        req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, None)

        return req


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
        spider.parsingSettings = parsingSettings
        return spider


    #deprecated since Google API is deprecated and scrapping get's detected after a few times
    def SearchGoogle(self):
        #now we have to construct a search query from the returned terms
        searchTerms = ""
        for word in self.keywords:
            searchTerms += word[0] + "+"
        searchTerms = searchTerms[:-1] #strip last +
        searchURL = applicationConfig.baseSearchURL.format(applicationConfig.publicAddress, urllib2.quote(searchTerms), '/')
        print("Escaped search URL is: ", searchURL)

        #startch fetching
        for start in range(0, applicationConfig.resultsToExamine):
            currentURL = searchURL + "&start=" + str(start*10)
            try: #fetching
                page = urllib2.urlopen(currentURL)
                json = simplejson.load(page)
            except:
                print("There was an error fetching Google results:")
                continue

            responseStatus = json["responseStatus"]
            if responseStatus is not 200:
                raise CrawlerError("Error fetching results from Google: {0}".format(responseStatus))
                if applicationConfig.debugOutput is true:
                    print(page)

            results = json["responseData"]["results"]
            for result in results:

                unescapedURL = result["unescapedUrl"]
                self.urls.append(unescapedURL)

            time.sleep(applicationConfig.queryDelay) #try to make Google bot detection happy
            print("Fetching more results")

        self.ValidateResults()


    def SearchYahoo(self):
        #now we have to construct a search query from the returned terms
        searchTerms = ""
        for word in self.keywords:
            searchTerms += word[0] + " "
        searchTerms = searchTerms[:-1] #strip last  " "

        #encode/escape request parameters
        req = Crawler.oauth_request(applicationConfig.ybossURL, {"q": searchTerms}, "GET", applicationConfig.ybossOAuthKey, applicationConfig.ybossOAuthSecret)
        req['q'] = req['q'].encode('utf8')
        searchURL = req.to_url().replace('+', '%20')

        #try fetching results & parsing json
        print("Escaped search URL is: ", searchURL)
        try:
            page = urllib2.urlopen(searchURL)
            json = simplejson.load(page)
            results = json["bossresponse"]["web"]["results"]
        except (urllib2.HTTPError, urllib2.URLError):
                print("There was an error fetching Yahoo results")

        #try parsing json
        for result in results:
            url = result["clickurl"]
            self.urls.append(url)
            if applicationConfig.debugOutput is True:
                print(url)

        self.ValidateResults()


    def ValidateResults(self):

        for url in self.urls:
            #before saving the result, we have to open the page to verify it's subject
            #verification is done by comparing the first N (as configured) terms.

            #get keywords of web article
            try:
                pureArticle = Readability.GetPageContent(applicationConfig.readabilityToken, url)
            except ReadabilityAccessError as e:
                continue
            doc = Document(pureArticle)
            topKeywords = doc.CalculateTF(self.parsingSettings, True, applicationConfig.termsToSearch)

            #compare self.keywords with topKeywords
            differentTerms = 0
            for i in range(0, len(topKeywords)):
                print("a:", topKeywords[i][0], "b:", self.keywords[i][0])
                if topKeywords[i][0] != self.keywords[i][0]:
                    differentTerms += 1

            if differentTerms > len(topKeywords)/3:
                continue #this article is not about the same thing, examine next

            #it matches, so save it
            try: #parsing domain
                parsedURI = urllib2.urlparse(unescapedURL)
                domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsedURI)
                self.domains.append(domain)
            except:
                print("Error parsing URL:", unescapedURL, sys.exc_info()[0])

        if applicationConfig.debugOutput is True:
            print("Following domains matched:")
            print(self.domains)

        return self.domains



if __name__ == "__main__":
    print("Nothing to run here! Execute the main application file instead!")
