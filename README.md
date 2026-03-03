# RespiratoryAI

AI-powered respiratory disease detection from chest X-ray images using deep learning.

## Overview

RespiratoryAI is an end-to-end system that uses a ResNet50V2-based convolutional neural network to classify chest X-ray images into four categories:

- **COVID-19** - SARS-CoV-2 infection patterns
- **Normal** - Healthy chest X-ray
- **Pneumonia** - Bacterial or viral pneumonia
- **Tuberculosis** - TB infection patterns

## Features

- **ResNet50V2 Architecture**: State-of-the-art deep learning model pre-trained on ImageNet
- **Grad-CAM Explainability**: Visual heatmaps showing model focus areas
- **Multi-Modal Fusion**: Combine X-ray analysis with patient risk factors
- **Modern Web Interface**: React + Tailwind CSS frontend
- **REST API**: FastAPI backend with comprehensive endpoints
- **Docker Ready**: Containerized for easy cloud deployment

## Project Structure

```
RespiratoryAI/
├── backend/
│   ├── api/                    # API routes
│   │   └── routes/
│   │       ├── predict.py      # Prediction endpoints
│   │       ├── gradcam.py      # Explainability endpoints
│   │       ├── history.py      # History endpoints
│   │       └── health.py       # Health check
│   ├── models/
│   │   ├── image_model.py      # ResNet50V2 classifier
│   │   ├── risk_model.py       # Tabular risk model
│   │   └── fusion_model.py     # Combined model
│   ├── inference/
│   │   ├── predictor.py        # Inference pipeline
│   │   └── gradcam.py          # Grad-CAM visualization
│   ├── preprocessing/
│   │   └── image.py            # Image data generators
│   ├── datasets/
│   │   ├── download.py         # Kaggle dataset downloader
│   │   └── harmonize.py        # Data consolidation
│   ├── training/
│   │   └── train.py            # Training pipeline
│   ├── config.py               # Configuration
│   └── app.py                  # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── api/                # API client
│   │   └── types/              # TypeScript types
│   └── package.json
├── data/                       # Datasets
├── saved_models/               # Trained models
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Kaggle API credentials (for dataset download)

### 1. Clone and Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Download Datasets

```bash
# Configure Kaggle API (place kaggle.json in ~/.kaggle/)
python -m backend.datasets.download --all
```

### 3. Harmonize Data

```bash
python -m backend.datasets.harmonize
```

### 4. Train the Model

```bash
python -m backend.training.train --model image
```

### 5. Run the Application

**Backend:**
```bash
uvicorn backend.app:app --reload
```

**Frontend (in another terminal):**
```bash
cd frontend
npm run dev
```

Open http://localhost:3000 in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict` | Predict from X-ray image |
| `POST` | `/api/predict/full` | Predict with risk factors |
| `GET` | `/api/history` | List prediction history |
| `GET` | `/api/history/{id}` | Get prediction details |
| `GET` | `/api/gradcam/{filename}` | Get Grad-CAM image |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/model/info` | Model information |

API documentation available at http://localhost:8000/docs

## Docker Deployment

```bash
# Build and run
docker-compose up --build

# Or build only
docker build -t respiratory-ai .
docker run -p 8000:8000 respiratory-ai
```

## Training Details

### Model Architecture

- **Base**: ResNet50V2 (pre-trained on ImageNet)
- **Head**: GlobalAveragePooling2D → BatchNorm → Dropout(0.5) → Dense(256) → BatchNorm → Dropout(0.3) → Dense(4, softmax)
- **Input**: 224 × 224 × 3 RGB images
- **Output**: 4-class probability distribution

### Training Configuration

- Optimizer: Adam (lr=1e-4)
- Loss: Categorical Cross-Entropy
- Batch Size: 16
- Epochs: 20 (with early stopping)
- Data Augmentation: Rotation, zoom, horizontal flip
- Class Weighting: Balanced for handling class imbalance

### Datasets

- COVID-19 Radiography Database
- Tuberculosis Chest X-ray Dataset
- Chest X-ray Images (Pneumonia)

## Disclaimer

This tool is for **research and educational purposes only**. It is not intended to be used as a medical diagnostic device and should not replace professional medical advice, diagnosis, or treatment.

## License

MIT License
