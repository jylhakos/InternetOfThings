#!/usr/bin/env python3
"""
Demo script showing integrated evaluation tools for BERT
Demonstrates how to use multiple evaluation metrics together
"""

import os
import json
import time
from typing import List, Dict

# Mock BERT model for demonstration (when real model isn't available)
class MockBERTModel:
    """Mock BERT model for demonstration purposes"""
    
    def __init__(self):
        self.labels = ["negative", "positive"]
    
    def predict(self, texts: List[str]) -> Dict:
        """Mock predictions with realistic confidence scores"""
        import random
        random.seed(42)  # For reproducible results
        
        predictions = []
        confidences = []
        
        for text in texts:
            # Simple heuristic for demo
            positive_words = ["love", "great", "excellent", "amazing", "fantastic", "good", "best"]
            negative_words = ["hate", "terrible", "awful", "worst", "bad", "horrible", "poor"]
            
            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                pred = 1  # positive
                conf = 0.7 + random.random() * 0.25
            elif neg_count > pos_count:
                pred = 0  # negative
                conf = 0.7 + random.random() * 0.25
            else:
                pred = random.choice([0, 1])
                conf = 0.5 + random.random() * 0.3
            
            predictions.append(pred)
            confidences.append(min(conf, 0.95))
        
        return {
            "predictions": predictions,
            "labels": [self.labels[p] for p in predictions],
            "confidences": confidences
        }

