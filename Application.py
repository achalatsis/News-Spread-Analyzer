#!/usr/bin/env python

import os, sys, inspect
from ConfigBundle import *
from Document import *
from Crawler import *
import os

global applicationConfig

#search URLs
baseSearchURLfromGreece = "http://www.google.gr/search?q={0}&tbs=ctr:countryGR&cr=countryGR"
baseSearchURLSimple = "http://www.google.gr/search?q={0}"
baseSearchURLinGreek = "http://www.google.gr/search?q={0}&tbs=lr:lang_1el&lr=lang_el"
baseSearchURLfromGreeceInGreek = "http://www.google.gr/search?q={0}&cr=countryGR&tbas=0&tbs=ctr:countryGR,lr:lang_1el&lr=lang_el"


#main application code
def ApplicationEntryPoint():
    applicationConfig.debugOutput = True
    applicationConfig.termsToSearch = 10
    applicationConfig.resultsToExamine = 20 #must be a multiple of 10
    applicationConfig.baseSearchURL = baseSearchURLfromGreeceInGreek
    applicationConfig.userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"
    applicationConfig.crawlerFetchTimeout = 2 #seconds
    applicationConfig.relativeArticleDirectory = "sample data/articles"

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



if __name__ == "__main__":
    ApplicationEntryPoint()
