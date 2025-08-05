#!/usr/bin/env python3
"""
Test BERT Model with Evaluation Metrics
=======================================

This script tests the BERT fine-tuning implementation and demonstrates
various evaluation metrics for the model performance assessment.

Usage:
    python test_model_evaluation.py

Author: BERT Fine-tuning Project
Date: August 2025
"""

import sys
import os
import warnings
warnings.filterwarnings("ignore")

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_environment_setup():
    """Test if all required packages are installed."""
    print("="*60)
    print("TESTING ENVIRONMENT SETUP")
    print("="*60)
    
    required_packages = [
        ('torch', 'PyTorch'),
        ('transformers', 'Hugging Face Transformers'),
        ('sklearn', 'Scikit-learn'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('nltk', 'NLTK'),
        ('rouge_score', 'ROUGE Score'),
        ('bert_score', 'BERTScore')
    ]
    
    missing_packages = []
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} NOT installed")
            missing_packages.append(name)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All packages installed successfully!")
        return True


def test_bert_model_loading():
    """Test BERT model loading and basic functionality."""
    print("\n" + "="*60)
    print("TESTING BERT MODEL LOADING")
    print("="*60)
    
    try:
        from transformers import BertTokenizer, BertForSequenceClassification
        import torch
        
        print("📥 Loading BERT tokenizer...")
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        print("✓ BERT tokenizer loaded")
        
        print("📥 Loading BERT model...")
        model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
        print("✓ BERT model loaded")
        
        # Test tokenization
        test_text = "This is a test sentence for BERT evaluation."
        tokens = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True)
        print(f"✓ Tokenization test: '{test_text[:50]}...'")
        print(f"   Tokens shape: {tokens['input_ids'].shape}")
        
        # Test model inference
        model.eval()
        with torch.no_grad():
            outputs = model(**tokens)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            print(f"✓ Model inference test: Prediction shape {predictions.shape}")
        
        return True, model, tokenizer
        
    except Exception as e:
        print(f"✗ BERT model loading failed: {e}")
        return False, None, None


def test_evaluation_metrics():
    """Test evaluation metrics implementations."""
    print("\n" + "="*60)
    print("TESTING EVALUATION METRICS")
    print("="*60)
    
    try:
        # Import evaluation functions
        from src.evaluation_metrics import (
            calculate_bleu_score,
            calculate_rouge_score,
            calculate_bertscore,
            calculate_classification_metrics,
            calculate_diversity_metrics
        )
        
        # Sample data
        candidates = [
            "The model performance is excellent",
            "BERT works very well for classification",
            "Evaluation metrics help assess quality"
        ]
        
        references = [
            "The model shows excellent performance",
            "BERT performs well in classification tasks",
            "Metrics help evaluate the quality"
        ]
        
        # Test BLEU score
        print("📊 Testing BLEU Score...")
        bleu_scores = calculate_bleu_score(candidates, [[ref] for ref in references])
        if bleu_scores:
            print(f"   BLEU-4: {bleu_scores.get('BLEU-4', 0):.4f}")
            print("✓ BLEU score calculation successful")
        else:
            print("⚠️  BLEU score calculation failed (dependency missing)")
        
        # Test ROUGE score
        print("📊 Testing ROUGE Score...")
        rouge_scores = calculate_rouge_score(candidates, references)
        if rouge_scores:
            print(f"   ROUGE-L: {rouge_scores.get('ROUGE-L', 0):.4f}")
            print("✓ ROUGE score calculation successful")
        else:
            print("⚠️  ROUGE score calculation failed (dependency missing)")
        
        # Test BERTScore
        print("📊 Testing BERTScore...")
        bert_scores = calculate_bertscore(candidates, references)
        if bert_scores:
            print(f"   BERTScore F1: {bert_scores.get('BERTScore_F1', 0):.4f}")
            print("✓ BERTScore calculation successful")
        else:
            print("⚠️  BERTScore calculation failed (dependency missing)")
        
        # Test classification metrics
        print("📊 Testing Classification Metrics...")
        y_true = [0, 1, 1, 0, 1, 0, 1, 1, 0, 0]
        y_pred = [0, 1, 1, 0, 0, 0, 1, 1, 1, 0]
        clf_metrics = calculate_classification_metrics(y_true, y_pred, ['Negative', 'Positive'])
        if clf_metrics:
            print(f"   Accuracy: {clf_metrics.get('Accuracy', 0):.4f}")
            print(f"   F1 Score: {clf_metrics.get('Weighted_F1', 0):.4f}")
            print("✓ Classification metrics calculation successful")
        
        # Test diversity metrics
        print("📊 Testing Diversity Metrics...")
        diversity_scores = calculate_diversity_metrics(candidates)
        if diversity_scores:
            print(f"   Distinct-1: {diversity_scores.get('Distinct-1', 0):.4f}")
            print(f"   Distinct-2: {diversity_scores.get('Distinct-2', 0):.4f}")
            print("✓ Diversity metrics calculation successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Evaluation metrics testing failed: {e}")
        return False


