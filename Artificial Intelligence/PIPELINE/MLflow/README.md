# 🐟 Fish Weight Prediction MLflow Pipeline

## Overview

```
📁 Fish Weight Prediction MLflow Pipeline
├── Data Layer
│   ├── Dataset/Fish.csv (Raw fish measurements)
│   └── processed_data/ (Cleaned and engineered features)
├── Processing Layer  
│   ├── preprocessing.py (Data cleaning & feature engineering)
│   ├── train.py (Model training with multiple algorithms)
│   └── evaluate.py (Model evaluation & validation)
├── Model Layer
│   ├── Linear Regression (Primary)
│   ├── Ridge Regression
│   ├── Lasso Regression  
│   ├── Elastic Net
│   └── Random Forest (Comparison)
├── Deployment Layer
│   ├── serve_api.py (FastAPI REST API)
│   ├── inference.py (Local predictions)
│   └── AWS SageMaker (Cloud deployment)
└── Tracking Layer
    └── MLflow (Experiment tracking & model registry)
```

## Project

This project demonstrates a **complete MLflow pipeline** for predicting fish weight using **Linear Regression** and other machine learning algorithms. The pipeline includes data preprocessing, model training, evaluation, and deployment with both local REST API and AWS SageMaker integration.

### Features

- **End-to-end MLflow pipeline**: Complete ML lifecycle management
- **Multiple regression models**: Linear, Ridge, Lasso, Elastic Net, Random Forest
- **Comprehensive evaluation**: Statistical metrics, visualizations, residuals analysis
- **REST API**: FastAPI server with cURL examples
- **Cloud deployment**: AWS SageMaker integration
- **Interactive visualizations**: Plotly dashboards and matplotlib plots
- **Confidence intervals**: Bootstrap-based prediction uncertainty

### Dataset: Fish.csv

The Fish.csv dataset contains physical measurements of various fish species:

| Feature | Description | Example |
|---------|-------------|---------|
| Species | Fish species | Bream, Perch, Pike |
| Weight | Fish weight (grams) | 242.0 |
| Length1 | Vertical length (cm) | 23.2 |
| Length2 | Diagonal length (cm) | 25.4 |
| Length3 | Cross length (cm) | 30.0 |
| Height | Height (cm) | 11.52 |
| Width | Diagonal width (cm) | 4.02 |

