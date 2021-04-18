import re
import nltk
from nltk.stem import WordNetLemmatizer
from stop_words import get_stop_words
import string
from string import digits
from io import StringIO
from html.parser import HTMLParser
nltk.download('punkt')
nltk.download('wordnet')
stop_words = get_stop_words('en')


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def remove_stopwords(s):
    """For removing stop words
    """
    s = ' '.join(word for word in s.split() if word not in stop_words)
    return s


def preprocess(text):
    # remove html tags
    text = strip_tags(text)

    # Convert to lowercase
    text = text.lower()

    # remove stopwords
    text = remove_stopwords(text)

    # Remove numbers from text
    remove_digits = str.maketrans('', '', digits)
    text = text.translate(remove_digits)

    # Remove punctuation & single letter words
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.replace(r'\b\w\b', '')
    text = text.replace(r'\s+', ' ')
    text = text.replace(r'\n', ' ')
    text = text.replace(r'\r\n', ' ')

    # Remove nan
    text = re.sub(r'\bnan\b', '', text)

    # Tokenize: Split the sentence into words & Lemmatize list of words and join
    lemmatizer = WordNetLemmatizer()
    word_list = nltk.word_tokenize(text)
    text = ' '.join([lemmatizer.lemmatize(w) for w in word_list])

    return text