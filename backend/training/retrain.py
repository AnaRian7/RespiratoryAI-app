"""
Skeleton retraining utilities for RespiratoryAI.

This module collects labeled cases (predictions + confirmed ground-truth labels)
from the SQLite database and prepares them for offline retraining.

Usage (from project root):

    python -m backend.training.retrain

This will:
    - Print how many labeled cases exist
    - Show class distribution of true labels
    - Write an optional CSV manifest of image paths and labels (if extended)

You can later extend this script to:
    - Load images + labels into a tf.data.Dataset
    - Retrain a new model version
    - Evaluate it, then manually promote it to production
"""

from pathlib import Path
import sqlite3
from collections import Counter
from typing import List, Dict

from backend.config import settings


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def collect_labeled_cases() -> List[Dict]:
    """
    Return all predictions that have an attached ground-truth label.

    Each record contains:
        - prediction_id
        - image_path (absolute path to uploaded X-ray)
        - predicted_class
        - true_label
        - model_type
        - confidence
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            p.prediction_id,
            p.image_filename,
            p.predicted_class,
            p.model_type,
            p.confidence,
            l.true_label
        FROM predictions p
        JOIN training_labels l
            ON p.prediction_id = l.prediction_id
        ORDER BY l.created_at DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    results: List[Dict] = []
    uploads_dir = Path(settings.UPLOADS_DIR)

    for row in rows:
        image_filename = row["image_filename"]
        image_path = uploads_dir / image_filename if image_filename else None

        results.append(
            {
                "prediction_id": row["prediction_id"],
                "image_path": str(image_path) if image_path else None,
                "predicted_class": row["predicted_class"],
                "true_label": row["true_label"],
                "model_type": row["model_type"],
                "confidence": float(row["confidence"]),
            }
        )

    return results


def summarize_labeled_cases(cases: List[Dict]) -> None:
    """Print a simple summary of available labeled data."""
    total = len(cases)
    print("\n" + "=" * 70)
    print("LABELED CASES SUMMARY")
    print("=" * 70)
    print(f"Total labeled cases: {total}")

    if total == 0:
        print("No labeled cases yet. Use the /api/history/{prediction_id}/label endpoint")
        print("to attach ground-truth labels before retraining.")
        return

    label_counts = Counter(c["true_label"] for c in cases)
    print("\nClass distribution (true_label):")
    for cls in settings.CLASSES:
        count = label_counts.get(cls, 0)
        print(f"  {cls:15s}: {count:6d}")


def main():
    """
    Entry point for offline retraining preparation.

    This does NOT actually retrain the model yet. It only:
        - Gathers labeled cases
        - Prints a summary

    Extend this function to:
        - Build a training/validation split
        - Feed data into a Keras training loop
        - Save a new model version (e.g., resnet50v2_xray_v2.keras)
    """
    cases = collect_labeled_cases()
    summarize_labeled_cases(cases)


if __name__ == "__main__":
    main()

