"""
RespiratoryAI - FastAPI Backend

Chest X-ray respiratory disease classification using ResNet50V2.
Supports image-only and fusion (image + risk factors) predictions.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.config import settings
from backend.api.routes import predict, gradcam, history, health


app = FastAPI(
    title="RespiratoryAI",
    description="""
    AI-powered respiratory disease detection from chest X-rays.
    
    ## Features
    - **Image Classification**: Detect COVID-19, Pneumonia, Tuberculosis, or Normal
    - **Risk Factor Analysis**: Combine X-ray with patient risk factors
    - **Explainability**: Grad-CAM visualizations showing model focus areas
    
    ## Models
    - ResNet50V2 for image classification
    - Risk factor model for tabular data
    - Fusion model combining both modalities
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(gradcam.router)
app.include_router(history.router)
app.include_router(health.router)

uploads_dir = Path(settings.UPLOADS_DIR)
if uploads_dir.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/", tags=["Root"])
async def root():
    """API root - basic status check."""
    return {
        "name": "RespiratoryAI",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    settings.ensure_dirs()
    
    image_model_exists = Path(settings.IMAGE_MODEL_PATH).exists()
    
    print("\n" + "="*50)
    print("RespiratoryAI API Started")
    print("="*50)
    print(f"Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"Image model: {'✅ Loaded' if image_model_exists else '❌ Not found'}")
    print("="*50 + "\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
