#!/bin/bash

# BERT Model Evaluation Tools Setup Script
# This script sets up the evaluation environment with all necessary tools

echo "🚀 Setting up BERT Model Evaluation Tools"
echo "=========================================="

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "bert_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv bert_env
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source bert_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install basic requirements
echo "📥 Installing basic requirements..."
pip install -r requirements.txt

# Install evaluation-specific requirements
echo "🔍 Installing evaluation tools..."
pip install -r requirements-evaluation.txt

# Test installations
echo "🧪 Testing installations..."

echo "Testing PyTorch..."
python -c "import torch; print(f'PyTorch: {torch.__version__}')"

echo "Testing Transformers..."
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"

echo "Testing DeepEval..."
python -c "
try:
    import deepeval
    print('✅ DeepEval: Available')
except ImportError as e:
    print('⚠️  DeepEval: Not available -', str(e))
"

echo "Testing BERTScore..."
python -c "
try:
    from bert_score import BERTScorer
    print('✅ BERTScore: Available')
except ImportError as e:
    print('⚠️  BERTScore: Not available -', str(e))
"

echo "Testing ROUGE..."
python -c "
try:
    from rouge_score import rouge_scorer
    print('✅ ROUGE: Available')
except ImportError as e:
    print('⚠️  ROUGE: Not available -', str(e))
"

echo "Testing BLEU..."
python -c "
try:
    import sacrebleu
    print('✅ BLEU: Available')
except ImportError as e:
    print('⚠️  BLEU: Not available -', str(e))
"

echo "Testing HuggingFace Evaluate..."
python -c "
try:
    import evaluate
    print('✅ HF Evaluate: Available')
except ImportError as e:
    print('⚠️  HF Evaluate: Not available -', str(e))
"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Activate the environment: source bert_env/bin/activate"
echo "2. Run BERT fine-tuning: python src/bert_fine_tuning.py"
echo "3. Run evaluation: python src/bert_evaluation.py"
echo ""
echo "For detailed usage, see the README.md file."
