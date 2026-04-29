#!/usr/bin/env python3
"""
LLM Evaluation Metrics Implementation
=====================================

This script demonstrates various evaluation metrics for Large Language Models,
including perplexity, BLEU, ROUGE, BERTScore, and other important metrics
commonly used in NLP model evaluation.

Author: BERT Fine-tuning Project
Date: August 2025
"""

import torch
import numpy as np
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings("ignore")


def calculate_perplexity(model, tokenizer, text: str, device: torch.device) -> float:
    """
    Calculate perplexity for a given text using a language model.
    
    Args:
        model: Pre-trained language model
        tokenizer: Corresponding tokenizer
        text: Input text to evaluate
        device: Computation device (CPU/GPU)
    
    Returns:
        float: Perplexity score (lower is better)
    """
    try:
        # Tokenize the input text
        encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        input_ids = encoded["input_ids"].to(device)
        
        # Move model to device
        model = model.to(device)
        model.eval()
        
        with torch.no_grad():
            # Calculate loss
            outputs = model(input_ids, labels=input_ids)
            loss = outputs.loss
            
            # Calculate perplexity
            perplexity = torch.exp(loss)
            
        return perplexity.item()
    
    except Exception as e:
        print(f"Error calculating perplexity: {e}")
        return float('inf')


def calculate_bleu_score(candidates: List[str], references: List[List[str]], 
                        max_n: int = 4) -> Dict[str, float]:
    """
    Calculate BLEU score for text generation evaluation.
    
    Args:
        candidates: List of generated texts
        references: List of reference texts (each can have multiple references)
        max_n: Maximum n-gram size to consider
    
    Returns:
        Dict containing BLEU scores for different n-grams
    """
    try:
        from nltk.translate.bleu_score import corpus_bleu, SmoothingFunction
        import nltk
        nltk.download('punkt', quiet=True)
        
        # Tokenize references and candidates
        tokenized_refs = []
        for ref_list in references:
            tokenized_refs.append([ref.lower().split() for ref in ref_list])
        
        tokenized_candidates = [cand.lower().split() for cand in candidates]
        
        # Calculate BLEU scores
        smoothing = SmoothingFunction().method1
        bleu_scores = {}
        
        for n in range(1, max_n + 1):
            weights = [1/n] * n + [0] * (4-n)
            score = corpus_bleu(
                tokenized_refs, 
                tokenized_candidates, 
                weights=weights,
                smoothing_function=smoothing
            )
            bleu_scores[f'BLEU-{n}'] = score
        
        return bleu_scores
    
    except ImportError:
        print("NLTK not available. Install with: pip install nltk")
        return {}
    except Exception as e:
        print(f"Error calculating BLEU score: {e}")
        return {}


def calculate_rouge_score(candidates: List[str], references: List[str]) -> Dict[str, float]:
    """
    Calculate ROUGE score for text summarization evaluation.
    
    Args:
        candidates: List of generated summaries
        references: List of reference summaries
    
    Returns:
        Dict containing ROUGE-1, ROUGE-2, and ROUGE-L scores
    """
    try:
        from rouge_score import rouge_scorer
        
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        
        rouge_scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}
        
        for candidate, reference in zip(candidates, references):
            scores = scorer.score(reference, candidate)
            for metric in rouge_scores:
                rouge_scores[metric].append(scores[metric].fmeasure)
        
        # Calculate average scores
        avg_scores = {}
        for metric in rouge_scores:
            avg_scores[f'ROUGE-{metric[-1]}' if metric != 'rougeL' else 'ROUGE-L'] = np.mean(rouge_scores[metric])
        
        return avg_scores
    
    except ImportError:
        print("rouge-score not available. Install with: pip install rouge-score")
        return {}
    except Exception as e:
        print(f"Error calculating ROUGE score: {e}")
        return {}


