import pandas as pd
from src.extraction import extract_text_from_file, split_into_sentences
from src.preprocessing import preprocess
from src.features import create_tfidf_features, add_numeric_feature

def process_pdf(path, vectorizer=None):
    text = extract_text_from_file(path)
    sentences = split_into_sentences(text)

    clean_sentences = [preprocess(s) for s in sentences]

    if vectorizer is None:
        X, vectorizer = create_tfidf_features(clean_sentences)
    else:
        X = vectorizer.transform(clean_sentences)

    X_combined = add_numeric_feature(X, pd.Series(sentences))

    return sentences, X_combined
