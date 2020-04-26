import os.path
import re
import threading
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from string import punctuation
from flask import current_app as app
from .core import LimitedSizeDict


# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

stopword = stopwords.words('english')
wordnet_lemmatizer = WordNetLemmatizer()
normalization_cache = LimitedSizeDict(size_limit=1000000)

contractions = {
    "ain't": "am not",
    "aren't": "are not",
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he had",
    "he'd've": "he would have",
    "he'll": "he will",
    "he'll've": "he will have",
    "he's": "he is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how is",
    "I'd": "I had",
    "I'd've": "I would have",
    "I'll": "I will",
    "I'll've": "I will have",
    "I'm": "I am",
    "I've": "I have",
    "isn't": "is not",
    "it'd": "it had",
    "it'd've": "it would have",
    "it'll": "it will",
    "it'll've": "iit will have",
    "it's": "it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she had",
    "she'd've": "she would have",
    "she'll": "she will",
    "she'll've": "she will have",
    "she's": "she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so is",
    "that'd": "that had",
    "that'd've": "that would have",
    "that's": "that is",
    "there'd": "there had",
    "there'd've": "there would have",
    "there's": "there is",
    "they'd": "they had",
    "they'd've": "they would have",
    "they'll": "they will",
    "they'll've": "they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we had",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what will",
    "what'll've": "what will have",
    "what're": "what are",
    "what's": "what is",
    "what've": "what have",
    "when's": "when is",
    "when've": "when have",
    "where'd": "where did",
    "where's": "where is",
    "where've": "where have",
    "who'll": "who will",
    "who'll've": "who will have",
    "who's": "who is",
    "who've": "who have",
    "why's": "why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you had",
    "you'd've": "you would have",
    "you'll": "you will",
    "you'll've": "you will have",
    "you're": "you are",
    "you've": "you have"
}


def normalize_multiple(texts):
    new_texts = [text for text in texts if text not in normalization_cache]

    if len(new_texts) > 0:
        app.logger.debug(f'Normalizing {len(new_texts)} texts')
        new_normalized_texts = [__normalize(text) for text in new_texts]
        normalization_cache.update(zip(new_texts, new_normalized_texts))
        __save_normalization_cache()

    return [normalization_cache[text] for text in texts]


def normalize_single(text):
    normalized_text = __normalize(text)
    __save_normalization_cache()
    return normalized_text


def __normalize(text):
    if text in normalization_cache:
        return normalization_cache[text]
    normalized_text = text.lower()
    normalized_text = expand_contractions(normalized_text, contractions)
    normalized_text = ''.join(char for char in normalized_text if char not in punctuation)
    tokens = nltk.word_tokenize(normalized_text)
    tokens = [wordnet_lemmatizer.lemmatize(token) for token in tokens if token not in stopword]
    tokens = [token for token in tokens if token not in stopword]
    normalized_text = ''.join(token for token in tokens)
    normalization_cache[text] = normalized_text
    return normalized_text


def expand_contractions(text, contractions):
    pattern = re.compile('({})'.format('|'.join(contractions.keys())), flags=re.IGNORECASE | re.DOTALL)

    def expand_match(contraction):
        match = contraction.group(0)
        expanded_contraction = contractions.get(match)
        return expanded_contraction

    expanded_text = pattern.sub(expand_match, text)
    expanded_text = re.sub("'", "", expanded_text)

    return expanded_text


def init_normalization():
    normalization_cache = __load_normalization_cache()
    __normalize('warmup')


def __load_normalization_cache():
    path = os.path.join(app.config['DATA_PATH'], 'normalization_cache.pkl')
    if os.path.exists(path):
        with open(path, 'rb') as f:
            cache = LimitedSizeDict(size_limit=1000000)
            cache.update(pickle.load(f))
            return cache
    return LimitedSizeDict(size_limit=1000000)


def __save_normalization_cache():
    path = os.path.join(app.config['DATA_PATH'], 'normalization_cache.pkl')
    with open(path, 'wb') as f:
        pickle.dump({key: normalization_cache[key] for key in normalization_cache.keys()}, f)