def calculate_bertscore(candidates: List[str], references: List[str], 
                       lang: str = "en") -> Dict[str, float]:
    """
    Calculate BERTScore for semantic similarity evaluation.
    
    Args:
        candidates: List of generated texts
        references: List of reference texts
        lang: Language code for evaluation
    
    Returns:
        Dict containing precision, recall, and F1 scores
    """
    try:
        from bert_score import score
        
        P, R, F1 = score(candidates, references, lang=lang, verbose=False)
        
        return {
            'BERTScore_Precision': P.mean().item(),
            'BERTScore_Recall': R.mean().item(),
            'BERTScore_F1': F1.mean().item()
        }
    
    except ImportError:
        print("bert-score not available. Install with: pip install bert-score")
        return {}
    except Exception as e:
        print(f"Error calculating BERTScore: {e}")
        return {}


def calculate_classification_metrics(y_true: List[int], y_pred: List[int], 
                                   labels: Optional[List[str]] = None) -> Dict[str, float]:
    """
    Calculate classification metrics for model evaluation.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        labels: Label names for detailed reporting
    
    Returns:
        Dict containing accuracy, precision, recall, and F1 scores
    """
    try:
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
        
        # Basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')
        
        metrics = {
            'Accuracy': accuracy,
            'Weighted_Precision': precision,
            'Weighted_Recall': recall,
            'Weighted_F1': f1
        }
        
        # Detailed classification report
        if labels:
            report = classification_report(y_true, y_pred, target_names=labels, output_dict=True)
            for label in labels:
                if label in report:
                    metrics[f'{label}_Precision'] = report[label]['precision']
                    metrics[f'{label}_Recall'] = report[label]['recall']
                    metrics[f'{label}_F1'] = report[label]['f1-score']
        
        return metrics
    
    except Exception as e:
        print(f"Error calculating classification metrics: {e}")
        return {}


def calculate_diversity_metrics(texts: List[str]) -> Dict[str, float]:
    """
    Calculate diversity metrics for text generation.
    
    Args:
        texts: List of generated texts
    
    Returns:
        Dict containing diversity metrics
    """
    try:
        # Calculate distinct n-grams
        def get_ngrams(text: str, n: int) -> set:
            words = text.lower().split()
            return set(zip(*[words[i:] for i in range(n)]))
        
        # Distinct-1 and Distinct-2
        all_unigrams = set()
        all_bigrams = set()
        total_unigrams = 0
        total_bigrams = 0
        
        for text in texts:
            unigrams = get_ngrams(text, 1)
            bigrams = get_ngrams(text, 2)
            
            all_unigrams.update(unigrams)
            all_bigrams.update(bigrams)
            
            total_unigrams += len(unigrams)
            total_bigrams += len(bigrams)
        
        distinct_1 = len(all_unigrams) / max(total_unigrams, 1)
        distinct_2 = len(all_bigrams) / max(total_bigrams, 1)
        
        return {
            'Distinct-1': distinct_1,
            'Distinct-2': distinct_2,
            'Vocabulary_Size': len(all_unigrams)
        }
    
    except Exception as e:
        print(f"Error calculating diversity metrics: {e}")
        return {}


