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
        self.path: dict = {}

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

    def wordPostings(self, textList: list)->dict:
        words: dict = {}
        for i in range(len(textList)):
            if textList[i] not in words:
                words[textList[i]] = [postings.Postings()]
                words[textList[i]][0].frequs = 1
                words[textList[i]][0].docID = self.docID
            else:
                words[textList[i]][0].frequs += 1
            words[textList[i]][0].pos.append(i)

        self.calculateTF(words, len(textList))
        return words

    def buildIndex(self, wordposts: dict, url: str):
        """
        creates an inverted index of the document that is passed in and updates the document id index(URL dict)
        :param textList: content of the passed in document
        :return: dict - dictionary of words and the amount of times they appear in a document
        """
        for word in wordposts:
            path = self.path[word[0]]
            if os.path.isfile(path) == False:
                with open(path, "wb") as f:
                    index: dict = {}
                    index[word] = wordposts[word]
                    pickle.dump(index, f)
                    f.close()
            else:
                with open(path, "rb+") as f:
                    index: dict = pickle.load(f)
                    self.updateFile(word, wordposts, index)
                    f.seek(0)
                    pickle.dump(index, f)
                f.close()

        #keep track of the url with the document ID
        self.urlDict[self.docID] = url
        self.docID += 1

    def updateFile(self, word: str, src: dict, dest: dict)->None:
        """
        updateFile updates the dest param with info contained in src param
        param: src key, src dict, dest dict
        Void function
        """
        if word not in dest:
            dest[word] = src[word]
        else:
            dest[word].append(src[word][0])

    def calculateTF(self, wordsDict: dict, total_doc_tokens)->None:
        """
        Calculate TF score
        param: dict, int 
        :return:
        """
        for key in wordsDict:
            frequencies = wordsDict[key][0].frequs
            wordsDict[key][0].tf = (frequencies / total_doc_tokens)
    
    def calculateIDF(self)->None:
        """
        calculateIDF calculates the idf score for each term in the
        posting. It gets deployed after the index is built and docID
        is the value of the last document searched which repesents the
        nth document in the index. 
        param: None
        return: None
        """
        total_docs = self.docID #docID will be the nth doc
        for i in range(26): # total letters in alphabet
            letter = chr(ord('a') + i)
            path = self.path[letter]
            # check if path exists first
            if os.path.isfile(path):
                with open(path, "rb") as f:
                    letter_index = pickle.load(f)
                    # each word is the key in the partial index
                    for word in letter_index:
                        total_word_app = len(letter_index[word]) # total appearance in n docs
                        idf_score = log(total_docs / total_word_app)
                        # each post is Posting() struct that will have the new idf score
                        for post in letter_index[word]:
                            post.idf = idf_score
                    f.close()
        
        for i in range(10):
            path = self.path[i]

            if os.path.isfile(path):
                with open(path, "rb") as f:
                    numbers_index = pickle.load(f)
                    
                    for num in numbers_index:
                        total_num_apps = len(numbers_index[num])
                        idf_score = log(total_docs / total_num_apps)

                        for post in numbers_index[num]:
                            post.idf = idf_score
                    f.close()

    def alphaToPath(self)->None:
        """
        Func: modifies the self.path dict so that it maps lowers case
        letters to a file path contain terms that start with the key.
        param: None
        return: None
        """
        for i in range(26):
            letter = str(chr(ord('a') + i))
            self.path[letter] = "./pickle/" + letter + ".pickle"
            if i < 10:
                self.path[str(i)] = "./pickle/numbers.pickle"

    def store(self, content, fileName):
        """
                Stores the inverted index/urlDict into a pickle file
                :param freqDict: dict
                :return: none
                """
        with open(fileName, 'wb') as file:
            pickle.dump(content,file, protocol= pickle.HIGHEST_PROTOCOL)

    def docIndex(self):
        """
        Getter function for document indexes
        :return: dict
        """
        return self.urlDict

    def clearIndex(self)->None:
        alpha = {}
        for i in range(26):
            letter = chr(ord('a') + i)
            alpha[letter] = "./pickle/" + letter + ".pickle"

        for key in alpha:
            clear: dict = {}
            with open(alpha[key], "wb") as f:
                pickle.dump(clear, f)
                f.close()
            print(os.path.getsize(alpha[key]))

    def Run(self):
        """
        The return method handles the main logic of this program
        :return: None
        """
        #assuming the DEV folder is in the same directory as the code
        path = r"/home/anvieyra/cs121/space-time-crawler/index/DEV"

        self.alphaToPath() #creates mapping to pickle files
        #traverse the files in the DEV directory
        for subdir, dir, files in os.walk(path):
            for f in files:
                file = os.path.join(subdir, f) #create file path
                text, url = self.readFile(file) #read the file
                processedTextList = self.processText(text) #process the text into a word list
                wordposts = self.wordPostings(processedTextList)
                docIndex = self.buildIndex(wordposts, url) #build the inverted index for the single document
                print(f"{self.docID}:{url}")
            #store content that was retrieved
            self.store(self.urlDict,"./pickle/url_index.pickle")
        self.calculateIDF()

if __name__ == '__main__':
    inverted_index = InvertedIndex()
    inverted_index.Run()
