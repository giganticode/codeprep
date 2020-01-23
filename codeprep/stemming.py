from nltk.stem import PorterStemmer

stemmer = PorterStemmer()


def stem(word: str):
    if not word:
        return word

    stemmed = stemmer.stem(word)
    if word.isupper():
        return stemmed.upper()
    elif word[0].isupper():
        return stemmed.capitalize()
    else:
        return stemmed