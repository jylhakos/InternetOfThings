#!/usr/bin/env python3
"""
Enhanced BERT Fine-tuning with Dataset Management Integration
Integrates with the dataset manager and data wrangling tools for complete pipeline
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dataset_manager import DatasetManager, BERTDatasetConfig
from data_wrangling import DataExplorer, DataCleaner
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import BertForSequenceClassification, BertTokenizer, AdamW, get_scheduler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np
import pandas as pd
import time
import argparse
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigurableBERTTrainer:
    """BERT trainer with configurable dataset management"""
    
    def __init__(self, config_file: str = None, dataset_name: str = "custom"):
        """Initialize trainer with configuration"""
        self.config_file = config_file or "config/dataset_config.json"
        self.dataset_name = dataset_name
        
        # Initialize managers
        self.dataset_manager = DatasetManager(self.config_file)
        self.config = self.dataset_manager.config
        
        # Initialize device
        self.device = self._setup_device()
        
        # Training metrics
        self.training_history = []
        
    def _setup_device(self):
        """Setup optimal device for training"""
        if torch.cuda.is_available():
            device = torch.device('cuda')
            logger.info(f"Using GPU: {torch.cuda.get_device_name()}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            device = torch.device('cpu')
            logger.info("Using CPU for training")
        
        return device
    
    def load_and_explore_dataset(self, limit_samples: int = None, explore: bool = True, clean: bool = True):
        """Load dataset with optional exploration and cleaning"""
        logger.info(f"Loading dataset: {self.dataset_name}")
        
        # Load dataset
        df, dataset_config = self.dataset_manager.load_dataset(self.dataset_name, limit_samples)
        self.dataset_config = dataset_config
        
        logger.info(f"Loaded {len(df)} samples")
        
        # Explore data if requested
        if explore:
            logger.info("Starting data exploration...")
            explorer = DataExplorer(df, dataset_config['text_column'], dataset_config['label_column'])
            self.exploration_results = explorer.full_analysis()
        
        # Clean data if requested
        if clean:
            logger.info("Starting data cleaning...")
            cleaner = DataCleaner(df, dataset_config['text_column'], dataset_config['label_column'])
            
            # Apply standard cleaning
            df = cleaner.remove_missing_data()
            df = cleaner.clean_text(
                remove_html=dataset_config.get('preprocessing', {}).get('remove_html', True),
                remove_urls=True,
                remove_emails=True,
                normalize_whitespace=True
            )
            df = cleaner.remove_duplicates()
            
            # Apply length filtering
            preprocessing = dataset_config.get('preprocessing', {})
            if 'min_length' in preprocessing or 'max_length' in preprocessing:
                min_len = preprocessing.get('min_length', 10)
                max_len = preprocessing.get('max_length', 5000)
                df = cleaner.filter_by_length(min_len, max_len)
            
            # Check class balance
            label_counts = df[dataset_config['label_column']].value_counts()
            imbalance_ratio = label_counts.max() / label_counts.min()
            
            if imbalance_ratio > 3.0:
                logger.warning(f"Dataset is imbalanced (ratio: {imbalance_ratio:.1f})")
                balance_method = input("Balance classes? (undersample/oversample/none): ").strip().lower()
                
                if balance_method in ['undersample', 'oversample']:
                    df = cleaner.balance_classes(method=balance_method)
            
            self.cleaning_summary = cleaner.get_cleaning_summary()
            logger.info("Data cleaning completed")
        
        self.raw_data = df
        return df
    
    def prepare_data_for_training(self, df: pd.DataFrame):
        """Prepare data splits and dataloaders"""
        logger.info("Preparing data for training...")
        
        # Split data
        train_df, val_df, test_df = self.dataset_manager.prepare_train_val_test(df, self.dataset_config)
        
        # Initialize tokenizer
        model_name = "bert-base-uncased"  # Could be configurable
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        
        # Get optimal batch size based on device
        if self.device.type == 'cuda':
            batch_size = self.config.config.get('model_configs', {}).get(model_name, {}).get('batch_size_gpu', 16)
            
            # Adjust batch size based on available memory
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            if gpu_memory < 8:
                batch_size = max(4, batch_size // 2)
                logger.info(f"Reduced batch size to {batch_size} due to limited GPU memory")
        else:
            batch_size = self.config.config.get('model_configs', {}).get(model_name, {}).get('batch_size_cpu', 4)
        
        self.batch_size = batch_size
        
        # Create dataloaders
        self.train_dataloader, self.val_dataloader, self.test_dataloader = self.dataset_manager.create_dataloaders(
            train_df, val_df, test_df, self.dataset_config, self.tokenizer, batch_size
        )
        
        # Save processed data
        self.dataset_manager.save_processed_data(train_df, val_df, test_df, self.dataset_name)
        
        logger.info(f"Data preparation complete:")
        logger.info(f"  Train: {len(train_df)} samples, {len(self.train_dataloader)} batches")
        logger.info(f"  Validation: {len(val_df)} samples, {len(self.val_dataloader)} batches")
        logger.info(f"  Test: {len(test_df)} samples, {len(self.test_dataloader)} batches")
        logger.info(f"  Batch size: {batch_size}")
        
        return train_df, val_df, test_df
    
    def initialize_model(self):
        """Initialize BERT model for classification"""
        # Determine number of classes
        if hasattr(self, 'raw_data'):
            num_labels = len(self.raw_data[self.dataset_config['label_column']].unique())
        else:
            num_labels = len(self.dataset_config.get('classes', [0, 1]))
        
        logger.info(f"Initializing BERT model for {num_labels} classes")
        
        # Initialize model
        model_name = "bert-base-uncased"
        self.model = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels,
            output_attentions=False,
            output_hidden_states=False,
        )
        
        self.model.to(self.device)
        
        # Initialize optimizer
        learning_rate = self.config.config.get('model_configs', {}).get(model_name, {}).get('learning_rate', 2e-5)
        self.optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        
        # Initialize scheduler
        num_epochs = self.config.config.get('model_configs', {}).get(model_name, {}).get('num_epochs', 3)
        num_training_steps = len(self.train_dataloader) * num_epochs
        warmup_steps = self.config.config.get('model_configs', {}).get(model_name, {}).get('warmup_steps', 500)
        
        self.scheduler = get_scheduler(
            "linear",
            optimizer=self.optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=num_training_steps
        )
        
        self.num_epochs = num_epochs
        
        logger.info(f"Model initialized:")
        logger.info(f"  Model: {model_name}")
        logger.info(f"  Number of labels: {num_labels}")
        logger.info(f"  Learning rate: {learning_rate}")
        logger.info(f"  Epochs: {num_epochs}")
        logger.info(f"  Warmup steps: {warmup_steps}")
        
        return self.model
    
    def train_model(self):
        """Train the BERT model"""
        logger.info("Starting model training...")
        
        self.model.train()
        
        for epoch in range(self.num_epochs):
            epoch_start_time = time.time()
            total_loss = 0
            total_correct = 0
            total_samples = 0
            
            logger.info(f"Epoch {epoch + 1}/{self.num_epochs}")
            
            for batch_idx, batch in enumerate(self.train_dataloader):
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Zero gradients
                self.optimizer.zero_grad()
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                logits = outputs.logits
                
                # Backward pass
                loss.backward()
                self.optimizer.step()
                self.scheduler.step()
                
                # Calculate accuracy
                predictions = torch.argmax(logits, dim=-1)
                correct = (predictions == labels).sum().item()
                
                total_loss += loss.item()
                total_correct += correct
                total_samples += labels.size(0)
                
                # Print progress
                if (batch_idx + 1) % 10 == 0:
                    avg_loss = total_loss / (batch_idx + 1)
                    accuracy = total_correct / total_samples
                    logger.info(f"  Batch {batch_idx + 1}/{len(self.train_dataloader)} - Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}")
            
            # Epoch summary
            epoch_time = time.time() - epoch_start_time
            avg_loss = total_loss / len(self.train_dataloader)
            accuracy = total_correct / total_samples
            
            # Validation
            val_accuracy, val_loss = self.evaluate_model(self.val_dataloader)
            
            epoch_metrics = {
                'epoch': epoch + 1,
                'train_loss': avg_loss,
                'train_accuracy': accuracy,
                'val_loss': val_loss,
                'val_accuracy': val_accuracy,
                'epoch_time': epoch_time
            }
            
            self.training_history.append(epoch_metrics)
            
            logger.info(f"Epoch {epoch + 1} Summary:")
            logger.info(f"  Train Loss: {avg_loss:.4f}, Train Accuracy: {accuracy:.4f}")
            logger.info(f"  Val Loss: {val_loss:.4f}, Val Accuracy: {val_accuracy:.4f}")
            logger.info(f"  Time: {epoch_time:.1f}s")
        
        logger.info("Training completed!")
    
    def evaluate_model(self, dataloader):
        """Evaluate model on given dataloader"""
        self.model.eval()
        total_loss = 0
        total_correct = 0
        total_samples = 0
        
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                logits = outputs.logits
                
                predictions = torch.argmax(logits, dim=-1)
                correct = (predictions == labels).sum().item()
                
                total_loss += loss.item()
                total_correct += correct
                total_samples += labels.size(0)
        
        avg_loss = total_loss / len(dataloader)
        accuracy = total_correct / total_samples
        
        self.model.train()  # Reset to training mode
        return accuracy, avg_loss
    
    def test_model(self):
        """Comprehensive testing on test set"""
        logger.info("Testing model on test set...")
        
        self.model.eval()
        all_predictions = []
        all_labels = []
        
        with torch.no_grad():
            for batch in self.test_dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                
                predictions = torch.argmax(logits, dim=-1)
                
                all_predictions.extend(predictions.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        # Calculate metrics
        accuracy = accuracy_score(all_labels, all_predictions)
        report = classification_report(all_labels, all_predictions)
        
        logger.info(f"Test Results:")
        logger.info(f"  Accuracy: {accuracy:.4f}")
        logger.info(f"Classification Report:\n{report}")
        
        return accuracy, all_predictions, all_labels, report
    
    def save_model(self, output_dir: str = "models/bert_fine_tuned"):
        """Save the fine-tuned model"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save model and tokenizer
        self.model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        
        # Save training configuration and history
        config_data = {
            'dataset_name': self.dataset_name,
            'dataset_config': self.dataset_config,
            'training_config': {
                'batch_size': self.batch_size,
                'num_epochs': self.num_epochs,
                'learning_rate': self.optimizer.param_groups[0]['lr']
            },
            'training_history': self.training_history,
            'device': str(self.device)
        }
        
        if hasattr(self, 'exploration_results'):
            config_data['exploration_results'] = self.exploration_results
        
        if hasattr(self, 'cleaning_summary'):
            config_data['cleaning_summary'] = self.cleaning_summary
        
        with open(output_path / 'training_config.json', 'w') as f:
            json.dump(config_data, f, indent=2, default=str)
        
        logger.info(f"Model saved to {output_path}")
        return output_path
    
    def predict_text(self, text: str):
        """Make prediction on single text"""
        self.model.eval()
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.config.config['tokenization']['max_length'],
            return_tensors='pt'
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            prediction = torch.argmax(logits, dim=-1).item()
            confidence = probabilities[0][prediction].item()
        
        return prediction, confidence, probabilities.cpu().numpy()[0]

