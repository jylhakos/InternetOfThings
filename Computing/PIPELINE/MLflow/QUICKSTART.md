# Quick Start - Fish Weight prediction MLflow pipeline

Here's steps how to start MLflow pipeline for 🐟 fish weight prediction.

### Step 1: Setup environment (One-time)

```bash
# Navigate to the project directory
cd PIPELINE/MLflow

# Run the setup script
./setup_mlflow.sh

# Activate the environment
source activate_env.sh
```

### Step 2: Run the demo

```bash
# Run the comprehensive demo (recommended first run)
python demo_pipeline.py
```

### Step 3: Pipeline execution

```bash
# Option 1: Use Make (recommended)
make pipeline

# Option 2: Use MLflow
mlflow run .

# Option 3: Step by step
make preprocess
make train
make evaluate
```

### Step 4: Start services

```bash
# Start MLflow UI (tracks experiments)
make ui
# Access at: http://localhost:5000

# Start REST API (in new terminal)
make serve
# Access at: http://localhost:8000
# API docs: http://localhost:8000/docs
```

## 🐋 Docker start

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.mlflow.yml up

# Or run training first
docker-compose -f docker-compose.mlflow.yml --profile training up

# API will be available at: http://localhost:8000
# MLflow UI at: http://localhost:5000
```

## Test the API

```bash
# Health check
curl http://localhost:8000/

# Make a prediction
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

## ☁️ Deploy to Amazon AWS

```bash
# Setup AWS credentials first
aws configure

# Deploy to SageMaker
./deploy_aws.sh
```

### Files
- `MLproject` - MLflow project definition
- `conda.yaml` - Environment specification
- `preprocessing.py` - Data cleaning and feature engineering
- `train.py` - Model training with comparison
- `evaluate.py` - Comprehensive model evaluation
- `inference.py` - Local predictions with confidence intervals
- `serve_api.py` - FastAPI REST API server
- `deploy_aws.sh` - AWS SageMaker deployment
- `demo_pipeline.py` - Complete demonstration
- `Makefile` - Build automation
- `README.md` - Comprehensive documentation

### Features
- **Linear Regression** (primary) + 4 other algorithms
- **Feature Engineering**: 6 additional features created
- **Bootstrap Confidence Intervals**: Uncertainty quantification
- **Interactive Visualizations**: Plotly dashboards
- **cURL Examples**: Ready-to-use API commands
- **Docker Support**: Complete containerization
- **AWS Integration**: SageMaker deployment ready

## Expected results

With the Fish.csv dataset, you should see:
- **R² Score**: ~0.92 (92% variance explained)
- **RMSE**: ~45 grams
- **MAE**: ~32 grams
- **Training Time**: <5 seconds
- **API Response Time**: <1ms per prediction

## Help?

```bash
# Test the setup
python test_setup.py

# See all available commands
make help

# Check logs
ls logs/

# Read the complete documentation
cat README.md
```

---