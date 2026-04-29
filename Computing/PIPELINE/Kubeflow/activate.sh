#!/bin/bash

# Activation script for BERT Kubeflow pipeline

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE} BERT Kubeflow pipeline environment${NC}"
echo "=========================================="

# Activate virtual environment
if [ -d "bert-kubeflow-env" ]; then
    source bert-kubeflow-env/bin/activate
    echo -e "${GREEN}✅ Python virtual environment activated${NC}"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ Python virtual environment activated${NC}"
else
    echo "⚠️  Virtual environment not found. Run './scripts/setup.sh python' first"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo -e "${GREEN}✅ Environment variables loaded${NC}"
fi

echo ""
echo " Available Commands:"
echo "  Local Development:"
echo "    python src/bert_fine_tuning.py       # Run BERT fine-tuning"
echo "    python api.py                        # Start FastAPI server"
echo "    python test_model.py                 # Test model inference"
echo ""
echo "  Kubeflow Pipeline:"
echo "    python pipeline/bert_pipeline.py     # Compile Kubeflow pipeline"
echo ""
echo "  Docker Commands:"
echo "    docker build -t bert-serving .       # Build serving image"
echo "    docker run -p 8000:8000 bert-serving # Run serving container"
echo ""
echo "  AWS Deployment:"
echo "    ./scripts/deploy.sh                  # Full deployment"
echo "    ./scripts/deploy.sh build            # Build images only"
echo "    ./scripts/deploy.sh deploy           # Deploy to Kubernetes"
echo ""
echo "  Infrastructure:"
echo "    ./scripts/deploy-cloudformation.sh   # Deploy with CloudFormation"
echo "    cd terraform && terraform apply     # Deploy with Terraform"
echo ""
echo "  Setup & Configuration:"
echo "    ./scripts/setup.sh                  # Full environment setup"
echo "    sudo ./scripts/setup-iptables.sh    # Configure firewall"
echo ""
echo "🌐 Access Points (after deployment):"
echo "  Kubeflow UI: kubectl port-forward -n istio-system svc/istio-ingressgateway 8080:80"
echo "  BERT API: kubectl port-forward -n kubeflow svc/bert-serving-service 8000:80"
echo "  Local API: http://localhost:8000"
echo ""
