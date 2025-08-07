#!/usr/bin/env python3
"""
Test script for BERT evaluation tools setup
Verifies that all evaluation tools are properly installed and working
"""

import sys
import traceback

def test_evaluation_tools():
    """Test all evaluation tools and their dependencies"""
    
    print("TESTING BERT EVALUATION TOOLS SETUP")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Basic imports
    print("\n1. Testing basic imports...")
    tests_total += 1
    try:
        import torch
        import transformers
        import numpy as np
        import pandas as pd
        from sklearn.metrics import accuracy_score
        print("   ✅ Basic imports successful")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Basic imports failed: {e}")
    
    # Test 2: BERTScore
    print("\n2. Testing BERTScore...")
    tests_total += 1
    try:
        from bert_score import BERTScorer
        scorer = BERTScorer(lang="en", rescale_with_baseline=True)
        
        # Simple test
        predictions = ["This is a positive sentiment"]
        references = ["This text has positive sentiment"]
        P, R, F1 = scorer.score(predictions, references)
        
        print(f"   ✅ BERTScore working - F1: {F1.item():.3f}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ BERTScore failed: {e}")
    
    # Test 3: ROUGE
    print("\n3. Testing ROUGE...")
    tests_total += 1
    try:
        from rouge_score import rouge_scorer
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        
        # Simple test
        pred = "This is a positive sentiment"
        ref = "This text has positive sentiment"
        scores = scorer.score(pred, ref)
        
        print(f"   ✅ ROUGE working - ROUGE-1 F1: {scores['rouge1'].fmeasure:.3f}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ ROUGE failed: {e}")
    
    # Test 4: BLEU
    print("\n4. Testing BLEU...")
    tests_total += 1
    try:
        import sacrebleu
        
        # Simple test
        predictions = ["This is a positive sentiment"]
        references = [["This text has positive sentiment"]]
        bleu = sacrebleu.corpus_bleu(predictions, references)
        
        print(f"   ✅ BLEU working - Score: {bleu.score:.3f}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ BLEU failed: {e}")
    
    # Test 5: Matplotlib/Seaborn for visualization
    print("\n5. Testing visualization libraries...")
    tests_total += 1
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Simple test plot
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(['Test'], [1])
        plt.close(fig)  # Don't display
        
        print("   ✅ Matplotlib/Seaborn working")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Visualization libraries failed: {e}")
    
    # Test 6: BERT model loading
    print("\n6. Testing BERT model loading...")
    tests_total += 1
    try:
        from transformers import BertTokenizer, BertForSequenceClassification
        
        # Load a small model for testing
        model_name = 'bert-base-uncased'
        tokenizer = BertTokenizer.from_pretrained(model_name)
        
        # Test tokenization
        text = "This is a test"
        tokens = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        
        print(f"   ✅ BERT tokenizer working - Tokens: {tokens['input_ids'].shape}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ BERT model loading failed: {e}")
    
    # Test 7: DeepEval (optional)
    print("\n7. Testing DeepEval (optional)...")
    tests_total += 1
    try:
        import deepeval
        print("   ✅ DeepEval available")
        tests_passed += 1
    except ImportError:
        print("   ⚠️  DeepEval not installed (optional)")
        # Don't count as failure since it's optional
        tests_total -= 1
    except Exception as e:
        print(f"   ❌ DeepEval error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print(f"Success rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("Tests passed: Evaluation setup is ready.")
        print("\nNext steps:")
        print("1. Run BERT fine-tuning: python src/bert_fine_tuning.py")
        print("2. Run evaluation: python src/bert_evaluation.py")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed. Check installation.")
        print("\nTo fix issues:")
        print("1. Run: ./setup_evaluation.sh")
        print("2. Or manually install missing packages")
        return False

def test_hardware():
    """Test hardware configuration"""
    print("\n🔧 HARDWARE CONFIGURATION")
    print("-"*40)
    
    import torch
    
    # CPU info
    import psutil
    cpu_count = psutil.cpu_count(logical=True)
    ram = psutil.virtual_memory()
    print(f"CPU cores: {cpu_count}")
    print(f"RAM: {ram.total / (1024**3):.1f} GB (Available: {ram.available / (1024**3):.1f} GB)")
    
    # GPU info
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        current_gpu = torch.cuda.current_device()
        gpu_name = torch.cuda.get_device_name(current_gpu)
        gpu_memory = torch.cuda.get_device_properties(current_gpu).total_memory / (1024**3)
        
        print(f"GPU: {gpu_name}")
        print(f"GPU Memory: {gpu_memory:.1f} GB")
        print(f"GPU Count: {gpu_count}")
        print("CUDA available - GPU acceleration enabled")
    else:
        print("💻 No GPU detected - using CPU only")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-"*25)
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        if gpu_memory >= 8:
            print("✅ GPU memory sufficient for BERT fine-tuning")
            print("   Recommended batch size: 8-16")
        else:
            print("⚠️  Limited GPU memory detected")
            print("   Recommended batch size: 2-4")
    else:
        if ram.total / (1024**3) >= 8:
            print("✅ RAM sufficient for CPU-based training")
            print("   Recommended batch size: 2-4")
        else:
            print("⚠️  Limited RAM - consider using smaller models")

if __name__ == "__main__":
    try:
        # Test hardware first
        test_hardware()
        
        # Test evaluation tools
        success = test_evaluation_tools()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)
