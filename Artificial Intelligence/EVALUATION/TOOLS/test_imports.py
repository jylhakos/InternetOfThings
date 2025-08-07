#!/usr/bin/env python3
"""
Import Test Script
Tests all critical imports for BERT fine-tuning and evaluation
"""

def test_critical_imports():
    """Test all imports required for BERT fine-tuning and evaluation"""
    
    print("🧪 TESTING CRITICAL IMPORTS")
    print("="*50)
    
    # Test 1: PyTorch
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name()}")
    except ImportError as e:
        print(f"❌ PyTorch: {e}")
        return False
    
    # Test 2: Transformers
    try:
        from transformers import BertForSequenceClassification, BertTokenizer, get_scheduler
        import transformers
        print(f"✅ Transformers: {transformers.__version__}")
    except ImportError as e:
        print(f"❌ Transformers: {e}")
        return False
    
    # Test 3: AdamW optimizer (fixed import)
    try:
        from torch.optim import AdamW
        print("✅ AdamW optimizer: Available from torch.optim")
    except ImportError as e:
        print(f"❌ AdamW: {e}")
        return False
    
    # Test 4: Scikit-learn
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report
        import sklearn
        print(f"✅ Scikit-learn: {sklearn.__version__}")
    except ImportError as e:
        print(f"❌ Scikit-learn: {e}")
        return False
    
    # Test 5: Evaluation tools
    try:
        from bert_score import BERTScorer
        print("✅ BERTScore: Available")
    except ImportError:
        print("⚠️  BERTScore: Not available (optional)")
    
    try:
        from rouge_score import rouge_scorer
        print("✅ ROUGE: Available")
    except ImportError:
        print("⚠️  ROUGE: Not available (optional)")
    
    try:
        import sacrebleu
        print("✅ BLEU: Available")
    except ImportError:
        print("⚠️  BLEU: Not available (optional)")
    
    # Test 6: Basic functionality
    try:
        # Test tokenizer loading
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        test_text = "This is a test"
        tokens = tokenizer(test_text, return_tensors="pt")
        print(f"✅ BERT tokenizer: Working (tokens shape: {tokens['input_ids'].shape})")
        
        # Test optimizer creation
        model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
        optimizer = AdamW(model.parameters(), lr=2e-5)
        print("✅ Model and optimizer: Created successfully")
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False
    
    print("\n🎉 All critical imports working!")
    return True

def test_environment_setup():
    """Test environment configuration"""
    print(f"\n🔧 ENVIRONMENT CONFIGURATION")
    print("-"*30)
    
    import sys
    print(f"Python version: {sys.version}")
    
    try:
        import psutil
        ram = psutil.virtual_memory()
        print(f"Available RAM: {ram.available / (1024**3):.1f} GB")
        print(f"CPU cores: {psutil.cpu_count()}")
    except ImportError:
        print("⚠️  psutil not available for system info")
    
    print("Virtual environment:", 'bert_env' in sys.prefix)

if __name__ == "__main__":
    try:
        # Test environment
        test_environment_setup()
        
        # Test imports
        success = test_critical_imports()
        
        if success:
            print("\n✅ Ready to run BERT fine-tuning!")
            print("   Next: python src/bert_fine_tuning.py")
        else:
            print("\n❌ Some imports failed. Check installation.")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
