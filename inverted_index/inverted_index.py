import os
from bs4 import BeautifulSoup
import pickle
from nltk.stem import PorterStemmer
from collections import Counter
import helpers
import json
import postings

class InvertedIndex:
    """
    Class used to create an inverted index from the given directory
    """
    def __init__(self):
        self.docID: int = 0
        self.stopWords = helpers.stopWords()
        self.urlDict = {}
        self.invertedIndex = {} 

    def readFile(self, path):
        """
        :param path: string - file paths to open from directory
        :return soup.get_text(): string - content left from removing the html
        """

        with open(path, 'r') as f:
            data = json.load(f)
            content = data['content']
            soup = BeautifulSoup(content, 'lxml-xml')
            text = soup.get_text() #filter out html

            url = data['url'] #get url
        return text, url

    def processText(self, text):
        """
        processText method tokenizes text taken from the readFile method and returns the list of tokens
        :param text: string
        :return: list
        """
        position: int = 0
        wordList = helpers.tokenize(text) #tokenizes the text
        ps = PorterStemmer()
        wordList = [ps.stem(word) for word in wordList] #make a list of just the stem of the words

        return wordList

    def wordFrequencies(self, textList: list)->dict:
        words = {}
        for word in textList:
            if word not in words:
                words[word] = postings.Postings()
                words[word] = posting
            else:
                words[word] += 1
        
        for pos in range(textList):
            words[textList[pos]]

    def buildIndex(self, textList, url):
        """
        creates an inverted index of the document that is passed in and updates the document id index(URL dict)
        :param textList: content of the passed in document
        :return: dict - dictionary of words and the amount of times they appear in a document
        """

        docIndex = {} #initialize a dictionary for the document
        countDict = Counter(textList) #get a dictionary in the format of {token:appearances in the doc}
        docID = f"DocID: {self.docID}"

        #create the inverted index for the document
        for key, value in countDict.items():
            docIndex[key] = [(docID, value)]

        #keep track of the url with the document ID
        self.urlDict[docID] = url
        self.docID += 1

        return docIndex

    def updateIndex(self, docIndex):
        """
        updates the inverted index
        :param docIndex:
        :return:
        """
        #traverse the document index
        for key, value in docIndex.items():
            #if the token is found in the Inverted index then append to the keys values
            if key in self.invertedIndex:
                self.invertedIndex[key].append(value)
            #if token isnt found -> create new key in inverted index
            if key not in self.invertedIndex:
                self.invertedIndex[key] = value

    def store(self, content, fileName):
        """
                Stores the inverted index/urlDict into a pickle file
                :param freqDict: dict
                :return: none
                """
        with open(fileName, 'wb') as file:
            pickle.dump(content,file, protocol= pickle.HIGHEST_PROTOCOL)

    def calculateTF(self): #implement later
        """
        Calculate TF score
        :return:
        """
        pass

    def getinvertedIndex(self):
        """
        Getter function for the inverted index
        :return: dict
        """
        return self.invertedIndex

    def docIndex(self):
        """
        Getter function for document indexes
        :return: dict
        """
        return self.urlDict

    def Run(self):
        """
        The return method handles the main logic of this program
        :return: None
        """
        #assuming the DEV folder is in the same directory as the code
        path = r"DEV"
        #traverse the files in the DEV directory
        for subdir, dir, files in os.walk(path):
            for f in files:
                file = os.path.join(subdir, f) #create file path
                text, url = self.readFile(file) #read the file
                processedTextList = self.processText(text) #process the text
                docIndex = self.buildIndex(processedTextList, url) #build the inverted index for the single document
                self.updateIndex(docIndex) #update the actual Inverted Index
                print(f"{self.docID}:{url}")
            #store content that was retrieved
            self.store(self.invertedIndex, "inverted_index.pickle")
            self.store(self.urlDict,"url_index.pickle")

        print(f"Report:\n"
              f"Word Count: {len(self.invertedIndex.keys())}\n"
              f"Unique Pages: {self.docID}")

if __name__ == '__main__':
    inverted_index = InvertedIndex()
    inverted_index.Run()
