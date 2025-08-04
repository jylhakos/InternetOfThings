# Makefile for Fish Weight Prediction MLflow Pipeline

.PHONY: help setup preprocess train evaluate serve clean pipeline ui

# Default target
help:
	@echo "Fish Weight Prediction MLflow Pipeline"
	@echo "======================================"
	@echo ""
	@echo "Available targets:"
	@echo "  setup       - Setup environment and dependencies"
	@echo "  preprocess  - Run data preprocessing"
	@echo "  train       - Train machine learning models"
	@echo "  evaluate    - Evaluate trained models"
	@echo "  serve       - Start REST API server"
	@echo "  pipeline    - Run complete pipeline (preprocess + train + evaluate)"
	@echo "  clean       - Clean generated files"
	@echo "  ui          - Start MLflow UI"
	@echo "  test        - Test the setup"
	@echo "  aws-deploy  - Deploy to AWS SageMaker"

setup:
	@echo "Setting up environment..."
	bash setup_mlflow.sh

preprocess:
	@echo "Running data preprocessing..."
	python preprocessing.py

train:
	@echo "Training models..."
	python train.py

evaluate:
	@echo "Evaluating models..."
	python evaluate.py

serve:
	@echo "Starting REST API server..."
	python serve_api.py

pipeline: preprocess train evaluate
	@echo "Complete pipeline executed successfully!"

ui:
	@echo "Starting MLflow UI..."
	mlflow ui --host 0.0.0.0 --port 5000

test:
	@echo "Testing setup..."
	python test_setup.py

aws-deploy:
	@echo "Deploying to AWS SageMaker..."
	bash deploy_aws.sh

clean:
	@echo "Cleaning generated files..."
	rm -rf plots evaluation_plots detailed_evaluation processed_data models
	rm -rf mlruns sagemaker_deployment
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# MLflow pipeline commands
mlflow-run:
	mlflow run . --experiment-name fish_weight_prediction

mlflow-serve:
	mlflow models serve -m models:/fish_weight_predictor/latest -p 8001

# Development commands
dev-install:
	pip install -e .
	pip install pytest pytest-cov black flake8

dev-test:
	pytest tests/ -v

dev-format:
	black .

dev-lint:
	flake8 .
