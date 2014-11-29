#!/usr/bin/env python

from __future__ import print_function
import os, sys, getopt
import urllib2
import simplejson
import time
from serviceTokens import *

from ConfigBundle import *
from Document import *
from Crawler import *
from Visualization import *

#import global variable defined in ConfigBundle module
global applicationConfig


##  @package Main application package
#   This is the main application package and the application entry point.


#Google search various base URL configurations
#basic search
GoogleBaseSearchURLSimple = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&userip={0}&q={1}"
#limit results to pages from Greece
GoogleBaseSearchURLfromGreece = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&tbs=ctr:countryGR&cr=countryGR&userip={0}&q={1}"
#limit results to pages in Greek
GoogleBaseSearchURLinGreek = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&tbs=lr:lang_1el&lr=lang_el&userip={0}&q={1}"
#limit results to pages in Greek and from Greece
GoogleBaseSearchURLfromGreeceInGreek = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&cr=countryGR&tbas=0&tbs=ctr:countryGR,lr:lang_1el&lr=lang_el&userip={0}&q={1}"

#Readability service URL
readabilityBaseURL = "https://www.readability.com/api/content/v1/parser?url={0}&token={1}"

#Yahoo! search base URL
yahooBaseURL = "http://yboss.yahooapis.com/ysearch/web"

#Help message/usage options
usage = 'Usage: Application.py -m <punctuation marks file> -w <words to ignore file> -l <article links file> [-o <output directory>]'


