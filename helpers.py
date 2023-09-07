import re
def tokenize(text):
    """
    Tokenizes text and returns a list of the tokens
    :param text: string - text from files
    :return: list - tokens
    """
    text_words = []
    text = re.split("[\W_À-ÖØ-öø-ÿ]+", text)  # Split on nonalphanumerics to create list of words in line.
    for word in text:
        token = word.lower()  # Make lowercase so the capitalization does not matter.
        if token != '' and token.isascii() == True:
            text_words.append(token)  # Adds to list
    return text_words

def stopWords():
    """
    Creates a set of stop words from stopwords.txt
    :return: set - stopwords
    """
    stopwords = set()
    with open("stopwords.txt") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line is not None:
                stopwords.add(line)
    return stopwords
    
def searchInvertedIndex(word):
    with open("pointerIndex.txt",'r') as file:
        pointerIndex = json.load(file)
        if word in pointerIndex:
            pointerNum = pointerIndex[word][0]
            with open("invertedIndex.txt",'r') as invertedFile:
                invertedFile.seek(pointerNum)
                return json.loads(invertedFile.readline())
        else:
            print("Word not found")
