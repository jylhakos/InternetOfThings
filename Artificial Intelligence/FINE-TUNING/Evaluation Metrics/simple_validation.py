#!/usr/bin/env python3
"""
Simple validation test for BERT fine-tuning environment
"""

def test_basic_setup():
    print("="*50)
    print("BASIC ENVIRONMENT VALIDATION")
    print("="*50)
    
    # Test PyTorch
    try:
        import torch
        print(f"✓ PyTorch: {torch.__version__}")
        print(f"✓ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✓ CUDA device: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"✗ PyTorch: {e}")
    
    # Test Transformers
    try:
        import transformers
        print(f"✓ Transformers: {transformers.__version__}")
    except ImportError as e:
        print(f"✗ Transformers: {e}")
    
    # Test BERT model loading
    try:
        from transformers import BertTokenizer, BertForSequenceClassification
        print("✓ BERT imports successful")
        
        # Test tokenizer
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        print("✓ BERT tokenizer loaded")
        
        # Test basic tokenization
        text = "This is a test."
        tokens = tokenizer(text, return_tensors="pt")
        print(f"✓ Tokenization: '{text}' -> shape {tokens['input_ids'].shape}")
        
    except Exception as e:
        print(f"✗ BERT loading: {e}")
    
    # Test evaluation libraries
    eval_libs = [
        ('sklearn', 'Scikit-learn'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('nltk', 'NLTK'),
        ('bert_score', 'BERTScore')
    ]
    
    print("\nEvaluation Libraries:")
    for lib, name in eval_libs:
        try:
            __import__(lib)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} (optional)")
    
    print("\n" + "="*50)
    print("VALIDATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    test_basic_setup()
