import os
import sqlite3
from backend.config import settings

def build_xray_db():
    db_path = settings.DB_PATH
    base_dir = settings.DATA_PROCESSED

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Recreate table cleanly
    cur.execute("DROP TABLE IF EXISTS xray_images")
    cur.execute("""
        CREATE TABLE xray_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT NOT NULL,
            label TEXT NOT NULL
        )
    """)

    total = 0

    for label in settings.CLASSES:
        class_dir = os.path.join(base_dir, label)

        if not os.path.isdir(class_dir):
            print(f"Skipping missing folder: {class_dir}")
            continue

        for img in os.listdir(class_dir):
            if img.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(class_dir, img)
                cur.execute(
                    "INSERT INTO xray_images (filepath, label) VALUES (?, ?)",
                    (path, label)
                )
                total += 1

    conn.commit()
    conn.close()
    print(f"Inserted {total} X-ray images")

if __name__ == "__main__":
    build_xray_db()

