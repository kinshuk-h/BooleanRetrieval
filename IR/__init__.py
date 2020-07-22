__all__ = [ 'document', 'normalization' ]

# import nltk
# import os
# import re
# from nltk.stem import WordNetLemmatizer
# from nltk.corpus import stopwords
# from nltk.tokenize import sent_tokenize,word_tokenize

# Stopwords = set(stopwords.words('english'))

# wordlemmatizer = WordNetLemmatizer()
# def lemmatize_words(words):
#     lemmatized_words = []
#     for word in words:
#        lemmatized_words.append(wordlemmatizer.lemmatize(word))
#     return lemmatized_words

# def stem_words(words):
#     stemmed_words = []
#     for word in words:
#        stemmed_words.append(stemmer.stem(word))
#     return stemmed_words

# def remove_special_characters(text):
#     regex = r'[^a-zA-Z0-9\s]'
#     text = re.sub(regex,'',text)
#     return text

# file = 'input.txt'
# file = open(file , 'r')
# text = file.read()
# tokenized_sentence = sent_tokenize(text)
# text = remove_special_characters(str(text))
# text = re.sub(r'\d+', '', text)
# tokenized_words_with_stopwords = word_tokenize(text)
# tokenized_words = [word for word in tokenized_words_with_stopwords if word not in Stopwords]
# tokenized_words = [word for word in tokenized_words if len(word) > 1]
# tokenized_words = [word.lower() for word in tokenized_words]
# tokenized_words = stem_words(tokenized_words)
# tokenized_words = lemmatize_words(tokenized_words)
