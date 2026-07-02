"""Text preprocessing utilities for greenwashing detection.

The preprocessing step is intentionally kept transparent and lightweight so the
same transformations can be reproduced for training data and new company report
sentences. The module works even in offline environments by using built-in
fallbacks when optional NLTK resources are unavailable.
"""

from __future__ import annotations

import re
from typing import Iterable, List

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
except Exception:  # pragma: no cover - protects environments without nltk
    nltk = None
    stopwords = None
    WordNetLemmatizer = None

FALLBACK_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "between", "by", "for", "from",
    "has", "have", "in", "is", "it", "of", "on", "or", "our", "the", "to", "we",
    "will", "with", "this", "that", "these", "those", "was", "were", "been",
}


def _safe_stopwords() -> set[str]:
    """Return English stop words without requiring internet access."""
    if nltk is not None and stopwords is not None:
        try:
            nltk.data.find("corpora/stopwords")
            return set(stopwords.words("english"))
        except LookupError:
            return FALLBACK_STOP_WORDS
    return FALLBACK_STOP_WORDS


class _FallbackLemmatizer:
    """Small fallback lemmatizer used only when WordNet is unavailable."""

    def lemmatize(self, word: str) -> str:
        if len(word) > 4 and word.endswith("ies"):
            return word[:-3] + "y"
        if len(word) > 4 and word.endswith("s"):
            return word[:-1]
        return word


def _safe_lemmatizer():
    """Return WordNet lemmatizer when available; otherwise a simple fallback."""
    if nltk is not None and WordNetLemmatizer is not None:
        try:
            nltk.data.find("corpora/wordnet")
            return WordNetLemmatizer()
        except LookupError:
            return _FallbackLemmatizer()
    return _FallbackLemmatizer()


STOP_WORDS = _safe_stopwords()
LEMMATIZER = _safe_lemmatizer()


def preprocess(text: str) -> str:
    """Normalize one sentence for TF-IDF feature extraction.

    Steps:
    1. lowercase text to avoid treating ``Green`` and ``green`` differently;
    2. remove punctuation but keep digits, because measurable claims often use
       numbers, for example "20% reduction";
    3. remove English stop words;
    4. lemmatize tokens where possible.
    """
    if not isinstance(text, str):
        text = "" if text is None else str(text)

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    tokens = [LEMMATIZER.lemmatize(word) for word in tokens if word not in STOP_WORDS]
    return " ".join(tokens)


def preprocess_many(texts: Iterable[str]) -> List[str]:
    """Apply the same preprocessing function to many sentences."""
    return [preprocess(text) for text in texts]
