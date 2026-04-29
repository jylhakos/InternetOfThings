#!/bin/bash
# Activate the MLflow Fish Weight Prediction environment

echo "🐟 Activating Fish Weight Prediction MLflow Environment"
echo "======================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   ./setup_mlflow.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export MLFLOW_TRACKING_URI=./mlruns
export PYTHONPATH=${PYTHONPATH}:.

echo "✅ Environment activated!"
echo "📊 MLflow tracking URI: $MLFLOW_TRACKING_URI"
echo ""
echo "🚀 Available commands:"
echo "  make help                    # Show all available commands"
echo "  make pipeline                # Run complete pipeline"
echo "  make ui                      # Start MLflow UI (http://localhost:5000)"
echo "  make serve                   # Start REST API server (http://localhost:8000)"
echo "  python demo_pipeline.py      # Run comprehensive demo"
echo ""
echo "📋 Individual pipeline steps:"
echo "  make preprocess              # Data preprocessing"
echo "  make train                   # Model training"
echo "  make evaluate                # Model evaluation"
echo ""
echo "🧪 Testing and inference:"
echo "  python inference.py --samples           # Sample predictions"
echo "  python test_setup.py                    # Test setup"
echo ""
echo "☁️ Cloud deployment:"
echo "  make aws-deploy              # Deploy to AWS SageMaker"
echo ""
echo "🧹 Cleanup:"
echo "  make clean                   # Clean generated files"
echo "  deactivate                   # Deactivate environment"
echo ""
echo "📚 Documentation: See README.md for detailed instructions"