##  This is the main application function
def ApplicationEntryPoint(argv):

    #first we will load some default values for our configuration
    #various configuration options
    applicationConfig.termsToSearch = 10
    applicationConfig.publicAddress = PublicIPAddress();

    #google search related options
    applicationConfig.resultsToExamine = 50 #must be a multiple of 10. 50 match yahoo's result count
    applicationConfig.GoogleURL = GoogleBaseSearchURLfromGreeceInGreek
    applicationConfig.userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"
    applicationConfig.crawlerFetchTimeout = 2 #seconds
    applicationConfig.queryDelay = 5 #seconds

    #readability related options
    applicationConfig.readabilityToken = readabilityToken
    applicationConfig.readabilityBaseURL = readabilityBaseURL

    #yahoo related options
    applicationConfig.ybossURL = yahooBaseURL
    applicationConfig.ybossOAuthKey = yboss_oauth_key
    applicationConfig.ybossOAuthSecret = yboss_oauth_secret

    #data exporting/chart creation options
    applicationConfig.chartSubtitle = "News stories count"


    #now we will parse our command line arguments for our input/run data
    articleLinksFilename = ''       #file that contains links to various news articles
    punctuationMarksFilename = ''   #file that contains punctuation marks to strip
    ignoredWordsFilename = ''       #file that contains the words to ignore
    outputDirectory = 'output' #default

    try:
        opts, args = getopt.getopt(argv[1:], "hm:w:l:o:", [])
    #if an invalid option/switch is supplied or a value is missing from a switch that requires a value
    except getopt.GetoptError:
        print(usage)
        sys.exit(-1)

    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit(0)
        elif opt == '-m':
            punctuationMarksFilename = arg
        elif opt == '-w':
            ignoredWordsFilename = arg
        elif opt == '-l':
            articleLinksFilename = arg
        elif opt == '-o':
            outputDirectory = arg

    #if additional debug output is requested print the supplied filenames
    if applicationConfig.debugOutput is True:
        print("Start options are:")
        print("\tpunctuation marks file:", punctuationMarksFilename)
        print("\tignored words file:", ignoredWordsFilename)
        print("\tarticle links file:", articleLinksFilename)
        print("\toutput directory:", outputDirectory)

    #if one of the required options is missing, we cannot proceed
    if len(articleLinksFilename) == 0 or len(punctuationMarksFilename) == 0 or len(ignoredWordsFilename) == 0:
        print(usage)
        sys.exit(-1)

    #settings for parsing article contents
    parsingSettings = DocumentParsingSettings(punctuationMarksFilename, ignoredWordsFilename, 4)

    #output files
    domainsFilename = outputDirectory + '/domains.txt'
    postsFilename = outputDirectory + '/posts.txt'
    chartFilename = outputDirectory + '/chart' #don't add an extension, it will be added automatically based on the type!

    #load article links from the file
    articleLinks = []
    try:
        file = open(articleLinksFilename, "rU")
        chartTitle = file.readline() #we read the first line that contains the chart title
        for line in file: #for the remainder lines that contain links
            articleLinks.append(line)
    except IOError as exc:
        print("Error reading from file:", articeLinksFilename, exc.strerror)
        sys.exit()
    finally:
        file.close()

    #now this is the main loop
    #for every link/article that is supplied, we launch a crawler and we search for related articles
    domains = {}
    for link in articleLinks:
        try:
            crawler = Crawler.FromLink(link[:-1], parsingSettings) #create crawler
        except CrawlerError as exc:
                print("Error getting initial content from article:", link)

        if crawler is not None:
            crawler.outputFile = postsFilename
            crawler.SearchYahoo() #search
            #crawler.SearchGoogle()
            crawler.SaveFoundPosts() #and save complete URls to a file
        else:
            print("Error building crawler for article:", link)
            continue

        #additionally save the domains so we can track which domains have published multiple articles
        for domain in crawler.domains:
            if domain in domains:
                domains[domain] += 1
            else:
                domains[domain] = 1

    if len(domains) == 0: #no results :(
        print("A serious error occured and there are no results")
        sys.exit(0)

    #domains is a dictionary. first we have to convert it to a tupple list
    domainsList = []
    for key, value in domains.iteritems():
        tmp = [key, value]
        domainsList.append(tmp)

    #sort domains in reverse (most occurences) order
    domainsSortedByOccurences = sorted(domainsList, key=lambda tup: tup[1], reverse=True) #output is a list

    #we will save all these data ([domains, occurences]) in a file for future use
    try:
        file = open(domainsFilename, "w")
        for domain in domainsSortedByOccurences:
            file.write(domain[0] + ' ' + str(domain[1]) + '\n')
            print(domain[0], str(domain[1]))
    except IOError as exc:
        print("Error saving list of domains to file:", domainsFilename, exc.strerror)
    finally:
        file.close()

    #from the complete list extract the top 10 to use them in the cart
    topDomainsSortedByOccurences = domainsSortedByOccurences[:10] #now we have top 10 domains based on occurences

    #now we have to sort that alphabetically for the chart
    topDomainsSortedAlphabetically = sorted(topDomainsSortedByOccurences, key=lambda tup: tup[0])

    #print collected data
    if applicationConfig.debugOutput is True:
        for domain in topDomainsSortedAlphabetically:
            print (domain[0], domain[1])

    #create a bar chart to display the domains
    values = [i[1] for i in topDomainsSortedAlphabetically]
    labels = [i[0] for i in topDomainsSortedAlphabetically]
    for i in range(0, len(labels)):
        print(labels[i], values[i])
    domainChart = BarChart(chartTitle, values, labels)

    #and finally save the chart
    domainChart.saveAsPNG(chartFilename)
    domainChart.saveAsSVG(chartFilename)



##  Determines what our public IP address is
#   @return     Our public IP address
def PublicIPAddress():
    #in order to determine our address we will query a service that reports this
    addressServiceURL = "http://api.ipify.org?format=json"
    try:
        page = urllib2.urlopen(addressServiceURL)
        json = simplejson.load(page)
        address = json["ip"]
        return address
    except:
        print("Could not determine, public IP address, exiting...")
        sys.exit()



#enter the main application function and pass along all command line arguments
if __name__ == "__main__":
    ApplicationEntryPoint(sys.argv)