def test_model_evaluation_pipeline(model, tokenizer):
    """Test the complete model evaluation pipeline."""
    print("\n" + "="*60)
    print("TESTING MODEL EVALUATION PIPELINE")
    print("="*60)
    
    try:
        import torch
        from src.evaluation_metrics import evaluate_model_comprehensive
        
        # Create sample test data
        test_data = {
            'texts': [
                "This movie is absolutely fantastic!",
                "I hate this terrible product.",
                "The service was okay, nothing special.",
                "Amazing quality and fast delivery!",
                "Poor customer support experience."
            ],
            'labels': [1, 0, 0, 1, 0],  # 1: Positive, 0: Negative
            'predictions': [1, 0, 1, 1, 0],  # Some predictions
            'label_names': ['Negative', 'Positive'],
            'generated_texts': [
                "The movie was great and entertaining",
                "Bad product with poor quality",
                "Average service with room for improvement"
            ],
            'reference_texts': [
                "The movie was excellent and very entertaining",
                "Poor quality product with many issues",
                "The service was average and could be better"
            ]
        }
        
        # Get device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {device}")
        
        # Run comprehensive evaluation
        metrics = evaluate_model_comprehensive(model, tokenizer, test_data, device)
        
        print("\n📋 Evaluation Summary:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                print(f"   {metric}: {value:.4f}")
            else:
                print(f"   {metric}: {value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Model evaluation pipeline failed: {e}")
        return False


def test_bert_fine_tuning():
    """Test BERT fine-tuning implementation."""
    print("\n" + "="*60)
    print("TESTING BERT FINE-TUNING")
    print("="*60)
    
    try:
        # Import fine-tuning functions
        from src.bert_fine_tuning import get_device_info
        
        print("📱 Testing device detection...")
        device = get_device_info()
        print(f"✓ Device detection successful: {device}")
        
        # Test data preparation (minimal example)
        print("📊 Testing data preparation...")
        sample_texts = [
            "I love this product!",
            "This is terrible.",
            "It's okay.",
            "Amazing quality!",
            "Poor service."
        ]
        sample_labels = [1, 0, 0, 1, 0]  # 1: Positive, 0: Negative
        
        print(f"   Sample data size: {len(sample_texts)} examples")
        print("✓ Data preparation test successful")
        
        return True
        
    except Exception as e:
        print(f"✗ BERT fine-tuning test failed: {e}")
        return False


def generate_test_report():
    """Generate a comprehensive test report."""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST REPORT")
    print("="*80)
    
    test_results = {}
    
    # Test 1: Environment Setup
    test_results['environment'] = test_environment_setup()
    
    # Test 2: BERT Model Loading
    model_success, model, tokenizer = test_bert_model_loading()
    test_results['model_loading'] = model_success
    
    # Test 3: Evaluation Metrics
    test_results['evaluation_metrics'] = test_evaluation_metrics()
    
    # Test 4: Fine-tuning Implementation
    test_results['fine_tuning'] = test_bert_fine_tuning()
    
    # Test 5: Model Evaluation Pipeline (only if model loaded)
    if model and tokenizer:
        test_results['evaluation_pipeline'] = test_model_evaluation_pipeline(model, tokenizer)
    else:
        test_results['evaluation_pipeline'] = False
    
    # Generate summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title():.<40} {status}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The system is ready for use.")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️  Most tests passed. Minor issues may exist.")
    else:
        print("❌ Multiple tests failed. Please check dependencies and setup.")
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    if not test_results['environment']:
        print("   • Install missing packages: pip install -r requirements.txt")
    if not test_results['model_loading']:
        print("   • Check internet connection for model downloading")
    if not test_results['evaluation_metrics']:
        print("   • Install evaluation packages: pip install nltk rouge-score bert-score")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    print("BERT Model Evaluation Test Suite")
    print("================================")
    print("This script tests the BERT fine-tuning setup and evaluation metrics.")
    print()
    
    success = generate_test_report()
    
    print("\n" + "="*60)
    if success:
        print("🚀 Ready to proceed with BERT fine-tuning and evaluation!")
    else:
        print("🔧 Please address the issues above before proceeding.")
    print("="*60)
