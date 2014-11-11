#!/usr/bin/env python

import sys
from Document import *
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from ConfigBundle import *
import simplejson
import time
from serviceTokens import *

global applicationConfig

#search URLs
baseSearchURLfromGreece = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&tbs=ctr:countryGR&cr=countryGR&userip={0}&q={1}"
baseSearchURLSimple = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&userip={0}&q={1}"
baseSearchURLinGreek = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&tbs=lr:lang_1el&lr=lang_el&userip={0}&q={1}"
baseSearchURLfromGreeceInGreek = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&cr=countryGR&tbas=0&tbs=ctr:countryGR,lr:lang_1el&lr=lang_el&userip={0}&q={1}"

readabilityBaseURL = "https://www.readability.com/api/content/v1/parser?url={0}&token={1}"


#main application code
def ApplicationEntryPoint():

    #configuration
    applicationConfig.debugOutput = True
    applicationConfig.termsToSearch = 10
    applicationConfig.resultsToExamine = 20 #must be a multiple of 10
    applicationConfig.baseSearchURL = baseSearchURLfromGreeceInGreek
    applicationConfig.userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"
    applicationConfig.crawlerFetchTimeout = 2 #seconds
    applicationConfig.relativeArticleDirectory = "sample data/articles"
    applicationConfig.publicAddress = PublicIPv4Address();
    applicationConfig.queryDelay = 5 #seconds
    applicationConfig.readabilityToken = readabilityToken
    applicationConfig.readabilityBaseURL = readabilityBaseURL

    punctuationMarksFilename = "sample data/punctuationmarks"
    ignoredWordsFilename = "sample data/ignoredWords"
    parsingSettings = DocumentParsingSettings(punctuationMarksFilename, ignoredWordsFilename, 4)

    #load available articles
    articleFilenames = []
    for filename in os.listdir(applicationConfig.relativeArticleDirectory):
        if filename.endswith(".article"):
            articleFilenames.append(applicationConfig.relativeArticleDirectory + "/" + filename)
    print("Loaded the following articles:", articleFilenames)

    domains = {}
    for filename in articleFilenames:
        try:
            crawler = Crawler.FromFile(filename, parsingSettings)
            crawler.SearchGoogle()
            for domain in crawler.domains:
                if domain in trackedDomains:
                    trackedDomains[domain] += 1
                else:
                    trackedDomains[domain] = 1
        except CrawlerError as exc:
            print("Error while searching:", exc.strerror, end="\n\n")


    #print collected data
    for domain, occurences in domains:
        print (domain, domains[domain])



def PublicIPv4Address():
    addressServiceURL = "http://api.ipify.org?format=json"
    try:
        page = request.urlopen(addressServiceURL)
        json = simplejson.load(page)
        address = json["ip"]
        return address
    except:
        print("Could not determine, public IP address, exiting...", sys.exc_info()[0])
        sys.exit()



if __name__ == "__main__":
    ApplicationEntryPoint()
