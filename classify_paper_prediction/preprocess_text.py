import re
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


def stemming_and_lemmatization(sentence):
    stemmer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    newSentence = re.sub(r'\W', ' ', sentence)
    newSentence = re.sub(r'\s+[a-zA-Z]\s+', ' ', newSentence)
    newSentence = re.sub(r'\^[a-zA-Z]\s+', ' ', newSentence)
    newSentence = re.sub(r'\s+', ' ', newSentence, flags=re.I)
    newSentence = newSentence.lower()
    newSentence = newSentence.split()
    newSentence = [w for w in newSentence if not w in stop_words]
    newSentence = [stemmer.lemmatize(word) for word in newSentence]
    newSentence = ' '.join(newSentence)
    return newSentence

def preprocess_dataframe(df):
    for index, row in df.iterrows():
        print(index)
        row['abstractText'] = stemming_and_lemmatization(str(row['abstractText']))
        row['title'] = stemming_and_lemmatization(str(row['title']))
        row[' Introduction'] = stemming_and_lemmatization(str(row[' Introduction']))
        row[' Related Work'] = stemming_and_lemmatization(str(row[' Related Work']))
        row[' Conclusion'] = stemming_and_lemmatization(str(row[' Conclusion']))
        row[' Experiments'] = stemming_and_lemmatization(str(row[' Experiments']))
        row[' Results'] = stemming_and_lemmatization(str(row[' Results']))
        row[' Discussion'] = stemming_and_lemmatization(str(row[' Discussion']))
    return df

if __name__=="__main__":
    abstractText = "Cross lingual projection of linguistic annotation suffers from many sources of bias and noise, leading to unreliable annotations that cannot be used directly. In this paper, we introduce a novel approach to sequence tagging that learns to correct the errors from cross-lingual projection using an explicit noise layer. This is framed as joint learning over two corpora, one tagged with gold standard and the other with projected tags. We evaluated with only 1000 tokens tagged with gold standard tags, along with more plentiful parallel data. Our system equals or exceeds the state-of-the-art on eight simulated lowresource settings, as well as two real lowresource languages, Malagasy and Kinyarwanda."
    stemming_and_lemmatization(abstractText)