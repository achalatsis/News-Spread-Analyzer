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
    def __init__(self, keywords, parsingSettings):
        self.keywords = keywords
        self.domains = []
        self.urls = []
        self.parsingSettings = parsingSettings


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
    def FromLink(linkURL, parsingSettings):
        try:
            pureArticle = Readability.GetPageContent(applicationConfig.readabilityToken, linkURL)
        except ReadabilityAccessError:
            print("There was an error extracting the content of the article")
            return

        doc = Document(pureArticle)
        topKeywords = doc.CalculateTF(parsingSettings, True, applicationConfig.termsToSearch)
        print("Most common terms in are:")
        for keyword in topKeywords:
            print(keyword[0], ":", keyword[1], end=", ")
        print("")

        spider = Crawler(topKeywords, parsingSettings)
        spider.urls.append(linkURL)
        return spider


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
            except (ReadabilityAccessError, ReadabilityURLError):
                continue

            doc = Document(pureArticle)
            topKeywords = doc.CalculateTF(self.parsingSettings, True, applicationConfig.termsToSearch)

            #compare self.keywords with topKeywords
            list1 = []
            list2 = []
            for keyword in topKeywords:
                list1.append(keyword[0])
            for keyword in self.keywords:
                list2.append(keyword[0])
            matchingKeywords = set(list1).intersection(list2)

            if applicationConfig.debugOutput is True:
                print("Matching keywords: ")
                for keyword in matchingKeywords:
                    print(keyword, end=", ")
                print("")

            if len(matchingKeywords) < 2/3*len(self.keywords):
                print("Skipping post because not enough keywords match")
                continue

            #it matches, so save it
            try: #parsing domain
                parsedURI = urlparse(url)
                domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsedURI)
                self.domains.append(domain)
                if applicationConfig.debugOutput is True:
                    print("Extracted url is:", domain)
            except:
                print("Error parsing URL")

        return self.domains



if __name__ == "__main__":
    print("Nothing to run here! Execute the main application file instead!")
