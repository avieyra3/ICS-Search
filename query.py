import helpers
from inverted_index import InvertedIndex
import pickle
import os
import json
import math
import time
from nltk.corpus import stopwords

class Query:
    def __init__(self):
        #funself.stopWords = stopwords.txt
        self.urls = self.loadURL()
        self.important_terms = self.load_important_terms()
        self.key_positions = self.load_key_positions()
        self.index_file = '../final_index_files/full_index.txt'
        self.stopWords = set(stopwords.words('english'))
        
    def loadURL(self)->dict:
        """
        Loads the urls into a dict where the key is the docid.
        param: None
        return: a dictionary
        """
        with open("../final_index_files/url_index.pickle", "rb") as f:
            urls = pickle.load(f)
        return urls

    def load_important_terms(self)->dict:
        """
        Loads the important terms into a dict where values are a set of docID's
        param: None
        return: a dictionary
        """
        with open("../final_index_files/important_terms.pickle", "rb") as f:
            text = pickle.load(f)
        return text

    def load_key_positions(self)->dict:
        """
        Loads the key_positions into a dict.
        param: None
        return: dictionary
        """
        with open("../final_index_files/key_positions.pickle", "rb") as f:
            keys = pickle.load(f)
        return keys

    def get_termDict_frequency_in_doc(self, termDict: dict, term: str, doc_id: int)->int:
        """
        This function gets the frequencies of a specific term in a specific doc
        param: word str, doc_id int 
        return: an int frequencies or -1 on error
        example: termDict[term][doc_id][0] = frequencies
        """
        doc_id = str(doc_id)
        if doc_id in termDict[term]:
            return termDict[doc_id]
        else:
            return -1

    def total_num_docs_in_corpus(self)->int:
        """
        returns the total number of documents in the corpus
        param: none
        return: int
        """
        return len(self.urls)

    def total_docs_in_termDict(self, termDict: dict, term: str)->int:
        """
        return the total number of documents a term is featured in.
        param: data - dictionary containing terms and their postings
               word - a string that is the term itself.
        return: int 
        """
        return len(termDict[term])

    def get_termsDict(self, textList: list)->dict:
        """
        fetches the data from the index for each word in textList.
        param: list of words
        return: a dict with the token words and their postings
        Example: data = {'term1': {'docid': [posting]}, 'term2': 
            {'docid': [posting]}}
        """
        data = {}
        with open(self.index_file, 'r') as file:
            for word in textList:
                if word in self.key_positions:
                    file.seek(self.key_positions[word])
                    line = file.readline()
                    term = json.loads(line.strip())
                    for key in term:
                        if key not in data:
                            data[key] = term[key]
        return data

    def get_idf(self, termDict: dict, term: str)->float:
        """
        This calculates the inverted document frequency.
        param: termDict - a dict containg the terms.
               term - the term want to measure for idf
        return: idf - a float 
        """
        if term in termDict.keys():
            return math.log(len(self.urls) / len(termDict[term]))
        else:
            return 0

    def get_docIDs(self, termDict: dict, term: str)->set:
        """
        This grabs the document IDs associated with a term in the 
        inverted index
        param: termDict - a dict containing the words
            term - the term you want to grab the DocIDs for
        return: term-docIds - a set
        """
        term_docIds = set(termDict[term].keys())
        return term_docIds

    def Run(self):
        """
        This calculates the weights for the query and documents 
        and then sorts them so that the 5 best matching pages
        are printed out.
        """
        while True:
            response = str(input("Type in your Query: ")) # get user input
            start_time = time.time() #start timer
            #queryList = [word for word in queryList if not word in self.stopWords]
            queryList = InvertedIndex.processText(self, response) #processing text, put terms in list
            queryList = [word for word in queryList if word not in self.stopWords]
            data = self.get_termsDict(queryList) #get postings for terms

            #calculating weight for query
            queryTerms = {}
            for term in queryList:
                queryTermCount = queryList.count(term) 
                qTF = 1 + math.log(queryTermCount)
                qIDF = self.get_idf(data, term)
                qWeight = qTF * qIDF
                if term not in queryTerms and qWeight != 0:
                    queryTerms[term] = qWeight

            #normalizing
            avgQLength = 0
            for key, value in queryTerms.items():
                avgQLength += value ** 2

            avgQLength = math.sqrt(avgQLength)

            for key, value in queryTerms.items():
                queryTerms[key] = value / avgQLength

            #only calculating cosine similarity for docs with at least one query term
            docsToCalc = set()
            for term in queryTerms.keys():
                termfreq = self.get_docIDs(data, term)
                docsToCalc.update(termfreq)

            #calculating weight for documents
            scores = {}
            for doc in docsToCalc: #document at a time
                docTotalScore = 0
                avgDocLength = 0

                for term in queryTerms:
                    if doc not in data[term]: #check if current term is in this document
                        termCount = 0
                    else:
                        termCount = data[term][doc] #if it is, get count
                    avgDocLength += termCount ** 2 
                avgDocLength = math.sqrt(avgDocLength) #get avg doc length for this document

                for term, weight in queryTerms.items():
                    if doc not in data[term]: 
                        counts = 0
                    else:
                        counts = data[term][doc]
                    if counts != 0:
                        docWeight = 1 + math.log(counts) #get weighted tf
                    else:
                        docWeight = 0
                    docWeight = docWeight / avgDocLength  # normalizing

                    termDocScore = docWeight * weight # get weight for this term for this doc
                    
                    #check if term is an important term within this document
                    if term in self.important_terms:
                        if doc in self.important_terms[term]:
                            termDocScore += 1

                    docTotalScore += termDocScore #add this terms score to the doc's total score

                scores[doc] = docTotalScore # add to dict containing docId and its weight

            #sort so best matches are first
            scores = dict((sorted(scores.items(), key = lambda x: x[1], reverse = True)))
            scores = list(scores.keys()) #get ordered list of best matches
            scores = scores[:5] #get 5 best matches

            for dID in scores:
                print(self.urls[int(dID)]) #print results to user

            end_time = time.time()
            time_diff = end_time - start_time
            execution_time = time_diff * 1000
            print()
            print(str(execution_time))    #print time in milliseconds


if __name__ == '__main__':
    query = Query()
    query.Run()