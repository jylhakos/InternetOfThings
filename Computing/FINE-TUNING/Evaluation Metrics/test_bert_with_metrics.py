#!/usr/bin/env python3
"""
Test BERT Fine-tuning with Evaluation Metrics
=============================================

This script tests the BERT fine-tuning implementation and validates
it with comprehensive evaluation metrics.

Usage:
    python test_bert_with_metrics.py

Author: BERT Fine-tuning Project
Date: August 2025
"""

import os
import sys
import time
import warnings
warnings.filterwarnings("ignore")

def test_imports():
    """Test if all required imports work."""
    print("="*60)
    print("TESTING IMPORTS")
    print("="*60)
    
    required_modules = [
        ('torch', 'PyTorch'),
        ('transformers', 'Hugging Face Transformers'),
        ('sklearn', 'Scikit-learn'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas')
    ]
    
    success = True
    for module, name in required_modules:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name}: {e}")
            success = False
    
    return success

def test_bert_model():
    """Test BERT model loading and basic functionality."""
    print("\n" + "="*60)
    print("TESTING BERT MODEL")
    print("="*60)
    
    try:
        import torch
        from transformers import BertTokenizer, BertForSequenceClassification
        
        print("Loading BERT tokenizer...")
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        print("✓ Tokenizer loaded")
        
        print("Loading BERT model...")
        model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
        print("✓ Model loaded")
        
        # Test basic functionality
        test_text = "This is a positive sentiment example."
        inputs = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True)
        
        model.eval()
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        print(f"✓ Model inference successful")
        print(f"   Input: '{test_text}'")
        print(f"   Predictions: {predictions.numpy()}")
        
        return True, model, tokenizer
        
    except Exception as e:
        print(f"✗ BERT model test failed: {e}")
        return False, None, None

def test_evaluation_metrics():
    """Test evaluation metrics with sample data."""
    print("\n" + "="*60)
    print("TESTING EVALUATION METRICS")
    print("="*60)
    
    try:
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
        
        # Sample data for testing
        y_true = [0, 1, 1, 0, 1, 0, 1, 1, 0, 0]
        y_pred = [0, 1, 1, 0, 0, 0, 1, 1, 1, 0]
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')
        
        print(f"✓ Accuracy: {accuracy:.4f}")
        print(f"✓ Precision: {precision:.4f}")
        print(f"✓ Recall: {recall:.4f}")
        print(f"✓ F1 Score: {f1:.4f}")
        
        # Test classification report
        report = classification_report(y_true, y_pred, target_names=['Negative', 'Positive'])
        print("✓ Classification Report Generated")
        
        return True
        
    except Exception as e:
        print(f"✗ Evaluation metrics test failed: {e}")
        return False

def test_fine_tuning_setup():
    """Test fine-tuning setup without actually training."""
    print("\n" + "="*60)
    print("TESTING FINE-TUNING SETUP")
    print("="*60)
    
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
        from transformers import BertTokenizer, BertForSequenceClassification, AdamW
        
        # Load model and tokenizer
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
        
        # Sample training data
        texts = [
            "I love this product!",
            "This is terrible.",
            "Great quality and service.",
            "Poor performance, very disappointed."
        ]
        labels = [1, 0, 1, 0]  # 1: positive, 0: negative
        
        # Tokenize
        inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt", max_length=128)
        
        # Create dataset
        dataset = TensorDataset(inputs['input_ids'], inputs['attention_mask'], torch.tensor(labels))
        dataloader = DataLoader(dataset, batch_size=2, shuffle=True)
        
        # Setup optimizer
        optimizer = AdamW(model.parameters(), lr=2e-5)
        
        print(f"✓ Training data prepared: {len(texts)} samples")
        print(f"✓ DataLoader created: {len(dataloader)} batches")
        print(f"✓ Optimizer configured")
        
        # Test one forward pass
        model.train()
        batch = next(iter(dataloader))
        input_ids, attention_mask, batch_labels = batch
        
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=batch_labels)
        loss = outputs.loss
        
        print(f"✓ Forward pass successful, Loss: {loss.item():.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Fine-tuning setup failed: {e}")
        return False

def test_perplexity_calculation():
    """Test perplexity calculation."""
    print("\n" + "="*60)
    print("TESTING PERPLEXITY CALCULATION")
    print("="*60)
    
    try:
        import torch
        from transformers import GPT2LMHeadModel, GPT2Tokenizer
        
        # Use GPT2 for perplexity calculation
        model = GPT2LMHeadModel.from_pretrained('gpt2')
        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        
        # Add padding token
        tokenizer.pad_token = tokenizer.eos_token
        
        text = "The quick brown fox jumps over the lazy dog."
        encoded = tokenizer(text, return_tensors="pt")
        
        model.eval()
        with torch.no_grad():
            outputs = model(**encoded, labels=encoded["input_ids"])
            loss = outputs.loss
            perplexity = torch.exp(loss)
        
        print(f"✓ Perplexity calculation successful")
        print(f"   Text: '{text}'")
        print(f"   Perplexity: {perplexity.item():.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Perplexity calculation failed: {e}")
        return False

def generate_comprehensive_report():
    """Generate a comprehensive test report."""
    print("\n" + "="*80)
    print("BERT FINE-TUNING COMPREHENSIVE TEST REPORT")
    print("="*80)
    
    tests = [
        ("Import Test", test_imports),
        ("BERT Model Test", lambda: test_bert_model()[0]),
        ("Evaluation Metrics Test", test_evaluation_metrics),
        ("Fine-tuning Setup Test", test_fine_tuning_setup),
        ("Perplexity Calculation Test", test_perplexity_calculation)
    ]
    
    results = {}
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results[test_name] = False
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<35} {status}")
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print(f"Total Time: {total_time:.2f} seconds")
    
    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if passed == total:
        print("🎉 All tests passed! Your BERT fine-tuning environment is ready.")
        print("✓ You can proceed with fine-tuning")
        print("✓ All evaluation metrics are available")
        print("✓ Environment is properly configured")
    elif passed >= total * 0.8:
        print("⚠️  Most tests passed. Minor issues detected:")
        failed_tests = [name for name, result in results.items() if not result]
        for test in failed_tests:
            print(f"   • {test} needs attention")
    else:
        print("❌ Multiple tests failed. Please address the following:")
        print("   • Check dependency installation")
        print("   • Verify internet connection for model downloads")
        print("   • Ensure sufficient system resources")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Run BERT fine-tuning: python src/bert_fine_tuning.py")
    print("2. Test API server: python api.py")
    print("3. Run evaluation: python src/evaluation_metrics.py")
    print("4. Check documentation: README.md")
    
    return passed == total

if __name__ == "__main__":
    print("BERT Fine-tuning Environment Test")
    print("=================================")
    print("This script validates the complete BERT fine-tuning setup.")
    print()
    
    success = generate_comprehensive_report()
    
    if success:
        print("\n🚀 Environment validation successful!")
        print("You can now proceed with BERT fine-tuning and evaluation.")
    else:
        print("\n🔧 Please address the issues above before proceeding.")
    
    print("\nFor detailed information, see README.md")
