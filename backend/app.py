"""
RespiratoryAI - FastAPI backend

Paper-based chest X-ray classifier: ResNet-50, four classes, Grad-CAM, web UI.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.api.routes import predict, gradcam, history, health


app = FastAPI(
    title="RespiratoryAI",
    description="""
    Deep learning system for respiratory disease detection from chest X-rays.

    Classifies COVID-19, Pneumonia, Tuberculosis, or Normal using ResNet-50
    and returns Grad-CAM heatmaps for interpretability.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(gradcam.router)
app.include_router(history.router)
app.include_router(health.router)

uploads_dir = Path(settings.UPLOADS_DIR)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

FRONTEND_DIST = Path(settings.FRONTEND_DIST)
if (FRONTEND_DIST / "assets").exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets")),
        name="frontend-assets",
    )


@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    """Serve the web UI when built; otherwise return API status."""
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return FileResponse(index)
    return {
        "name": "RespiratoryAI",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    """Serve the React app for client-side routes."""
    reserved = ("api", "docs", "redoc", "openapi.json", "uploads")
    if full_path.startswith(reserved) or full_path.split("/")[0] in reserved:
        raise HTTPException(status_code=404, detail="Not found")

    index = FRONTEND_DIST / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Frontend not built")

    candidate = FRONTEND_DIST / full_path
    if candidate.is_file():
        return FileResponse(candidate)
    return FileResponse(index)


@app.on_event("startup")
async def startup_event():
    """Initialize directories and report model status."""
    settings.ensure_dirs()

    image_model_exists = Path(settings.IMAGE_MODEL_PATH).exists()
    frontend_built = (FRONTEND_DIST / "index.html").exists()

    print("\n" + "=" * 50)
    print("RespiratoryAI API Started")
    print("=" * 50)
    print(f"Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"App:  http://{settings.API_HOST}:{settings.API_PORT}/")
    print(f"Image model: {'loaded' if image_model_exists else 'NOT FOUND'}")
    print(f"Frontend:    {'built' if frontend_built else 'NOT BUILT (run npm run build)'}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
