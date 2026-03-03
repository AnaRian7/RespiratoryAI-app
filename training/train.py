"""
Training Pipeline for RespiratoryAI Models

Usage:
    python -m backend.training.train --model image
    python -m backend.training.train --model risk
    python -m backend.training.train --model fusion
    python -m backend.training.train --all
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from backend.config import settings


def train_image_model(fine_tune: bool = False):
    """Train the ResNet50V2 image classification model."""
    from backend.models.image_model import train_image_model as _train
    
    print("\n" + "="*70)
    print("TRAINING: ResNet50V2 Chest X-Ray Classifier")
    print("="*70)
    
    history, metrics = _train(fine_tune=fine_tune)
    
    save_training_log("image_model", metrics)
    
    return history, metrics


def train_risk_model():
    """Train the tabular risk factor model."""
    from backend.models.risk_model import build_risk_model
    
    print("\n" + "="*70)
    print("TRAINING: Risk Factor Model")
    print("="*70)
    
    model = build_risk_model()
    
    print("⚠️  Risk model training requires patient tabular data.")
    print("   Implement data loading in backend/preprocessing/tabular.py")
    
    model.save(settings.RISK_MODEL_PATH)
    print(f"\n✅ Risk model saved: {settings.RISK_MODEL_PATH}")
    
    return None


def train_fusion_model():
    """Train the fusion model combining image and risk features."""
    import tensorflow as tf
    from backend.models.fusion_model import build_fusion_model
    
    print("\n" + "="*70)
    print("TRAINING: Fusion Model (Image + Risk Factors)")
    print("="*70)
    
    image_model_path = Path(settings.IMAGE_MODEL_PATH)
    risk_model_path = Path(settings.RISK_MODEL_PATH)
    
    if not image_model_path.exists():
        print("❌ Image model not found. Train it first:")
        print("   python -m backend.training.train --model image")
        return None
    
    image_model = tf.keras.models.load_model(str(image_model_path))
    
    image_features = tf.keras.Model(
        inputs=image_model.input,
        outputs=image_model.get_layer("dense_256").output
    )
    
    fusion_model = build_fusion_model(image_features)
    
    print("⚠️  Fusion model training requires paired image + tabular data.")
    print("   This is a placeholder - implement full training loop as needed.")
    
    fusion_model.save(settings.FUSION_MODEL_PATH)
    print(f"\n✅ Fusion model saved: {settings.FUSION_MODEL_PATH}")
    
    return None


def save_training_log(model_name: str, metrics: dict):
    """Save training metrics to a log file."""
    log_dir = Path(settings.MODELS_DIR) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{model_name}_{timestamp}.json"
    
    log_data = {
        "model_name": model_name,
        "timestamp": timestamp,
        "metrics": metrics,
        "config": {
            "image_size": settings.IMAGE_SIZE,
            "batch_size": settings.BATCH_SIZE,
            "epochs": settings.EPOCHS,
            "learning_rate": settings.LEARNING_RATE,
            "classes": settings.CLASSES
        }
    }
    
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)
    
    print(f"📝 Training log saved: {log_file}")


def train_all():
    """Train all models in sequence."""
    print("\n" + "="*70)
    print("TRAINING ALL MODELS")
    print("="*70)
    
    print("\n[1/3] Training image model...")
    train_image_model()
    
    print("\n[2/3] Training risk model...")
    train_risk_model()
    
    print("\n[3/3] Training fusion model...")
    train_fusion_model()
    
    print("\n" + "="*70)
    print("ALL MODELS TRAINED SUCCESSFULLY")
    print("="*70)


def main():
    parser = argparse.ArgumentParser(description="Train RespiratoryAI models")
    parser.add_argument(
        "--model", "-m",
        choices=["image", "risk", "fusion"],
        help="Which model to train"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Train all models"
    )
    parser.add_argument(
        "--fine-tune", "-f",
        action="store_true",
        help="Fine-tune with more unfrozen layers (image model only)"
    )
    
    args = parser.parse_args()
    
    if args.all:
        train_all()
        return
    
    if args.model == "image":
        train_image_model(fine_tune=args.fine_tune)
    elif args.model == "risk":
        train_risk_model()
    elif args.model == "fusion":
        train_fusion_model()
    else:
        parser.print_help()
        print("\n💡 Examples:")
        print("   python -m backend.training.train --model image")
        print("   python -m backend.training.train --all")


if __name__ == "__main__":
    main()

