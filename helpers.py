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