import os
from bs4 import BeautifulSoup
import pickle
from nltk.stem import PorterStemmer
from collections import Counter
import sys
import helpers
import json
import lxml

class InvertedIndex:
    """
    Class used to create an inverted index from the given directory
    """
    def __init__(self):
        self.docID = 0
        self.stopWords = helpers.stopWords()
        self.dict = dict()

    def readFile(self, path):
        """
        :param path: string - file paths to open from directory
        :return soup.get_text(): string - content left from removing the html
        """
        with open(path, 'r') as f:
            data = json.load(f)
            content = data['content']
            soup = BeautifulSoup(content, 'lxml-xml')
        return soup.get_text()

    def processText(self, text):
        """
        processText method tokenizes text taken from the readFile method and returns the list of tokens
        :param text: string
        :return: list
        """
        #noSW_list = [] #sw stands for stopwords
        wordList = helpers.tokenize(text) #import tokenize function helper functions later
        # for words in wordList:
        #     if words not in self.stopWords:
        #         noSW_list.append(words)

        # ps = PorterStemmer()
        # processedTextList = []
        # for i in noSW_list:
        #     processedTextList.append(ps.stem(i))

        return wordList #processedTextList

    def frequency(self, textList):
        """
        The frequency method takes the textList and counts how many times a token appears and puts it into a dictionary
        :param textList:
        :return: dict - dictionary of words and the amount of times they appear in a document
        """
        freq_dict = dict()
        for word in textList:
            if word in freq_dict:
                freq_dict[word] += 1
            else:
                freq_dict[word] = 1
        return freq_dict

#merges all the docs into one file to make the inverted index(not sure if this function is needed at the moment)
    def mergeSort(self):
        """
        unsure
        :return:
        """
        pass

#takes frequencies and stores it into a file with its docID by using pickle
    def store(self, freqDict):
        """
        Stores the inverted index into a pickle file
        :param freqDict: dict
        :return: none
        """
        self.docID += 1
        newDict = dict()
        newDict[freqDict.keys()] = [(f"DocID:{self.docID}",freqDict.values())] #incorrectly done but place holder for now
        self.dict.update(newDict)
        with open("inverted_index.p", 'wb') as file:
            pickle.dump(newDict, file)

    def getIndex(self):
        """
        getIndex reads the inverted_index pickle file and returns the inverted index
        :return: dict - index
        """
        with open("inverted_index.p", "r")as file:
            index = pickle.load(file)
        return index


#deals with the main logic
    def Run(self):
        """
        The return method handles the main logic of this program
        :return: None
        """
        # change filepath = sys.argv[1] to run in terminal by running "python inverted_index.py [file/path]"
        path = ""
        for subdir, dir, files in os.walk(path):
            for f in files:
                file = os.path.join(subdir, f)
                text = self.readFile(file)
                processedTextList = self.processText(text)
                freqDict = self.frequency(processedTextList)
                self.store(freqDict)
        print(f"Reported:\n"
              f"Unique words: {len(self.dict.keys())}"
              f"Total documents: {self.docID}")


if __name__ == '__main__':
    #change later to get input from terminal
    inverted_index = InvertedIndex()
    inverted_index.Run()