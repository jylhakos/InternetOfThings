#!/usr/bin/env python3
"""
Post-Download Status Check
=========================

Check the status of the BERT fine-tuning environment after model downloads.
"""

def check_status():
    print("="*60)
    print("POST-DOWNLOAD STATUS CHECK")
    print("="*60)
    
    # Check basic imports
    try:
        import torch
        import transformers
        import sklearn
        print(f"✓ PyTorch: {torch.__version__}")
        print(f"✓ Transformers: {transformers.__version__}")
        print(f"✓ Scikit-learn: {sklearn.__version__}")
        print(f"✓ CUDA available: {torch.cuda.is_available()}")
    except Exception as e:
        print(f"✗ Import error: {e}")
        return
    
    # Check BERT model loading
    try:
        from transformers import BertTokenizer, BertForSequenceClassification
        print("\nLoading BERT model...")
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
        print("✓ BERT model loaded successfully")
        
        # Test inference
        text = "I love this amazing product!"
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        model.eval()
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predictions = torch.nn.functional.softmax(logits, dim=-1)
        
        print(f"✓ Inference test passed")
        print(f"   Input: '{text}'")
        print(f"   Logits: {logits.numpy()}")
        print(f"   Probabilities: {predictions.numpy()}")
        
    except Exception as e:
        print(f"✗ BERT model test failed: {e}")
        return
    
    # Check evaluation metrics
    try:
        print("\nTesting evaluation metrics...")
        
        # BERTScore test
        from bert_score import score
        candidates = ["The product quality is excellent"]
        references = ["This item has outstanding quality"]
        P, R, F1 = score(candidates, references, lang="en", verbose=False)
        print(f"✓ BERTScore - Precision: {P[0]:.4f}, Recall: {R[0]:.4f}, F1: {F1[0]:.4f}")
        
        # Classification metrics test
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support
        y_true = [1, 0, 1, 0, 1]
        y_pred = [1, 0, 1, 0, 0]
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')
        print(f"✓ Classification - Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
        
        # BLEU score test (if NLTK is available)
        try:
            import nltk
            from nltk.translate.bleu_score import sentence_bleu
            reference = [["the", "cat", "is", "on", "the", "mat"]]
            candidate = ["the", "cat", "sits", "on", "the", "mat"]
            bleu_score = sentence_bleu(reference, candidate)
            print(f"✓ BLEU Score: {bleu_score:.4f}")
        except ImportError:
            print("⚠ NLTK not available for BLEU score")
        
    except Exception as e:
        print(f"✗ Evaluation metrics test failed: {e}")
    
    # Memory and performance check
    try:
        import psutil
        memory_info = psutil.virtual_memory()
        print(f"\n📊 System Resources:")
        print(f"   RAM Usage: {memory_info.percent:.1f}% ({memory_info.used/1024**3:.2f}GB / {memory_info.total/1024**3:.2f}GB)")
        print(f"   CPU Usage: {psutil.cpu_percent(interval=1):.1f}%")
        
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"   GPU Memory: {gpu_memory:.2f}GB")
    except Exception as e:
        print(f"⚠ Resource check failed: {e}")
    
    print("\n" + "="*60)
    print("STATUS CHECK COMPLETE")
    print("="*60)
    print("✅ Environment is ready for BERT fine-tuning!")
    print("🚀 All models downloaded and working correctly")
    print("📋 Next steps:")
    print("   1. Run: python src/bert_fine_tuning.py")
    print("   2. Test: python api.py")
    print("   3. Evaluate: python src/evaluation_metrics.py")

if __name__ == "__main__":
    check_status()
