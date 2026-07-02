"""Data extraction helpers.

The project currently supports plain-text sustainability reports. PDF parsing is
not silently assumed; reports should first be converted to UTF-8 text and placed
in ``data/raw_reports``. Keeping this step explicit improves reproducibility and
makes it clear which source text was actually analyzed.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

try:
    import nltk
    from nltk.tokenize import sent_tokenize
except Exception:  # pragma: no cover
    nltk = None
    sent_tokenize = None


def extract_text_from_file(path: str | Path) -> str:
    """Read a UTF-8 text report from disk.

    Raises:
        FileNotFoundError: when the report path does not exist.
        ValueError: when the file is empty.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input report not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Input report is empty: {file_path}")
    return text


def split_into_sentences(text: str) -> List[str]:
    """Split report text into non-empty sentences.

    NLTK sentence tokenization is used when its tokenizer data is available. A
    regex fallback is provided so the workflow remains executable offline.
    """
    sentences: list[str]
    if nltk is not None and sent_tokenize is not None:
        try:
            nltk.data.find("tokenizers/punkt")
            sentences = sent_tokenize(text)
        except LookupError:
            sentences = re.split(r"(?<=[.!?])\s+", text)
    else:
        sentences = re.split(r"(?<=[.!?])\s+", text)

    return [sentence.strip() for sentence in sentences if sentence.strip()]
