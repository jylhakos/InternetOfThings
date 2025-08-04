#!/usr/bin/env python3

import sys
print("Python version:", sys.version)

try:
    import torch
    print("✓ PyTorch installed, version:", torch.__version__)
except ImportError as e:
    print("✗ PyTorch not installed:", e)

try:
    import transformers
    print("✓ Transformers installed, version:", transformers.__version__)
except ImportError as e:
    print("✗ Transformers not installed:", e)

try:
    import sklearn
    print("✓ Scikit-learn installed, version:", sklearn.__version__)
except ImportError as e:
    print("✗ Scikit-learn not installed:", e)

try:
    import numpy
    print("✓ NumPy installed, version:", numpy.__version__)
except ImportError as e:
    print("✗ NumPy not installed:", e)

try:
    import pandas
    print("✓ Pandas installed, version:", pandas.__version__)
except ImportError as e:
    print("✗ Pandas not installed:", e)

print("\nTesting BERT model loading...")
try:
    from transformers import BertTokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    print("✓ BERT tokenizer loaded successfully")
    
    # Test tokenization
    text = "Hello world"
    tokens = tokenizer.encode(text)
    print(f"✓ Tokenization test: '{text}' -> {tokens}")
    
except Exception as e:
    print("✗ BERT model loading failed:", e)

print("\nEnvironment setup verification completed!")
