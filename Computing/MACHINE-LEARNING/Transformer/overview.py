#!/usr/bin/env python3
"""
Project Summary and Quick Start Guide
This script provides an overview of the RNN + Transformer Language Model project
and demonstrates key features without running full training.
"""

import torch
import os
import sys
from pathlib import Path

def print_banner():
    """Print project banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        RNN + TRANSFORMER LANGUAGE MODELS WITH PYTORCH         ║
    ║                                                               ║
    ║    🔥 Combining the best of Recurrent and Attention-based     ║
    ║       architectures for state-of-the-art language modeling   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_environment():
    """Check the environment setup."""
    print("\n🔍 ENVIRONMENT CHECK")
    print("=" * 50)
    
    # Python version
    python_version = sys.version.split()[0]
    print(f"✅ Python version: {python_version}")
    
    # PyTorch version
    print(f"✅ PyTorch version: {torch.__version__}")
    print(f"✅ CUDA available: {torch.cuda.is_available()}")
    
    # Device info
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"✅ Computing device: {device}")
    
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    return device

def demo_architectures():
    """Demonstrate the three model architectures."""
    print("\n🏗️  MODEL ARCHITECTURES")
    print("=" * 50)
    
    from model import create_model, count_parameters
    
    # Small vocabulary for demo
    vocab_size = 5000
    device = torch.device('cpu')  # Use CPU for quick demo
    
    models = {
        'RNN (LSTM)': {
            'type': 'rnn',
            'config': {'embed_size': 128, 'hidden_size': 256, 'num_layers': 2}
        },
        'Transformer': {
            'type': 'transformer', 
            'config': {'d_model': 256, 'nhead': 8, 'num_layers': 4}
        },
        'Hybrid RNN+Transformer': {
            'type': 'hybrid',
            'config': {
                'embed_size': 128, 'hidden_size': 128, 'd_model': 256,
                'nhead': 8, 'num_transformer_layers': 2, 'num_rnn_layers': 1
            }
        }
    }
    
    print(f"{'Model':<25} {'Parameters':<12} {'Description'}")
    print("-" * 70)
    
    for name, info in models.items():
        try:
            model = create_model(info['type'], vocab_size, **info['config'])
            params = count_parameters(model)
            
            descriptions = {
                'RNN (LSTM)': 'Sequential processing, memory efficient',
                'Transformer': 'Parallel processing, global attention',
                'Hybrid RNN+Transformer': 'Best of both worlds'
            }
            
            print(f"{name:<25} {params:>8,}   {descriptions[name]}")
            
        except Exception as e:
            print(f"{name:<25} {'Error':>12}   {str(e)[:30]}...")

def show_pipeline_overview():
    """Show the machine learning pipeline."""
    print("\n🔄 MACHINE LEARNING PIPELINE")
    print("=" * 50)
    
    pipeline_steps = [
        ("1. Data Loading", "WikiText-2 → Raw text articles"),
        ("2. Preprocessing", "Tokenization → Vocabulary building"),
        ("3. Dataset Creation", "Sequences → PyTorch DataLoader"),
        ("4. Model Training", "Forward pass → Loss → Backprop"),
        ("5. Evaluation", "Perplexity → Validation loss"),
        ("6. Text Generation", "Sampling strategies → Output text"),
        ("7. API Deployment", "Flask server → REST endpoints")
    ]
    
    for step, description in pipeline_steps:
        print(f"   {step:<20} {description}")

def show_key_features():
    """Show key features of the project."""
    print("\n⭐ KEY FEATURES")
    print("=" * 50)
    
    features = [
        "🧠 Three model architectures: RNN, Transformer, Hybrid",
        "📚 WikiText-2 dataset integration via Hugging Face",
        "🔧 Complete training pipeline with checkpoints",
        "🎯 Multiple text generation strategies (top-k, nucleus)",
        "🌐 REST API for model inference and comparison",
        "📊 Training visualization and model comparison",
        "🐳 Virtual environment with all dependencies",
        "🧪 Comprehensive testing and demo scripts"
    ]
    
    for feature in features:
        print(f"   {feature}")

def show_quick_start():
    """Show quick start commands."""
    print("\n🚀 QUICK START GUIDE")
    print("=" * 50)
    
    commands = [
        ("Setup Environment", "./run.sh  # Interactive setup script"),
        ("Run Demo", "python demo.py  # Model architecture demo"),
        ("Train Models", "python train.py  # Train all three models"),
        ("Generate Text", "python generate.py --demo  # Test generation"),
        ("Start API", "python api.py  # Launch REST API server"),
        ("Test API", "python test_api.py  # Test all endpoints"),
    ]
    
    print("Choose one of these commands to get started:")
    print()
    
    for i, (title, command) in enumerate(commands, 1):
        print(f"   {i}. {title}")
        print(f"      {command}")
        print()

def show_file_structure():
    """Show project file structure."""
    print("\n📁 PROJECT STRUCTURE")
    print("=" * 50)
    
    current_dir = Path(".")
    important_files = {
        'model.py': 'Core model architectures (RNN, Transformer, Hybrid)',
        'data_utils.py': 'Dataset loading and preprocessing utilities',
        'train.py': 'Training script for all model types',
        'generate.py': 'Text generation and inference script',
        'api.py': 'Flask REST API server',
        'demo.py': 'Interactive demonstration script',
        'test_api.py': 'API testing and validation',
        'run.sh': 'Interactive setup and run script',
        'README.md': 'Comprehensive documentation',
        'requirements.txt': 'Python package dependencies'
    }
    
    print("Key files and their purposes:")
    print()
    
    for filename, description in important_files.items():
        exists = "✅" if (current_dir / filename).exists() else "❌"
        print(f"   {exists} {filename:<15} {description}")

def show_learning_resources():
    """Show learning resources."""
    print("\n📖 LEARNING RESOURCES")
    print("=" * 50)
    
    resources = [
        ("Paper", '"Attention Is All You Need" - Original Transformer paper'),
        ("Tutorial", "PyTorch Data Loading - pytorch.org/tutorials/beginner/basics/data_tutorial.html"),
        ("Reference", "PyTorch RNN Docs - pytorch.org/docs/stable/generated/torch.nn.RNN.html"),
        ("Reference", "PyTorch Transformer - pytorch.org/docs/stable/generated/torch.nn.Transformer.html"),
        ("Example", "PyTorch Word Language Model - github.com/pytorch/examples/tree/main/word_language_model"),
        ("Dataset", "WikiText Dataset - huggingface.co/datasets/wikitext")
    ]
    
    for resource_type, description in resources:
        print(f"   [{resource_type}] {description}")

def main():
    """Main function."""
    print_banner()
    
    try:
        device = check_environment()
        demo_architectures()
        show_pipeline_overview()
        show_key_features()
        show_quick_start()
        show_file_structure()
        show_learning_resources()
        
        print("\n" + "=" * 70)
        print("🎉 PROJECT OVERVIEW COMPLETED!")
        print("=" * 70)
        print()
        print("Ready to start? Run one of these commands:")
        print("   ./run.sh           # Interactive guided setup")
        print("   python demo.py     # Quick architecture demo")
        print("   python train.py    # Full model training")
        print()
        print("For detailed instructions, see README.md")
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nThis likely means the virtual environment is not activated.")
        print("Please run: source .venv/bin/activate")
        print("Or use the setup script: ./run.sh")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
