"""Command-line entry point for the Greenwashing Detection project.

This script now covers the complete reproducible workflow:
1. load and validate labelled training data;
2. document preprocessing and feature extraction;
3. evaluate the classifier and save metrics;
4. train the final model;
5. apply the model to raw report text files when available.

Example:
    python main.py --train-data data/sustainability_sentences.csv --reports-folder data/raw_reports
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.model import train_evaluate_and_save
from src.pipeline import process_report
from src.validation import load_and_validate_training_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train and run a sentence-level greenwashing detector.")
    parser.add_argument("--train-data", default="data/sustainability_sentences_1000_unique.csv", help="CSV with columns text,label")
    parser.add_argument("--reports-folder", default="data/raw_reports", help="Folder containing UTF-8 .txt reports")
    parser.add_argument("--output-dir", default="outputs", help="Folder for models, metrics, and predictions")
    return parser.parse_args()


def predict_reports(reports_folder: Path, output_dir: Path, model, vectorizer) -> None:
    """Run predictions for every .txt report in the raw reports folder."""
    if not reports_folder.exists():
        print(f"No report folder found at {reports_folder}. Training/evaluation completed only.")
        return

    report_files = sorted(reports_folder.glob("*.txt"))
    if not report_files:
        print(f"No .txt reports found in {reports_folder}. Training/evaluation completed only.")
        return

    predictions_dir = output_dir / "predictions"
    predictions_dir.mkdir(parents=True, exist_ok=True)

    for report_path in report_files:
        print(f"\nProcessing report: {report_path.name}")
        sentences, X_report = process_report(report_path, vectorizer=vectorizer)
        predictions = model.predict(X_report)
        probabilities = model.predict_proba(X_report)[:, 1]

        total = len(sentences)
        greenwash_count = int(predictions.sum())
        percentage = (greenwash_count / total * 100) if total else 0

        results_df = pd.DataFrame({
            "sentence": sentences,
            "greenwashing_prediction": predictions.astype(int),
            "greenwashing_probability": probabilities.round(4),
        })

        output_path = predictions_dir / f"{report_path.stem}_results.csv"
        results_df.to_csv(output_path, index=False, encoding="utf-8-sig")

        print(f"Total sentences: {total}")
        print(f"Predicted greenwashing sentences: {greenwash_count}")
        print(f"Predicted greenwashing percentage: {percentage:.2f}%")
        print(f"Results saved to: {output_path}")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_and_validate_training_data(args.train_data)
    print(f"Loaded and validated {len(df)} labelled training sentences.")

    model, vectorizer, metrics_payload = train_evaluate_and_save(
        df=df,
        model_path=output_dir / "greenwashing_model.pkl",
        vectorizer_path=output_dir / "tfidf_vectorizer.pkl",
        metrics_path=output_dir / "evaluation_metrics.json",
    )

    print("\nEvaluation summary:")
    print(json.dumps(metrics_payload["metrics"], indent=2))
    if metrics_payload.get("reliability_warning"):
        print(f"\nReliability warning: {metrics_payload['reliability_warning']}")

    predict_reports(Path(args.reports_folder), output_dir, model, vectorizer)


if __name__ == "__main__":
    main()
