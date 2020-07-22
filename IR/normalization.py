import os
import re

from nltk.stem     import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus   import stopwords

Stopwords = set(stopwords.words('english'))

__lemmatizer__ = WordNetLemmatizer()
__stemmer__    = PorterStemmer()

def lemmatize_words(words): return [ __lemmatizer__.lemmatize(word) for word in words ]
def stem_words(words)     : return [ __stemmer__.stem(word) for word in words ]

def tokenizer(text, exclusions = ()):
    """Tokenizes text into processed tokens.

        :param `text`: (string) The text to tokenize.
        :param `exclusions`: (list, optional) stopword exclusions.

        :returns: a list of tokens.
    """
    sentences = [ re.sub(r'[^a-zA-Z\s]+', '', sentence) for sentence in sent_tokenize(text) ]
    tokens = [ word.lower() for sentence in sentences for word in word_tokenize(sentence) ]
    keywords = [ word for word in tokens if (word.lower() not in stopwords.words('english') or word.lower() in exclusions) and len(word) > 1 ]
    # keywords = stem_words(keywords)
    keywords = lemmatize_words(keywords)
    return keywords

def query_tokenizer(text):
    return tokenizer(text, exclusions = ('and', 'or', 'not'))

if __name__ == "__main__":
    file = input("File: ")
    with open(os.path.join(os.path.dirname(__file__), file), 'r+') as fin:
        text = '\n'.join(fin.readlines())
        for word in tokenizer(text):
            print(word)