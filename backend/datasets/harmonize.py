"""
Dataset Harmonization Pipeline

Consolidates multiple chest X-ray datasets into a unified folder structure
with consistent naming and registers all images in the SQLite database.

Output structure:
    data/images/
    ├── COVID/
    ├── NORMAL/
    ├── PNEUMONIA/
    └── TUBERCULOSIS/

Usage:
    python -m backend.datasets.harmonize
"""

import os
import sqlite3
import hashlib
import shutil
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from PIL import Image

from backend.config import settings


CLASS_MAPPINGS = {
    "COVID": ["covid", "covid-19", "covid19", "sars-cov-2"],
    "NORMAL": ["normal", "healthy", "no finding"],
    "PNEUMONIA": ["pneumonia", "viral pneumonia", "bacterial pneumonia", "lung_opacity"],
    "TUBERCULOSIS": ["tuberculosis", "tb"],
}


def normalize_class(folder_name: str) -> str | None:
    """Map various folder names to our standard 4 classes."""
    name_lower = folder_name.lower().strip()
    
    for standard_class, variants in CLASS_MAPPINGS.items():
        if any(variant in name_lower for variant in variants):
            return standard_class
    
    return None


def get_file_hash(filepath: Path) -> str:
    """Calculate MD5 hash to detect duplicates."""
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def is_valid_image(path: Path) -> bool:
    """Check if a file is a valid image that PIL can open."""
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def init_database() -> sqlite3.Connection:
    """Initialize the xray_images table."""
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS xray_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT NOT NULL UNIQUE,
            label TEXT NOT NULL,
            source_dataset TEXT,
            original_filename TEXT,
            file_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_xray_label ON xray_images(label)
    """)
    
    conn.commit()
    return conn


def harmonize(
    raw_dir: Path = None,
    output_dir: Path = None,
    copy_files: bool = True,
    register_db: bool = True
):
    """
    Harmonize datasets from raw downloads into unified structure.
    
    Args:
        raw_dir: Source directory with raw dataset downloads
        output_dir: Destination for organized images
        copy_files: If True, copy files; if False, just register in DB
        register_db: If True, register images in SQLite database
    """
    raw_dir = Path(raw_dir or settings.DATA_RAW)
    output_dir = Path(output_dir or settings.DATA_IMAGES)
    
    print("\n" + "="*60)
    print("DATASET HARMONIZATION")
    print("="*60)
    print(f"Source: {raw_dir}")
    print(f"Output: {output_dir}")
    print(f"Target classes: {settings.CLASSES}")
    
    if not raw_dir.exists():
        print(f"\n❌ Raw data directory not found: {raw_dir}")
        print("   Run: python -m backend.datasets.download --all")
        return
    
    for cls in settings.CLASSES:
        (output_dir / cls).mkdir(parents=True, exist_ok=True)
    
    conn = None
    if register_db:
        conn = init_database()
        cursor = conn.cursor()
    
    stats = defaultdict(int)
    seen_hashes = set()
    duplicates = 0
    
    print("\n🔍 Scanning for images...")
    
    for root, dirs, files in os.walk(raw_dir):
        root_path = Path(root)
        
        # Skip mask folders (used for segmentation, not classification)
        if "mask" in root_path.name.lower():
            continue
        
        # Check from leaf folder up to root (most specific first)
        # This ensures "Normal" is found before "COVID-19_Radiography_Dataset"
        standard_class = None
        for part in reversed(root_path.parts):
            # Skip generic folder names
            if part.lower() in ("images", "train", "test", "val", "data", "raw"):
                continue
            standard_class = normalize_class(part)
            if standard_class:
                break
        
        if standard_class is None:
            continue
        
        for filename in files:
            if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            
            src_path = root_path / filename

            # Skip corrupt or unreadable images to avoid PIL errors during training
            if not is_valid_image(src_path):
                print(f"⚠️ Skipping corrupt image: {src_path}")
                continue
            
            file_hash = get_file_hash(src_path)
            if file_hash in seen_hashes:
                duplicates += 1
                continue
            seen_hashes.add(file_hash)
            
            source_dataset = "unknown"
            for parent in root_path.parents:
                if parent.parent == Path(settings.DATA_RAW):
                    source_dataset = parent.name
                    break
            
            new_filename = f"{source_dataset}_{standard_class}_{len(seen_hashes):06d}{src_path.suffix}"
            dst_path = output_dir / standard_class / new_filename
            
            if copy_files and not dst_path.exists():
                shutil.copy2(src_path, dst_path)
            
            if register_db:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO xray_images 
                        (filepath, label, source_dataset, original_filename, file_hash)
                        VALUES (?, ?, ?, ?, ?)
                    """, (str(dst_path), standard_class, source_dataset, filename, file_hash))
                except sqlite3.IntegrityError:
                    pass
            
            stats[standard_class] += 1
    
    if register_db:
        conn.commit()
        conn.close()
    
    print("\n" + "="*60)
    print("HARMONIZATION COMPLETE")
    print("="*60)
    print("\n📊 Class distribution:")
    
    total = 0
    for cls in settings.CLASSES:
        count = stats.get(cls, 0)
        total += count
        bar = "█" * min(count // 100, 50)
        print(f"  {cls:15s}: {count:6d} {bar}")
    
    print(f"\n  {'TOTAL':15s}: {total:6d}")
    print(f"  Duplicates skipped: {duplicates}")
    print(f"\n📁 Images saved to: {output_dir}")
    
    if register_db:
        print(f"📝 Database updated: {settings.DB_PATH}")
    
    print("\n👉 Next step: Train the model")
    print("   python -m backend.training.train")


def main():
    parser = argparse.ArgumentParser(description="Harmonize chest X-ray datasets")
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="Don't copy files, only register in database"
    )
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Don't register in database"
    )
    
    args = parser.parse_args()
    
    harmonize(
        copy_files=not args.no_copy,
        register_db=not args.no_db
    )


if __name__ == "__main__":
    main()

