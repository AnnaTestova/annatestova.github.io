"""Model training and evaluation for greenwashing detection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split

from src.features import add_numeric_features, create_numeric_features, create_tfidf_features
from src.preprocessing import preprocess_many
from src.validation import dataset_summary, reliability_warning


def build_feature_matrix(df: pd.DataFrame) -> Tuple[object, object, pd.Series]:
    """Preprocess text and build the combined TF-IDF + numeric feature matrix."""
    cleaned_text = preprocess_many(df["text"])
    X_tfidf, vectorizer = create_tfidf_features(cleaned_text)
    X = add_numeric_features(X_tfidf, df["text"])
    return X, vectorizer, df["label"]


def train_model(X, y: pd.Series) -> LogisticRegression:
    """Train a class-balanced logistic regression classifier.

    ``class_weight='balanced'`` is used because greenwashing datasets are often
    imbalanced.  It prevents the model from ignoring a minority class during
    training.
    """
    model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    model.fit(X, y)
    return model


def evaluate_model(X, y: pd.Series) -> Dict[str, object]:
    """Evaluate the model with an approach suited to the available data size.

    For sufficiently large classes, a stratified train/test split is used.  For
    very small datasets, stratified cross-validation with the largest feasible
    fold count is used.  This avoids a common problem where a random split loses
    one of the classes entirely.
    """
    y = pd.Series(y).reset_index(drop=True)
    class_counts = y.value_counts()
    min_class_size = int(class_counts.min())

    if min_class_size >= 5 and len(y) >= 20:
        evaluation_method = "stratified_train_test_split"
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        model = train_model(X_train, y_train)
        y_pred = model.predict(X_test)
        y_score = model.predict_proba(X_test)[:, 1]
    else:
        evaluation_method = f"stratified_{min(3, min_class_size)}_fold_cross_validation_sanity_check"
        n_splits = max(2, min(3, min_class_size))
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        estimator = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
        y_pred = cross_val_predict(estimator, X, y, cv=cv, method="predict")
        y_score = cross_val_predict(estimator, X, y, cv=cv, method="predict_proba")[:, 1]
        y_test = y

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="binary", zero_division=0
    )

    metrics = {
        "evaluation_method": evaluation_method,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, zero_division=0, output_dict=True),
    }

    if len(np.unique(y_test)) == 2:
        metrics["roc_auc"] = float(roc_auc_score(y_test, y_score))
    else:
        metrics["roc_auc"] = None

    return metrics


def train_evaluate_and_save(df: pd.DataFrame, model_path: str | Path, vectorizer_path: str | Path, metrics_path: str | Path) -> Tuple[LogisticRegression, object, Dict[str, object]]:
    """Run the complete training workflow and save reproducible artifacts."""
    X, vectorizer, y = build_feature_matrix(df)
    metrics = evaluate_model(X, y)
    final_model = train_model(X, y)

    model_path = Path(model_path)
    vectorizer_path = Path(vectorizer_path)
    metrics_path = Path(metrics_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(final_model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    metrics_payload = {
        "dataset_summary": dataset_summary(df),
        "reliability_warning": reliability_warning(df),
        "numeric_features": list(create_numeric_features(df["text"]).columns),
        "metrics": metrics,
        "label_definition": {
            "0": "substantiated/concrete sustainability claim",
            "1": "possible greenwashing or vague sustainability claim",
        },
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")
    return final_model, vectorizer, metrics_payload


# Backwards-compatible wrapper for the original project API.
def train_and_evaluate(X, y):
    metrics = evaluate_model(X, y)
    print(json.dumps(metrics, indent=2))
    return train_model(X, y)
