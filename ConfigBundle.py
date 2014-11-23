#!/usr/bin/env python

##  @package ConfigBundle
#   This package provides a class for holding all configuration parameters together
#   in a single object.

##  This class provides an object for encapsulating all configuration options.
#
#   An object of this type is initialized upon application launch, configured appropriately,
#   and then it is referenced by all other modules.
class ConfigBundle:
    def __init__(self):

        #   Various options

        ##  @var debugOutput
        #   Flag wether additional output assisting in debugging should be printed
        self.debugOutput = False

        ##  @var termsToSearch
        #   How many terms to use for constructing the search query
        self.termsToSearch = 0

        ##  @var chartSubtitle
        #   Subtitle/ledge to use in exported charts
        self.chartSubtitle = ""


        #   The following options affecting Google search

        ##  @var GoogleURL
        #   Base URL for Google search
        self.GoogleURL = ""

        ##  @var GoogleResultsToExamine
        #   How many results to request. Has to be a multiple of 10
        self.GoogleResultsToExamine = 0

        ##  @var userAgent
        #   User agent to report in requests
        self.userAgent = ""

        ##  @var queryDealy
        #   Interval between requests, trying to fool Google bot detection
        self.queryDelay = 0

        ##  @var publicAddress
        #   Our public IP Address
        self.publicAddress = ""


        #   Configuration of Readability service

        ##  @var readabilityBaseURL
        #   Base URL for Readability service
        self.readabilityBaseURL = ""

        ##  @var readabilityToken
        #   Secret token for authenticating with Readability
        self.readabilityToken = ""


        #   Configuration of Yahoo! BOSS search

        ##  @var ybossURL
        #   Base URL for Yahoo! search
        self.ybossURL = ""

        ##  @var ybossOauthKey
        #   OAuth key for Yahoo! BOSS authentication
        self.ybossOAuthKey = ""

        ##  @var ybossOAuthSecret
        #   OAuth secret for Yahoo! BOSS authentication
        self.ybossOAuthSecret = ""



##      Globally shared instance of configuration object
applicationConfig = ConfigBundle()



#there is nothing to run directly from here
if __name__ == "__main__":
    print("Nothing to run here! Execute the main application file instead!")
