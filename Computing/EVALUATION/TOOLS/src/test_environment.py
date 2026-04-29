#!/usr/bin/env python3
"""
BERT Fine-tuning Environment Test
Tests PyTorch, CUDA, and required packages
"""

import sys
import time

def test_imports():
    """Test all required imports"""
    print("TESTING ENVIRONMENT FOR BERT FINE-TUNING")
    print("="*60)
    
    try:
        import torch
        print(f"PyTorch: {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        from transformers import BertTokenizer, BertForSequenceClassification
        print("Transformers library imported successfully")
    except ImportError as e:
        print(f"❌ Transformers import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"NumPy: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        from sklearn.metrics import accuracy_score
        print("Scikit-learn imported successfully")
    except ImportError as e:
        print(f"❌ Scikit-learn import failed: {e}")
        return False
    
    return True

def test_cuda():
    """Test CUDA availability and setup"""
    print(f"\nCUDA AVAILABILITY CHECK")
    print("-"*40)
    
    import torch
    
    if torch.cuda.is_available():
        print(f"CUDA Available: YES")
        print(f"GPU Count: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"   GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
        
        # Test basic CUDA operations
        try:
            device = torch.device("cuda:0")
            test_tensor = torch.randn(100, 100).to(device)
            result = torch.mm(test_tensor, test_tensor.t())
            print(f"CUDA tensor operations working")
            return True, device
        except Exception as e:
            print(f"❌ CUDA operations failed: {e}")
            return False, torch.device("cpu")
    else:
        print(f"CUDA Available: NO (will use CPU)")
        return False, torch.device("cpu")

def test_model_loading():
    """Test BERT model loading"""
    print(f"\n🤖 TESTING BERT MODEL LOADING")
    print("-"*40)
    
    try:
        from transformers import BertTokenizer, BertForSequenceClassification
        
        model_name = "bert-base-uncased"
        print(f"Loading {model_name}...")
        
        # Load tokenizer
        tokenizer = BertTokenizer.from_pretrained(model_name)
        print("Tokenizer loaded successfully")
        
        # Load model
        model = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=2,
            output_attentions=False,
            output_hidden_states=False
        )
        print("BERT model loaded successfully")
        
        # Test tokenization
        test_text = "This is a test sentence for BERT tokenization."
        tokens = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True)
        print(f"Tokenization test passed (tokens: {tokens['input_ids'].shape[1]})")
        
        return True, model, tokenizer
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False, None, None

def main():
    """Main test function"""
    start_time = time.time()
    
    print("BERT FINE-TUNING ENVIRONMENT TEST")
    print("="*60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install required packages.")
        sys.exit(1)
    
    # Test CUDA
    cuda_available, device = test_cuda()
    
    # Test model loading
    model_ok, model, tokenizer = test_model_loading()
    
    if not model_ok:
        print("\n❌ Model loading failed.")
        sys.exit(1)
    
    # Summary
    elapsed = time.time() - start_time
    print(f"\nENVIRONMENT TEST COMPLETED!")
    print("="*60)
    print(f"Test duration: {elapsed:.2f} seconds")
    print(f"Device: {device}")
    print(f"CUDA: {'Available' if cuda_available else 'Not Available'}")
    print(f"BERT model: Ready")
    print(f"📦 All Dependencies: Installed")
    print("="*60)
    print("Your environment is ready for BERT fine-tuning!")
    
    return True

if __name__ == "__main__":
    main()
