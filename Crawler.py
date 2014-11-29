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

#import global variable defined in ConfigBundle module
global applicationConfig


##  @package Crawler
#   Packages that provides all the searching-related functionality


##  Exception thrown when there is a network related problem
class CrawlerError(Exception):
    def __init__(self, strerror):
        self.strerror = strerror



##  This class defines an object that has search functionality
#
#   Using this interface it's possible to find similar pages based on top keywords of the provided page
class Crawler:

    ##  Creates a new crawler object
    #   @param      keywords            The keywords to search for
    #   @param      parsingSettings     Settings on how to parse downlaoded pages
    def __init__(self, keywords, parsingSettings):

        ##  @var keywords
        #   Keywords to search for
        self.keywords = keywords

        ##  @var parsingSettings
        #   Settings on how to parse downloaded pages
        self.parsingSettings = parsingSettings

        ##  @var urls
        #   URLs found that match based on keyword extraction
        self.urls = []

        ##  @var domains
        #   Just the domain part of the URls
        self.domains = []

        ##  @var outputFile
        #   File to save results to
        self.outputFile = ''


    ##  Constructs an OAuth request with SHA1 signature
    #   @param      url             The URL of the request
    #   @param      params          Parameters to the request
    #   @param      method          Method of the request. Possible values: 'GET', 'POST'
    #   @param      oauth_key       Key for OAuth authentication
    #   @param      oauth_secret    Secret for OAuth authentication
    #   @return     An oauth object
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


    ##  Creates a new crawler after examining a link.
    #   @param      linkURL             URL of article to base crawler on
    #   @param      parsingSettings     Settings for parsing downloaded pages
    #   @return     A Crawler instance
    @staticmethod
    def FromLink(linkURL, parsingSettings):
        try: #we try extracting the content with Readability
            pureArticle = Readability.GetPageContent(applicationConfig.readabilityToken, linkURL)
        except ReadabilityAccessError:
            print("There was an error extracting the content of the article")
            return

        #and then apply tf metrics on it to extract top keywords
        doc = Document(pureArticle)
        topKeywords = doc.CalculateTF(parsingSettings, True, applicationConfig.termsToSearch)
        if applicationConfig.debugOutput is True:
            print("Most common terms in are:")
            for keyword in topKeywords:
                print(keyword[0], ":", keyword[1], end=", ")
            print("")

        #finally we create the Crawler instance
        spider = Crawler(topKeywords, parsingSettings)
        spider.urls.append(linkURL)
        return spider


    ##  Performs a search using Yahoo! search engine
    #   @return     A list of domains that matched
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
        if applicationConfig.debugOutput is True:
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

        #finally we have to verify that the pages in the results are indeed relevant
        self.ValidateResults()


    ##  Peforms a search using Google search engine
    #   @return     A list of domains that matched
    def SearchGoogle(self):
        #now we have to construct a search query from the return terms
        searchTerms = ""
        for word in self.keywords:
            searchTerms += wrd[0] + "+"
        searchTerms = searchTerms[:-1] #strip last +
        searchURL = applicationConfig.GoogleURL.format(applicationConfig.publicAddress, urllib2.quote(searchTerms), '/')
        if applicationconfig.debugOutput is True:
            print("Escaped search URL is: ", searchURL)

        #startch fetching
        for start in range(0, applicationConfig.GoogleResultsToExamine):
            currentURL = searchURL + "&start=" + str(start*10)
            try: #fetching
                page = urllib2.urlopen(currentURL)
                json = simplejson.load(page)
            except:
                print("There was an error fetching Google results:")
                continue

            #check the response status of the request
            responseStatus = json["responseStatus"]
            if responseStatus is not 200:
                raise CrawlerError("Error fetching results from Google: {0}".format(responseStatus))
            if applicationConfig.debugOutput is true:
                print(page)

            #and get the important data
            results = json["responseData"]["results"]
            for result in results:
                unescapedURL = result["unescapedUrl"]
                self.urls.append(unescapedURL)

            #try to make Google bot detection happy, so sleep between requests
            time.sleep(applicationConfig.queryDelay)
            print("Fetching more results")

        self.ValidateResults()


    ##  Validates that the pages return in the results are indeed relevant
    #   @return     A list of domains that matched
    def ValidateResults(self):

        verifiedURLS = []
        for url in self.urls:
            #before saving the result, we have to open the page to verify it's subject
            #verification is done by comparing the first N (as configured) terms.

            #extract the content using Readability
            try:
                pureArticle = Readability.GetPageContent(applicationConfig.readabilityToken, url)
            except (ReadabilityAccessError, ReadabilityURLError):
                continue

            #create a Document from it and perform tf metrics
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

            #if additional debug output is requested, output the keywords that matched
            if applicationConfig.debugOutput is True:
                print("Matching keywords: ")
                for keyword in matchingKeywords:
                    print(keyword, end=", ")
                print("")

            #in order to accept the page as a match we must have at least 2/3 of the keywords matching
            if len(matchingKeywords) < 2/3*len(self.keywords):
                print("Skipping post because not enough keywords match")
                continue

            #it matches, so save it

            #save the full URL
            verifiedURLS.append(url)

            #extract only the domain part
            try:
                parsedURI = urlparse(url)
                #domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsedURI) #for saving a usable link with protocol
                domain = '{uri.netloc}'.format(uri=parsedURI)

                #check if the domain contains a www. prefix and strip it


                self.domains.append(domain)

                if applicationConfig.debugOutput is True:
                    print("Extracted url is:", domain)
            except:
                print("Error parsing URL")

        #and now we will replace the list of all urls with the ones
        #that were successfully verified
        self.urls = verifiedURLS

        return self.domains


    ##  Saves the complete resulting URLs (not just the domains) to a text file
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



#nothing to run directly from here
if __name__ == "__main__":
    print("Nothing to run here! Execute the main application file instead!")
