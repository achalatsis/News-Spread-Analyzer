#!/usr/bin/env python



class ConfigBundle:
    def __init__(self):
        self.debugOutput = False

        self.termsToSearch = 0
        self.userAgent = ""

        self.publicAddress = ""
        self.queryDelay = 0

        self.readabilityToken = ""
        self.readabilityBaseURL = ""

        self.ybossURL = ""
        self.ybossOAuthKey = ""
        self.ybossOAuthSecret = ""



applicationConfig = ConfigBundle()



if __name__ == "__main__":
    print("Nothing to run here! Execute the main application file instead!")