**Dataset Source**: [Hugging Face - scikit-learn Fish Dataset](https://huggingface.co/datasets/scikit-learn/Fish)

## Steps

### Choose your environment manager

This project supports both **Conda** (recommended) and **Python Virtual Environment**:

#### **Option 1: Conda (Recommended for MLflow)**

```bash
# Setup with conda (better for MLflow projects)
./setup_conda.sh
source activate_conda_env.sh

# Run pipeline
make pipeline
```

**Why Conda is better for MLflow?**
- Native MLflow support with `conda.yaml`
- Dependency management (system + Python packages)
- Optimized scientific computing libraries (Intel MKL, etc.)
- Reproducible across different systems
- Handles complex ML library dependencies automatically

#### **Option 2: Python Virtual Environment**

```bash
# Setup with venv (traditional Python approach)
./setup_mlflow.sh
source activate_env.sh

# Run pipeline
make pipeline
```

### 1. Environment setup (Once)

```bash
# Clone or navigate to the project directory
cd MLflow

# Choose setup method:
# For Conda (recommended):
./setup_conda.sh && source activate_conda_env.sh

# For Virtual Environment:
./setup_mlflow.sh && source activate_env.sh
```

### 2. Download dataset

```bash
# Option 1: Download from Hugging Face
wget https://huggingface.co/datasets/scikit-learn/Fish/raw/main/Fish.csv -O Dataset/Fish.csv

# Option 2: Use existing dataset (if already present)
# The Dataset/Fish.csv should already be in the project
```

### 3. Run pipeline

```bash
# Option 1: Using Make (recommended)
make pipeline

# Option 2: Using MLflow
mlflow run . --experiment-name fish_weight_prediction

# Option 3: Step by step
python preprocessing.py
python train.py
python evaluate.py
```

### 4. Start MLflow UI

```bash
# Start MLflow tracking UI
make ui
# or
mlflow ui --host 0.0.0.0 --port 5000

# Access at: http://localhost:5000
```

### 5. Start REST API server

```bash
# Start FastAPI server
make serve
# or
python serve_api.py

# Access at: http://localhost:8000
# API docs: http://localhost:8000/docs
```

## � Environment Management: Conda vs Virtual Environment

### Conda vs Python Virtual Environment comparison

| Feature | Conda | Python venv |
|---------|-------|-------------|
| **MLflow integration** | ✅ Native support | ⚠️ Requires manual setup |
| **Dependency management** | ✅ System + Python packages | ❌ Python packages only |
| **Libraries** | ✅ Optimized builds (Intel MKL) | ⚠️ Default builds |
| **Reproducibility** | ✅ Cross-platform consistent | ⚠️ Platform dependent |
| **Dependencies** | ✅ Automatic resolution | ❌ Manual management |
| **Setup speed** | ⚠️ Slower initial setup | ✅ Faster setup |
| **Disk space** | ⚠️ Larger footprint | ✅ Smaller footprint |
| **Learning curve** | ⚠️ Steeper | ✅ Familiar to Python devs |

### **Recommendation: Use Conda for MLflow projects**

For this MLflow pipeline, **conda is strongly recommended** because:

1. **MLflow native support**: MLflow automatically creates conda environments from `conda.yaml`
2. **Performance**: Optimized scientific computing libraries
3. **Dependencies**: Conda resolves complex ML library conflicts
4. **Production**: More reliable for deployment scenarios

### Available setup options

```bash
# Conda Setup (Recommended)
./setup_conda.sh
source activate_conda_env.sh

# Python venv Setup (Alternative)
./setup_mlflow.sh
source activate_env.sh

# 🐋 Docker Setup (Container)
docker-compose -f docker-compose.mlflow.yml up
```

## � Setup instructions

### Prerequisites

- **Operating System**: Linux/Debian (Ubuntu 20.04+ recommended)
- **Python**: 3.8 or higher
- **Make**: GNU Make tool
- **Git**: Version control
- **curl**: For API testing

### System dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git curl wget build-essential make

# CentOS/RHEL
sudo yum update -y
sudo yum install -y python3 python3-pip git curl wget gcc gcc-c++ make
```

### Python environment setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate

# Install MLflow with pipelines support
pip install mlflow[pipelines]>=2.8.0

# Install all dependencies
pip install -r requirements.txt
```

### Directory structure creation

```bash
mkdir -p {models,plots,evaluation_plots,detailed_evaluation,processed_data,logs}
```

## Data processing pipeline

### 1. Data cloading and exploration

```python
# Load dataset
python preprocessing.py
```

**Outputs:**
- Dataset shape and statistics
- Missing value analysis
- Species distribution
- Feature correlation matrix

### 2. Data cleaning

- **Missing Values**: Removal of incomplete records
- **Outlier Detection**: IQR-based outlier removal for weight
- **Data Type Conversion**: Ensure numeric types
- **Quality Validation**: Data integrity checks

### 3. Feature Engineering

```python
# Generated Features:
Length_avg = (Length1 + Length2 + Length3) / 3
Volume_proxy = Length_avg × Height × Width
Length_diff = Length3 - Length1
Aspect_ratio = Length_avg / Height
Body_index = Height / Width
Species_encoded = LabelEncoded(Species)
```

### 4. Visualization

- Species distribution plots
- Correlation heatmaps
- Feature scatter matrices
- Interactive Plotly dashboards

## Model training

### Algorithms

1. **Linear Regression** (Primary)
   - Simple linear relationship modeling
   - Coefficient interpretability
   - Fast training and prediction

2. **Ridge Regression**
   - L2 regularization
   - Handles multicollinearity
   - Prevents overfitting

3. **Lasso Regression**
   - L1 regularization
   - Feature selection capability
   - Sparse coefficient vectors

4. **Elastic Net**
   - Combined L1 and L2 regularization
   - Balanced feature selection and grouping
   - Robust to correlated features

5. **Random Forest** (Comparison)
   - Ensemble method
   - Feature importance ranking
   - Non-linear relationship modeling

### Training process

```bash
# Train all models with comparison
python train.py --test_size 0.2 --random_state 42 --alpha 1.0

# With custom parameters
python train.py --test_size 0.3 --alpha 0.5
```

### Model selection criteria

- **Primary Metric**: R² (Coefficient of Determination)
- **Secondary Metrics**: RMSE, MAE, Cross-validation score
- **Validation**: 5-fold cross-validation
- **Best Model**: Automatically selected and saved

## Model evaluation

### Evaluation metrics

```python
python evaluate.py
```

**Metrics:**
- **R² Score**: Variance explained by the model
- **RMSE**: Root Mean Square Error
- **MAE**: Mean Absolute Error
- **MAPE**: Mean Absolute Percentage Error
- **Residuals Analysis**: Distribution and patterns

### Evaluation visualizations

1. **Actual vs Predicted Plot**
   - Perfect prediction line
   - Confidence bands
   - R² annotation

2. **Residuals Analysis**
   - Residuals vs Predicted
   - Residuals distribution histogram
   - Q-Q plot for normality
   - Residuals vs Actual values

3. **Error Analysis by Weight Range**
   - Absolute error boxplots
   - Relative error analysis
   - Performance across different fish sizes

4. **Feature Importance Analysis**
   - Coefficient magnitudes (Linear models)
   - Feature importance scores (Tree models)

### Sample results

```
Evaluation Results:
  R² Score: 0.9234
  RMSE: 45.67 grams
  MAE: 32.14 grams
  MAPE: 8.45%
```

## Inference and predictions

### Local predictions

```bash
# Sample predictions
python inference.py --samples

# Custom prediction
python inference.py \
  --species "Bream" \
  --length1 23.2 \
  --length2 25.4 \
  --length3 30.0 \
  --height 11.52 \
  --width 4.02 \
  --confidence

# Using MLflow model registry
python inference.py --model_uri "models:/fish_weight_predictor/latest"
```

### Prediction with confidence intervals

```python
# Example output:
Predicted Weight: 242.15 grams
95% Confidence Interval: [228.34, 255.96] grams
```

## REST API server

### Starting the API server

```bash
# Start FastAPI server
python serve_api.py

# Server starts at: http://localhost:8000
# Interactive docs: http://localhost:8000/docs
# Redoc docs: http://localhost:8000/redoc
```

### API Endpoints

#### Health Check
```bash
curl -X GET "http://localhost:8000/"
```

#### Single Fish prediction
```bash
curl -X POST "http://localhost:8000/predict" \
-H "Content-Type: application/json" \
-d '{
  "species": "Bream",
  "length1": 23.2,
  "length2": 25.4,
  "length3": 30.0,
  "height": 11.52,
  "width": 4.02
}'
```

#### Batch predictions
```bash
curl -X POST "http://localhost:8000/predict/batch" \
-H "Content-Type: application/json" \
-d '{
  "fish_list": [
    {
      "species": "Bream",
      "length1": 23.2,
      "length2": 25.4,
      "length3": 30.0,
      "height": 11.52,
      "width": 4.02
    },
    {
      "species": "Perch",
      "length1": 18.7,
      "length2": 20.0,
      "length3": 22.2,
      "height": 8.54,
      "width": 2.56
    }
  ]
}'
```

#### Get available species
```bash
curl -X GET "http://localhost:8000/species"
```

#### Model information
```bash
curl -X GET "http://localhost:8000/model/info"
```

#### cURL examples
```bash
curl -X GET "http://localhost:8000/examples/curl"
```

### API response format

```json
{
  "species": "Bream",
  "predicted_weight": 242.15,
  "confidence_interval_lower": 228.34,
  "confidence_interval_upper": 255.96,
  "features_used": {
    "Length1": 23.2,
    "Length2": 25.4,
    "Length3": 30.0,
    "Height": 11.52,
    "Width": 4.02,
    "Length_avg": 26.2,
    "Volume_proxy": 1217.47,
    "Length_diff": 6.8,
    "Aspect_ratio": 2.27,
    "Body_index": 2.87,
    "Species_encoded": 0
  },
  "prediction_timestamp": "2025-08-04T10:30:45.123456"
}
```

## ☁️ Amazon AWS deployment

### Prerequisites for Amazon AWS deployment

```bash
# Install AWS CLI
sudo apt-get install awscli
# or
pip install awscli

# Configure AWS credentials
aws configure
```

### Deploy to Amazon SageMaker

```bash
# Deploy model to SageMaker
chmod +x deploy_aws.sh
./deploy_aws.sh
```

### Amazon AWS deployment process

1. **S3 Bucket Creation**: For model artifacts storage
2. **IAM Role Setup**: SageMaker execution permissions
3. **Model Packaging**: Tar file with inference code
4. **SageMaker Model**: Model registration in SageMaker
5. **Endpoint Configuration**: Instance type and scaling
6. **Endpoint Creation**: Live inference endpoint

### Testing SageMaker Endpoint

```bash
# Test the deployed endpoint
python test_sagemaker_endpoint.py
```

### Amazon AWS resources

```bash
# Monitor endpoint status
aws sagemaker describe-endpoint --endpoint-name fish-weight-endpoint

# List all endpoints
aws sagemaker list-endpoints

# Cleanup resources (to avoid charges)
./cleanup_aws_resources.sh
```

### Cost

- **ml.t2.medium**: ~$0.0464 per hour
- **Data transfer**: Minimal for small predictions
- **Storage**: S3 charges for model artifacts

** Important**: Delete endpoints when not in use to avoid unnecessary charges.

## MLflow Integration

### MLflow components

1. **MLflow Tracking**: Experiment and run tracking
2. **MLflow Projects**: Reproducible ML code packaging
3. **MLflow Models**: Model packaging and deployment
4. **MLflow Model Registry**: Model versioning and staging

### MLflow experiments

```bash
# View experiments in UI
mlflow ui

# List experiments via CLI
mlflow experiments list

# Search runs
mlflow runs list --experiment-id 1
```

### Model Registry operations

```bash
# Register model
mlflow models register --model-uri runs:/<run-id>/fish_weight_predictor --name fish_weight_predictor

# Transition model stage
mlflow models transition --name fish_weight_predictor --version 1 --stage Production

# Serve model locally
mlflow models serve -m models:/fish_weight_predictor/Production -p 8001
```

### Experiment tracking

Each run automatically logs:
- **Parameters**: test_size, random_state, alpha, model_type
- **Metrics**: R², RMSE, MAE, MAPE, cross-validation scores
- **Artifacts**: Model files, plots, evaluation reports
- **Tags**: Git commit, user, environment info

## 🛠️ Development commands

### Make commands

```bash
# See all available commands
make help

# Setup environment
make setup

# Run individual steps
make preprocess    # Data preprocessing
make train        # Model training
make evaluate     # Model evaluation
make serve        # Start API server

# Complete pipeline
make pipeline

# Start MLflow UI
make ui

# Clean generated files
make clean

# MLflow specific commands
make mlflow-run    # Run MLflow project
make mlflow-serve  # Serve model via MLflow
```

### MLflow commands

```bash
# Run complete pipeline
mlflow run . --experiment-name fish_weight_prediction

# Run with parameters
mlflow run . -P test_size=0.3 -P alpha=0.5

# Run specific entry point
mlflow run . -e train -P test_size=0.2

# Serve model
mlflow models serve -m models:/fish_weight_predictor/latest -p 8001
```

### Python scripts

```bash
# Data preprocessing
python preprocessing.py

# Model training with parameters
python train.py --test_size 0.2 --random_state 42 --alpha 1.0

# Model evaluation
python evaluate.py

# Inference examples
python inference.py --samples
python inference.py --species "Pike" --length1 35.0 --length2 38.5 --length3 41.0 --height 9.85 --width 3.33 --confidence

# API server
python serve_api.py

# Test setup
python test_setup.py
```

## 📁 Project Structure

```
📦 MLflow/
├── 📄 MLproject                 # MLflow project definition
├── 📄 conda.yaml              # Conda environment specification
├── 📄 requirements.txt        # Python dependencies
├── 📄 README.md               # This documentation
├── 📄 Makefile                # Build automation
├── 🔧 setup_mlflow.sh         # Environment setup script
├── 🔧 activate_env.sh          # Environment activation script
├── 🔧 deploy_aws.sh           # AWS deployment script
├── 🔧 test_setup.py           # Setup verification script
├── 🐍 preprocessing.py        # Data preprocessing pipeline
├── 🐍 train.py                # Model training pipeline
├── 🐍 evaluate.py             # Model evaluation pipeline
├── 🐍 inference.py            # Inference and prediction script
├── 🐍 serve_api.py            # FastAPI REST API server
├── 📁 Dataset/
│   └── 📊 Fish.csv            # Raw fish dataset
├── 📁 scikit-learn/           # Legacy scikit-learn scripts
│   ├── 🐍 fish_analysis.py
│   ├── 🐍 fish_predictive_model.py
│   ├── 🐍 fish_regression.py
│   └── 📄 requirements.txt
├── 📁 models/                 # Trained model artifacts
├── 📁 plots/                  # EDA visualizations
├── 📁 evaluation_plots/       # Model evaluation plots
├── 📁 detailed_evaluation/    # Comprehensive evaluation
├── 📁 processed_data/         # Processed datasets
├── 📁 sagemaker_deployment/   # SageMaker deployment files
├── 📁 mlruns/                 # MLflow tracking data
└── 📁 logs/                   # Application logs
```

## Advanced features

### Bootstrap confidence intervals

The pipeline includes bootstrap-based confidence interval estimation:

```python
# Confidence interval calculation
predictions = []
for _ in range(100):
    noise = np.random.normal(0, 0.05, X.shape)
    X_noisy = X + noise
    pred = model.predict(X_noisy)
    predictions.append(pred)

lower_ci = np.percentile(predictions, 2.5)
upper_ci = np.percentile(predictions, 97.5)
```

### Cross-Validation

All models use 5-fold cross-validation for robust performance estimation:

```python
cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
cv_rmse = np.sqrt(-cv_scores.mean())
```

### Interactive visualizations

Plotly-based interactive dashboards are generated:

- Scatter matrix plots
- 3D surface plots
- Interactive correlation heatmaps
- Dynamic filtering and zooming

### Model comparison

Automatic comparison across multiple algorithms:

- Linear Regression
- Ridge Regression (L2 regularization)
- Lasso Regression (L1 regularization)
- Elastic Net (L1 + L2 regularization)
- Random Forest (ensemble method)


### Development setup
```bash
# Fork the repository
git clone <your-fork>
cd MLflow

# Setup development environment
./setup_mlflow.sh
source activate_env.sh

# Install development dependencies
pip install pytest pytest-cov black flake8

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

**🐟 Fish Weight Predicting 🐟**
Bream,290.0,24.0,26.3,31.2,12.48,4.3056
Pike,270.0,16.2,18.0,22.2,8.544,4.1472
...
```

**Features (Variables):**
- `Length1`: Body length (cm)
- `Length2`: Diagonal length (cm) 
- `Length3`: Cross length (cm)
- `Height`: Body height (cm)
- `Width`: Diagonal width (cm)
- `Species`: Fish species (categorical)

**Target (Dependent variable)**
- `Weight`: Fish weight in grams (continuous)

### Supervised Learning

#### 1. **Problem Type**: Regression
- **Goal**: Predict continuous weight values
- **Algorithm**: Random Forest Regressor, Linear Regression
- **Evaluation Metrics**: R², RMSE, MAE

#### 2. **Feature Engineering**
```python
# Categorical encoding for species
species_encoded = pd.get_dummies(df['Species'], prefix='Species')

# Feature scaling for numerical variables
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_numeric)

# Feature interactions
df['length_height_ratio'] = df['Length1'] / df['Height']
df['volume_estimate'] = df['Length1'] * df['Height'] * df['Width']
```

#### 3. **Model training pipeline**
```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model training
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Predictions and evaluation
y_pred = rf_model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
```

---

## 🛠️ Environment setup & requirements

### Virtual Environment

Create isolated Python environment for the project:

```bash
# Create virtual environment
python3 -m venv fish_prediction_env

# Activate environment
source fish_prediction_env/bin/activate  # Linux/macOS
# fish_prediction_env\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip
```

#### **scikit-learn/requirements.txt**
```txt
# Machine Learning Core
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.17.0

# Model Evaluation
scikit-plot>=0.3.7
yellowbrick>=1.5.0

# Model Persistence
joblib>=1.3.0

# Hyperparameter Tuning
optuna>=3.4.0
scikit-optimize>=0.9.0

# Development
jupyter>=1.0.0
ipykernel>=6.25.0
```

### Installation commands

```bash
# Install main requirements
pip install -r requirements.txt


# Install scikit-learn specific requirements
pip install -r scikit-learn/requirements.txt

# Verify installation
python -c "import sklearn, pandas; print('All packages installed successfully!')"
```

## FastAPI model deployment

Deploy the trained model as a RESTful API for real-time predictions.

### RESTful API

```python
# fish_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from typing import List, Optional

app = FastAPI(title="Fish Weight Prediction API", version="1.0.0")

# Load trained model at startup
model = joblib.load('models/fish_weight_predictor.pkl')
scaler = joblib.load('models/feature_scaler.pkl')

class FishMeasurement(BaseModel):
    species: str
    length1: float
    length2: float
    length3: float
    height: float
    width: float

class PredictionResponse(BaseModel):
    predicted_weight: float
    confidence_score: Optional[float] = None
    model_version: str = "1.0.0"

@app.post("/predict", response_model=PredictionResponse)
async def predict_fish_weight(measurement: FishMeasurement):
    try:
        # Prepare features
        features = np.array([[
            measurement.length1, measurement.length2, measurement.length3,
            measurement.height, measurement.width
        ]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        
        return PredictionResponse(
            predicted_weight=round(prediction, 2),
            confidence_score=0.95  # Calculate based on model uncertainty
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}
```

### Docker deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "fish_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  fish-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    environment:
      - MODEL_PATH=/app/models/fish_weight_predictor.pkl
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: fish_predictions
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## Troubleshooting

### Issues

#### 1. MLflow installation issues
```bash
# Reinstall MLflow with all dependencies
pip uninstall mlflow
pip install mlflow[pipelines] --upgrade
```

#### 2. Dataset Not Found
```bash
# Verify dataset location
ls -la Dataset/Fish.csv

# Download dataset
wget https://huggingface.co/datasets/scikit-learn/Fish/raw/main/Fish.csv -O Dataset/Fish.csv
```

#### 3. Port Already in Use
```bash
# Check running processes
lsof -i :8000  # for API server
lsof -i :5000  # for MLflow UI

# Kill processes if needed
kill -9 <PID>
```

#### 4. AWS deployment issues
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check IAM permissions
aws iam list-attached-role-policies --role-name FishWeightSageMakerRole
```

#### 5. Model loading issues
```bash
# Verify model file exists
ls -la models/best_fish_weight_model.pkl

# Retrain if needed
python train.py
```

#### 6. Network configuration for ML pipeline

**🔧 When you need iptables/nginx:**

| Scenario | iptables | nginx | Why |
|----------|----------|-------|-----|
| **Local Development** | ❌ No | ❌ No | localhost only |
| **Team Sharing** | ⚠️ Maybe | ⚠️ Maybe | Network access |
| **Production** | ✅ Yes | ✅ Yes | Security & SSL |
| **Load Balancing** | ⚠️ Maybe | ✅ Yes | Multiple instances |

**For LOCAL DEVELOPMENT (current setup):**
-  No iptables configuration needed
-  No nginx configuration needed  
-  Services bind to localhost (127.0.0.1) by default
-  Only accessible from your local machine
-  Access via: `http://localhost:8000` (API), `http://localhost:5000` (MLflow UI)

**For team sharing (if needed):**
```bash
# Modify serve_api.py to bind to all interfaces:
uvicorn.run("serve_api:app", host="0.0.0.0", port=8000)

# Start MLflow UI for external access:
mlflow ui --host 0.0.0.0 --port 5000

# Add firewall rules (Ubuntu/Debian):
sudo ufw allow 8000/tcp
sudo ufw allow 5000/tcp

# Access via: http://YOUR_IP:8000 (API), http://YOUR_IP:5000 (MLflow UI)
```

**For production deployment:**
```bash
# nginx reverse proxy configuration
# /etc/nginx/sites-available/mlflow-api
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /mlflow/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site:
sudo ln -s /etc/nginx/sites-available/mlflow-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# iptables rules for production:
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # SSH
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # HTTP
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS
sudo iptables -A INPUT -j DROP                       # Drop all other

# Save rules:
sudo iptables-save > /etc/iptables/rules.v4
```

**Network configuration check:**
```bash
# Run network analysis script
./check_network_config.sh

# Check what's listening on ports
netstat -tuln | grep -E ":5000|:8000"

# Test local access
curl http://localhost:8000/
```

### Environment Issues

#### Virtual Environment Problems
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Permission issues
```bash
# Make scripts executable
chmod +x setup_mlflow.sh
chmod +x activate_env.sh
chmod +x deploy_aws.sh
```
### Performance

#### Memory issues
```bash
# Monitor memory usage
htop

# Reduce batch size for predictions
# Limit plot generation for large datasets
```

#### Speed
```bash
# Use specific model instead of comparing all
python train.py --model_type linear_regression

# Reduce cross-validation folds
# Limit bootstrap iterations for confidence intervals
```

## Resources

### MLflow Documentation
- [MLflow Official Documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow Tutorials](https://mlflow.org/docs/latest/tutorials-and-examples/index.html)
- [MLflow Pipelines Guide](https://mlflow.org/docs/latest/pipelines.html)

### AWS SageMaker Resources
- [SageMaker MLflow Integration](https://docs.aws.amazon.com/sagemaker/latest/dg/mlflow.html)
- [Deploy MLflow to SageMaker](https://mlflow.org/docs/latest/ml/deployment/deploy-model-to-sagemaker/)
- [SageMaker Pipelines with MLflow](https://sagemaker-examples.readthedocs.io/en/latest/sagemaker-mlflow/sagemaker_pipelines_mlflow.html)

### Machine Learning Resources
- [Scikit-learn Documentation](https://scikit-learn.org/stable/)
- [Linear Regression Theory](https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares)
- [Model Evaluation Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)

---
