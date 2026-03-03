"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RiskFactors(BaseModel):
    """Patient risk factors for fusion prediction."""
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    gender: str = Field(..., pattern="^(male|female)$", description="Patient gender")
    smoker: bool = Field(default=False, description="Current or former smoker")
    asthma: bool = Field(default=False, description="History of asthma")
    genetic_risk: bool = Field(default=False, description="Family history of respiratory disease")
    congenital_lung_defect: bool = Field(default=False, description="Congenital lung defects")


class PredictionProbabilities(BaseModel):
    """Probability distribution across disease classes."""
    COVID: float
    NORMAL: float
    PNEUMONIA: float
    TUBERCULOSIS: float


class PredictionResponse(BaseModel):
    """Response schema for prediction endpoints."""
    prediction_id: str
    timestamp: str
    predicted_class: str
    confidence: float = Field(..., ge=0, le=1)
    probabilities: PredictionProbabilities
    model_type: str
    gradcam_url: Optional[str] = None


class FusionPredictionResponse(PredictionResponse):
    """Extended response including risk factor analysis."""
    risk_factors: RiskFactors


class PredictionHistoryItem(BaseModel):
    """Single prediction history record."""
    id: int
    prediction_id: str
    predicted_class: str
    confidence: float
    model_type: str
    created_at: datetime
    image_filename: Optional[str] = None
    gradcam_filename: Optional[str] = None


class PredictionHistoryResponse(BaseModel):
    """Paginated prediction history response."""
    items: list[PredictionHistoryItem]
    total: int
    page: int
    page_size: int


class TrainingLabelCreate(BaseModel):
    """Request body for assigning a ground-truth label to a prediction."""
    true_label: str = Field(..., description="Confirmed ground-truth class")
    notes: Optional[str] = Field(default=None, description="Optional annotation or comments")


class TrainingLabelResponse(BaseModel):
    """Response for a stored training label."""
    prediction_id: str
    true_label: str
    notes: Optional[str] = None
    created_at: datetime


class HealthResponse(BaseModel):
    """API health check response."""
    status: str
    version: str
    models_loaded: dict[str, bool]


class ModelInfoResponse(BaseModel):
    """Model information response."""
    name: str
    architecture: str
    input_shape: list[int]
    num_classes: int
    classes: list[str]
    trainable_params: Optional[int] = None
