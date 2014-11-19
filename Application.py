#!/usr/bin/env python

from __future__ import print_function
import os, sys
import urllib2
import simplejson
import time
from serviceTokens import *

from ConfigBundle import *
from Document import *
from Crawler import *
from Visualization import *


global applicationConfig

#search URLs
readabilityBaseURL = "https://www.readability.com/api/content/v1/parser?url={0}&token={1}"
yahooBaseURL = "http://yboss.yahooapis.com/ysearch/web"


#main application code
def ApplicationEntryPoint():

    #configuration
    applicationConfig.debugOutput = False
    applicationConfig.termsToSearch = 10
    applicationConfig.userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"
    applicationConfig.crawlerFetchTimeout = 2 #seconds
    applicationConfig.publicAddress = PublicIPv4Address();
    applicationConfig.queryDelay = 5 #seconds
    applicationConfig.readabilityToken = readabilityToken
    applicationConfig.readabilityBaseURL = readabilityBaseURL
    applicationConfig.ybossURL = yahooBaseURL
    applicationConfig.ybossOAuthKey = yboss_oauth_key
    applicationConfig.ybossOAuthSecret = yboss_oauth_secret
    applicationConfig.chartTitle = "News spread chart"
    applicationConfig.chartSubtitle = "News stories count"

    #settings for parsing article contents
    punctuationMarksFilename = "sample data/punctuationmarks"
    ignoredWordsFilename = "sample data/ignoredWords"
    parsingSettings = DocumentParsingSettings(punctuationMarksFilename, ignoredWordsFilename, 4)

    #load available articles
    articleLinks = []
    articleLinksFilename = "sample data/articleLinks"
    try:
        file = open(articleLinksFilename, "rU")
        for line in file:
            articleLinks.append(line)
    except IOError as exc:
        print("Error reading from file: ", exc.strerror)
        sys.exit()

    #for each link start a new crawl
    domains = {}
    for link in articleLinks:
        try:
            crawler = Crawler.FromLink(link, parsingSettings)
        except CrawlerError as exc:
                print("Error getting initial content from article:", link)

        if crawler is not None:
            crawler.SearchYahoo()
        else:
            print("Error building crawler for article:", link)
            continue

        for domain in crawler.domains:
            if domain in domains:
                domains[domain] += 1
            else:
                domains[domain] = 1

    #sort domains in reverse (most occurences) order
    sortedDomains = sorted(domains, key=lambda tup: tup[1], reverse=True)
    topDomains = sortedDomains[:10]

    #print collected data
    if applicationConfig.debugOutput is True:
        for domain in topDomains:
            print (domain[0], domain[1])

    #create a bar chart to display the domains
    values = [i[1] for i in topDomains]
    labels = [i[0] for i in topDomains]

    domainChart = BarChart(values, labels)
    domainChart.saveAsPNG("chart.png")



def PublicIPv4Address():
    addressServiceURL = "http://api.ipify.org?format=json"
    try:
        page = urllib2.urlopen(addressServiceURL)
        json = simplejson.load(page)
        address = json["ip"]
        return address
    except:
        print("Could not determine, public IP address, exiting...")
        sys.exit()



if __name__ == "__main__":
    ApplicationEntryPoint()
