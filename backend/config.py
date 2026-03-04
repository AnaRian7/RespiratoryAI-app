import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BASE_DIR.parent


class Settings:
    # ------------------ DATABASE ------------------
    DB_PATH = str(BASE_DIR / "medical_ai.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"

    # ------------------ DATA PATHS ------------------
    DATA_DIR = PROJECT_ROOT / "data"
    DATA_RAW = str(DATA_DIR / "raw")
    DATA_PROCESSED = str(DATA_DIR / "processed")
    DATA_IMAGES = str(DATA_DIR / "images")

    # ------------------ MODEL PATHS ------------------
    MODELS_DIR = PROJECT_ROOT / "saved_models"
    IMAGE_MODEL_PATH = str(MODELS_DIR / "resnet50v2_xray.keras")
    RISK_MODEL_PATH = str(MODELS_DIR / "risk_model.keras")
    FUSION_MODEL_PATH = str(MODELS_DIR / "fusion_model.keras")

    # ✅ NEW: remote model URLs (Hugging Face)
    IMAGE_MODEL_URL = os.getenv(
        "IMAGE_MODEL_URL",
        "https://huggingface.co/Ana7Rian/respiratoryai-image-model/resolve/main/resnet50v2_xray.keras",
    )
    RISK_MODEL_URL = os.getenv(
        "RISK_MODEL_URL",
        "https://huggingface.co/Ana7Rian/respiratoryai-image-model/resolve/main/risk_model.keras",
    )
    FUSION_MODEL_URL = os.getenv(
        "FUSION_MODEL_URL",
        "https://huggingface.co/Ana7Rian/respiratoryai-image-model/resolve/main/fusion_model.keras",
    )

    # ------------------ UPLOADS ------------------
    UPLOADS_DIR = PROJECT_ROOT / "uploads"
    GRADCAM_DIR = PROJECT_ROOT / "gradcam_outputs"
    

    # ------------------ IMAGE SETTINGS ------------------
    IMAGE_SIZE = (224, 224)

    CLASSES = ["COVID", "NORMAL", "PNEUMONIA", "TUBERCULOSIS"]

    CLASS_MAP = {
        "COVID": 0,
        "NORMAL": 1,
        "PNEUMONIA": 2,
        "TUBERCULOSIS": 3,
    }

    INDEX_TO_CLASS = {v: k for k, v in CLASS_MAP.items()}

    NUM_CLASSES = len(CLASSES)

    # ------------------ RISK FACTORS ------------------
    RISK_FEATURES = ["age", "gender", "smoker", "asthma", "genetic_risk", "congenital_lung_defect"]
    NUM_RISK_FEATURES = len(RISK_FEATURES)

    # ------------------ TRAINING ------------------
    BATCH_SIZE = 16
    EPOCHS = 20
    VALIDATION_SPLIT = 0.2
    TEST_SPLIT = 0.1
    LEARNING_RATE = 1e-4

    # ------------------ API SETTINGS ------------------
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

    @classmethod
    def ensure_dirs(cls):
        """Create necessary directories if they don't exist."""
        dirs = [
            cls.DATA_DIR,
            Path(cls.DATA_RAW),
            Path(cls.DATA_PROCESSED),
            Path(cls.DATA_IMAGES),
            cls.MODELS_DIR,
            cls.UPLOADS_DIR,
            cls.GRADCAM_DIR,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()