def evaluate_model_comprehensive(model, tokenizer, test_data: Dict, device: torch.device) -> Dict[str, float]:
    """
    Comprehensive evaluation of a language model using multiple metrics.
    
    Args:
        model: Pre-trained model
        tokenizer: Corresponding tokenizer
        test_data: Dictionary containing test examples
        device: Computation device
    
    Returns:
        Dict containing all evaluation metrics
    """
    print("="*60)
    print("COMPREHENSIVE MODEL EVALUATION")
    print("="*60)
    
    all_metrics = {}
    
    # 1. Perplexity evaluation
    if 'texts' in test_data:
        print("📊 Calculating Perplexity...")
        perplexities = []
        for text in test_data['texts'][:10]:  # Limit to first 10 for speed
            ppl = calculate_perplexity(model, tokenizer, text, device)
            perplexities.append(ppl)
        
        avg_perplexity = np.mean(perplexities)
        all_metrics['Average_Perplexity'] = avg_perplexity
        print(f"   Average Perplexity: {avg_perplexity:.2f}")
    
    # 2. Classification metrics (if labels available)
    if 'labels' in test_data and 'predictions' in test_data:
        print("📊 Calculating Classification Metrics...")
        clf_metrics = calculate_classification_metrics(
            test_data['labels'], 
            test_data['predictions'],
            test_data.get('label_names')
        )
        all_metrics.update(clf_metrics)
        print(f"   Accuracy: {clf_metrics.get('Accuracy', 0):.4f}")
        print(f"   F1 Score: {clf_metrics.get('Weighted_F1', 0):.4f}")
    
    # 3. Text generation metrics (if generated texts available)
    if 'generated_texts' in test_data and 'reference_texts' in test_data:
        print("📊 Calculating Text Generation Metrics...")
        
        # BLEU Score
        bleu_scores = calculate_bleu_score(
            test_data['generated_texts'],
            [[ref] for ref in test_data['reference_texts']]
        )
        all_metrics.update(bleu_scores)
        
        # ROUGE Score
        rouge_scores = calculate_rouge_score(
            test_data['generated_texts'],
            test_data['reference_texts']
        )
        all_metrics.update(rouge_scores)
        
        # BERTScore
        bert_scores = calculate_bertscore(
            test_data['generated_texts'],
            test_data['reference_texts']
        )
        all_metrics.update(bert_scores)
        
        # Diversity metrics
        diversity_scores = calculate_diversity_metrics(test_data['generated_texts'])
        all_metrics.update(diversity_scores)
        
        print(f"   BLEU-4: {bleu_scores.get('BLEU-4', 0):.4f}")
        print(f"   ROUGE-L: {rouge_scores.get('ROUGE-L', 0):.4f}")
        print(f"   BERTScore F1: {bert_scores.get('BERTScore_F1', 0):.4f}")
    
    print("="*60)
    print("EVALUATION COMPLETED")
    print("="*60)
    
    return all_metrics


def demo_evaluation_metrics():
    """
    Demonstrate evaluation metrics with sample data.
    """
    print("="*60)
    print("LLM EVALUATION METRICS DEMONSTRATION")
    print("="*60)
    
    # Sample data for demonstration
    candidates = [
        "The cat sits on the mat",
        "A dog runs in the park",
        "The weather is nice today"
    ]
    
    references = [
        "A cat is sitting on a mat",
        "The dog is running in the park",
        "Today has beautiful weather"
    ]
    
    print("📊 Sample Texts:")
    for i, (cand, ref) in enumerate(zip(candidates, references)):
        print(f"   Generated {i+1}: {cand}")
        print(f"   Reference {i+1}: {ref}")
        print()
    
    # Calculate different metrics
    print("📊 Evaluation Results:")
    
    # BLEU Score
    bleu_scores = calculate_bleu_score(candidates, [[ref] for ref in references])
    for metric, score in bleu_scores.items():
        print(f"   {metric}: {score:.4f}")
    
    # ROUGE Score
    rouge_scores = calculate_rouge_score(candidates, references)
    for metric, score in rouge_scores.items():
        print(f"   {metric}: {score:.4f}")
    
    # BERTScore
    bert_scores = calculate_bertscore(candidates, references)
    for metric, score in bert_scores.items():
        print(f"   {metric}: {score:.4f}")
    
    # Diversity metrics
    diversity_scores = calculate_diversity_metrics(candidates)
    for metric, score in diversity_scores.items():
        print(f"   {metric}: {score:.4f}")
    
    # Classification metrics example
    print("\n📊 Classification Metrics Example:")
    y_true = [0, 1, 1, 0, 1, 0, 1, 1, 0, 0]
    y_pred = [0, 1, 1, 0, 0, 0, 1, 1, 1, 0]
    
    clf_metrics = calculate_classification_metrics(y_true, y_pred, ['Negative', 'Positive'])
    for metric, score in clf_metrics.items():
        print(f"   {metric}: {score:.4f}")


if __name__ == "__main__":
    print("LLM Evaluation Metrics Library")
    print("==============================")
    print("This script provides implementations of various LLM evaluation metrics.")
    print("Run demo_evaluation_metrics() to see examples.")
    print()
    
    try:
        demo_evaluation_metrics()
    except Exception as e:
        print(f"Demo failed: {e}")
        print("Some dependencies may be missing. Install with:")
        print("pip install nltk rouge-score bert-score")
