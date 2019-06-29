from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

def stem(word: str):
    return stemmer.stem(word)