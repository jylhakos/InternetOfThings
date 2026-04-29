# Quick Start - Dagster BERT Pipeline

## Prerequisites

Before running the pipeline, ensure you have the following setup:
- Python 3.8+ installed
- Virtual environment activated
- All dependencies installed

## 🔧 Installation

### 1. Setup Virtual Environment
```bash
# Create and activate virtual environment
python3 -m venv bert_dagster_env
source bert_dagster_env/bin/activate  # Linux/Mac
```

### 2. Install dependencies
```bash
# Install core dependencies
pip install --upgrade pip

# Install Dagster and related packages
pip install dagster dagster-webserver dagster-aws

# Install ML dependencies
pip install torch transformers scikit-learn pandas numpy

# Install API dependencies  
pip install fastapi uvicorn pydantic

# Install additional utilities
pip install boto3 requests pytest structlog
```

### 3. Environment
```bash
# Set environment variables
export DAGSTER_HOME=$(pwd)/dagster_home
export PYTHONPATH=$(pwd)

# Create Dagster home directory
mkdir -p dagster_home
```

## Running the Pipeline

### Option 1: Dagster development server
```bash
# Start Dagster development server
dagster dev -w workspace.yaml

# Open browser to http://localhost:3000
# Navigate to Assets tab
# Click "Materialize All" or materialize assets individually
```

### Option 2: Command line execution
```bash
# Materialize individual assets
dagster asset materialize --select training_dataset
dagster asset materialize --select trained_bert_model
dagster asset materialize --select model_evaluation
dagster asset materialize --select deployed_model
dagster asset materialize --select inference_tests

# Or run complete job
dagster job execute --job bert_pipeline_job
```

### Option 3: API testing
```bash
# Start API server (in separate terminal)
python api.py

# Test API endpoints
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!", "return_confidence": true}'

# Check API health
curl http://localhost:8000/health
```

## Pipeline stages

1. **training_dataset** - Generate dummy training data
2. **trained_bert_model** - Fine-tune BERT model
3. **model_evaluation** - Evaluate model performance
4. **deployed_model** - Deploy model for inference
5. **inference_tests** - Test deployed model

## Troubleshooting

### Issues

1. **Import Errors**
```bash
# Ensure Python path is set
export PYTHONPATH=$(pwd)

# Ensure virtual environment is activated
source bert_dagster_env/bin/activate
```

2. **Dagster Home Not Found**
```bash
# Set Dagster home
export DAGSTER_HOME=$(pwd)/dagster_home
mkdir -p dagster_home
```

3. **Port Already in Use**
```bash
# Kill existing processes
pkill -f dagster
pkill -f uvicorn

# Or use different ports
dagster dev -p 3001 -w workspace.yaml
```

4. **Memory Issues**
```bash
# Reduce batch size in bert_assets.py
# Use smaller model: "distilbert-base-uncased"
# Reduce dataset size in configuration
```

## 📁 Output Locations

- **Models**: `models/bert_fine_tuned/`
- **Data**: `data/training/`
- **Results**: `results/evaluation/`, `results/inference_tests/`
- **Logs**: `dagster_home/logs/`

## Monitoring

- **Dagster UI**: http://localhost:3000 - Pipeline monitoring
- **API Docs**: http://localhost:8000/docs - API documentation
- **Logs**: Check `dagster_home/logs/` for detailed logs

## ⚡ Next Steps

1. Customize model parameters in `bert_assets.py`
2. Add real training data in place of dummy data
3. Deploy to AWS using `./deploy_aws.sh`
4. Set up automated scheduling
5. Integrate with your existing ML infrastructure

## Success Indicators

 Dagster UI loads at http://localhost:3000

 Check logs in `dagster_home/logs/`