def demo_evaluation_tools():
    """Demonstrate the evaluation tools integration"""
    
    print("🚀 BERT EVALUATION TOOLS DEMO")
    print("="*50)
    
    # Sample test data
    test_data = {
        'texts': [
            "I absolutely love this product! It exceeded my expectations.",
            "This is the worst service I've ever experienced.",
            "The movie was fantastic, great acting and plot.",
            "Terrible quality, would not recommend to anyone.",
            "Amazing customer support, very helpful staff.",
            "Poor design and functionality, waste of money.",
            "It's okay, nothing special but not bad either.",
            "Excellent value for money, highly recommended!"
        ],
        'true_labels': [1, 0, 1, 0, 1, 0, 1, 1],  # 1 = positive, 0 = negative
        'references': [
            "positive sentiment expressed with enthusiasm",
            "negative sentiment about poor service quality", 
            "positive sentiment about entertainment content",
            "negative sentiment about product quality",
            "positive sentiment about customer service",
            "negative sentiment about product value",
            "neutral to positive sentiment",
            "positive sentiment about value"
        ]
    }
    
    # Initialize mock model (replace with real BERT model when available)
    print("📊 Initializing model...")
    model = MockBERTModel()
    
    # Get predictions
    print("🔍 Generating predictions...")
    results = model.predict(test_data['texts'])
    
    # Traditional metrics
    print("\n📈 Computing traditional metrics...")
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
    
    accuracy = accuracy_score(test_data['true_labels'], results['predictions'])
    precision, recall, f1, _ = precision_recall_fscore_support(
        test_data['true_labels'], results['predictions'], average='weighted'
    )
    
    traditional_metrics = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "avg_confidence": float(sum(results['confidences']) / len(results['confidences']))
    }
    
    print(f"   Accuracy: {traditional_metrics['accuracy']:.3f}")
    print(f"   F1-Score: {traditional_metrics['f1_score']:.3f}")
    print(f"   Avg Confidence: {traditional_metrics['avg_confidence']:.3f}")
    
    # BERTScore evaluation
    print("\n🎯 Computing BERTScore...")
    try:
        from bert_score import BERTScorer
        
        scorer = BERTScorer(lang="en", rescale_with_baseline=True)
        pred_texts = [f"{label} sentiment prediction" for label in results['labels']]
        
        P, R, F1 = scorer.score(pred_texts, test_data['references'])
        
        bertscore_metrics = {
            "precision": float(P.mean()),
            "recall": float(R.mean()), 
            "f1": float(F1.mean())
        }
        
        print(f"   BERTScore F1: {bertscore_metrics['f1']:.3f}")
        print(f"   BERTScore Precision: {bertscore_metrics['precision']:.3f}")
        print(f"   BERTScore Recall: {bertscore_metrics['recall']:.3f}")
        
    except Exception as e:
        print(f"   ⚠️  BERTScore error: {e}")
        bertscore_metrics = {}
    
    # ROUGE evaluation
    print("\n📝 Computing ROUGE scores...")
    try:
        from rouge_score import rouge_scorer
        
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        
        rouge_scores = []
        for pred_text, ref_text in zip(pred_texts, test_data['references']):
            scores = scorer.score(pred_text, ref_text)
            rouge_scores.append(scores)
        
        # Average ROUGE scores
        rouge1_f1 = sum(s['rouge1'].fmeasure for s in rouge_scores) / len(rouge_scores)
        rouge2_f1 = sum(s['rouge2'].fmeasure for s in rouge_scores) / len(rouge_scores)
        rougeL_f1 = sum(s['rougeL'].fmeasure for s in rouge_scores) / len(rouge_scores)
        
        rouge_metrics = {
            "rouge1_f1": float(rouge1_f1),
            "rouge2_f1": float(rouge2_f1),
            "rougeL_f1": float(rougeL_f1)
        }
        
        print(f"   ROUGE-1 F1: {rouge_metrics['rouge1_f1']:.3f}")
        print(f"   ROUGE-2 F1: {rouge_metrics['rouge2_f1']:.3f}")
        print(f"   ROUGE-L F1: {rouge_metrics['rougeL_f1']:.3f}")
        
    except Exception as e:
        print(f"   ⚠️  ROUGE error: {e}")
        rouge_metrics = {}
    
    # BLEU evaluation
    print("\n🎯 Computing BLEU scores...")
    try:
        import sacrebleu
        
        references_list = [[ref] for ref in test_data['references']]
        bleu = sacrebleu.corpus_bleu(pred_texts, references_list)
        
        bleu_metrics = {
            "bleu_score": float(bleu.score)
        }
        
        print(f"   BLEU Score: {bleu_metrics['bleu_score']:.3f}")
        
    except Exception as e:
        print(f"   ⚠️  BLEU error: {e}")
        bleu_metrics = {}
    
    # Compile results
    evaluation_results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_type": "Mock BERT (Demo)",
        "dataset_size": len(test_data['texts']),
        "traditional_metrics": traditional_metrics,
        "bertscore": bertscore_metrics,
        "rouge": rouge_metrics,
        "bleu": bleu_metrics,
        "sample_predictions": [
            {
                "text": text,
                "true_label": true_label,
                "predicted_label": pred_label,
                "confidence": conf
            }
            for text, true_label, pred_label, conf in zip(
                test_data['texts'][:3],  # Show first 3 samples
                test_data['true_labels'][:3],
                results['predictions'][:3],
                results['confidences'][:3]
            )
        ]
    }
    
    # Save results
    print(f"\n💾 Saving evaluation results...")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"demo_evaluation_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    
    print(f"   Results saved to: {filename}")
    
    # Summary
    print(f"\n" + "="*50)
    print("📊 EVALUATION SUMMARY")
    print("="*50)
    print(f"✅ Traditional Metrics: Computed")
    print(f"✅ BERTScore: {'Computed' if bertscore_metrics else 'Failed'}")
    print(f"✅ ROUGE: {'Computed' if rouge_metrics else 'Failed'}")
    print(f"✅ BLEU: {'Computed' if bleu_metrics else 'Failed'}")
    print(f"\n🎯 Key Results:")
    print(f"   Model Accuracy: {traditional_metrics['accuracy']:.1%}")
    if bertscore_metrics:
        print(f"   BERTScore F1: {bertscore_metrics['f1']:.3f}")
    if rouge_metrics:
        print(f"   ROUGE-1 F1: {rouge_metrics['rouge1_f1']:.3f}")
    if bleu_metrics:
        print(f"   BLEU Score: {bleu_metrics['bleu_score']:.3f}")
    
    print(f"\n🚀 Demo completed successfully!")
    print(f"📝 Results saved in: {filename}")
    
    return evaluation_results

def show_next_steps():
    """Show next steps for using the evaluation tools"""
    print(f"\n" + "="*50)
    print("🎯 NEXT STEPS")
    print("="*50)
    print("1. Train a real BERT model:")
    print("   python src/bert_fine_tuning.py")
    print("")
    print("2. Run comprehensive evaluation:")
    print("   python src/bert_evaluation.py")
    print("")
    print("3. Use G-Eval (requires OpenAI API key):")
    print("   export OPENAI_API_KEY='your-key'")
    print("   python src/geval_integration.py")
    print("")
    print("4. Install additional tools:")
    print("   pip install deepeval  # For DeepEval")
    print("   pip install wandb     # For experiment tracking")
    print("")
    print("📖 See README.md for detailed documentation")

if __name__ == "__main__":
    try:
        # Run the demo
        results = demo_evaluation_tools()
        
        # Show next steps
        show_next_steps()
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n💡 Try running: python src/test_evaluation_setup.py")
        print(f"   to diagnose setup issues.")
