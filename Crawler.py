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
        self.outputFile = ''


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


    def SearchGoogle(self):
        #now we have to construct a search query from the return terms
        searchTerms = ""
        for word in self.keywords:
            searchTerms += wrd[0] + "+"
        searchTerms = searchTerms[:-1] #strip last +
        searchURL = applicationConfig.GoogleURL.format(applicationConfig.publicAddress, urllib2.quote(searchTerms), '/')
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


    def ValidateResults(self):

        verifiedURLS = []
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

            #first, add it to the verified list
            verifiedURLS.append(url)

            try: #parsing domain
                parsedURI = urlparse(url)
                #domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsedURI)
                domain = '{uri.netloc}'.format(uri=parsedURI)
                self.domains.append(domain)
                if applicationConfig.debugOutput is True:
                    print("Extracted url is:", domain)
            except:
                print("Error parsing URL")

        #and now we will replace the list of all urls with the ones
        #that were successfully verified
        self.urls = verifiedURLS

        return self.domains


    def SaveFoundPosts(self):
        #we will save all found related posts
        try:
            file = open(self.outputFile, "a")
            for url in self.urls:
                file.write(url + '\n')
            file.write('\n') #acts as a separator between related posts
        except IOError as exc:
            print("Error saving list of posts to file:", self.outputFile, exc.strerror)
        finally:
            file.close()



if __name__ == "__main__":
    print("Nothing to run here! Execute the main application file instead!")
