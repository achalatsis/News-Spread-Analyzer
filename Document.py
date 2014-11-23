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



##  @package Document
#   Provides operations on pieces of text/documents


#import global variable defined in ConfigBundle module
global applicationConfig



##  This class provides an object that unifies all extra data needed for document parsing
#
#   This object contains any punctuation marks that will be stripped from articles, along
#   with any common words that should be prevented from appearing as keywords (due to their frequency)
class DocumentParsingSettings:

    ##  Initializes a new object and loads the data from the supplied files
    #   @param      punctuationMarksFilename        The file to load the punctuation marks from
    #   @param      ignoredWordsFilename            The file to load the words to ignore from
    #   @param      minLength                       Minimum acceptable length for a word
    def __init__(self, punctuationMarksFilename, ignoredWordsFilename, minLength):

        ##  @var minLength
        #   Minimum length for a word to take it into account
        self.minLength = minLength

        ##  @var punctuationMarks
        #   Punctuation marks to strip from content
        self.punctuationMarks = []

        ##  @var ignoredWords
        #   Words to explicitly not take into account
        self.ignoredWords = []

        #if additional debug output is requested, print the filenames
        if applicationConfig.debugOutput is True:
            print("Will load default parsing settings from {0}, {1}".format(punctuationMarksFilename, ignoredWordsFilename))

        #read the data from the files supplied
        try:
            defaultWordsTxt = Document.FromFile(ignoredWordsFilename)
            self.ignoredWords = defaultWordsTxt.text.split()

            defaultPunctuationMarks = Document.FromFile(punctuationMarksFilename)
            self.punctuationMarks = defaultPunctuationMarks.text.split()
        #things that can go wrong here are filesystem-related (very rarely device-related)
        except IOError as exc:
            print("Error reading from file: {0}".format(exc.strerror))
            raise

        #if additional debug output is requested, print the punctuation marks and the wods to ignore
        if applicationConfig.debugOutput is True:
            print("The following words will not be counted:", end=" ")
            for word in self.ignoredWords:
                print(word, end=" ")
            print("\nThe following punctuation marks will be stripped:", end=" ")
            for punctuationMark in self.punctuationMarks:
                print(punctuationMark, end=" ")
            print("\n")



##  Common text(file) related operations
#
#   This implements text file loading along with TF metrics.
class Document:

    ##  Initialize a new Document
    #   @param      text        The text
    def __init__(self, text):

        ##  @var text
        #   The loaded text
        self.text = text

        ##  @var words
        #   The text splitted in words
        self.words = []

        ##  @var tf
        #   Frequency of appearance for each word
        self.tf = []


    ##  Method for loading text from a file
    #   @param      filename        The name of the file to load text from
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

        #after we have successfully loaded text from a file, create a new Document object
        newDoc = Document(text)
        return newDoc


    ##  Calculate term-frequency table
    #   @param      parsingSettings     Parse the document with these settings
    #   @param      returnPart          Boolean variable indicating wether to return a part of the calculated table or the complete table
    #   @param      termsWanted         If a partial table is requested, size of the table
    def CalculateTF(self, parsingSettings, returnPart, termsWanted):
        rawWords = self.text.lower().split() #spit the text into words
        frequencies = {}
        for word in rawWords:
            for punctuationMark in parsingSettings.punctuationMarks: #strip characters
                if punctuationMark in word:
                    word = word.replace(punctuationMark, "")
            if word not in parsingSettings.ignoredWords and len(word) >= parsingSettings.minLength: #check if in (common) words to ignore
                self.words.append(word)
                if word in frequencies:
                    frequencies[word] += 1 #increment occurences
                else:
                    frequencies[word] = 1 #add to dictionary

        #convert the word array & the frequency dict in an array of arrays
        for word, count in frequencies.items():
            tmp = [word, count]
            self.tf.append(tmp)

        sortedTF = sorted(self.tf, key=lambda tup: tup[1], reverse=True)
        if returnPart is True: #if a partial table is requested
            return sortedTF[:termsWanted]
        else:
            return sortedTF



#nothing to run directly from here
if __name__ == "__main__":
    print("Nothing to run here! Execute the main application file instead!")
