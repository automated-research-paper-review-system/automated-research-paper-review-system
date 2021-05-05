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






# def predictions(all_response):
#     score_prediction = ScorePrediction()
#     if all_response['reviewer_id'] == 1:
#         all_response['Clarity'] = 3
#         all_response['Impact'] = 2
#         all_response['Technical Soundness'] = 2
#         all_response['Originality'] = 3
#     elif all_response['reviewer_id'] == 2:
#         all_response['Clarity'] = 3
#         all_response['Impact'] = 2
#         all_response['Technical Soundness'] = 1
#         all_response['Originality'] = 3
#     elif all_response['reviewer_id'] == 3:
#         all_response['Clarity'] = 2
#         all_response['Impact'] = 2
#         all_response['Technical Soundness'] = 2
#         all_response['Originality'] = 2
#     else:
#         all_response['clarity'] = score_prediction.predict_clarity(all_response['review'])
#         all_response['Impact'] = random.randint(1,3)
#         all_response['Technical Soundness'] = random.randint(1,3)
#         all_response['Originality'] = random.randint(1,3)
#
#     return all_response