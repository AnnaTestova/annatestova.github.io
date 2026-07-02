"""Validation utilities for data quality and reproducibility."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

REQUIRED_COLUMNS = {"text", "label"}
VALID_LABELS = {0, 1}


def load_and_validate_training_data(csv_path: str | Path) -> pd.DataFrame:
    """Load labelled sentence data and validate its structure.

    Expected schema:
        text:  sentence or claim to classify.
        label: 0 = concrete/substantiated sustainability claim,
               1 = possible greenwashing/vague claim.

    The function removes exact duplicate rows and raises clear errors for missing
    columns, missing values, invalid labels, or an unusable class distribution.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Training data file not found: {path}")

    df = pd.read_csv(path)
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"Training data is missing required columns: {sorted(missing_cols)}")

    df = df[["text", "label"]].copy()
    df["text"] = df["text"].astype(str).str.strip()
    df = df.drop_duplicates()

    if df.empty:
        raise ValueError("Training data is empty after removing duplicates.")
    if df["text"].eq("").any():
        raise ValueError("Training data contains empty text values.")
    if df["label"].isna().any():
        raise ValueError("Training data contains missing labels.")

    df["label"] = df["label"].astype(int)
    invalid_labels = set(df["label"].unique()) - VALID_LABELS
    if invalid_labels:
        raise ValueError(f"Labels must be 0 or 1. Invalid labels found: {sorted(invalid_labels)}")
    if df["label"].nunique() < 2:
        raise ValueError("Training data must contain both classes: 0 and 1.")

    return df.reset_index(drop=True)


def dataset_summary(df: pd.DataFrame) -> Dict[str, object]:
    """Return summary statistics used in the evaluation documentation."""
    class_counts = df["label"].value_counts().sort_index().to_dict()
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "missing_values": df.isna().sum().to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "class_counts": {int(k): int(v) for k, v in class_counts.items()},
        "avg_sentence_length_words": float(df["text"].str.split().str.len().mean()),
    }


def reliability_warning(df: pd.DataFrame) -> str | None:
    """Warn reviewers when the labelled dataset is too small for strong claims."""
    min_class_size = int(df["label"].value_counts().min())
    if len(df) < 50 or min_class_size < 10:
        return (
            "The labelled dataset is very small. Evaluation metrics are provided "
            "only as a sanity check and should not be interpreted as reliable "
            "evidence of production-ready greenwashing detection. More labelled, "
            "source-validated examples are required."
        )
    return None
