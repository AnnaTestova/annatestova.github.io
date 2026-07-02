"""Feature extraction for sentence-level greenwashing detection.

The model uses two transparent feature groups:
1. TF-IDF text features, capturing important words and short phrases.
2. Simple numeric/claim-strength features, capturing whether a sentence contains
   numbers, percentages, years, environmental keywords, and vague marketing terms.

These features are intentionally interpretable so the project can explain what is
being extracted from each source sentence.
"""

from __future__ import annotations

import re
from typing import Iterable, Tuple

import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer

ENVIRONMENTAL_KEYWORDS = {
    "green", "sustainable", "sustainability", "climate", "carbon", "co2",
    "emission", "emissions", "renewable", "recyclable", "recycle", "energy",
    "net zero", "eco", "environment", "planet", "packaging",
}

VAGUE_CLAIM_TERMS = {
    "committed", "care", "deeply", "future", "greener", "better", "responsible",
    "friendly", "natural", "clean", "leading", "strive", "aim", "believe",
}


def contains_number(text: str) -> int:
    """Return 1 when a sentence contains any digit."""
    return int(bool(re.search(r"\d", str(text))))


def contains_percentage(text: str) -> int:
    """Return 1 when a sentence includes a percentage claim."""
    return int(bool(re.search(r"\d+(\.\d+)?\s?%", str(text))))


def contains_year_or_deadline(text: str) -> int:
    """Return 1 when a sentence references a plausible year/deadline."""
    return int(bool(re.search(r"\b(19|20)\d{2}\b", str(text))))


def keyword_count(text: str, keywords: set[str]) -> int:
    """Count how many configured keywords appear in a sentence."""
    lowered = str(text).lower()
    return sum(1 for keyword in keywords if keyword in lowered)


def create_tfidf_features(text_series: Iterable[str], max_features: int = 5000) -> Tuple[csr_matrix, TfidfVectorizer]:
    """Fit a TF-IDF vectorizer and transform cleaned training text.

    Unigrams and bigrams are used because phrases such as "net zero" or
    "carbon neutral" can carry meaning that single words miss.
    """
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=max_features)
    X = vectorizer.fit_transform(text_series)
    return X, vectorizer


def create_numeric_features(original_text_series: Iterable[str]) -> pd.DataFrame:
    """Create interpretable sentence-level numeric features.

    The feature names are stored in evaluation artifacts so reviewers can inspect
    exactly what was added beyond TF-IDF.
    """
    series = pd.Series(list(original_text_series)).fillna("")
    return pd.DataFrame({
        "contains_number": series.apply(contains_number),
        "contains_percentage": series.apply(contains_percentage),
        "contains_year_or_deadline": series.apply(contains_year_or_deadline),
        "environmental_keyword_count": series.apply(lambda x: keyword_count(x, ENVIRONMENTAL_KEYWORDS)),
        "vague_claim_term_count": series.apply(lambda x: keyword_count(x, VAGUE_CLAIM_TERMS)),
        "sentence_length_words": series.apply(lambda x: len(str(x).split())),
    })


def add_numeric_features(X: csr_matrix, original_text_series: Iterable[str]) -> csr_matrix:
    """Append transparent numeric features to a sparse TF-IDF matrix."""
    numeric_df = create_numeric_features(original_text_series)
    return hstack([X, csr_matrix(numeric_df.values)])


# Backwards-compatible alias for older code/tests.
def add_numeric_feature(X: csr_matrix, original_text_series: Iterable[str]) -> csr_matrix:
    return add_numeric_features(X, original_text_series)
