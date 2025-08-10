#!/usr/bin/env python3
"""
Transfer Learning for BERT + CoLA - Corpus of Linguistic Acceptability
==============================================================

An implementation of BERT transfer learning on the CoLA dataset
for grammatical acceptability classification.

CoLA (Corpus of Linguistic Acceptability) is part of the GLUE benchmark
and contains English sentences labeled as grammatically acceptable (1)
or unacceptable (0).

Dataset Details:
- Training: 8,551 sentences
- Validation: 1,043 sentences
- Classes: Binary (0=unacceptable, 1=acceptable)
- Source: Part of GLUE benchmark
- Task: Single sentence classification

This implementation demonstrates:
- Loading CoLA from GLUE benchmark via Hugging Face
- Proper BERT tokenization with special tokens
- Optimized dataset preparation and data loading
- Complete fine-tuning pipeline with evaluation
- Linguistic acceptability analysis and visualization

Usage Examples:
    # Train BERT on CoLA dataset
    python cola_bert_transfer_learning.py --epochs 4 --batch-size 16

    # Quick test with smaller dataset
    python cola_bert_transfer_learning.py --epochs 2 --max-samples 1000

    # Evaluate existing model
    python cola_bert_transfer_learning.py --evaluate-only --model-path best_cola_bert.pth

    # Test with custom sentences
    python cola_bert_transfer_learning.py --test-sentence "The cat is sleeping on the mat."

References:
- CoLA: http://nyu-mll.github.io/CoLA/
- GLUE: https://gluebenchmark.com/
- BERT: Devlin et al. (2018)

Author: Feature Learning Project
License: MIT
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import (
    BertForSequenceClassification,
    BertTokenizer,
    AdamW,
    get_linear_schedule_with_warmup
)
import numpy as np
from datasets import load_dataset
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_recall_fscore_support,
    matthews_corrcoef,
    classification_report,
    confusion_matrix
)

# PyTorch Metrics for native PyTorch implementation
try:
    from torchmetrics import MatthewsCorrCoef, Accuracy, F1Score
    TORCHMETRICS_AVAILABLE = True
    print("TorchMetrics available - using native PyTorch MCC calculation")
except ImportError:
    TORCHMETRICS_AVAILABLE = False
    print("⚠️ TorchMetrics not available - falling back to sklearn implementation")
    print("   Install with: pip install torchmetrics")
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
import json
import time
from tqdm import tqdm
import logging
from collections import Counter

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Using device: {device}")


class CoLADataset(Dataset):
    """
    Custom Dataset class for CoLA (Corpus of Linguistic Acceptability)
    Optimized for BERT fine-tuning with proper tokenization
    """
    
    def __init__(self, sentences, labels, tokenizer, max_length=128):
        self.sentences = sentences
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Data validation
        assert len(sentences) == len(labels), "Mismatch between sentences and labels"
        
        logger.info(f"CoLA Dataset initialized: {len(sentences)} samples, max_length={max_length}")
    
    def __len__(self):
        return len(self.sentences)
    
    def __getitem__(self, idx):
        sentence = str(self.sentences[idx])
        label = self.labels[idx]
        
        # BERT tokenization
        encoding = self.tokenizer(
            sentence,
            add_special_tokens=True,      # Add [CLS] and [SEP]
            max_length=self.max_length,
            padding='max_length',         # Pad to max_length
            truncation=True,              # Truncate if longer
            return_attention_mask=True,
            return_token_type_ids=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'token_type_ids': encoding['token_type_ids'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }


class CoLABERTClassifier:
    """
    BERT-based classifier for CoLA linguistic acceptability task
    """
    
    def __init__(self, model_name='bert-base-uncased', max_length=128):
        self.model_name = model_name
        self.max_length = max_length
        
        # Load tokenizer and model
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=2,  # Binary classification
            output_attentions=False,
            output_hidden_states=False
        )
        self.model.to(device)
        
        # Initialize PyTorch metrics if available
        if TORCHMETRICS_AVAILABLE:
            self.mcc_metric = MatthewsCorrCoef(num_classes=2).to(device)
            self.accuracy_metric = Accuracy(task='binary').to(device)
            self.f1_metric = F1Score(task='binary').to(device)
            logger.info("Using PyTorch metrics (torchmetrics)")
        else:
            self.mcc_metric = None
            self.accuracy_metric = None
            self.f1_metric = None
            logger.info("⚠️ Using scikit-learn metrics (install torchmetrics for native PyTorch implementation)")
        
        logger.info(f"Loaded BERT model: {model_name}")
        logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        logger.info(f"Device: {device}")
    
    def calculate_mcc_manual(self, predictions, labels):
        """
        Calculate MCC manually for educational purposes
        Shows the mathematical formula: MCC = (TP*TN - FP*FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))
        """
        # Convert to numpy arrays
        pred_np = np.array(predictions)
        true_np = np.array(labels)
        
        # Calculate confusion matrix components
        tp = np.sum((pred_np == 1) & (true_np == 1))  # True Positives
        tn = np.sum((pred_np == 0) & (true_np == 0))  # True Negatives
        fp = np.sum((pred_np == 1) & (true_np == 0))  # False Positives
        fn = np.sum((pred_np == 0) & (true_np == 1))  # False Negatives
        
        # MCC formula
        numerator = (tp * tn) - (fp * fn)
        denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        
        if denominator == 0:
            mcc = 0.0
        else:
            mcc = numerator / denominator
        
        logger.info(f" MCC Calculation:")
        logger.info(f"   TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn}")
        logger.info(f"   Numerator: ({tp} × {tn}) - ({fp} × {fn}) = {numerator}")
        logger.info(f"   Denominator: sqrt({tp + fp} × {tp + fn} × {tn + fp} × {tn + fn}) = {denominator:.4f}")
        logger.info(f"   MCC: {numerator} / {denominator:.4f} = {mcc:.6f}")
        
        return mcc
    
    def load_cola_dataset(self, max_samples=None):
        """Load CoLA dataset from GLUE benchmark"""
        
        logger.info("Loading CoLA dataset from GLUE benchmark...")
        
        # Load full CoLA dataset
        cola_dataset = load_dataset("glue", "cola")
        
        # Extract data
        train_sentences = cola_dataset["train"]["sentence"]
        train_labels = cola_dataset["train"]["label"]
        val_sentences = cola_dataset["validation"]["sentence"]
        val_labels = cola_dataset["validation"]["label"]
        
        # Limit samples if requested (for testing)
        if max_samples:
            train_sentences = train_sentences[:max_samples]
            train_labels = train_labels[:max_samples]
            val_samples = max_samples // 4  # Use 1/4 for validation
            val_sentences = val_sentences[:val_samples]
            val_labels = val_labels[:val_samples]
        
        # Dataset statistics
        train_acceptable = sum(train_labels)
        train_unacceptable = len(train_labels) - train_acceptable
        val_acceptable = sum(val_labels)
        val_unacceptable = len(val_labels) - val_acceptable
        
        logger.info(f"CoLA Dataset loaded:")
        logger.info(f"  Training: {len(train_sentences)} sentences")
        logger.info(f"    Acceptable: {train_acceptable} ({train_acceptable/len(train_labels)*100:.1f}%)")
        logger.info(f"    Unacceptable: {train_unacceptable} ({train_unacceptable/len(train_labels)*100:.1f}%)")
        logger.info(f"  Validation: {len(val_sentences)} sentences")
        logger.info(f"    Acceptable: {val_acceptable} ({val_acceptable/len(val_labels)*100:.1f}%)")
        logger.info(f"    Unacceptable: {val_unacceptable} ({val_unacceptable/len(val_labels)*100:.1f}%)")
        
        # Show sample sentences
        print("\n Sample CoLA sentences:")
        for i in range(5):
            label_text = " Acceptable" if train_labels[i] == 1 else "❌ Unacceptable"
            print(f"   {label_text}: '{train_sentences[i]}'")
        
        return train_sentences, train_labels, val_sentences, val_labels
    
    def analyze_sentence_lengths(self, sentences):
        """Analyze sentence lengths to optimize max_length"""
        
        lengths = []
        for sentence in sentences:
            tokens = self.tokenizer.tokenize(sentence)
            lengths.append(len(tokens) + 2)  # +2 for [CLS] and [SEP]
        
        lengths = np.array(lengths)
        
        print(f"\nSentence Length Analysis:")
        print(f"   Mean: {lengths.mean():.1f} tokens")
        print(f"   Median: {np.median(lengths):.1f} tokens")
        print(f"   Min: {lengths.min()} tokens")
        print(f"   Max: {lengths.max()} tokens")
        print(f"   95th percentile: {np.percentile(lengths, 95):.1f} tokens")
        
        # Visualization
        plt.figure(figsize=(10, 6))
        plt.hist(lengths, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(lengths.mean(), color='red', linestyle='--', 
                   label=f'Mean: {lengths.mean():.1f}')
        plt.axvline(np.percentile(lengths, 95), color='orange', linestyle='--', 
                   label=f'95th percentile: {np.percentile(lengths, 95):.1f}')
        plt.xlabel('Sentence Length (tokens)')
        plt.ylabel('Frequency')
        plt.title('CoLA Dataset - Sentence Length Distribution')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('cola_sentence_lengths.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return int(np.percentile(lengths, 95))
    
    def create_data_loaders(self, train_sentences, train_labels, val_sentences, val_labels, batch_size=16):
        """Create optimized data loaders"""
        
        # Create datasets
        train_dataset = CoLADataset(train_sentences, train_labels, self.tokenizer, self.max_length)
        val_dataset = CoLADataset(val_sentences, val_labels, self.tokenizer, self.max_length)
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=True if torch.cuda.is_available() else False
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True if torch.cuda.is_available() else False
        )
        
        logger.info(f"Data loaders created: {len(train_loader)} train batches, {len(val_loader)} val batches")
        
        return train_loader, val_loader
    
    def train_model(self, train_loader, val_loader, epochs=4, learning_rate=2e-5):
        """Train BERT model on CoLA dataset"""
        
        # Setup optimizer
        optimizer = AdamW(self.model.parameters(), lr=learning_rate, eps=1e-8)
        
        # Learning rate scheduler
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=int(0.1 * total_steps),
            num_training_steps=total_steps
        )
        
        # Training history
        history = {
            'train_loss': [],
            'val_loss': [],
            'val_accuracy': [],
            'val_f1': [],
            'matthews_corr': []  # Important metric for CoLA
        }
        
        best_matthews = -1  # Matthews correlation is key metric for CoLA
        
        logger.info(f"Starting training for {epochs} epochs...")
        logger.info(f"Total training steps: {total_steps}")
        
        for epoch in range(epochs):
            print(f"\n{'='*60}")
            print(f"Epoch {epoch + 1}/{epochs}")
            print('='*60)
            
            # Training phase
            self.model.train()
            total_train_loss = 0
            
            train_progress = tqdm(train_loader, desc=f"Training Epoch {epoch+1}")
            for batch in train_progress:
                # Move to device
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                token_type_ids = batch['token_type_ids'].to(device)
                labels = batch['label'].to(device)
                
                # Clear gradients
                optimizer.zero_grad()
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    token_type_ids=token_type_ids,
                    labels=labels
                )
                
                loss = outputs.loss
                total_train_loss += loss.item()
                
                # Backward pass
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                
                # Update weights
                optimizer.step()
                scheduler.step()
                
                # Update progress
                train_progress.set_postfix({'Loss': f'{loss.item():.4f}'})
            
            avg_train_loss = total_train_loss / len(train_loader)
            
            # Validation phase
            val_loss, val_metrics = self.evaluate_model(val_loader)
            
            # Store history
            history['train_loss'].append(avg_train_loss)
            history['val_loss'].append(val_loss)
            history['val_accuracy'].append(val_metrics['accuracy'])
            history['val_f1'].append(val_metrics['f1'])
            history['matthews_corr'].append(val_metrics['matthews_corr'])
            
            print(f"\n📊 Epoch {epoch + 1} Results:")
            print(f"   Training Loss: {avg_train_loss:.4f}")
            print(f"   Validation Loss: {val_loss:.4f}")
            print(f"   Validation Accuracy: {val_metrics['accuracy']:.4f}")
            print(f"   Validation F1: {val_metrics['f1']:.4f}")
            print(f"   Matthews Correlation: {val_metrics['matthews_corr']:.4f}")
            
            # Save best model (based on Matthews correlation)
            if val_metrics['matthews_corr'] > best_matthews:
                best_matthews = val_metrics['matthews_corr']
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'matthews_corr': best_matthews,
                    'metrics': val_metrics
                }, 'best_cola_bert.pth')
                print(f" New best model saved! (Matthews: {best_matthews:.4f})")
        
        logger.info(f"Training completed! Best Matthews correlation: {best_matthews:.4f}")
        return history
    
    def evaluate_model(self, val_loader, detailed=False):
        """Evaluate model performance"""
        
        self.model.eval()
        total_loss = 0
        all_predictions = []
        all_labels = []
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Evaluating", leave=False):
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                token_type_ids = batch['token_type_ids'].to(device)
                labels = batch['label'].to(device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    token_type_ids=token_type_ids,
                    labels=labels
                )
                
                loss = outputs.loss
                logits = outputs.logits
                
                total_loss += loss.item()
                
                # Get predictions
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                labels_np = labels.cpu().numpy()
                
                all_predictions.extend(preds)
                all_labels.extend(labels_np)
        
        # Calculate metrics using both PyTorch and sklearn implementations
        avg_loss = total_loss / len(val_loader)
        
        # Convert to tensors for PyTorch metrics
        predictions_tensor = torch.tensor(all_predictions, dtype=torch.long)
        labels_tensor = torch.tensor(all_labels, dtype=torch.long)
        
        if TORCHMETRICS_AVAILABLE and self.mcc_metric is not None:
            # Use PyTorch-native metrics
            predictions_tensor = predictions_tensor.to(device)
            labels_tensor = labels_tensor.to(device)
            
            # Reset metrics (important for proper calculation)
            self.mcc_metric.reset()
            self.accuracy_metric.reset()
            self.f1_metric.reset()
            
            # Calculate PyTorch metrics
            mcc_pytorch = self.mcc_metric(predictions_tensor, labels_tensor).item()
            accuracy_pytorch = self.accuracy_metric(predictions_tensor, labels_tensor).item()
            f1_pytorch = self.f1_metric(predictions_tensor, labels_tensor).item()
            
            # Use PyTorch metrics as primary
            accuracy = accuracy_pytorch
            f1 = f1_pytorch
            matthews_corr = mcc_pytorch
            
            metrics_source = "PyTorch (torchmetrics)"
        else:
            # Fall back to scikit-learn metrics
            accuracy = accuracy_score(all_labels, all_predictions)
            f1 = f1_score(all_labels, all_predictions)
            matthews_corr = matthews_corrcoef(all_labels, all_predictions)
            
            metrics_source = "scikit-learn"
        
        metrics = {
            'accuracy': accuracy,
            'f1': f1,
            'matthews_corr': matthews_corr,
            'source': metrics_source
        }
        
        if detailed:
            print(f"\n Detailed Evaluation Results:")
            print(f"   Validation Loss: {avg_loss:.4f}")
            print(f"   Metrics Source: {metrics_source}")
            print(f"   Accuracy: {accuracy:.4f}")
            print(f"   F1-Score: {f1:.4f}")
            print(f"   Matthews Correlation: {matthews_corr:.4f}")
            
            # Show comparison between PyTorch and sklearn if both available
            if TORCHMETRICS_AVAILABLE and self.mcc_metric is not None:
                sklearn_acc = accuracy_score(all_labels, all_predictions)
                sklearn_f1 = f1_score(all_labels, all_predictions)
                sklearn_mcc = matthews_corrcoef(all_labels, all_predictions)
                
                print(f"\n Metrics Comparison:")
                print(f"   PyTorch vs sklearn:")
                print(f"     Accuracy:  {accuracy:.6f} vs {sklearn_acc:.6f}")
                print(f"     F1-Score:  {f1:.6f} vs {sklearn_f1:.6f}")
                print(f"     MCC:       {matthews_corr:.6f} vs {sklearn_mcc:.6f}")
            
            # Classification report
            print("\n📋 Classification Report:")
            target_names = ['Unacceptable', 'Acceptable']
            print(classification_report(all_labels, all_predictions, target_names=target_names))
            
            # Confusion matrix
            cm = confusion_matrix(all_labels, all_predictions)
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                       xticklabels=target_names, yticklabels=target_names)
            plt.title('CoLA Classification - Confusion Matrix')
            plt.ylabel('Actual')
            plt.xlabel('Predicted')
            plt.tight_layout()
            plt.savefig('cola_confusion_matrix.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        return avg_loss, metrics
    
    def predict_sentence(self, sentence, return_confidence=True):
        """Predict linguistic acceptability of a sentence"""
        
        self.model.eval()
        
        # Tokenize
        encoding = self.tokenizer(
            sentence,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        token_type_ids = encoding['token_type_ids'].to(device)
        
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids
            )
            
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            prediction = torch.argmax(logits, dim=1).item()
            confidence = probabilities.max().item()
        
        result = {
            'sentence': sentence,
            'prediction': prediction,
            'label': 'Acceptable' if prediction == 1 else 'Unacceptable',
            'confidence': confidence,
            'probabilities': {
                'unacceptable': probabilities[0][0].item(),
                'acceptable': probabilities[0][1].item()
            }
        }
        
        return result
    
    def test_linguistic_examples(self):
        """Test model on various linguistic phenomena"""
        
        test_cases = [
            # Grammatically correct
            ("The cat is sleeping on the mat.", 1),
            ("She gave him a book.", 1),
            ("The students are studying for their exams.", 1),
            
            # Grammatically incorrect - word order
            ("Sleeping cat the on mat is the.", 0),
            ("Him she gave a book.", 0),
            ("Are students the studying for exams their.", 0),
            
            # Grammatically incorrect - agreement
            ("The cat are sleeping.", 0),
            ("She give him a book.", 0),
            ("The student are studying.", 0),
            
            # Complex but correct
            ("The book that the student read was interesting.", 1),
            ("Having finished the assignment, she went home.", 1),
            
            # Complex and incorrect
            ("The book that the student read were interesting.", 0),
            ("Having finished the assignment, the assignment was submitted.", 0)
        ]
        
        print(f"\n Testing Linguistic Phenomena:")
        print("=" * 80)
        
        correct_predictions = 0
        
        for i, (sentence, expected) in enumerate(test_cases):
            result = self.predict_sentence(sentence)
            prediction = result['prediction']
            confidence = result['confidence']
            
            status = "✅" if prediction == expected else "❌"
            print(f"{status} {sentence}")
            print(f"    Predicted: {result['label']} (confidence: {confidence:.3f})")
            print(f"    Expected: {'Acceptable' if expected == 1 else 'Unacceptable'}")
            print()
            
            if prediction == expected:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(test_cases)
        print(f"📊 Test Set Accuracy: {accuracy:.2f} ({correct_predictions}/{len(test_cases)})")


def plot_training_history(history):
    """Plot training progress"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    epochs = range(1, len(history['train_loss']) + 1)
    
    # Loss plot
    ax1.plot(epochs, history['train_loss'], 'b-', label='Training Loss', marker='o')
    ax1.plot(epochs, history['val_loss'], 'r-', label='Validation Loss', marker='s')
    ax1.set_title('Training and Validation Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Accuracy plot
    ax2.plot(epochs, history['val_accuracy'], 'g-', label='Validation Accuracy', marker='o')
    ax2.set_title('Validation Accuracy')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # F1 Score plot
    ax3.plot(epochs, history['val_f1'], 'orange', label='Validation F1', marker='s')
    ax3.set_title('Validation F1 Score')
    ax3.set_xlabel('Epoch')
    ax3.set_ylabel('F1 Score')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Matthews Correlation plot (important for CoLA)
    ax4.plot(epochs, history['matthews_corr'], 'purple', label='Matthews Correlation', marker='d')
    ax4.set_title('Matthews Correlation Coefficient')
    ax4.set_xlabel('Epoch')
    ax4.set_ylabel('Matthews Correlation')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('cola_training_history.png', dpi=300, bbox_inches='tight')
    plt.show()


def main():
    parser = argparse.ArgumentParser(description='CoLA BERT Transfer Learning')
    parser.add_argument('--model-name', default='bert-base-uncased', help='BERT model name')
    parser.add_argument('--max-length', type=int, default=128, help='Maximum sequence length')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--epochs', type=int, default=4, help='Number of epochs')
    parser.add_argument('--learning-rate', type=float, default=2e-5, help='Learning rate')
    parser.add_argument('--max-samples', type=int, help='Limit dataset size (for testing)')
    parser.add_argument('--evaluate-only', action='store_true', help='Only evaluate existing model')
    parser.add_argument('--model-path', default='best_cola_bert.pth', help='Model path')
    parser.add_argument('--test-sentence', type=str, help='Test sentence for acceptability')
    parser.add_argument('--analyze-lengths', action='store_true', help='Analyze sentence lengths')
    
    args = parser.parse_args()
    
    print(" CoLA BERT Transfer Learning")
    print("Corpus of Linguistic Acceptability - GLUE Benchmark")
    print("=" * 60)
    
    # Initialize classifier
    classifier = CoLABERTClassifier(args.model_name, args.max_length)
    
    # Load dataset
    train_sentences, train_labels, val_sentences, val_labels = classifier.load_cola_dataset(args.max_samples)
    
    # Analyze sentence lengths if requested
    if args.analyze_lengths:
        recommended_length = classifier.analyze_sentence_lengths(train_sentences + val_sentences)
        print(f"\n Recommended max_length: {recommended_length}")
    
    if args.evaluate_only:
        # Load and evaluate existing model
        if os.path.exists(args.model_path):
            checkpoint = torch.load(args.model_path, map_location=device)
            classifier.model.load_state_dict(checkpoint['model_state_dict'])
            logger.info(f"Model loaded from {args.model_path}")
            
            # Create validation loader
            _, val_loader = classifier.create_data_loaders(
                train_sentences, train_labels, val_sentences, val_labels, args.batch_size
            )
            
            # Evaluate
            classifier.evaluate_model(val_loader, detailed=True)
            
            # Test linguistic examples
            classifier.test_linguistic_examples()
        else:
            logger.error(f"Model file not found: {args.model_path}")
            return
    else:
        # Train model
        train_loader, val_loader = classifier.create_data_loaders(
            train_sentences, train_labels, val_sentences, val_labels, args.batch_size
        )
        
        # Train
        history = classifier.train_model(train_loader, val_loader, args.epochs, args.learning_rate)
        
        # Plot results
        plot_training_history(history)
        
        # Final evaluation
        classifier.evaluate_model(val_loader, detailed=True)
        
        # Test linguistic examples
        classifier.test_linguistic_examples()
    
    # Test custom sentence if provided
    if args.test_sentence:
        print(f"\n Testing Custom Sentence:")
        print(f"Input: '{args.test_sentence}'")
        
        result = classifier.predict_sentence(args.test_sentence)
        print(f"Prediction: {result['label']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Probabilities:")
        print(f"  Unacceptable: {result['probabilities']['unacceptable']:.3f}")
        print(f"  Acceptable: {result['probabilities']['acceptable']:.3f}")
    
    print("\n CoLA BERT Transfer Learning Complete!")
    print(" References:")
    print("   - CoLA: http://nyu-mll.github.io/CoLA/")
    print("   - GLUE: https://gluebenchmark.com/")
    print("   - BERT: Devlin et al. (2018)")


if __name__ == '__main__':
    main()
