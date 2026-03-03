# RespiratoryAI - Complete Setup Guide

This guide walks you through setting up Kaggle credentials, training the model, and deploying to the cloud.

---

## Part 1: Kaggle API Setup

### Step 1: Create Kaggle Account
1. Go to [kaggle.com](https://www.kaggle.com) and sign up/login
2. Verify your email address

### Step 2: Generate API Token
1. Click on your profile picture (top right) → **Settings**
2. Scroll down to **API** section
3. Click **Create New Token**
4. This downloads a file called `kaggle.json`

### Step 3: Install Kaggle Credentials

**Windows (PowerShell):**
```powershell
# Create .kaggle directory
mkdir $env:USERPROFILE\.kaggle -Force

# Copy your downloaded kaggle.json
Copy-Item "C:\Users\YourName\Downloads\kaggle.json" "$env:USERPROFILE\.kaggle\kaggle.json"

# Verify
Get-Content "$env:USERPROFILE\.kaggle\kaggle.json"
```

**Linux/Mac:**
```bash
mkdir -p ~/.kaggle
cp ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Step 4: Verify Kaggle Setup
```powershell
# Activate your virtual environment first
.\venv\Scripts\Activate

# Test Kaggle CLI
kaggle datasets list --sort-by votes
```

If you see a list of datasets, you're set!

---

## Part 2: Download and Prepare Data

### Step 1: Download Datasets
```powershell
# From project root
cd C:\Users\anari\OneDrive\Desktop\RespiratoryAI

# Activate virtual environment
.\venv\Scripts\Activate

# Download all datasets (may take 10-30 minutes depending on internet)
python -m backend.datasets.download --all
```

### Step 2: Harmonize Data
```powershell
# Consolidate datasets into unified structure
python -m backend.datasets.harmonize
```

This creates:
- `data/images/COVID/` - COVID-19 X-rays
- `data/images/NORMAL/` - Healthy X-rays
- `data/images/PNEUMONIA/` - Pneumonia X-rays
- `data/images/TUBERCULOSIS/` - TB X-rays

---

## Part 3: Train the Model

### Option A: Train Image Model Only (Recommended for start)
```powershell
python -m backend.training.train --model image
```

Expected output:
- Training progress with loss/accuracy per epoch
- Early stopping if validation loss stops improving
- Model saved to `saved_models/resnet50v2_xray.keras`

**Training time estimates:**
- CPU: 2-4 hours (depending on dataset size)
- GPU: 15-30 minutes

### Option B: Train All Models
```powershell
python -m backend.training.train --all
```

### Option C: Fine-tune (after initial training)
```powershell
python -m backend.training.train --model image --fine-tune
```

---

## Part 4: Run Locally

### Start Backend
```powershell
# Terminal 1
cd C:\Users\anari\OneDrive\Desktop\RespiratoryAI
.\venv\Scripts\Activate
uvicorn backend.app:app --reload
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Start Frontend
```powershell
# Terminal 2
cd C:\Users\anari\OneDrive\Desktop\RespiratoryAI\frontend
npm install  # First time only
npm run dev
```

Frontend runs at: http://localhost:3000

---

## Part 5: Cloud Deployment

### Option A: Deploy to Azure (Recommended for Windows users)

#### 1. Install Azure CLI
Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows

#### 2. Login and Setup
```powershell
az login
az group create --name respiratory-ai-rg --location eastus
az acr create --resource-group respiratory-ai-rg --name respiratoryairegistry --sku Basic
az acr login --name respiratoryairegistry
```

#### 3. Build and Push Docker Image
```powershell
# Build image
docker build -t respiratory-ai .

# Tag for Azure Container Registry
docker tag respiratory-ai respiratoryairegistry.azurecr.io/respiratory-ai:v1

# Push
docker push respiratoryairegistry.azurecr.io/respiratory-ai:v1
```

#### 4. Deploy to Azure Container Instances
```powershell
az container create `
  --resource-group respiratory-ai-rg `
  --name respiratory-ai-container `
  --image respiratoryairegistry.azurecr.io/respiratory-ai:v1 `
  --cpu 2 --memory 4 `
  --ports 8000 `
  --dns-name-label respiratory-ai-app `
  --registry-login-server respiratoryairegistry.azurecr.io `
  --registry-username $(az acr credential show --name respiratoryairegistry --query username -o tsv) `
  --registry-password $(az acr credential show --name respiratoryairegistry --query passwords[0].value -o tsv)
```

Your app will be available at: `http://respiratory-ai-app.eastus.azurecontainer.io:8000`

---

### Option B: Deploy to AWS (ECS)

#### 1. Install AWS CLI
Download from: https://aws.amazon.com/cli/

#### 2. Configure AWS
```powershell
aws configure
# Enter your AWS Access Key ID, Secret Key, Region (e.g., us-east-1)
```

#### 3. Create ECR Repository
```powershell
aws ecr create-repository --repository-name respiratory-ai
```

#### 4. Build and Push
```powershell
# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t respiratory-ai .
docker tag respiratory-ai:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/respiratory-ai:latest

# Push
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/respiratory-ai:latest
```

#### 5. Deploy with ECS (using AWS Console)
1. Go to AWS ECS Console
2. Create Cluster → Networking only (Fargate)
3. Create Task Definition with your ECR image
4. Create Service with ALB load balancer

---

### Option C: Deploy to Google Cloud Run (Simplest)

#### 1. Install gcloud CLI
Download from: https://cloud.google.com/sdk/docs/install

#### 2. Setup Project
```powershell
gcloud init
gcloud config set project YOUR_PROJECT_ID
```

#### 3. Deploy (One Command!)
```powershell
gcloud run deploy respiratory-ai `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 4Gi `
  --cpu 2
```

Google Cloud Run automatically:
- Builds your Docker image
- Deploys it
- Gives you an HTTPS URL

---

### Option D: Deploy to Railway (Easiest for beginners)

1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway auto-detects Dockerfile and deploys
4. Get a free HTTPS URL instantly

---

## Part 6: Environment Variables for Production

Create a `.env` file for production:

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# CORS (update with your frontend domain)
CORS_ORIGINS=https://your-frontend-domain.com,http://localhost:3000

# Database (for production, consider PostgreSQL)
DATABASE_URL=sqlite:///./medical_ai.db
```

---

## Troubleshooting

### Kaggle API Errors

**"Could not find kaggle.json"**
```powershell
# Check if file exists
Test-Path "$env:USERPROFILE\.kaggle\kaggle.json"

# Check contents
Get-Content "$env:USERPROFILE\.kaggle\kaggle.json"
```

**"401 - Unauthorized"**
- Regenerate your API token on Kaggle
- Replace the old `kaggle.json`

### Training Errors

**"OOM (Out of Memory)"**
- Reduce batch size in `backend/config.py`: `BATCH_SIZE = 8`
- Use a smaller image size: `IMAGE_SIZE = (160, 160)`

**"No images found"**
- Verify data downloaded: `ls data/raw/`
- Re-run harmonization: `python -m backend.datasets.harmonize`

### Docker Errors

**"Cannot connect to Docker daemon"**
- Ensure Docker Desktop is running
- On Windows, check WSL2 is enabled

---

## GPU Support (Optional but Recommended)

### NVIDIA GPU (CUDA)
```powershell
# Install CUDA-enabled TensorFlow
pip install tensorflow[and-cuda]
```

### Verify GPU
```python
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
```

---

## Next Steps

1. **Improve Accuracy**: Collect more diverse training data
2. **Add More Diseases**: Extend to other lung conditions
3. **Mobile App**: Build a React Native companion app
4. **HIPAA Compliance**: For clinical use, add proper data encryption and audit logs
