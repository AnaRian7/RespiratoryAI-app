"""
Inference Pipeline for Respiratory Disease Classification

Supports:
- Image-only prediction (chest X-ray)
- Risk factor prediction (tabular data)
- Fusion prediction (image + risk factors combined)
"""

import numpy as np
import tensorflow as tf
from pathlib import Path
from PIL import Image
from typing import Optional
import uuid
from datetime import datetime
import requests

from backend.config import settings
from backend.inference.gradcam import GradCAM


def ensure_image_model_present() -> None:
    """Download the image model from remote storage if it's missing."""
    model_path = Path(settings.IMAGE_MODEL_PATH)

    if model_path.exists() or not settings.IMAGE_MODEL_URL:
        return

    model_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading image model from {settings.IMAGE_MODEL_URL}...")
    resp = requests.get(settings.IMAGE_MODEL_URL, stream=True)
    resp.raise_for_status()

    with open(model_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Saved image model to {model_path}")


def ensure_risk_model_present() -> None:
    """Download the risk model from remote storage if it's missing."""
    model_path = Path(settings.RISK_MODEL_PATH)

    if model_path.exists() or not settings.RISK_MODEL_URL:
        return

    model_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading risk model from {settings.RISK_MODEL_URL}...")
    resp = requests.get(settings.RISK_MODEL_URL, stream=True)
    resp.raise_for_status()

    with open(model_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Saved risk model to {model_path}")


def ensure_fusion_model_present() -> None:
    """Download the fusion model from remote storage if it's missing."""
    model_path = Path(settings.FUSION_MODEL_PATH)

    if model_path.exists() or not settings.FUSION_MODEL_URL:
        return

    model_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading fusion model from {settings.FUSION_MODEL_URL}...")
    resp = requests.get(settings.FUSION_MODEL_URL, stream=True)
    resp.raise_for_status()

    with open(model_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Saved fusion model to {model_path}")


class ModelLoader:
    """Lazy model loader with caching."""

    _image_model = None
    _risk_model = None
    _fusion_model = None
    _gradcam = None

    @classmethod
    def get_image_model(cls) -> tf.keras.Model:
        if cls._image_model is None:
            model_path = Path(settings.IMAGE_MODEL_PATH)
            ensure_image_model_present()
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Image model not found at {model_path}. "
                    "Train the model locally or configure IMAGE_MODEL_URL."
                )
            cls._image_model = tf.keras.models.load_model(str(model_path))
        return cls._image_model

    @classmethod
    def get_risk_model(cls) -> tf.keras.Model:
        if cls._risk_model is None:
            model_path = Path(settings.RISK_MODEL_PATH)
            ensure_risk_model_present()
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Risk model not found at {model_path}. "
                    "Train locally or configure RISK_MODEL_URL."
                )
            cls._risk_model = tf.keras.models.load_model(str(model_path))
        return cls._risk_model

    @classmethod
    def get_fusion_model(cls) -> tf.keras.Model:
        if cls._fusion_model is None:
            model_path = Path(settings.FUSION_MODEL_PATH)
            ensure_fusion_model_present()
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Fusion model not found at {model_path}. "
                    "Train locally or configure FUSION_MODEL_URL."
                )
            cls._fusion_model = tf.keras.models.load_model(str(model_path))
        return cls._fusion_model
    
    @classmethod
    def get_gradcam(cls) -> GradCAM:
        if cls._gradcam is None:
            cls._gradcam = GradCAM(cls.get_image_model())
        return cls._gradcam
    
    @classmethod
    def reload_models(cls):
        """Force reload all models (useful after retraining)."""
        cls._image_model = None
        cls._risk_model = None
        cls._fusion_model = None
        cls._gradcam = None


def preprocess_image(
    image: Image.Image | np.ndarray | str | Path
) -> np.ndarray:
    """
    Preprocess image for model inference.
    
    Args:
        image: PIL Image, numpy array, or path to image file
        
    Returns:
        Preprocessed numpy array of shape (1, H, W, 3)
    """
    if isinstance(image, (str, Path)):
        image = Image.open(image)
    
    if isinstance(image, Image.Image):
        image = image.convert("RGB")
        image = image.resize(settings.IMAGE_SIZE)
        image = np.array(image)
    
    if image.dtype == np.uint8:
        image = image.astype(np.float32) / 255.0
    
    if len(image.shape) == 3:
        image = np.expand_dims(image, axis=0)
    
    return image


def preprocess_risk_factors(
    age: int,
    gender: str,
    smoker: bool,
    asthma: bool,
    genetic_risk: bool,
    congenital_lung_defect: bool = False
) -> np.ndarray:
    """
    Preprocess risk factors for model inference.
    
    Args:
        age: Patient age (0-120)
        gender: 'male' or 'female'
        smoker: Smoking status
        asthma: Asthma history
        genetic_risk: Family history of respiratory disease
        congenital_lung_defect: Congenital lung defects
        
    Returns:
        Numpy array of shape (1, num_features)
    """
    age_normalized = np.clip(age / 100.0, 0, 1.2)
    gender_encoded = 1.0 if gender.lower() == "male" else 0.0
    
    features = np.array([
        age_normalized,
        gender_encoded,
        float(smoker),
        float(asthma),
        float(genetic_risk),
        float(congenital_lung_defect)
    ]).reshape(1, -1)
    
    return features


