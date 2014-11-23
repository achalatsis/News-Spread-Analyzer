#!/usr/bin/env python

from __future__ import print_function
import sys
import math
import re
import string
from operator import itemgetter
from ConfigBundle import *
from urlparse import *
import simplejson


global applicationConfig



#class for storing parsing settings
class DocumentParsingSettings:
    def __init__(self, punctuationMarksFilename, ignoredWordsFilename, minLength):
        self.minLength = minLength
        self.punctuationMarks = []
        self.ignoredWords = []

        if applicationConfig.debugOutput is True:
            print("Will load default parsing settings from {0}, {1}".format(punctuationMarksFilename, ignoredWordsFilename))

        #try to load default words that are not counted
        try:
            defaultWordsTxt = Document.FromFile(ignoredWordsFilename)
            self.ignoredWords = defaultWordsTxt.text.split()

            defaultPunctuationMarks = Document.FromFile(punctuationMarksFilename)
            self.punctuationMarks = defaultPunctuationMarks.text.split()
        except IOError as exc:
            print("Error reading from file: {0}".format(exc.strerror))
            raise

        if applicationConfig.debugOutput is True:
            print("The following words will not be counted:", end=" ")
            for word in self.ignoredWords:
                print(word, end=" ")
            print("\nThe following punctuation marks will be stripped:", end=" ")
            for punctuationMark in self.punctuationMarks:
                print(punctuationMark, end=" ")
            print("\n")



#class for storing documents and providing parsing methods
class Document:
    def __init__(self, text):
        self.text = text
        self.words = []
        self.tf = []
        self.frequencies = []


    @staticmethod
    def FromFile(filename):
        text = ""
        try:
            file = open(filename, "rU")
            for line in file:
                text += line
        except IOError as exc:
            print("Error reading from file: ", exc.strerror)
            raise
        finally:
            file.close()

        newDoc = Document(text)
        return newDoc


    def CalculateTF(self, parsingSettings, returnPart, termsWanted):
        rawWords = self.text.lower().split()
        frequencies = {}
        for word in rawWords:
            for punctuationMark in parsingSettings.punctuationMarks: #strip characters
                if punctuationMark in word:
                    word = word.replace(punctuationMark, "")
            if word not in parsingSettings.ignoredWords and len(word) >= parsingSettings.minLength: #check if in (common) words to ignore
                self.words.append(word)
                if word in frequencies:
                    frequencies[word] += 1
                else:
                    frequencies[word] = 1

        #convert the word array & the frequency dict in an array of arrays
        for word, count in frequencies.items():
            tmp = [word, count]
            self.tf.append(tmp)

        sortedTF = sorted(self.tf, key=lambda tup: tup[1], reverse=True)
        if returnPart is True:
            return sortedTF[:termsWanted]
        else:
            return sortedTF



if __name__ == "__main__":
    print("Nothing to run here! Execute the main application file instead!")
