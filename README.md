# RespiratoryAI

AI-powered respiratory disease detection from chest X-ray images using deep learning.

Paper: *Respiratory Disease Detection and Classification using Deep Learning* (ICAIEHS 2025).

## Overview

RespiratoryAI classifies chest X-rays into four classes with a ResNet-50 CNN and Grad-CAM explainability:

- **COVID-19**
- **Normal**
- **Pneumonia**
- **Tuberculosis**

The deployed app follows the paper pipeline: upload an X-ray in the web UI → preprocess (224×224) → ResNet-50 classification → Grad-CAM heatmap → diagnostic report.

## Features

- **ResNet-50**: residual CNN, ImageNet initialization, 4-class softmax
- **Grad-CAM**: heatmap of regions that influenced the prediction
- **Web interface**: upload, confidence scores, and prediction history
- **REST API**: FastAPI (`/api/predict`, `/api/gradcam`, `/api/history`, `/api/health`)
- **Docker**: single container serving the UI and API

## Quick Start (local)

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### 2. Frontend (development)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. Vite proxies `/api` to the backend on port 8000.

### 3. Single-app deploy (UI + API on port 8000)

```bash
cd frontend
npm install
npm run build
cd ..
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

## Docker

Requires the trained weights in `saved_models/resnet50v2_xray.keras`.

```bash
docker compose up --build
```

Open http://localhost:8000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict` | Predict from X-ray image |
| `GET` | `/api/history` | List prediction history |
| `GET` | `/api/history/{id}` | Get prediction details |
| `GET` | `/api/gradcam/{filename}` | Get Grad-CAM image |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/model/info` | Model information |

API docs: http://localhost:8000/docs

## Training

```bash
python -m backend.datasets.download --all
python -m backend.datasets.harmonize
python -m backend.training.train --model image
```

- **Base**: ResNet-50 (pre-trained on ImageNet)
- **Head**: GlobalAveragePooling2D → BatchNorm → Dropout(0.5) → Dense(256) → BatchNorm → Dropout(0.3) → Dense(4, softmax)
- **Input**: 224 × 224 × 3
- **Loss**: categorical cross-entropy
- **Optimizer**: Adam (lr=1e-4)
- **Augmentation**: rotation, zoom, horizontal flip
- **Class weights**: balanced

## Disclaimer

This tool is for **research and educational purposes only**. It is not a medical device and must not replace professional medical advice, diagnosis, or treatment.

## License

MIT License
