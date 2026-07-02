"""Prediction pipeline for applying the trained model to report text files."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd

from src.extraction import extract_text_from_file, split_into_sentences
from src.features import add_numeric_features, create_tfidf_features
from src.preprocessing import preprocess_many


def process_report(path: str | Path, vectorizer=None) -> Tuple[list[str], object]:
    """Convert a sustainability report text file into model-ready features.

    Args:
        path: UTF-8 plain-text report path.
        vectorizer: fitted TF-IDF vectorizer from the training workflow.  When
            omitted, a new vectorizer is fitted; this is useful only for testing.

    Returns:
        Original sentences and the combined feature matrix for prediction.
    """
    text = extract_text_from_file(path)
    sentences = split_into_sentences(text)
    clean_sentences = preprocess_many(sentences)

    if vectorizer is None:
        X_tfidf, vectorizer = create_tfidf_features(clean_sentences)
    else:
        X_tfidf = vectorizer.transform(clean_sentences)

    X_combined = add_numeric_features(X_tfidf, pd.Series(sentences))
    return sentences, X_combined


# Backwards-compatible alias: the original code called this process_pdf even
# though it only processed .txt files.
def process_pdf(path, vectorizer=None):
    return process_report(path, vectorizer=vectorizer)
