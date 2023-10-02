import os
from bs4 import BeautifulSoup
import pickle
from nltk.stem import PorterStemmer
from collections import Counter
import helpers
import json
import sys

class InvertedIndex:
    """
    Class used to create an inverted index from the given directory
    """
    def __init__(self):
        self.docID: int = 0
        self.urlDict = {}
        self.path: dict = {}
        self.key_positions = {}
        self.important_terms = {}
        self.pre_files_path = '../pre_index_files'
        self.index_file = '../final_index_files/full_index.txt'

    def readFile(self, path: str):
        """
        readFile method reads the file and returns the content of the file
        :param path: string - file paths to directory
        :return text: string - content of the file, url: string - url of the file, 
        importantText: string - content of the file that is deemed important
        """
        with open(path, 'r') as f:
            importantText = ''
            data = json.load(f)
            content = data['content']
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text() #filter out html

            url = data['url'] #get url

            for title in soup.find_all('title'):
                importantText += title.text.strip() + ' '
            for strong in soup.find_all("strong"):
                importantText += strong.text.strip() + ' '
            for bold in soup.find_all("b"):
                importantText += bold.text.strip() + ' '
            heading_tags = ["h1", "h2", "h3"]
            for heading in soup.find_all(heading_tags):
                importantText += heading.text.strip() + ' '

        return text, url, importantText

    def processText(self, text: str)->list:
        """
        processText method tokenizes the text and returns a list of tokens. 
        It also stems the words.
        :param text: string - content of the file
        :return: list - list of tokens
        """
        wordList = helpers.tokenize(text) #tokenizes the text
        ps = PorterStemmer()
        wordList = [ps.stem(word) for word in wordList] #make a list of just the stem of the words
        return wordList

    def wordPostings(self, index: dict, textList: list)->None:
        """
        wordPostings method records the frequency of the words in the document 
        and updates the inverted index accordingly.
        :param: index: dict - inverted index, textList: list - list of tokens
        :return: None
        """
        for i in range(len(textList)):
            if textList[i] not in index:
                index[textList[i]] = {self.docID: 0}
            if self.docID not in index[textList[i]]:
                index[textList[i]][self.docID] = 0
            index[textList[i]][self.docID] += 1 # update frequency

    def build_pre_partial_index(self, wordposts: dict, url: str):
        """
        creates an inverted index of the document that is passed in and updates the 
        document id index(URL dict)
        :param: wordposts: dict - dictionary of words and the amount of times they appear in a document, 
        url: string - url of the document
        :return: None
        """
        for word in wordposts:
            path = self.path[word[0]]
            with open(path, 'a') as file:
                file.write(json.dumps({word: wordposts[word]}) + '\n')

    def alphaToPath(self)->None:
        """
        alphaToPath method maps the letters of the alphabet to the path of the pickle 
        files that contain the inverted index of the words that start with that
        letter. It also maps the numbers to the path of the pickle file that contains 
        the inverted index of the numbers.
        :param: None
        :return: None
        """
        for i in range(26):
            letter = str(chr(ord('a') + i))
            self.path[letter] = "../pre_index_files/" + letter + ".txt"
            if i < 10:
                self.path[str(i)] = "../pre_index_files/numbers.txt"

    def docIndex(self):
        """
        docIndex method returns the document id index
        :return: dict - document id index
        """
        return self.urlDict

    def store(self, content, fileName):
        """
        Stores the content into a pickle file
        :param: content: the content to be stored, fileName: the name of the file
        :return: none
        """
        with open(fileName, 'wb') as file:
            pickle.dump(content,file, protocol= pickle.HIGHEST_PROTOCOL)

    def store_important_text(self,importantText: list)->None:
        """
        Stores the important text into a dict - important_terms 
        :param: importantText: list of important text
        return: None
        """
        for word in importantText:
            if word not in self.important_terms:
                self.important_terms[word] = set()
            if self.docID not in self.important_terms[word]:
                self.important_terms[word].add(self.docID)
    
    def sort_files(self, directory: str)->None:
        """
        Sorts the files in the directory. 
        :param: directory: the directory of the files to be sorted
        return: None
        """
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    terms = {}
                    with open(file_path, 'r') as file:
                        for line in file:
                            d = json.loads(line.strip())
                            for key in d:
                                if key not in terms:
                                    print("\n------ " + key + " -------\n")
                                    terms[key] = d[key]
                                for val in d[key]:
                                    if val not in terms[key]:
                                        terms[key][val] = d[key][val]

                    self.store_into_index(self.index_file, terms)

    def store_into_index(self, index_file: str, pindex: dict)->None:
        """
        Stores the partial index into the index file. 
        :param: index_file: the index file to be stored into, pindex: the partial index
        return: None
        """
        with open(index_file, 'a') as file:
            for key, value in pindex.items():
                position = file.tell()
                file.write(json.dumps({key:value}) + '\n')
                self.key_positions[key] = position
    
    def Run(self):
        """
        Run method traverses the DEV directory and creates an inverted index of the files stored. 
        It also creates a document id index and stores it in a pickle file.
        :param: None
        :return: None
        """
        #assuming the DEV folder is in the same directory as the code
        path = r"/home/anvieyra/cs121/space-time-crawler/index/DEV"
        partial_index: dict = {}
        self.alphaToPath() #creates mapping to pickle files
        #traverse the files in the DEV directory
        for subdir, dir, files in os.walk(path):
            for f in files:
                file = os.path.join(subdir, f) #create file path
                text, url, importantText = self.readFile(file) #read the file
                processedTextList = self.processText(text) #process the text
                processedImportantTextList = self.processText(importantText) #process the important text
                self.store_important_text(processedImportantTextList)
                self.wordPostings(partial_index, processedTextList) #modifies the partial index
                self.urlDict[self.docID] = url
                self.docID += 1
                print(f"{self.docID}:{url}")

                # hold 10 megabytes worth of data before clearing
                if sys.getsizeof(partial_index) >= 10000000:
                    print("\n\n-----------MAX CAPACITY------------")
                    print(sys.getsizeof(partial_index))
                    self.build_pre_partial_index(partial_index, url) #build the inverted index for the single document
                    print("-----------------------------------\n\n")
                    partial_index = {}

        #store content that was retrieved
        self.store(self.urlDict,"../final_index_files/url_index.pickle")
        self.store(self.important_terms, "../final_index_files/important_terms.pickle")
        self.sort_files(self.pre_files_path)
        self.store(self.key_positions, "../final_index_files/key_positions.pickle")

if __name__ == '__main__':
    inverted_index = InvertedIndex()
    inverted_index.Run()