def main():
    """Main training function with command line interface"""
    parser = argparse.ArgumentParser(description="BERT Fine-tuning with Dataset Management")
    parser.add_argument("--dataset", type=str, default="custom", help="Dataset name from config")
    parser.add_argument("--config", type=str, default="config/dataset_config.json", help="Configuration file path")
    parser.add_argument("--limit_samples", type=int, default=None, help="Limit number of samples")
    parser.add_argument("--no_explore", action="store_true", help="Skip data exploration")
    parser.add_argument("--no_clean", action="store_true", help="Skip data cleaning")
    parser.add_argument("--output_dir", type=str, default="models/bert_fine_tuned", help="Output directory for model")
    
    args = parser.parse_args()
    
    try:
        # Initialize trainer
        trainer = ConfigurableBERTTrainer(args.config, args.dataset)
        
        # Load and explore dataset
        df = trainer.load_and_explore_dataset(
            limit_samples=args.limit_samples,
            explore=not args.no_explore,
            clean=not args.no_clean
        )
        
        # Prepare data for training
        train_df, val_df, test_df = trainer.prepare_data_for_training(df)
        
        # Initialize and train model
        trainer.initialize_model()
        trainer.train_model()
        
        # Test model
        test_accuracy, predictions, labels, report = trainer.test_model()
        
        # Save model
        model_path = trainer.save_model(args.output_dir)
        
        logger.info("="*50)
        logger.info("TRAINING COMPLETED SUCCESSFULLY!")
        logger.info(f"Final test accuracy: {test_accuracy:.4f}")
        logger.info(f"Model saved to: {model_path}")
        logger.info("="*50)
        
        # Interactive testing
        print("\n🎯 Interactive Testing (type 'quit' to exit):")
        while True:
            text = input("\nEnter text to classify: ").strip()
            if text.lower() in ['quit', 'exit', 'q']:
                break
            
            if text:
                prediction, confidence, probabilities = trainer.predict_text(text)
                print(f"Prediction: {prediction} (confidence: {confidence:.3f})")
                print(f"All probabilities: {probabilities}")
    
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    main()
