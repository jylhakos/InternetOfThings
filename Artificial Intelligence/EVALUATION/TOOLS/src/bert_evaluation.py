#!/usr/bin/env python3
"""
BERT Model Evaluation with LLM Metrics
Comprehensive evaluation using DeepEval, BERTScore, BLEU, ROUGE, and other metrics
"""

import os
import json
import time
import torch
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from transformers import BertForSequenceClassification, BertTokenizer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# LLM Evaluation imports
try:
    from deepeval import evaluate
    from deepeval.metrics import (
        AnswerRelevancyMetric,
        FaithfulnessMetric,
        ContextualPrecisionMetric,
        ContextualRecallMetric,
        HallucinationMetric,
        BiasMetric
    )
    from deepeval.test_case import LLMTestCase
    DEEPEVAL_AVAILABLE = True
except ImportError:
    print("⚠️  DeepEval not available. Install with: pip install deepeval")
    DEEPEVAL_AVAILABLE = False

try:
    from bert_score import BERTScorer
    BERTSCORE_AVAILABLE = True
except ImportError:
    print("⚠️  BERTScore not available. Install with: pip install bert-score")
    BERTSCORE_AVAILABLE = False

try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    print("⚠️  ROUGE not available. Install with: pip install rouge-score")
    ROUGE_AVAILABLE = False

try:
    import sacrebleu
    BLEU_AVAILABLE = True
except ImportError:
    print("⚠️  BLEU not available. Install with: pip install sacrebleu")
    BLEU_AVAILABLE = False

try:
    import evaluate
    HF_EVALUATE_AVAILABLE = True
except ImportError:
    print("⚠️  HuggingFace Evaluate not available. Install with: pip install evaluate")
    HF_EVALUATE_AVAILABLE = False

