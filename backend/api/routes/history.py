"""
Prediction History API Routes

Endpoints:
    GET /api/history      - List past predictions
    GET /api/history/{id} - Get single prediction details
"""

import sqlite3
from typing import Optional
import json

from fastapi import APIRouter, HTTPException, Query, Body

from backend.config import settings
from backend.api.schemas import (
    PredictionHistoryItem,
    PredictionHistoryResponse,
    TrainingLabelCreate,
    TrainingLabelResponse,
)


router = APIRouter(prefix="/api", tags=["History"])


def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_predictions_table():
    """Initialize predictions and training label tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id TEXT UNIQUE NOT NULL,
            predicted_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            probabilities TEXT,
            model_type TEXT NOT NULL,
            image_filename TEXT,
            gradcam_filename TEXT,
            risk_factors TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_predictions_created 
        ON predictions(created_at DESC)
    """)

    # Ground-truth labels attached to predictions for future retraining
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id TEXT NOT NULL,
            true_label TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(prediction_id)
        )
    """)
    
    conn.commit()
    conn.close()


init_predictions_table()


@router.get("/history", response_model=PredictionHistoryResponse)
async def list_predictions(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    model_type: Optional[str] = Query(default=None, description="Filter by model type"),
    predicted_class: Optional[str] = Query(default=None, description="Filter by predicted class")
):
    """
    List prediction history with pagination and filtering.
    
    Returns past predictions sorted by most recent first.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clauses = []
    params = []
    
    if model_type:
        where_clauses.append("model_type = ?")
        params.append(model_type)
    
    if predicted_class:
        where_clauses.append("predicted_class = ?")
        params.append(predicted_class)
    
    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)
    
    cursor.execute(f"SELECT COUNT(*) FROM predictions {where_sql}", params)
    total = cursor.fetchone()[0]
    
    offset = (page - 1) * page_size
    
    cursor.execute(f"""
        SELECT id, prediction_id, predicted_class, confidence, model_type,
               image_filename, gradcam_filename, created_at
        FROM predictions
        {where_sql}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, params + [page_size, offset])
    
    rows = cursor.fetchall()
    conn.close()
    
    items = [
        PredictionHistoryItem(
            id=row["id"],
            prediction_id=row["prediction_id"],
            predicted_class=row["predicted_class"],
            confidence=row["confidence"],
            model_type=row["model_type"],
            image_filename=row["image_filename"],
            gradcam_filename=row["gradcam_filename"],
            created_at=row["created_at"]
        )
        for row in rows
    ]
    
    return PredictionHistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/history/{prediction_id}")
async def get_prediction(prediction_id: str):
    """
    Get detailed information about a specific prediction.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM predictions WHERE prediction_id = ?
    """, (prediction_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Prediction not found: {prediction_id}"
        )
    
    return {
        "id": row["id"],
        "prediction_id": row["prediction_id"],
        "predicted_class": row["predicted_class"],
        "confidence": row["confidence"],
        "probabilities": json.loads(row["probabilities"]) if row["probabilities"] else None,
        "model_type": row["model_type"],
        "image_filename": row["image_filename"],
        "gradcam_filename": row["gradcam_filename"],
        "gradcam_url": f"/api/gradcam/{row['gradcam_filename']}" if row["gradcam_filename"] else None,
        "risk_factors": json.loads(row["risk_factors"]) if row["risk_factors"] else None,
        "created_at": row["created_at"]
    }


@router.post("/history/{prediction_id}/label", response_model=TrainingLabelResponse)
async def add_training_label(
    prediction_id: str,
    payload: TrainingLabelCreate = Body(...),
):
    """
    Attach a confirmed ground-truth label to an existing prediction.
    """
    # Basic validation against known classes
    if payload.true_label not in settings.CLASSES:
        raise HTTPException(
            status_code=400,
            detail=f"true_label must be one of {settings.CLASSES}",
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure prediction exists
    cursor.execute(
        "SELECT 1 FROM predictions WHERE prediction_id = ?",
        (prediction_id,),
    )
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Prediction not found: {prediction_id}",
        )

    cursor.execute(
        """
        INSERT INTO training_labels (prediction_id, true_label, notes)
        VALUES (?, ?, ?)
        ON CONFLICT(prediction_id) DO UPDATE SET
            true_label = excluded.true_label,
            notes = excluded.notes
        """,
        (prediction_id, payload.true_label, payload.notes),
    )

    cursor.execute(
        """
        SELECT prediction_id, true_label, notes, created_at
        FROM training_labels WHERE prediction_id = ?
        """,
        (prediction_id,),
    )
    row = cursor.fetchone()
    conn.commit()
    conn.close()

    return TrainingLabelResponse(
        prediction_id=row["prediction_id"],
        true_label=row["true_label"],
        notes=row["notes"],
        created_at=row["created_at"],
    )
