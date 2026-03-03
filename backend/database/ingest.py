import os
import sqlite3
from pathlib import Path

from backend.config import settings


def ingest_images():
    dataset_path = settings.DATA_PROCESSED
    db_path = settings.DB_PATH

    print(f"📂 Dataset path: {dataset_path}")
    print(f"🗄️ Database path: {db_path}")

    # Ensure DB directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to DB
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Recreate table (clean + deterministic)
    cur.execute("DROP TABLE IF EXISTS xray_images")
    cur.execute("""
        CREATE TABLE xray_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT NOT NULL,
            label TEXT NOT NULL
        )
    """)
    conn.commit()

    total_inserted = 0

    # Iterate over expected classes ONLY
    for label in settings.CLASSES:
        label_dir = os.path.join(dataset_path, label)

        if not os.path.isdir(label_dir):
            print(f"⚠️ Skipping missing folder: {label}")
            continue

        image_files = [
            os.path.join(label_dir, f)
            for f in os.listdir(label_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        print(f"➡️ Processing label: {label}")
        print(f"   Found {len(image_files)} images")

        for img_path in image_files:
            cur.execute(
                "INSERT INTO xray_images (filepath, label) VALUES (?, ?)",
                (img_path, label)
            )

        total_inserted += len(image_files)
        conn.commit()

    conn.close()

    print(f"✅ Ingestion complete. Total images inserted: {total_inserted}")


if __name__ == "__main__":
    ingest_images()
