"""
Kaggle Dataset Downloader for Chest X-Ray Images

Downloads and extracts datasets from Kaggle for training the respiratory disease model.

Prerequisites:
    1. Install kaggle: pip install kaggle
    2. Create Kaggle API token at https://www.kaggle.com/settings
    3. Place kaggle.json in ~/.kaggle/ (Linux/Mac) or %USERPROFILE%\.kaggle\ (Windows)

Usage:
    python -m backend.datasets.download --all
    python -m backend.datasets.download --dataset covid
"""

import os
import sys
import shutil
import zipfile
import argparse
from pathlib import Path

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
except ImportError:
    print("ERROR: kaggle package not installed. Run: pip install kaggle")
    sys.exit(1)

from backend.config import settings


DATASETS = {
    "covid_radiography": {
        "slug": "tawsifurrahman/covid19-radiography-database",
        "description": "COVID-19 Radiography Database (COVID, Normal, Pneumonia)",
        "expected_classes": ["COVID", "NORMAL", "Viral Pneumonia"],
    },
    "tuberculosis": {
        "slug": "tawsifurrahman/tuberculosis-tb-chest-xray-dataset",
        "description": "Tuberculosis Chest X-ray Dataset",
        "expected_classes": ["Tuberculosis", "Normal"],
    },
    "chest_xray_pneumonia": {
        "slug": "paultimothymooney/chest-xray-pneumonia",
        "description": "Chest X-Ray Images (Pneumonia) - Guangzhou dataset",
        "expected_classes": ["NORMAL", "PNEUMONIA"],
    },
    "nih_chest_xrays": {
        "slug": "nih-chest-xrays/sample",
        "description": "NIH Chest X-rays (sample subset)",
        "expected_classes": ["multiple"],
    },
}


def authenticate_kaggle() -> KaggleApi:
    """Authenticate with Kaggle API."""
    api = KaggleApi()
    api.authenticate()
    print("✅ Kaggle API authenticated successfully")
    return api


def download_dataset(api: KaggleApi, dataset_key: str, force: bool = False) -> Path:
    """
    Download a specific dataset from Kaggle.
    
    Args:
        api: Authenticated KaggleApi instance
        dataset_key: Key from DATASETS dict
        force: If True, re-download even if exists
        
    Returns:
        Path to extracted dataset directory
    """
    if dataset_key not in DATASETS:
        raise ValueError(f"Unknown dataset: {dataset_key}. Available: {list(DATASETS.keys())}")

    dataset_info = DATASETS[dataset_key]
    slug = dataset_info["slug"]
    
    download_dir = Path(settings.DATA_RAW) / dataset_key
    
    if download_dir.exists() and not force:
        print(f"⏭️  Dataset '{dataset_key}' already exists at {download_dir}")
        print("   Use --force to re-download")
        return download_dir
    
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📥 Downloading: {dataset_info['description']}")
    print(f"   Kaggle slug: {slug}")
    print(f"   Destination: {download_dir}")
    
    api.dataset_download_files(
        slug,
        path=str(download_dir),
        unzip=True,
        quiet=False
    )
    
    for zip_file in download_dir.glob("*.zip"):
        print(f"   Extracting: {zip_file.name}")
        with zipfile.ZipFile(zip_file, 'r') as zf:
            zf.extractall(download_dir)
        zip_file.unlink()
    
    print(f"✅ Downloaded and extracted: {dataset_key}")
    
    return download_dir


def list_datasets():
    """Print available datasets."""
    print("\n📋 Available Kaggle Datasets:\n")
    print("-" * 70)
    for key, info in DATASETS.items():
        print(f"  {key}")
        print(f"    Description: {info['description']}")
        print(f"    Kaggle slug: {info['slug']}")
        print(f"    Classes: {info['expected_classes']}")
        print()


def download_all(force: bool = False):
    """Download all configured datasets."""
    api = authenticate_kaggle()
    
    print("\n" + "="*60)
    print("DOWNLOADING ALL CHEST X-RAY DATASETS")
    print("="*60)
    
    downloaded = []
    failed = []
    
    for dataset_key in DATASETS:
        try:
            download_dataset(api, dataset_key, force=force)
            downloaded.append(dataset_key)
        except Exception as e:
            print(f"❌ Failed to download {dataset_key}: {e}")
            failed.append(dataset_key)
    
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    print(f"✅ Successfully downloaded: {len(downloaded)}")
    for d in downloaded:
        print(f"   - {d}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for f in failed:
            print(f"   - {f}")
    
    print(f"\n📁 Data location: {settings.DATA_RAW}")
    print("\n👉 Next step: Run harmonization to create unified dataset")
    print("   python -m backend.datasets.harmonize")


def main():
    parser = argparse.ArgumentParser(
        description="Download chest X-ray datasets from Kaggle"
    )
    parser.add_argument(
        "--dataset", "-d",
        choices=list(DATASETS.keys()),
        help="Download a specific dataset"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Download all datasets"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available datasets"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force re-download even if exists"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_datasets()
        return
    
    if args.all:
        download_all(force=args.force)
        return
    
    if args.dataset:
        api = authenticate_kaggle()
        download_dataset(api, args.dataset, force=args.force)
        return
    
    parser.print_help()
    print("\n💡 Examples:")
    print("   python -m backend.datasets.download --list")
    print("   python -m backend.datasets.download --all")
    print("   python -m backend.datasets.download -d covid_radiography")


if __name__ == "__main__":
    main()