def predict_image(
    image: Image.Image | np.ndarray | str | Path,
    generate_gradcam: bool = True,
    save_gradcam: bool = True
) -> dict:
    """
    Predict respiratory disease from chest X-ray image.
    
    Args:
        image: Input image (PIL, numpy, or path)
        generate_gradcam: Whether to generate Grad-CAM visualization
        save_gradcam: Whether to save Grad-CAM image to disk
        
    Returns:
        Prediction result dictionary
    """
    prediction_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    processed_image = preprocess_image(image)
    
    model = ModelLoader.get_image_model()
    predictions = model.predict(processed_image, verbose=0)[0]
    
    predicted_idx = int(np.argmax(predictions))
    predicted_class = settings.INDEX_TO_CLASS[predicted_idx]
    confidence = float(predictions[predicted_idx])
    
    result = {
        "prediction_id": prediction_id,
        "timestamp": timestamp,
        "predicted_class": predicted_class,
        "confidence": confidence,
        "probabilities": {
            settings.INDEX_TO_CLASS[i]: float(p)
            for i, p in enumerate(predictions)
        },
        "model_type": "image_only"
    }
    
    if generate_gradcam:
        gradcam = ModelLoader.get_gradcam()
        heatmap = gradcam.compute_heatmap(processed_image, class_idx=predicted_idx)
        
        if save_gradcam:
            if isinstance(image, (str, Path)):
                original_image = Image.open(image)
            else:
                original_image = Image.fromarray(
                    (processed_image[0] * 255).astype(np.uint8)
                )
            
            overlaid = gradcam.overlay_heatmap(heatmap, original_image)
            
            gradcam_filename = f"{prediction_id}_gradcam.png"
            gradcam_path = Path(settings.GRADCAM_DIR) / gradcam_filename
            overlaid.save(gradcam_path)
            
            result["gradcam_path"] = str(gradcam_path)
            result["gradcam_filename"] = gradcam_filename
    
    return result


def predict_risk(
    age: int,
    gender: str,
    smoker: bool,
    asthma: bool,
    genetic_risk: bool,
    congenital_lung_defect: bool = False
) -> dict:
    """
    Predict disease risk from patient factors.
    
    Returns:
        Prediction result dictionary
    """
    features = preprocess_risk_factors(age, gender, smoker, asthma, genetic_risk, congenital_lung_defect)
    
    model = ModelLoader.get_risk_model()
    predictions = model.predict(features, verbose=0)[0]
    
    predicted_idx = int(np.argmax(predictions))
    predicted_class = settings.INDEX_TO_CLASS[predicted_idx]
    
    return {
        "prediction_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "predicted_class": predicted_class,
        "confidence": float(predictions[predicted_idx]),
        "probabilities": {
            settings.INDEX_TO_CLASS[i]: float(p)
            for i, p in enumerate(predictions)
        },
        "model_type": "risk_factors",
        "input_features": {
            "age": age,
            "gender": gender,
            "smoker": smoker,
            "asthma": asthma,
            "genetic_risk": genetic_risk,
            "congenital_lung_defect": congenital_lung_defect
        }
    }


def predict_fusion(
    image: Image.Image | np.ndarray | str | Path,
    age: int,
    gender: str,
    smoker: bool,
    asthma: bool,
    genetic_risk: bool,
    congenital_lung_defect: bool = False,
    generate_gradcam: bool = True
) -> dict:
    """
    Predict using combined image and risk factor analysis.
    
    Returns:
        Comprehensive prediction result
    """
    prediction_id = str(uuid.uuid4())
    
    processed_image = preprocess_image(image)
    risk_features = preprocess_risk_factors(age, gender, smoker, asthma, genetic_risk, congenital_lung_defect)
    
    fusion_model = ModelLoader.get_fusion_model()
    predictions = fusion_model.predict([processed_image, risk_features], verbose=0)[0]
    
    predicted_idx = int(np.argmax(predictions))
    predicted_class = settings.INDEX_TO_CLASS[predicted_idx]
    
    result = {
        "prediction_id": prediction_id,
        "timestamp": datetime.utcnow().isoformat(),
        "predicted_class": predicted_class,
        "confidence": float(predictions[predicted_idx]),
        "probabilities": {
            settings.INDEX_TO_CLASS[i]: float(p)
            for i, p in enumerate(predictions)
        },
        "model_type": "fusion",
        "risk_factors": {
            "age": age,
            "gender": gender,
            "smoker": smoker,
            "asthma": asthma,
            "genetic_risk": genetic_risk,
            "congenital_lung_defect": congenital_lung_defect
        }
    }
    
    if generate_gradcam:
        gradcam = ModelLoader.get_gradcam()
        heatmap = gradcam.compute_heatmap(processed_image, class_idx=predicted_idx)
        
        if isinstance(image, (str, Path)):
            original_image = Image.open(image)
        else:
            original_image = Image.fromarray(
                (processed_image[0] * 255).astype(np.uint8)
            )
        
        overlaid = gradcam.overlay_heatmap(heatmap, original_image)
        
        gradcam_filename = f"{prediction_id}_gradcam.png"
        gradcam_path = Path(settings.GRADCAM_DIR) / gradcam_filename
        overlaid.save(gradcam_path)
        
        result["gradcam_path"] = str(gradcam_path)
        result["gradcam_filename"] = gradcam_filename
    
    return result



