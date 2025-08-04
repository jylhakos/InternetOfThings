#!/usr/bin/env python3
"""
Test script for BERT fine-tuning evaluation
Includes comprehensive testing of model performance
"""

import torch
import numpy as np
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
import pandas as pd


class BERTEvaluator:
    def __init__(self, model_path="bert-base-uncased", device=None):
        """Initialize BERT evaluator with model and tokenizer"""
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        try:
            # Try to load fine-tuned model first
            self.model = BertForSequenceClassification.from_pretrained(model_path)
            self.tokenizer = BertTokenizer.from_pretrained(model_path)
            print(f"✓ Loaded fine-tuned model from {model_path}")
        except:
            # Fall back to pre-trained model
            self.model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
            self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
            print("✓ Loaded pre-trained BERT model (bert-base-uncased)")
        
        self.model.to(self.device)
        self.model.eval()
    
    def predict_single(self, text, return_probabilities=False):
        """Predict sentiment for a single text"""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, 
                               truncation=True, max_length=128)
        inputs = {key: val.to(self.device) for key, val in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            prediction = torch.argmax(logits, dim=-1).cpu().numpy()[0]
        
        if return_probabilities:
            return prediction, probabilities.cpu().numpy()[0]
        return prediction
    
    def predict_batch(self, texts):
        """Predict sentiment for multiple texts"""
        predictions = []
        probabilities = []
        
        for text in texts:
            pred, prob = self.predict_single(text, return_probabilities=True)
            predictions.append(pred)
            probabilities.append(prob)
        
        return np.array(predictions), np.array(probabilities)
    
    def evaluate_model(self, texts, true_labels):
        """Comprehensive model evaluation"""
        predictions, probabilities = self.predict_batch(texts)
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(true_labels, predictions, average='weighted')
        
        # Confusion matrix
        cm = confusion_matrix(true_labels, predictions)
        
        # Classification report
        report = classification_report(true_labels, predictions, 
                                     target_names=['Negative', 'Positive'])
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm,
            'classification_report': report,
            'predictions': predictions,
            'probabilities': probabilities
        }


def test_fine_tuning_success():
    """Test cases to verify fine-tuning success"""
    print("="*60)
    print("BERT FINE-TUNING EVALUATION")
    print("="*60)
    
    # Initialize evaluator
    evaluator = BERTEvaluator()
    
    # Test dataset
    test_cases = [
        # Clearly positive examples
        ("I absolutely love this product! It's amazing!", 1),
        ("This is fantastic and works perfectly!", 1),
        ("Excellent quality and great value for money", 1),
        ("I'm so happy with this purchase!", 1),
        ("Outstanding performance, highly recommend!", 1),
        
        # Clearly negative examples  
        ("This is terrible and completely useless", 0),
        ("Worst product ever, waste of money", 0),
        ("I hate this, it doesn't work at all", 0),
        ("Poor quality and bad customer service", 0),
        ("Completely disappointed, would not buy again", 0),
        
        # Neutral/ambiguous cases
        ("It's okay, nothing special", 0),
        ("Average product, could be better", 0),
        ("It works as expected", 1),
        ("Not bad, but not great either", 0),
        ("Decent for the price", 1),
    ]
    
    texts = [case[0] for case in test_cases]
    true_labels = [case[1] for case in test_cases]
    
    # Evaluate model
    results = evaluator.evaluate_model(texts, true_labels)
    
    # Print results
    print(f"\\nMODEL PERFORMANCE METRICS:")
    print(f"Accuracy: {results['accuracy']:.3f}")
    print(f"Precision: {results['precision']:.3f}")
    print(f"Recall: {results['recall']:.3f}")
    print(f"F1-Score: {results['f1_score']:.3f}")
    
    print(f"\\nCONFUSION MATRIX:")
    print(f"             Predicted")
    print(f"           Neg    Pos")
    print(f"Actual Neg  {results['confusion_matrix'][0][0]:3d}   {results['confusion_matrix'][0][1]:3d}")
    print(f"       Pos  {results['confusion_matrix'][1][0]:3d}   {results['confusion_matrix'][1][1]:3d}")
    
    print(f"\\nDETAILED CLASSIFICATION REPORT:")
    print(results['classification_report'])
    
    # Individual predictions
    print(f"\\nINDIVIDUAL PREDICTIONS:")
    print("-" * 80)
    for i, (text, true_label, pred, prob) in enumerate(zip(texts, true_labels, 
                                                           results['predictions'], 
                                                           results['probabilities'])):
        status = "✓" if pred == true_label else "✗"
        confidence = prob[pred]
        print(f"{status} [{i+1:2d}] True: {true_label}, Pred: {pred} (conf: {confidence:.3f})")
        print(f"      Text: {text}")
        print()
    
    # Success criteria
    print("\\nFINE-TUNING SUCCESS EVALUATION:")
    print("-" * 40)
    
    success_criteria = {
        "Accuracy > 0.7": results['accuracy'] > 0.7,
        "F1-Score > 0.7": results['f1_score'] > 0.7,
        "Precision > 0.7": results['precision'] > 0.7,
        "Recall > 0.7": results['recall'] > 0.7,
    }
    
    for criterion, passed in success_criteria.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {criterion}")
    
    overall_success = all(success_criteria.values())
    print(f"\\nOVERALL FINE-TUNING: {'✓ SUCCESS' if overall_success else '✗ NEEDS IMPROVEMENT'}")
    
    return results


def interactive_testing():
    """Interactive testing interface"""
    print("\\n" + "="*60)
    print("INTERACTIVE SENTIMENT TESTING")
    print("="*60)
    print("Enter text to test sentiment classification (type 'quit' to exit)")
    
    evaluator = BERTEvaluator()
    
    while True:
        try:
            user_text = input("\\nEnter text: ").strip()
            if user_text.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_text:
                continue
                
            prediction, probabilities = evaluator.predict_single(user_text, return_probabilities=True)
            sentiment = "Positive" if prediction == 1 else "Negative"
            confidence = probabilities[prediction]
            
            print(f"Prediction: {sentiment}")
            print(f"Confidence: {confidence:.3f}")
            print(f"Probabilities: Negative={probabilities[0]:.3f}, Positive={probabilities[1]:.3f}")
            
        except KeyboardInterrupt:
            print("\\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    try:
        # Run comprehensive evaluation
        results = test_fine_tuning_success()
        
        # Offer interactive testing
        response = input("\\nWould you like to test with your own text? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_testing()
            
    except Exception as e:
        print(f"Error during evaluation: {e}")
        print("\\nTroubleshooting tips:")
        print("1. Make sure the virtual environment is activated")
        print("2. Verify all packages are installed: pip list")
        print("3. Check if the model was saved properly")
