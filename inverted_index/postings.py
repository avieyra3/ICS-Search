import struct
import pickle
import os
import inverted_index
class Postings:
    def __init__(self)-> None:
        #self.term: str = ""
        self.docID: int = 0
        self.frequs: int = 0
        self.pos: list = []
        self.tf: float = 0
        self.idf: float = 0

    # We will calculate the TF (term Frequencies) in this function by
    # by dividing the total number of appearences by the total number
    # of words found in the doc.
    def termFrequency(self, appearances: int, total_doc_tokens: int)-> None:
        self.tf = (appearances / total_doc_tokens)
    
    # add the position that the word was found in the doc
    def addPosition(self, position: int)->None:
        self.pos.append(position)

    def printPosting(self, post)->None:
        print("\ndocID: " + str(post.docID) + "\tfrequencies: " + str(post.frequs) 
            + f"\npositions: {post.pos}" + "\tTF: " + f"{post.tf:.2f}")

    def Run(self):
        index = {}
        textList = ['the', 'in', 'the', 'be', 'to', 'from', 'to']
        for i in range(len(textList)):
            if textList[i] not in index:
                index[textList[i]] = [Postings()]
                index[textList[i]][0].frequs = 1
            else:
                index[textList[i]][0].frequs += 1
            index[textList[i]][0].pos.append(i)
        
        for key in index: 
            index[key][0].tf = index[key][0].frequs / len(textList)


if __name__ == '__main__':
    postings = Postings()
    postings.Run()