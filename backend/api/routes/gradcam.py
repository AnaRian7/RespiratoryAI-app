"""
Grad-CAM Visualization API Routes

Endpoints:
    GET /api/gradcam/{filename}  - Get Grad-CAM visualization image
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.config import settings


router = APIRouter(prefix="/api", tags=["Explainability"])


@router.get("/gradcam/{filename}")
async def get_gradcam(filename: str):
    """
    Retrieve Grad-CAM visualization image.
    
    Returns the heatmap overlay showing which regions of the X-ray
    most influenced the model's prediction.
    """
    safe_filename = Path(filename).name
    
    filepath = Path(settings.GRADCAM_DIR) / safe_filename
    
    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Grad-CAM visualization not found: {filename}"
        )
    
    return FileResponse(
        path=str(filepath),
        media_type="image/png",
        filename=safe_filename
    )
