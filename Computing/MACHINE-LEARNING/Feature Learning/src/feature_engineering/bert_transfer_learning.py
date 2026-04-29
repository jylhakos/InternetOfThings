#!/usr/bin/env python3
"""
Transfer Learning for BERT
===================================

An implementation of transfer learning with BERT for text classification for fine-tuning pre-trained BERT models on downstream tasks.

This script demonstrates:
- Loading pre-trained BERT models and tokenizers
- Custom dataset preparation with proper tokenization
- A training loop with validation
- Advanced techniques (layer-wise LR, gradient clipping)
- Model evaluation and inference

Usage Examples:
    # Basic BERT fine-tuning
    python bert_transfer_learning.py --task sentiment --epochs 3 --batch-size 16

    # Advanced training with custom learning rates
    python bert_transfer_learning.py --task classification --layerwise-lr --epochs 5

    # Evaluate only (requires pre-trained model)
    python bert_transfer_learning.py --evaluate-only --model-path best_bert_model.pth

Author: Feature Learning Project
License: MIT
Reference: Devlin et al. (2018) - BERT: Pre-training of Deep Bidirectional Transformers
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, random_split
from transformers import (
    BertForSequenceClassification,
    BertTokenizer,
    AdamW,
    get_linear_schedule_with_warmup,
    AutoTokenizer,
    AutoModelForSequenceClassification
)
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

# PyTorch Metrics for native PyTorch implementation
try:
    from torchmetrics import MatthewsCorrCoef, Accuracy, F1Score
    TORCHMETRICS_AVAILABLE = True
    print("TorchMetrics available - using native PyTorch metrics")
except ImportError:
    TORCHMETRICS_AVAILABLE = False
    print("⚠️ TorchMetrics not available - using sklearn fallback")
    print("   Install with: pip install torchmetrics")
from datasets import load_dataset
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
import json
import time
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Using device: {device}")
if torch.cuda.is_available():
    logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")


class BERTDataset(Dataset):
    """
    Custom Dataset class for BERT fine-tuning
    Handles tokenization, special tokens, padding, and attention masks
    """
    
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # BERT tokenization with all required components
        encoding = self.tokenizer(
            text,
            truncation=True,           # Truncate to max_length
            padding='max_length',      # Pad to max_length
            max_length=self.max_length,
            return_tensors='pt',       # Return PyTorch tensors
            add_special_tokens=True,   # Add [CLS] and [SEP] tokens
            return_attention_mask=True # Return attention mask
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }


class BERTTransferLearning:
    """
    Complete BERT Transfer Learning implementation
    """
    
    def __init__(self, model_name='bert-base-uncased', num_labels=2, max_length=512):
        self.model_name = model_name
        self.num_labels = num_labels
        self.max_length = max_length
        
        # Load tokenizer and model
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        )
        self.model.to(device)
        
        logger.info(f"Loaded BERT model: {model_name}")
        logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def create_data_loaders(self, train_texts, train_labels, val_texts, val_labels, batch_size=16):
        """Create training and validation data loaders"""
        
        # Create datasets
        train_dataset = BERTDataset(train_texts, train_labels, self.tokenizer, self.max_length)
        val_dataset = BERTDataset(val_texts, val_labels, self.tokenizer, self.max_length)
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=True
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True
        )
        
        logger.info(f"Training samples: {len(train_dataset)}")
        logger.info(f"Validation samples: {len(val_dataset)}")
        
        return train_loader, val_loader
    
    def setup_optimizer_and_scheduler(self, train_loader, epochs, learning_rate=2e-5, use_layerwise_lr=False):
        """Setup optimizer and learning rate scheduler"""
        
        if use_layerwise_lr:
            # Layer-wise learning rates (advanced technique)
            no_decay = ["bias", "LayerNorm.weight"]
            optimizer_grouped_parameters = [
                {
                    "params": [p for n, p in self.model.bert.embeddings.named_parameters()
                              if not any(nd in n for nd in no_decay)],
                    "weight_decay": 0.01,
                    "lr": learning_rate * 0.5,  # Lower LR for embeddings
                },
                {
                    "params": [p for n, p in self.model.bert.encoder.named_parameters()
                              if not any(nd in n for nd in no_decay)],
                    "weight_decay": 0.01,
                    "lr": learning_rate,  # Standard LR for encoder
                },
                {
                    "params": [p for n, p in self.model.classifier.named_parameters()
                              if not any(nd in n for nd in no_decay)],
                    "weight_decay": 0.01,
                    "lr": learning_rate * 2,  # Higher LR for classification head
                },
            ]
            optimizer = AdamW(optimizer_grouped_parameters, eps=1e-8)
            logger.info("🔧 Using layer-wise learning rates")
        else:
            # Standard optimizer setup
            optimizer = AdamW(
                self.model.parameters(),
                lr=learning_rate,
                eps=1e-8
            )
            logger.info(f"🔧 Using uniform learning rate: {learning_rate}")
        
        # Learning rate scheduler with warmup
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=int(0.1 * total_steps),  # 10% warmup
            num_training_steps=total_steps
        )
        
        logger.info(f"📈 Total training steps: {total_steps}")
        logger.info(f"📈 Warmup steps: {int(0.1 * total_steps)}")
        
        return optimizer, scheduler
    
    def train_model(self, train_loader, val_loader, epochs=3, learning_rate=2e-5, 
                   use_layerwise_lr=False, save_path='best_bert_model.pth'):
        """
        Complete training loop for BERT fine-tuning
        """
        
        # Setup optimizer and scheduler
        optimizer, scheduler = self.setup_optimizer_and_scheduler(
            train_loader, epochs, learning_rate, use_layerwise_lr
        )
        
        # Training tracking
        training_history = {
            'train_loss': [],
            'val_accuracy': [],
            'val_f1': []
        }
        
        best_val_acc = 0
        start_time = time.time()
        
        logger.info(f"Starting training for {epochs} epochs...")
        
        for epoch in range(epochs):
            print(f"\n{'='*60}")
            print(f"Epoch {epoch + 1}/{epochs}")
            print('='*60)
            
            # Training phase
            self.model.train()
            total_train_loss = 0
            train_progress = tqdm(train_loader, desc=f"Training Epoch {epoch+1}")
            
            for batch_idx, batch in enumerate(train_progress):
                # Move batch to device
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['label'].to(device)
                
                # Clear gradients
                optimizer.zero_grad()
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                total_train_loss += loss.item()
                
                # Backward pass
                loss.backward()
                
                # Gradient clipping to prevent exploding gradients
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                
                # Update weights
                optimizer.step()
                scheduler.step()
                
                # Update progress bar
                train_progress.set_postfix({
                    'Loss': f'{loss.item():.4f}',
                    'LR': f'{scheduler.get_last_lr()[0]:.2e}'
                })
            
            avg_train_loss = total_train_loss / len(train_loader)
            training_history['train_loss'].append(avg_train_loss)
            
            # Validation phase
            val_acc, val_f1 = self.evaluate_model(val_loader)
            training_history['val_accuracy'].append(val_acc)
            training_history['val_f1'].append(val_f1)
            
            print(f"\n📊 Epoch {epoch + 1} Results:")
            print(f"   Average Training Loss: {avg_train_loss:.4f}")
            print(f"   Validation Accuracy: {val_acc:.4f}")
            print(f"   Validation F1-Score: {val_f1:.4f}")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'val_accuracy': val_acc,
                    'val_f1': val_f1,
                    'model_config': {
                        'model_name': self.model_name,
                        'num_labels': self.num_labels,
                        'max_length': self.max_length
                    }
                }, save_path)
                print(f" New best model saved! (Acc: {val_acc:.4f})")
        
        total_time = time.time() - start_time
        print(f"\n Training completed in {total_time/60:.2f} minutes")
        print(f" Best validation accuracy: {best_val_acc:.4f}")
        
        return training_history
    
    def evaluate_model(self, val_loader, detailed=False):
        """
        Evaluate model performance on validation set
        """
        self.model.eval()
        predictions = []
        actual_labels = []
        total_loss = 0
        
        eval_progress = tqdm(val_loader, desc="Evaluating", leave=False)
        
        with torch.no_grad():
            for batch in eval_progress:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['label'].to(device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                logits = outputs.logits
                
                total_loss += loss.item()
                
                # Get predictions
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                labels_np = labels.cpu().numpy()
                
                predictions.extend(preds)
                actual_labels.extend(labels_np)
        
        # Calculate metrics
        accuracy = accuracy_score(actual_labels, predictions)
        f1 = f1_score(actual_labels, predictions, average='weighted')
        avg_loss = total_loss / len(val_loader)
        
        if detailed:
            print(f"\n Detailed Evaluation Results:")
            print(f"   Validation Loss: {avg_loss:.4f}")
            print(f"   Accuracy: {accuracy:.4f}")
            print(f"   F1-Score: {f1:.4f}")
            
            # Classification report
            print("\n Classification Report:")
            print(classification_report(actual_labels, predictions))
            
            # Confusion matrix
            cm = confusion_matrix(actual_labels, predictions)
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title('Confusion Matrix')
            plt.ylabel('Actual')
            plt.xlabel('Predicted')
            plt.tight_layout()
            plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
            plt.show()
            
        return accuracy, f1
    
    def predict_text(self, text, return_probabilities=False):
        """
        Make prediction on single text input
        """
        self.model.eval()
        
        # Tokenize input
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            prediction = torch.argmax(logits, dim=1).item()
            confidence = probabilities.max().item()
        
        if return_probabilities:
            return prediction, confidence, probabilities.cpu().numpy()[0]
        else:
            return prediction, confidence
    
    def load_model(self, model_path):
        """Load saved model checkpoint"""
        checkpoint = torch.load(model_path, map_location=device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        logger.info(f" Model loaded from {model_path}")
        
        # Return model info if available
        if 'model_config' in checkpoint:
            return checkpoint['model_config']
        return None


def load_sample_dataset(dataset_name="imdb", num_samples=1000):
    """
    Load sample dataset for demonstration
    """
    logger.info(f"📥 Loading {dataset_name} dataset...")
    
    if dataset_name == "imdb":
        # Load IMDb movie reviews
        dataset = load_dataset("imdb", split=f"train[:{num_samples}]")
        texts = dataset['text']
        labels = dataset['label']  # 0: negative, 1: positive
        num_labels = 2
        
    elif dataset_name == "squad":
        # Load SQuAD for question classification (simplified example)
        dataset = load_dataset("rajpurkar/squad", split=f"train[:{num_samples}]")
        texts = dataset['question']
        # Create dummy binary labels based on question length (demo purposes)
        labels = [1 if len(text.split()) > 10 else 0 for text in texts]
        num_labels = 2
        
    else:
        raise ValueError(f"Unsupported dataset: {dataset_name}")
    
    logger.info(f" Loaded {len(texts)} samples")
    return texts, labels, num_labels


def plot_training_history(history, save_path='training_history.png'):
    """Plot training progress"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Loss plot
    ax1.plot(history['train_loss'], label='Training Loss', marker='o')
    ax1.set_title('Training Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Accuracy and F1 plot
    ax2.plot(history['val_accuracy'], label='Validation Accuracy', marker='o', color='green')
    ax2.plot(history['val_f1'], label='Validation F1-Score', marker='s', color='orange')
    ax2.set_title('Validation Metrics')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Score')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    logger.info(f"Training history saved to {save_path}")


def main():
    parser = argparse.ArgumentParser(description='BERT Transfer Learning')
    parser.add_argument('--dataset', choices=['imdb', 'squad'], default='imdb', 
                       help='Dataset to use for training')
    parser.add_argument('--model-name', default='bert-base-uncased',
                       help='Pre-trained BERT model name')
    parser.add_argument('--max-length', type=int, default=512,
                       help='Maximum sequence length')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size for training')
    parser.add_argument('--epochs', type=int, default=3,
                       help='Number of training epochs')
    parser.add_argument('--learning-rate', type=float, default=2e-5,
                       help='Learning rate')
    parser.add_argument('--num-samples', type=int, default=1000,
                       help='Number of samples to use (for demo)')
    parser.add_argument('--layerwise-lr', action='store_true',
                       help='Use layer-wise learning rates')
    parser.add_argument('--evaluate-only', action='store_true',
                       help='Only evaluate existing model')
    parser.add_argument('--model-path', default='best_bert_model.pth',
                       help='Path to save/load model')
    parser.add_argument('--test-text', type=str,
                       help='Text to test with trained model')
    
    args = parser.parse_args()
    
    print("BERT Transfer Learning")
    print("=" * 50)
    
    # Load dataset
    texts, labels, num_labels = load_sample_dataset(args.dataset, args.num_samples)
    
    # Create train/validation split
    split_idx = int(0.8 * len(texts))
    train_texts, val_texts = texts[:split_idx], texts[split_idx:]
    train_labels, val_labels = labels[:split_idx], labels[split_idx:]
    
    # Initialize BERT model
    bert_model = BERTTransferLearning(
        model_name=args.model_name,
        num_labels=num_labels,
        max_length=args.max_length
    )
    
    if args.evaluate_only:
        # Load and evaluate existing model
        if os.path.exists(args.model_path):
            bert_model.load_model(args.model_path)
            
            # Create validation loader
            _, val_loader = bert_model.create_data_loaders(
                train_texts, train_labels, val_texts, val_labels, args.batch_size
            )
            
            # Evaluate
            print("\n🔍 Evaluating loaded model...")
            bert_model.evaluate_model(val_loader, detailed=True)
        else:
            logger.error(f"Model file not found: {args.model_path}")
            return
    else:
        # Train model
        # Create data loaders
        train_loader, val_loader = bert_model.create_data_loaders(
            train_texts, train_labels, val_texts, val_labels, args.batch_size
        )
        
        # Train model
        history = bert_model.train_model(
            train_loader=train_loader,
            val_loader=val_loader,
            epochs=args.epochs,
            learning_rate=args.learning_rate,
            use_layerwise_lr=args.layerwise_lr,
            save_path=args.model_path
        )
        
        # Plot training history
        plot_training_history(history)
        
        # Final evaluation
        print("\n Final Evaluation:")
        bert_model.evaluate_model(val_loader, detailed=True)
    
    # Test with custom text if provided
    if args.test_text:
        print(f"\n Testing with custom text:")
        print(f"Input: {args.test_text}")
        
        prediction, confidence, probabilities = bert_model.predict_text(
            args.test_text, return_probabilities=True
        )
        
        print(f"Prediction: {prediction}")
        print(f"Confidence: {confidence:.3f}")
        print(f"Probabilities: {probabilities}")
    
    print("\n BERT Transfer Learning Complete!")
    print(" Reference: Devlin et al. (2018) - BERT: Pre-training of Deep Bidirectional Transformers")


if __name__ == '__main__':
    main()
