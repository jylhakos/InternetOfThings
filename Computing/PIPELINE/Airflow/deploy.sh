#!/bin/bash

set -e

# Configuration
PROJECT_NAME="bert-fine-tuning"
AWS_REGION="us-east-1"
ENVIRONMENT="production"

echo "🚀 Starting BERT Fine-tuning Pipeline Deployment"
echo "Project: $PROJECT_NAME"
echo "Region: $AWS_REGION"
echo "Environment: $ENVIRONMENT"

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install Terraform first."
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup local environment
echo "🏠 Setting up local environment..."

# Create virtual environment
python3 -m venv bert_env
source bert_env/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-api.txt

# Install Airflow dependencies
pip install apache-airflow==2.7.2
pip install apache-airflow-providers-amazon
pip install apache-airflow-providers-docker

echo "✅ Local environment setup completed"

# Build Docker images
echo "🐳 Building Docker images..."

# Build BERT API image
docker build -t bert-classifier:latest .

echo "✅ Docker images built successfully"

# Deploy to AWS (optional)
read -p "🌐 Deploy to AWS? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "☁️ Deploying to AWS..."
    
    # Initialize Terraform
    cd terraform
    terraform init
    
    # Plan deployment
    terraform plan \
        -var="aws_region=$AWS_REGION" \
        -var="project_name=$PROJECT_NAME" \
        -var="environment=$ENVIRONMENT"
    
    # Apply deployment
    read -p "Continue with Terraform apply? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply \
            -var="aws_region=$AWS_REGION" \
            -var="project_name=$PROJECT_NAME" \
            -var="environment=$ENVIRONMENT" \
            -auto-approve
        
        echo "✅ AWS deployment completed"
        
        # Get outputs
        echo "📋 Deployment outputs:"
        terraform output
    else
        echo "⏸️ AWS deployment skipped"
    fi
    
    cd ..
fi

# Start local services
echo "🔧 Starting local services..."

# Start local Airflow
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting local Airflow..."
    
    # Set Airflow home
    export AIRFLOW_HOME=$(pwd)/airflow
    
    # Initialize Airflow database
    airflow db init
    
    # Create admin user
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin
    
    # Start Airflow services in background
    airflow webserver --port 8080 --daemon
    airflow scheduler --daemon
    
    echo "✅ Airflow started at http://localhost:8080"
fi

# Start Ollama (if available)
if command -v ollama &> /dev/null; then
    echo "🦙 Starting Ollama..."
    
    # Start Ollama service
    sudo systemctl start ollama
    
    # Pull base models
    ollama pull bert-base
    
    echo "✅ Ollama started"
fi

# Start Docker Compose services
echo "🐳 Starting Docker Compose services..."
docker-compose up -d

echo "✅ Docker services started"

# Health checks
echo "🏥 Performing health checks..."

# Check API health
sleep 10
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ BERT API is healthy"
else
    echo "⚠️ BERT API health check failed"
fi

# Check Airflow health
if curl -f http://localhost:8080/health &> /dev/null; then
    echo "✅ Airflow is healthy"
else
    echo "⚠️ Airflow health check failed"
fi

# Check Ollama health (if available)
if command -v ollama &> /dev/null; then
    if curl -f http://localhost:11434/api/tags &> /dev/null; then
        echo "✅ Ollama is healthy"
    else
        echo "⚠️ Ollama health check failed"
    fi
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "📍 Access points:"
echo "   - BERT API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Airflow UI: http://localhost:8080 (admin/admin)"
if command -v ollama &> /dev/null; then
    echo "   - Ollama API: http://localhost:11434"
fi
echo ""
echo "🔍 Next steps:"
echo "   1. Open Airflow UI and enable the bert_fine_tuning_pipeline DAG"
echo "   2. Upload your training data to the appropriate directory"
echo "   3. Monitor pipeline execution in the Airflow UI"
echo "   4. Test the API endpoints using the provided examples"
echo ""
echo "📚 For more information, see the README.md file"
