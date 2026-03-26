import re
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack

def contains_number(text):
    return int(bool(re.search(r'\d', text)))

def create_tfidf_features(text_series):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(text_series)
    return X, vectorizer

def add_numeric_feature(X, original_text_series):
    number_feature =original_text_series.apply(contains_number).values.reshape(-1, 1)
    X_combined = hstack([X, number_feature])
    return X_combined
