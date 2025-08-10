#!/usr/bin/env python3
"""
PyTorch Transformer Training Pipeline

This script provides a comprehensive training pipeline for transformer models including:
- BERT for text classification
- Vision Transformer (ViT) for image classification 
- GPT-style models for text generation
- Custom transformer architectures

Features:
- Multi-dataset support (CoLA, IMDB, CIFAR-10, MNIST)
- Multi-head attention visualization
- Feature extraction and analysis
- Comprehensive metrics and logging
- Checkpointing and model saving
- CLI interface for easy experimentation
"""

import argparse
import logging
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    import transformers
    from transformers import (
        AutoTokenizer, AutoModel, AutoConfig,
        BertModel, BertTokenizer, BertConfig,
        GPT2Model, GPT2Tokenizer, GPT2Config
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    warnings.warn("Transformers library not available. Some features will be limited.")

try:
    from torchmetrics import Accuracy, F1Score, MatthewsCorrCoef
    TORCHMETRICS_AVAILABLE = True
except ImportError:
    TORCHMETRICS_AVAILABLE = False
    warnings.warn("TorchMetrics not available. Using custom metrics.")

# Local imports
from models.transformers import create_transformer_model
from utils.data_loaders import (
    get_cola_loaders, get_imdb_loaders, get_cifar10_loaders, 
    get_mnist_loaders, get_dummy_text_loaders, get_dummy_image_loaders
)
from utils.metrics import calculate_accuracy, calculate_f1_score
from utils.visualization import plot_attention_weights, plot_training_curves, plot_features

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransformerTrainer:
    """Comprehensive transformer training class supporting multiple architectures and tasks."""
    
    def __init__(self, config: Dict):
        """
        Initialize the transformer trainer.
        
        Args:
            config: Configuration dictionary with training parameters
        """
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Initialize model, data, and training components
        self.model = None
        self.tokenizer = None
        self.train_loader = None
        self.val_loader = None
        self.test_loader = None
        self.optimizer = None
        self.scheduler = None
        self.criterion = None
        
        # Metrics
        if TORCHMETRICS_AVAILABLE:
            self.accuracy_metric = Accuracy(task='multiclass', num_classes=config.get('num_classes', 2))
            self.f1_metric = F1Score(task='multiclass', num_classes=config.get('num_classes', 2))
            if config.get('num_classes', 2) == 2:
                self.mcc_metric = MatthewsCorrCoef(task='binary')
            else:
                self.mcc_metric = MatthewsCorrCoef(task='multiclass', num_classes=config.get('num_classes', 2))
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
        self.attention_weights = []
        
        self.setup_model_and_data()
    
    def setup_model_and_data(self):
        """Setup model architecture and data loaders."""
        try:
            # Setup data loaders
            self.setup_data_loaders()
            
            # Setup model
            self.setup_model()
            
            # Setup training components
            self.setup_training_components()
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            # Fallback to minimal setup
            self.setup_fallback()
    
    def setup_data_loaders(self):
        """Setup data loaders based on dataset and task type."""
        dataset = self.config.get('dataset', 'cola')
        batch_size = self.config.get('batch_size', 16)
        test_mode = self.config.get('test_mode', False)
        
        try:
            if dataset == 'cola':
                self.train_loader, self.val_loader, self.test_loader = get_cola_loaders(
                    batch_size=batch_size, test_mode=test_mode
                )
                self.config['task_type'] = 'text_classification'
                self.config['num_classes'] = 2
                
            elif dataset == 'imdb':
                self.train_loader, self.val_loader, self.test_loader = get_imdb_loaders(
                    batch_size=batch_size, test_mode=test_mode
                )
                self.config['task_type'] = 'text_classification'
                self.config['num_classes'] = 2
                
            elif dataset == 'cifar10':
                self.train_loader, self.val_loader, self.test_loader = get_cifar10_loaders(
                    batch_size=batch_size, test_mode=test_mode
                )
                self.config['task_type'] = 'image_classification'
                self.config['num_classes'] = 10
                
            elif dataset == 'mnist':
                self.train_loader, self.val_loader, self.test_loader = get_mnist_loaders(
                    batch_size=batch_size, test_mode=test_mode
                )
                self.config['task_type'] = 'image_classification'
                self.config['num_classes'] = 10
                
            else:
                raise ValueError(f"Unsupported dataset: {dataset}")
                
            logger.info(f"Loaded {dataset} dataset with {len(self.train_loader)} training batches")
            
        except Exception as e:
            logger.warning(f"Failed to load {dataset} dataset: {e}")
            self.setup_fallback_data()
    
    def setup_fallback_data(self):
        """Setup fallback dummy data loaders."""
        task_type = self.config.get('task_type', 'text_classification')
        batch_size = self.config.get('batch_size', 16)
        
        if task_type == 'text_classification':
            self.train_loader, self.val_loader, self.test_loader = get_dummy_text_loaders(batch_size)
            self.config['num_classes'] = 2
        else:
            self.train_loader, self.val_loader, self.test_loader = get_dummy_image_loaders(batch_size)
            self.config['num_classes'] = 10
        
        logger.info("Using fallback dummy data loaders")
    
    def setup_model(self):
        """Setup the transformer model."""
        model_name = self.config.get('model_name', 'bert-base-uncased')
        task_type = self.config.get('task_type', 'text_classification')
        num_classes = self.config.get('num_classes', 2)
        
        try:
            self.model = create_transformer_model(
                model_type=model_name,
                task_type=task_type,
                num_classes=num_classes,
                pretrained=self.config.get('pretrained', True)
            )
            
            # Setup tokenizer if available and needed
            if TRANSFORMERS_AVAILABLE and task_type == 'text_classification':
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    logger.info(f"Loaded tokenizer for {model_name}")
                except Exception as e:
                    logger.warning(f"Could not load tokenizer: {e}")
            
            self.model.to(self.device)
            logger.info(f"Model {model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            self.setup_fallback_model()
    
    def setup_fallback_model(self):
        """Setup fallback transformer model."""
        task_type = self.config.get('task_type', 'text_classification')
        num_classes = self.config.get('num_classes', 2)
        
        # Create a simple transformer-like model
        if task_type == 'text_classification':
            self.model = nn.Sequential(
                nn.Embedding(1000, 512),  # Simple embedding
                nn.TransformerEncoder(
                    nn.TransformerEncoderLayer(d_model=512, nhead=8, batch_first=True),
                    num_layers=2
                ),
                nn.AdaptiveAvgPool1d(1),
                nn.Flatten(),
                nn.Linear(512, num_classes)
            )
        else:  # image classification
            self.model = nn.Sequential(
                nn.Conv2d(3, 64, 3, padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d(8),
                nn.Flatten(),
                nn.Linear(64*8*8, 512),
                nn.ReLU(),
                nn.Linear(512, num_classes)
            )
        
        self.model.to(self.device)
        logger.info("Using fallback transformer model")
    
    def setup_training_components(self):
        """Setup optimizer, scheduler, and loss function."""
        # Optimizer
        lr = self.config.get('learning_rate', 2e-5)
        weight_decay = self.config.get('weight_decay', 0.01)
        
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=lr,
            weight_decay=weight_decay
        )
        
        # Scheduler
        total_steps = len(self.train_loader) * self.config.get('epochs', 3)
        warmup_steps = int(0.1 * total_steps)
        
        self.scheduler = optim.lr_scheduler.LinearLR(
            self.optimizer,
            start_factor=0.1,
            total_iters=warmup_steps
        )
        
        # Loss function
        num_classes = self.config.get('num_classes', 2)
        if num_classes == 2:
            self.criterion = nn.BCEWithLogitsLoss()
        else:
            self.criterion = nn.CrossEntropyLoss()
    
    def setup_fallback(self):
        """Setup minimal fallback configuration."""
        logger.info("Setting up fallback configuration")
        
        # Fallback data
        self.setup_fallback_data()
        
        # Fallback model
        self.setup_fallback_model()
        
        # Fallback training components
        self.setup_training_components()
    
    def train_epoch(self) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        total_correct = 0
        total_samples = 0
        
        for batch_idx, batch in enumerate(self.train_loader):
            try:
                # Handle different batch formats
                if isinstance(batch, dict):
                    inputs = batch.get('input_ids', batch.get('data'))
                    targets = batch.get('labels', batch.get('target'))
                elif len(batch) == 2:
                    inputs, targets = batch
                else:
                    inputs, targets = batch[0], batch[1]
                
                # Move to device
                if isinstance(inputs, torch.Tensor):
                    inputs = inputs.to(self.device)
                if isinstance(targets, torch.Tensor):
                    targets = targets.to(self.device)
                
                # Forward pass
                self.optimizer.zero_grad()
                
                outputs = self.model(inputs)
                if isinstance(outputs, tuple):
                    outputs = outputs[0]  # Take logits if tuple
                
                # Calculate loss
                if self.config.get('num_classes', 2) == 2:
                    targets = targets.float()
                    if len(targets.shape) == 1:
                        targets = targets.unsqueeze(-1)
                    loss = self.criterion(outputs, targets)
                else:
                    loss = self.criterion(outputs, targets.long())
                
                # Backward pass
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                self.optimizer.step()
                if self.scheduler:
                    self.scheduler.step()
                
                # Statistics
                total_loss += loss.item()
                if self.config.get('num_classes', 2) == 2:
                    predicted = (torch.sigmoid(outputs) > 0.5).float()
                    total_correct += (predicted == targets).sum().item()
                else:
                    _, predicted = torch.max(outputs.data, 1)
                    total_correct += (predicted == targets).sum().item()
                
                total_samples += targets.size(0)
                
                # Log progress
                if batch_idx % 10 == 0:
                    logger.info(f"Batch {batch_idx}/{len(self.train_loader)}, "
                              f"Loss: {loss.item():.4f}")
                
                # Test mode - only run a few batches
                if self.config.get('test_mode', False) and batch_idx >= 2:
                    break
                    
            except Exception as e:
                logger.error(f"Error in training batch {batch_idx}: {e}")
                continue
        
        avg_loss = total_loss / max(len(self.train_loader), 1)
        accuracy = total_correct / max(total_samples, 1) * 100
        
        return {'loss': avg_loss, 'accuracy': accuracy}
    
    def validate_epoch(self) -> Dict[str, float]:
        """Validate for one epoch."""
        self.model.eval()
        total_loss = 0.0
        total_correct = 0
        total_samples = 0
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for batch_idx, batch in enumerate(self.val_loader):
                try:
                    # Handle different batch formats
                    if isinstance(batch, dict):
                        inputs = batch.get('input_ids', batch.get('data'))
                        targets = batch.get('labels', batch.get('target'))
                    elif len(batch) == 2:
                        inputs, targets = batch
                    else:
                        inputs, targets = batch[0], batch[1]
                    
                    # Move to device
                    if isinstance(inputs, torch.Tensor):
                        inputs = inputs.to(self.device)
                    if isinstance(targets, torch.Tensor):
                        targets = targets.to(self.device)
                    
                    # Forward pass
                    outputs = self.model(inputs)
                    if isinstance(outputs, tuple):
                        outputs = outputs[0]  # Take logits if tuple
                    
                    # Calculate loss
                    if self.config.get('num_classes', 2) == 2:
                        targets_loss = targets.float()
                        if len(targets_loss.shape) == 1:
                            targets_loss = targets_loss.unsqueeze(-1)
                        loss = self.criterion(outputs, targets_loss)
                    else:
                        loss = self.criterion(outputs, targets.long())
                    
                    total_loss += loss.item()
                    
                    # Predictions
                    if self.config.get('num_classes', 2) == 2:
                        predicted = (torch.sigmoid(outputs) > 0.5).float()
                        total_correct += (predicted == targets_loss).sum().item()
                    else:
                        _, predicted = torch.max(outputs.data, 1)
                        total_correct += (predicted == targets).sum().item()
                    
                    total_samples += targets.size(0)
                    
                    # Store for metrics
                    if self.config.get('num_classes', 2) == 2:
                        all_predictions.extend(predicted.cpu().numpy().flatten())
                        all_targets.extend(targets.cpu().numpy().flatten())
                    else:
                        all_predictions.extend(predicted.cpu().numpy())
                        all_targets.extend(targets.cpu().numpy())
                    
                    # Test mode - only run a few batches
                    if self.config.get('test_mode', False) and batch_idx >= 2:
                        break
                        
                except Exception as e:
                    logger.error(f"Error in validation batch {batch_idx}: {e}")
                    continue
        
        avg_loss = total_loss / max(len(self.val_loader), 1)
        accuracy = total_correct / max(total_samples, 1) * 100
        
        # Calculate additional metrics
        metrics = {'loss': avg_loss, 'accuracy': accuracy}
        
        if len(all_predictions) > 0 and len(all_targets) > 0:
            try:
                all_predictions = np.array(all_predictions)
                all_targets = np.array(all_targets)
                
                # F1 Score
                f1 = calculate_f1_score(all_predictions, all_targets)
                metrics['f1_score'] = f1
                
                # MCC if binary classification
                if self.config.get('num_classes', 2) == 2:
                    if TORCHMETRICS_AVAILABLE:
                        mcc = self.mcc_metric(torch.tensor(all_predictions), torch.tensor(all_targets))
                        metrics['mcc'] = mcc.item()
                
            except Exception as e:
                logger.warning(f"Could not calculate additional metrics: {e}")
        
        return metrics
    
    def extract_attention_weights(self) -> Optional[torch.Tensor]:
        """Extract attention weights from the model if available."""
        try:
            self.model.eval()
            with torch.no_grad():
                # Get a sample batch
                batch = next(iter(self.val_loader))
                if isinstance(batch, dict):
                    inputs = batch.get('input_ids', batch.get('data'))
                elif len(batch) == 2:
                    inputs, _ = batch
                else:
                    inputs = batch[0]
                
                if isinstance(inputs, torch.Tensor):
                    inputs = inputs.to(self.device)
                    inputs = inputs[:1]  # Take only first sample
                
                # Forward pass with attention
                if hasattr(self.model, 'bert'):
                    outputs = self.model.bert(inputs, output_attentions=True)
                    attention_weights = outputs.attentions[-1]  # Last layer
                elif hasattr(self.model, 'transformer'):
                    # For GPT-style models
                    outputs = self.model.transformer(inputs, output_attentions=True)
                    attention_weights = outputs.attentions[-1]
                else:
                    return None
                
                return attention_weights
                
        except Exception as e:
            logger.warning(f"Could not extract attention weights: {e}")
            return None
    
    def save_checkpoint(self, epoch: int, metrics: Dict[str, float], checkpoint_dir: str):
        """Save training checkpoint."""
        try:
            os.makedirs(checkpoint_dir, exist_ok=True)
            
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'config': self.config,
                'metrics': metrics,
                'train_losses': self.train_losses,
                'val_losses': self.val_losses,
                'train_accuracies': self.train_accuracies,
                'val_accuracies': self.val_accuracies
            }
            
            if self.scheduler:
                checkpoint['scheduler_state_dict'] = self.scheduler.state_dict()
            
            checkpoint_path = os.path.join(checkpoint_dir, f'transformer_epoch_{epoch}.pt')
            torch.save(checkpoint, checkpoint_path)
            
            # Save best model
            if not hasattr(self, 'best_val_acc') or metrics.get('accuracy', 0) > self.best_val_acc:
                self.best_val_acc = metrics.get('accuracy', 0)
                best_path = os.path.join(checkpoint_dir, 'transformer_best.pt')
                torch.save(checkpoint, best_path)
                logger.info(f"Saved new best model with accuracy: {self.best_val_acc:.2f}%")
            
            logger.info(f"Checkpoint saved: {checkpoint_path}")
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
    
    def train(self) -> Dict[str, List[float]]:
        """Main training loop."""
        epochs = self.config.get('epochs', 3)
        checkpoint_dir = self.config.get('checkpoint_dir', './checkpoints/transformer')
        save_interval = self.config.get('save_interval', 1)
        
        logger.info(f"Starting transformer training for {epochs} epochs")
        logger.info(f"Device: {self.device}")
        logger.info(f"Model: {self.config.get('model_name', 'fallback')}")
        logger.info(f"Dataset: {self.config.get('dataset', 'fallback')}")
        
        for epoch in range(epochs):
            epoch_start_time = time.time()
            
            logger.info(f"\nEpoch {epoch+1}/{epochs}")
            logger.info("-" * 50)
            
            # Training phase
            train_metrics = self.train_epoch()
            self.train_losses.append(train_metrics['loss'])
            self.train_accuracies.append(train_metrics['accuracy'])
            
            # Validation phase
            val_metrics = self.validate_epoch()
            self.val_losses.append(val_metrics['loss'])
            self.val_accuracies.append(val_metrics['accuracy'])
            
            epoch_time = time.time() - epoch_start_time
            
            # Log epoch results
            logger.info(f"Train Loss: {train_metrics['loss']:.4f}, "
                       f"Train Acc: {train_metrics['accuracy']:.2f}%")
            logger.info(f"Val Loss: {val_metrics['loss']:.4f}, "
                       f"Val Acc: {val_metrics['accuracy']:.2f}%")
            
            if 'f1_score' in val_metrics:
                logger.info(f"Val F1: {val_metrics['f1_score']:.4f}")
            if 'mcc' in val_metrics:
                logger.info(f"Val MCC: {val_metrics['mcc']:.4f}")
            
            logger.info(f"Epoch Time: {epoch_time:.2f}s")
            
            # Extract attention weights
            if epoch == epochs - 1:  # Last epoch
                attention_weights = self.extract_attention_weights()
                if attention_weights is not None:
                    self.attention_weights.append(attention_weights)
            
            # Save checkpoint
            if (epoch + 1) % save_interval == 0:
                self.save_checkpoint(epoch + 1, val_metrics, checkpoint_dir)
        
        logger.info("\nTraining completed!")
        
        # Create visualizations
        self.create_visualizations(checkpoint_dir)
        
        # Extract and save features
        self.extract_features(checkpoint_dir)
        
        return {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_accuracies': self.train_accuracies,
            'val_accuracies': self.val_accuracies
        }
    
    def create_visualizations(self, save_dir: str):
        """Create and save training visualizations."""
        try:
            # Training curves
            plot_training_curves(
                self.train_losses, self.val_losses,
                self.train_accuracies, self.val_accuracies,
                save_path=os.path.join(save_dir, 'transformer_training_curves.png')
            )
            
            # Attention weights visualization
            if self.attention_weights:
                plot_attention_weights(
                    self.attention_weights[-1],
                    save_path=os.path.join(save_dir, 'transformer_attention_weights.png')
                )
            
            logger.info("Visualizations saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to create visualizations: {e}")
    
    def extract_features(self, save_dir: str):
        """Extract and save transformer features."""
        try:
            self.model.eval()
            features_list = []
            labels_list = []
            
            with torch.no_grad():
                for batch_idx, batch in enumerate(self.val_loader):
                    if isinstance(batch, dict):
                        inputs = batch.get('input_ids', batch.get('data'))
                        targets = batch.get('labels', batch.get('target'))
                    elif len(batch) == 2:
                        inputs, targets = batch
                    else:
                        inputs, targets = batch[0], batch[1]
                    
                    if isinstance(inputs, torch.Tensor):
                        inputs = inputs.to(self.device)
                    
                    # Extract features (before final classification layer)
                    if hasattr(self.model, 'bert'):
                        features = self.model.bert(inputs).last_hidden_state.mean(dim=1)
                    elif hasattr(self.model, 'transformer'):
                        features = self.model.transformer(inputs).last_hidden_state.mean(dim=1)
                    else:
                        # For fallback models, get intermediate features
                        features = inputs.view(inputs.size(0), -1)
                    
                    features_list.append(features.cpu().numpy())
                    labels_list.append(targets.cpu().numpy() if isinstance(targets, torch.Tensor) else targets)
                    
                    if batch_idx >= 10:  # Limit for memory
                        break
            
            if features_list:
                features = np.vstack(features_list)
                labels = np.hstack(labels_list)
                
                # Save features
                np.save(os.path.join(save_dir, 'transformer_features.npy'), features)
                np.save(os.path.join(save_dir, 'transformer_labels.npy'), labels)
                
                # Plot features
                plot_features(
                    features, labels,
                    save_path=os.path.join(save_dir, 'transformer_features.png'),
                    method='pca'
                )
                
                logger.info(f"Extracted features shape: {features.shape}")
            
        except Exception as e:
            logger.error(f"Failed to extract features: {e}")


def create_config_from_args(args) -> Dict:
    """Create configuration dictionary from command line arguments."""
    config = {
        'model_name': args.model,
        'dataset': args.dataset,
        'task_type': 'text_classification' if args.dataset in ['cola', 'imdb'] else 'image_classification',
        'epochs': args.epochs,
        'batch_size': args.batch_size,
        'learning_rate': args.learning_rate,
        'weight_decay': args.weight_decay,
        'checkpoint_dir': args.checkpoint_dir,
        'save_interval': args.save_interval,
        'test_mode': args.test_mode,
        'pretrained': args.pretrained,
        'num_classes': 2 if args.dataset in ['cola', 'imdb'] else 10
    }
    return config


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description='PyTorch Transformer Training')
    
    # Model arguments
    parser.add_argument('--model', type=str, default='bert-base-uncased',
                        help='Transformer model name')
    parser.add_argument('--pretrained', action='store_true', default=True,
                        help='Use pretrained weights')
    
    # Data arguments
    parser.add_argument('--dataset', type=str, default='cola',
                        choices=['cola', 'imdb', 'cifar10', 'mnist'],
                        help='Dataset to use')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='Batch size for training')
    
    # Training arguments
    parser.add_argument('--epochs', type=int, default=3,
                        help='Number of epochs to train')
    parser.add_argument('--learning-rate', type=float, default=2e-5,
                        help='Learning rate')
    parser.add_argument('--weight-decay', type=float, default=0.01,
                        help='Weight decay')
    
    # Save/load arguments
    parser.add_argument('--checkpoint-dir', type=str, 
                        default='./checkpoints/transformer',
                        help='Directory to save checkpoints')
    parser.add_argument('--save-interval', type=int, default=1,
                        help='Save checkpoint every N epochs')
    
    # Test mode
    parser.add_argument('--test-mode', action='store_true',
                        help='Run in test mode with limited data')
    
    args = parser.parse_args()
    
    # Create configuration
    config = create_config_from_args(args)
    
    # Print configuration
    logger.info("Transformer Training Configuration:")
    for key, value in config.items():
        logger.info(f"  {key}: {value}")
    
    try:
        # Create trainer and start training
        trainer = TransformerTrainer(config)
        history = trainer.train()
        
        logger.info("\nTraining Summary:")
        logger.info(f"Final Train Loss: {history['train_losses'][-1]:.4f}")
        logger.info(f"Final Val Loss: {history['val_losses'][-1]:.4f}")
        logger.info(f"Final Train Acc: {history['train_accuracies'][-1]:.2f}%")
        logger.info(f"Final Val Acc: {history['val_accuracies'][-1]:.2f}%")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
