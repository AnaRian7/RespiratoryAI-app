"""
Health Check and Model Info API Routes

Endpoints:
    GET /api/health      - API health check
    GET /api/model/info  - Model metadata
"""

from pathlib import Path

from fastapi import APIRouter

from backend.config import settings
from backend.api.schemas import HealthResponse, ModelInfoResponse


router = APIRouter(prefix="/api", tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check API health and model availability.
    
    Returns status of API and whether models are loaded.
    """
    models_loaded = {
        "image_model": Path(settings.IMAGE_MODEL_PATH).exists(),
        "risk_model": Path(settings.RISK_MODEL_PATH).exists(),
        "fusion_model": Path(settings.FUSION_MODEL_PATH).exists()
    }
    
    all_critical_loaded = models_loaded["image_model"]
    
    return HealthResponse(
        status="healthy" if all_critical_loaded else "degraded",
        version="1.0.0",
        models_loaded=models_loaded
    )


@router.get("/model/info", response_model=ModelInfoResponse)
async def model_info():
    """
    Get information about the loaded image model.
    """
    model_exists = Path(settings.IMAGE_MODEL_PATH).exists()
    
    info = ModelInfoResponse(
        name="ResNet50V2_ChestXray",
        architecture="ResNet50V2 + Custom Head",
        input_shape=[*settings.IMAGE_SIZE, 3],
        num_classes=settings.NUM_CLASSES,
        classes=settings.CLASSES,
        trainable_params=None
    )
    
    if model_exists:
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(settings.IMAGE_MODEL_PATH)
            trainable = sum([
                tf.keras.backend.count_params(w) 
                for w in model.trainable_weights
            ])
            info.trainable_params = trainable
        except Exception:
            pass
    
    return info