class BERTEvaluator:
    """Comprehensive BERT model evaluator with LLM metrics"""
    
    def __init__(self, model_path: str, device: str = "auto"):
        """
        Initialize the BERT evaluator
        
        Args:
            model_path: Path to the fine-tuned BERT model
            device: Device to run evaluation on ('auto', 'cpu', 'cuda')
        """
        self.model_path = model_path
        self.device = self._setup_device(device)
        self.model, self.tokenizer = self._load_model()
        self.results = {}
        
        print(f"🚀 BERTEvaluator initialized on {self.device}")
        print(f"📁 Model loaded from: {model_path}")
    
    def _setup_device(self, device: str) -> torch.device:
        """Setup optimal device for evaluation"""
        if device == "auto":
            if torch.cuda.is_available():
                device = torch.device("cuda")
                print(f"🔥 GPU detected: {torch.cuda.get_device_name()}")
            else:
                device = torch.device("cpu")
                print("💻 Using CPU for evaluation")
        else:
            device = torch.device(device)
        return device
    
    def _load_model(self) -> Tuple[BertForSequenceClassification, BertTokenizer]:
        """Load the fine-tuned BERT model and tokenizer"""
        try:
            model = BertForSequenceClassification.from_pretrained(self.model_path)
            tokenizer = BertTokenizer.from_pretrained(self.model_path)
            model.to(self.device)
            model.eval()
            return model, tokenizer
        except Exception as e:
            raise ValueError(f"Failed to load model from {self.model_path}: {e}")
    
    def predict_batch(self, texts: List[str], return_probs: bool = True) -> Dict:
        """
        Predict labels and probabilities for a batch of texts
        
        Args:
            texts: List of input texts
            return_probs: Whether to return probability scores
            
        Returns:
            Dictionary with predictions, labels, and optionally probabilities
        """
        predictions = []
        probabilities = []
        
        with torch.no_grad():
            for text in texts:
                # Tokenize
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Forward pass
                outputs = self.model(**inputs)
                logits = outputs.logits
                
                # Get predictions
                pred = torch.argmax(logits, dim=-1).cpu().item()
                predictions.append(pred)
                
                if return_probs:
                    probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
                    probabilities.append(probs)
        
        result = {
            "predictions": predictions,
            "labels": ["negative" if p == 0 else "positive" for p in predictions]
        }
        
        if return_probs:
            result["probabilities"] = probabilities
            result["confidence"] = [max(probs) for probs in probabilities]
        
        return result
    
    def evaluate_traditional_metrics(self, texts: List[str], true_labels: List[int]) -> Dict:
        """
        Evaluate using traditional classification metrics
        
        Args:
            texts: List of input texts
            true_labels: List of true labels (0 or 1)
            
        Returns:
            Dictionary with traditional metrics
        """
        print("📊 Computing traditional classification metrics...")
        
        # Get predictions
        predictions = self.predict_batch(texts, return_probs=True)
        pred_labels = predictions["predictions"]
        confidences = predictions["confidence"]
        
        # Compute metrics
        accuracy = accuracy_score(true_labels, pred_labels)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_labels, pred_labels, average='weighted'
        )
        
        # Confusion matrix
        cm = confusion_matrix(true_labels, pred_labels)
        
        results = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "avg_confidence": float(np.mean(confidences)),
            "confusion_matrix": cm.tolist(),
            "num_samples": len(texts)
        }
        
        self.results["traditional_metrics"] = results
        return results
    
    def evaluate_bertscore(self, predictions: List[str], references: List[str]) -> Dict:
        """
        Evaluate using BERTScore for semantic similarity
        
        Args:
            predictions: List of predicted texts
            references: List of reference texts
            
        Returns:
            Dictionary with BERTScore metrics
        """
        if not BERTSCORE_AVAILABLE:
            return {"error": "BERTScore not available"}
        
        print("🎯 Computing BERTScore metrics...")
        
        scorer = BERTScorer(lang="en", rescale_with_baseline=True)
        P, R, F1 = scorer.score(predictions, references)
        
        results = {
            "bertscore_precision": float(P.mean()),
            "bertscore_recall": float(R.mean()),
            "bertscore_f1": float(F1.mean()),
            "bertscore_precision_std": float(P.std()),
            "bertscore_recall_std": float(R.std()),
            "bertscore_f1_std": float(F1.std()),
            "num_pairs": len(predictions)
        }
        
        self.results["bertscore"] = results
        return results
    
    def evaluate_rouge(self, predictions: List[str], references: List[str]) -> Dict:
        """
        Evaluate using ROUGE metrics
        
        Args:
            predictions: List of predicted texts
            references: List of reference texts
            
        Returns:
            Dictionary with ROUGE metrics
        """
        if not ROUGE_AVAILABLE:
            return {"error": "ROUGE not available"}
        
        print("📝 Computing ROUGE metrics...")
        
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        
        rouge_scores = {
            'rouge1_precision': [],
            'rouge1_recall': [],
            'rouge1_fmeasure': [],
            'rouge2_precision': [],
            'rouge2_recall': [],
            'rouge2_fmeasure': [],
            'rougeL_precision': [],
            'rougeL_recall': [],
            'rougeL_fmeasure': []
        }
        
        for pred, ref in zip(predictions, references):
            scores = scorer.score(pred, ref)
            for metric in scores:
                rouge_scores[f'{metric}_precision'].append(scores[metric].precision)
                rouge_scores[f'{metric}_recall'].append(scores[metric].recall)
                rouge_scores[f'{metric}_fmeasure'].append(scores[metric].fmeasure)
        
        # Calculate averages
        results = {}
        for key, values in rouge_scores.items():
            results[f"{key}_mean"] = float(np.mean(values))
            results[f"{key}_std"] = float(np.std(values))
        
        self.results["rouge"] = results
        return results
    
    def evaluate_bleu(self, predictions: List[str], references: List[str]) -> Dict:
        """
        Evaluate using BLEU score
        
        Args:
            predictions: List of predicted texts
            references: List of reference texts
            
        Returns:
            Dictionary with BLEU scores
        """
        if not BLEU_AVAILABLE:
            return {"error": "BLEU not available"}
        
        print("🎯 Computing BLEU scores...")
        
        # Convert to format expected by sacrebleu
        refs = [[ref] for ref in references]
        
        bleu = sacrebleu.corpus_bleu(predictions, refs)
        
        results = {
            "bleu_score": float(bleu.score),
            "bleu_precisions": [float(p) for p in bleu.precisions],
            "brevity_penalty": float(bleu.bp),
            "length_ratio": float(bleu.ratio),
            "num_pairs": len(predictions)
        }
        
        self.results["bleu"] = results
        return results
    
    def evaluate_deepeval_metrics(self, texts: List[str], predictions: List[str], 
                                references: List[str]) -> Dict:
        """
        Evaluate using DeepEval metrics
        
        Args:
            texts: Original input texts
            predictions: Model predictions
            references: Reference/expected outputs
            
        Returns:
            Dictionary with DeepEval metrics
        """
        if not DEEPEVAL_AVAILABLE:
            return {"error": "DeepEval not available"}
        
        print("🔍 Computing DeepEval metrics...")
        
        # Create test cases
        test_cases = []
        for text, pred, ref in zip(texts, predictions, references):
            test_case = LLMTestCase(
                input=text,
                actual_output=pred,
                expected_output=ref
            )
            test_cases.append(test_case)
        
        # Initialize metrics (adjust based on your use case)
        metrics = []
        
        try:
            # Answer relevancy metric
            answer_relevancy = AnswerRelevancyMetric(threshold=0.7)
            metrics.append(answer_relevancy)
        except Exception as e:
            print(f"⚠️  Answer Relevancy metric error: {e}")
        
        try:
            # Hallucination metric
            hallucination = HallucinationMetric(threshold=0.5)
            metrics.append(hallucination)
        except Exception as e:
            print(f"⚠️  Hallucination metric error: {e}")
        
        try:
            # Bias metric
            bias = BiasMetric(threshold=0.5)
            metrics.append(bias)
        except Exception as e:
            print(f"⚠️  Bias metric error: {e}")
        
        if not metrics:
            return {"error": "No DeepEval metrics available"}
        
        # Run evaluation
        results = {}
        for metric in metrics:
            try:
                scores = []
                for test_case in test_cases[:5]:  # Limit to 5 for demo
                    metric.measure(test_case)
                    scores.append(metric.score)
                
                metric_name = metric.__class__.__name__.replace("Metric", "").lower()
                results[f"deepeval_{metric_name}_mean"] = float(np.mean(scores))
                results[f"deepeval_{metric_name}_std"] = float(np.std(scores))
                
            except Exception as e:
                print(f"⚠️  Error with {metric.__class__.__name__}: {e}")
        
        self.results["deepeval"] = results
        return results
    
    def evaluate_comprehensive(self, test_data: Dict, save_results: bool = True) -> Dict:
        """
        Run comprehensive evaluation with all available metrics
        
        Args:
            test_data: Dictionary with 'texts', 'labels', 'references' keys
            save_results: Whether to save results to file
            
        Returns:
            Complete evaluation results
        """
        print("🚀 Starting comprehensive BERT evaluation...")
        print("="*60)
        
        texts = test_data['texts']
        true_labels = test_data['labels']
        references = test_data.get('references', [])
        
        # Get model predictions
        predictions_data = self.predict_batch(texts, return_probs=True)
        pred_texts = [f"{'positive' if p == 1 else 'negative'} sentiment" 
                     for p in predictions_data['predictions']]
        
        # Traditional metrics
        traditional = self.evaluate_traditional_metrics(texts, true_labels)
        
        # If references are provided, run text similarity metrics
        if references:
            bertscore = self.evaluate_bertscore(pred_texts, references)
            rouge = self.evaluate_rouge(pred_texts, references)
            bleu = self.evaluate_bleu(pred_texts, references)
            deepeval = self.evaluate_deepeval_metrics(texts, pred_texts, references)
        else:
            print("⚠️  No references provided - skipping text similarity metrics")
            bertscore = rouge = bleu = deepeval = {}
        
        # Compile results
        comprehensive_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_path": self.model_path,
            "device": str(self.device),
            "evaluation_summary": {
                "total_samples": len(texts),
                "has_references": len(references) > 0,
                "metrics_computed": list(self.results.keys())
            },
            "results": self.results
        }
        
        if save_results:
            self._save_results(comprehensive_results)
        
        self._print_summary()
        return comprehensive_results
    
    def _save_results(self, results: Dict):
        """Save evaluation results to JSON file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"bert_evaluation_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {filename}")
    
    def _print_summary(self):
        """Print evaluation summary"""
        print("\n" + "="*60)
        print("📊 EVALUATION SUMMARY")
        print("="*60)
        
        if "traditional_metrics" in self.results:
            tm = self.results["traditional_metrics"]
            print(f"🎯 Traditional Metrics:")
            print(f"   Accuracy: {tm['accuracy']:.3f}")
            print(f"   F1 Score: {tm['f1_score']:.3f}")
            print(f"   Precision: {tm['precision']:.3f}")
            print(f"   Recall: {tm['recall']:.3f}")
            print(f"   Avg Confidence: {tm['avg_confidence']:.3f}")
        
        if "bertscore" in self.results:
            bs = self.results["bertscore"]
            print(f"\n🎯 BERTScore:")
            print(f"   F1: {bs['bertscore_f1']:.3f} ± {bs['bertscore_f1_std']:.3f}")
            print(f"   Precision: {bs['bertscore_precision']:.3f}")
            print(f"   Recall: {bs['bertscore_recall']:.3f}")
        
        if "rouge" in self.results:
            rouge = self.results["rouge"]
            print(f"\n📝 ROUGE Scores:")
            print(f"   ROUGE-1 F1: {rouge['rouge1_fmeasure_mean']:.3f}")
            print(f"   ROUGE-2 F1: {rouge['rouge2_fmeasure_mean']:.3f}")
            print(f"   ROUGE-L F1: {rouge['rougeL_fmeasure_mean']:.3f}")
        
        if "bleu" in self.results:
            bleu = self.results["bleu"]
            print(f"\n🎯 BLEU Score: {bleu['bleu_score']:.3f}")
        
        if "deepeval" in self.results:
            de = self.results["deepeval"]
            print(f"\n🔍 DeepEval Metrics:")
            for key, value in de.items():
                if key.endswith("_mean"):
                    metric_name = key.replace("deepeval_", "").replace("_mean", "")
                    print(f"   {metric_name.title()}: {value:.3f}")

    def visualize_results(self, save_plots: bool = True):
        """Create visualizations of evaluation results"""
        print("📊 Creating evaluation visualizations...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('BERT Model Evaluation Results', fontsize=16, fontweight='bold')
        
        # Traditional metrics radar chart
        if "traditional_metrics" in self.results:
            tm = self.results["traditional_metrics"]
            metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
            values = [tm['accuracy'], tm['precision'], tm['recall'], tm['f1_score']]
            
            ax = axes[0, 0]
            bars = ax.bar(metrics, values, color=['skyblue', 'lightgreen', 'lightcoral', 'gold'])
            ax.set_title('Traditional Classification Metrics')
            ax.set_ylim(0, 1)
            ax.set_ylabel('Score')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{value:.3f}', ha='center', va='bottom')
        
        # Confusion matrix
        if "traditional_metrics" in self.results:
            cm = np.array(self.results["traditional_metrics"]["confusion_matrix"])
            ax = axes[0, 1]
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
            ax.set_title('Confusion Matrix')
            ax.set_xlabel('Predicted')
            ax.set_ylabel('Actual')
        
        # Text similarity metrics comparison
        similarity_metrics = {}
        if "bertscore" in self.results:
            similarity_metrics['BERTScore F1'] = self.results["bertscore"]["bertscore_f1"]
        if "rouge" in self.results:
            similarity_metrics['ROUGE-1'] = self.results["rouge"]["rouge1_fmeasure_mean"]
            similarity_metrics['ROUGE-L'] = self.results["rouge"]["rougeL_fmeasure_mean"]
        if "bleu" in self.results:
            similarity_metrics['BLEU'] = self.results["bleu"]["bleu_score"] / 100  # Normalize
        
        if similarity_metrics:
            ax = axes[1, 0]
            bars = ax.bar(similarity_metrics.keys(), similarity_metrics.values(),
                         color=['purple', 'orange', 'green', 'red'])
            ax.set_title('Text Similarity Metrics')
            ax.set_ylabel('Score')
            ax.tick_params(axis='x', rotation=45)
            
            for bar, value in zip(bars, similarity_metrics.values()):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{value:.3f}', ha='center', va='bottom')
        
        # Model confidence distribution
        if "traditional_metrics" in self.results:
            ax = axes[1, 1]
            # This would need the raw confidence scores from predictions
            ax.text(0.5, 0.5, f"Avg Confidence:\n{self.results['traditional_metrics']['avg_confidence']:.3f}",
                   ha='center', va='center', fontsize=20, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
            ax.set_title('Model Confidence')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        plt.tight_layout()
        
        if save_plots:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"bert_evaluation_plots_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📊 Plots saved to: {filename}")
        
        plt.show()


def main():
    """Example usage of the BERT evaluator"""
    
    # Check if model exists
    model_path = "./fine_tuned_bert"
    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}")
        print("Please run the BERT fine-tuning script first!")
        return
    
    # Sample test data
    test_data = {
        'texts': [
            "I absolutely love this product! It exceeded my expectations.",
            "This is the worst service I've ever experienced.",
            "The movie was fantastic, great acting and plot.",
            "Terrible quality, would not recommend to anyone.",
            "Amazing customer support, very helpful staff.",
            "Poor design and functionality, waste of money."
        ],
        'labels': [1, 0, 1, 0, 1, 0],  # 1 = positive, 0 = negative
        'references': [
            "positive sentiment expressed with enthusiasm",
            "negative sentiment about poor service quality",
            "positive sentiment about entertainment content",
            "negative sentiment about product quality",
            "positive sentiment about customer service",
            "negative sentiment about product value"
        ]
    }
    
    # Initialize evaluator
    evaluator = BERTEvaluator(model_path=model_path)
    
    # Run comprehensive evaluation
    results = evaluator.evaluate_comprehensive(test_data)
    
    # Create visualizations
    evaluator.visualize_results()
    
    print("\n🎉 Evaluation completed successfully!")
    return results


if __name__ == "__main__":
    main()
