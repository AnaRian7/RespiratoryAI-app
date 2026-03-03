"""
Prediction API Routes

Endpoints:
    POST /api/predict       - Predict from X-ray image only
    POST /api/predict/full  - Predict using image + risk factors (fusion)
"""

import shutil
import uuid
import sqlite3
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from PIL import Image
import io

from backend.config import settings
from backend.api.schemas import PredictionResponse, FusionPredictionResponse, RiskFactors
from backend.inference.predictor import predict_image, predict_fusion


router = APIRouter(prefix="/api", tags=["Predictions"])


def save_prediction_to_history(
    result: dict,
    image_path: Path,
    risk_factors: Optional[dict] = None,
) -> None:
    """Persist a prediction into the SQLite history table."""
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO predictions
        (prediction_id, predicted_class, confidence, probabilities, model_type,
         image_filename, gradcam_filename, risk_factors)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result["prediction_id"],
            result["predicted_class"],
            float(result["confidence"]),
            json.dumps(result["probabilities"]),
            result["model_type"],
            image_path.name,
            result.get("gradcam_filename"),
            json.dumps(risk_factors) if risk_factors else None,
        ),
    )

    conn.commit()
    conn.close()


def validate_image(file: UploadFile) -> None:
    """Validate uploaded image file."""
    allowed_types = {"image/jpeg", "image/png", "image/jpg"}
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed: {allowed_types}"
        )


async def save_upload(file: UploadFile) -> Path:
    """Save uploaded file and return path."""
    file_ext = Path(file.filename).suffix or ".png"
    filename = f"{uuid.uuid4()}{file_ext}"
    filepath = Path(settings.UPLOADS_DIR) / filename
    
    contents = await file.read()
    
    with open(filepath, "wb") as f:
        f.write(contents)
    
    return filepath


@router.post("/predict", response_model=PredictionResponse)
async def predict_xray(
    file: UploadFile = File(..., description="Chest X-ray image (JPEG or PNG)")
):
    """
    Predict respiratory disease from chest X-ray image.
    
    Analyzes the uploaded X-ray using the ResNet50V2 model and returns:
    - Predicted disease class (COVID, NORMAL, PNEUMONIA, TUBERCULOSIS)
    - Confidence score
    - Probability distribution across all classes
    - Grad-CAM visualization URL
    """
    validate_image(file)
    
    try:
        filepath = await save_upload(file)

        result = predict_image(
            image=filepath,
            generate_gradcam=True,
            save_gradcam=True,
        )

        if "gradcam_filename" in result:
            result["gradcam_url"] = f"/api/gradcam/{result['gradcam_filename']}"

        # Save to prediction history
        save_prediction_to_history(result, filepath)

        return PredictionResponse(
            prediction_id=result["prediction_id"],
            timestamp=result["timestamp"],
            predicted_class=result["predicted_class"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
            model_type=result["model_type"],
            gradcam_url=result.get("gradcam_url")
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/predict/full", response_model=FusionPredictionResponse)
async def predict_full(
    file: UploadFile = File(..., description="Chest X-ray image"),
    age: int = Form(..., ge=0, le=120, description="Patient age"),
    gender: str = Form(..., description="Patient gender (male/female)"),
    smoker: bool = Form(default=False, description="Smoking status"),
    asthma: bool = Form(default=False, description="Asthma history"),
    genetic_risk: bool = Form(default=False, description="Family history"),
    congenital_lung_defect: bool = Form(default=False, description="Congenital lung defects")
):
    """
    Predict using combined image and risk factor analysis.
    
    Combines:
    - Chest X-ray image analysis (ResNet50V2)
    - Patient risk factors (tabular model)
    
    Returns fused prediction with higher accuracy for complex cases.
    """
    validate_image(file)
    
    if gender.lower() not in ["male", "female"]:
        raise HTTPException(
            status_code=400,
            detail="Gender must be 'male' or 'female'"
        )
    
    try:
        filepath = await save_upload(file)

        risk_data = {
            "age": age,
            "gender": gender.lower(),
            "smoker": smoker,
            "asthma": asthma,
            "genetic_risk": genetic_risk,
            "congenital_lung_defect": congenital_lung_defect,
        }

        result = predict_fusion(
            image=filepath,
            age=age,
            gender=gender.lower(),
            smoker=smoker,
            asthma=asthma,
            genetic_risk=genetic_risk,
            congenital_lung_defect=congenital_lung_defect,
            generate_gradcam=True,
        )

        if "gradcam_filename" in result:
            result["gradcam_url"] = f"/api/gradcam/{result['gradcam_filename']}"

        # Save to prediction history (including risk factors)
        save_prediction_to_history(result, filepath, risk_factors=risk_data)

        return FusionPredictionResponse(
            prediction_id=result["prediction_id"],
            timestamp=result["timestamp"],
            predicted_class=result["predicted_class"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
            model_type=result["model_type"],
            gradcam_url=result.get("gradcam_url"),
            risk_factors=RiskFactors(**risk_data),
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
