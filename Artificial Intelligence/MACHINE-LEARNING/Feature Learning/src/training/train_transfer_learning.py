#!/usr/bin/env python3
"""
Training script for Transfer Learning with pre-trained models.
"""

import os
import sys
import argparse
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from typing import Tuple, Dict, List, Optional
import logging
from tqdm import tqdm
import json
from transformers import (
    BertTokenizer, BertForSequenceClassification,
    AutoTokenizer, AutoModel, AutoConfig
)
import torchvision.models as models
from torchmetrics import MatthewsCorrCoef, Accuracy, F1Score

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models.transformer_models import BERTFeatureExtractor, create_transfer_learning_model
from data.data_loaders import (
    get_cola_loaders, get_squad_loaders, get_mnist_loaders, 
    get_fashion_mnist_loaders, get_cifar10_loaders
)
from utils.metrics import calculate_accuracy, plot_training_curves


def setup_logging(log_dir: str = 'logs') -> logging.Logger:
    """Setup logging configuration."""
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'transfer_learning.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


class ImageTransferLearningModel(nn.Module):
    """Transfer learning model for image classification."""
    
    def __init__(self, architecture: str = 'resnet18', num_classes: int = 10, 
                 feature_dim: int = 512, freeze_backbone: bool = True):
        super(ImageTransferLearningModel, self).__init__()
        
        self.architecture = architecture
        self.num_classes = num_classes
        self.feature_dim = feature_dim
        self.freeze_backbone = freeze_backbone
        
        # Load pre-trained backbone
        if architecture == 'resnet18':
            self.backbone = models.resnet18(pretrained=True)
            backbone_dim = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()  # Remove final classification layer
        elif architecture == 'resnet50':
            self.backbone = models.resnet50(pretrained=True)
            backbone_dim = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()
        elif architecture == 'vgg16':
            self.backbone = models.vgg16(pretrained=True)
            backbone_dim = self.backbone.classifier[6].in_features
            self.backbone.classifier[6] = nn.Identity()
        elif architecture == 'efficientnet_b0':
            self.backbone = models.efficientnet_b0(pretrained=True)
            backbone_dim = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Identity()
        else:
            raise ValueError(f"Unsupported architecture: {architecture}")
        
        # Freeze backbone if specified
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        # Feature projection head
        self.feature_projection = nn.Sequential(
            nn.Linear(backbone_dim, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3)
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(feature_dim, feature_dim // 2),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(feature_dim // 2, num_classes)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        # Extract backbone features
        backbone_features = self.backbone(x)
        
        # Project to feature space
        features = self.feature_projection(backbone_features)
        
        # Classification
        outputs = self.classifier(features)
        
        return outputs
    
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract features without classification."""
        with torch.no_grad():
            backbone_features = self.backbone(x)
            features = self.feature_projection(backbone_features)
            return features


class TextTransferLearningModel(nn.Module):
    """Transfer learning model for text classification."""
    
    def __init__(self, model_name: str = 'bert-base-uncased', num_classes: int = 2,
                 feature_dim: int = 768, max_length: int = 512, freeze_backbone: bool = False):
        super(TextTransferLearningModel, self).__init__()
        
        self.model_name = model_name
        self.num_classes = num_classes
        self.feature_dim = feature_dim
        self.max_length = max_length
        self.freeze_backbone = freeze_backbone
        
        # Load pre-trained model and tokenizer
        self.config = AutoConfig.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.backbone = AutoModel.from_pretrained(model_name)
        
        # Freeze backbone if specified
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        # Get backbone hidden size
        backbone_dim = self.config.hidden_size
        
        # Feature projection head
        self.feature_projection = nn.Sequential(
            nn.Linear(backbone_dim, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3)
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(feature_dim, feature_dim // 2),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(feature_dim // 2, num_classes)
        )
    
    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor = None) -> torch.Tensor:
        """Forward pass."""
        # Get backbone outputs
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        
        # Use [CLS] token representation
        pooled_output = outputs.pooler_output if hasattr(outputs, 'pooler_output') else outputs.last_hidden_state[:, 0, :]
        
        # Project to feature space
        features = self.feature_projection(pooled_output)
        
        # Classification
        logits = self.classifier(features)
        
        return logits
    
    def extract_features(self, input_ids: torch.Tensor, attention_mask: torch.Tensor = None) -> torch.Tensor:
        """Extract features without classification."""
        with torch.no_grad():
            outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
            pooled_output = outputs.pooler_output if hasattr(outputs, 'pooler_output') else outputs.last_hidden_state[:, 0, :]
            features = self.feature_projection(pooled_output)
            return features


def train_epoch_image(model: nn.Module, train_loader: DataLoader, criterion: nn.Module,
                     optimizer: optim.Optimizer, device: torch.device, epoch: int) -> Tuple[float, float]:
    """Train model for one epoch on image data."""
    model.train()
    total_loss = 0.0
    correct = 0
    total_samples = 0
    
    progress_bar = tqdm(train_loader, desc=f'Epoch {epoch}')
    
    for batch_idx, (images, labels) in enumerate(progress_bar):
        images, labels = images.to(device), labels.to(device)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Statistics
        total_loss += loss.item()
        predictions = outputs.argmax(dim=1)
        correct += (predictions == labels).sum().item()
        total_samples += labels.size(0)
        
        # Update progress bar
        accuracy = 100.0 * correct / total_samples
        progress_bar.set_postfix({
            'Loss': f'{total_loss / (batch_idx + 1):.4f}',
            'Acc': f'{accuracy:.2f}%'
        })
    
    avg_loss = total_loss / len(train_loader)
    accuracy = 100.0 * correct / total_samples
    
    return avg_loss, accuracy


def train_epoch_text(model: nn.Module, train_loader: DataLoader, criterion: nn.Module,
                    optimizer: optim.Optimizer, device: torch.device, epoch: int) -> Tuple[float, float]:
    """Train model for one epoch on text data."""
    model.train()
    total_loss = 0.0
    correct = 0
    total_samples = 0
    
    progress_bar = tqdm(train_loader, desc=f'Epoch {epoch}')
    
    for batch_idx, batch in enumerate(progress_bar):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        loss = criterion(outputs, labels)
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        
        optimizer.step()
        
        # Statistics
        total_loss += loss.item()
        predictions = outputs.argmax(dim=1)
        correct += (predictions == labels).sum().item()
        total_samples += labels.size(0)
        
        # Update progress bar
        accuracy = 100.0 * correct / total_samples
        progress_bar.set_postfix({
            'Loss': f'{total_loss / (batch_idx + 1):.4f}',
            'Acc': f'{accuracy:.2f}%'
        })
    
    avg_loss = total_loss / len(train_loader)
    accuracy = 100.0 * correct / total_samples
    
    return avg_loss, accuracy


def evaluate_image(model: nn.Module, test_loader: DataLoader, criterion: nn.Module,
                  device: torch.device) -> Tuple[float, float, torch.Tensor, torch.Tensor]:
    """Evaluate model on image test set."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total_samples = 0
    
    all_features = []
    all_labels = []
    all_predictions = []
    
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc='Evaluating'):
            images, labels = images.to(device), labels.to(device)
            
            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Statistics
            total_loss += loss.item()
            predictions = outputs.argmax(dim=1)
            correct += (predictions == labels).sum().item()
            total_samples += labels.size(0)
            
            # Extract features
            features = model.extract_features(images)
            all_features.append(features.cpu())
            all_labels.append(labels.cpu())
            all_predictions.append(predictions.cpu())
    
    avg_loss = total_loss / len(test_loader)
    accuracy = 100.0 * correct / total_samples
    
    # Concatenate results
    features_tensor = torch.cat(all_features, dim=0)
    labels_tensor = torch.cat(all_labels, dim=0)
    predictions_tensor = torch.cat(all_predictions, dim=0)
    
    return avg_loss, accuracy, features_tensor, labels_tensor


def evaluate_text(model: nn.Module, test_loader: DataLoader, criterion: nn.Module,
                 device: torch.device, use_mcc: bool = True) -> Tuple[float, float, float, torch.Tensor, torch.Tensor]:
    """Evaluate model on text test set with MCC calculation."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total_samples = 0
    
    all_features = []
    all_labels = []
    all_predictions = []
    
    # Initialize metrics
    if use_mcc:
        mcc_metric = MatthewsCorrCoef(task="binary").to(device)
        accuracy_metric = Accuracy(task="binary").to(device)
        f1_metric = F1Score(task="binary").to(device)
    
    with torch.no_grad():
        for batch in tqdm(test_loader, desc='Evaluating'):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            # Forward pass
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = criterion(outputs, labels)
            
            # Statistics
            total_loss += loss.item()
            predictions = outputs.argmax(dim=1)
            correct += (predictions == labels).sum().item()
            total_samples += labels.size(0)
            
            # Update metrics
            if use_mcc:
                mcc_metric.update(predictions, labels)
                accuracy_metric.update(predictions, labels)
                f1_metric.update(predictions, labels)
            
            # Extract features
            features = model.extract_features(input_ids=input_ids, attention_mask=attention_mask)
            all_features.append(features.cpu())
            all_labels.append(labels.cpu())
            all_predictions.append(predictions.cpu())
    
    avg_loss = total_loss / len(test_loader)
    accuracy = 100.0 * correct / total_samples
    
    # Calculate MCC
    mcc_score = 0.0
    if use_mcc:
        mcc_score = mcc_metric.compute().item()
        acc_metric = accuracy_metric.compute().item()
        f1_score = f1_metric.compute().item()
    
    # Concatenate results
    features_tensor = torch.cat(all_features, dim=0) if all_features else torch.empty(0)
    labels_tensor = torch.cat(all_labels, dim=0) if all_labels else torch.empty(0)
    
    return avg_loss, accuracy, mcc_score, features_tensor, labels_tensor


def save_checkpoint(model: nn.Module, optimizer: optim.Optimizer, epoch: int,
                   loss: float, accuracy: float, model_config: Dict,
                   checkpoint_dir: str = 'models') -> str:
    """Save model checkpoint."""
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
        'accuracy': accuracy,
        'model_config': model_config
    }
    
    checkpoint_path = os.path.join(checkpoint_dir, f'transfer_learning_model_epoch_{epoch}.pth')
    torch.save(checkpoint, checkpoint_path)
    
    return checkpoint_path


def train_transfer_learning(task_type: str = 'image', dataset: str = 'mnist',
                          pretrained_model: str = 'resnet18', epochs: int = 10,
                          batch_size: int = 32, learning_rate: float = 0.001,
                          feature_dim: int = 512, freeze_backbone: bool = True,
                          device: str = 'auto', save_features: bool = True,
                          checkpoint_dir: str = 'models', log_dir: str = 'logs') -> Dict:
    """
    Main training function for Transfer Learning.
    
    Args:
        task_type: Type of task ('image', 'text')
        dataset: Dataset to use
        pretrained_model: Pre-trained model to use
        epochs: Number of training epochs
        batch_size: Batch size
        learning_rate: Learning rate
        feature_dim: Feature dimension
        freeze_backbone: Whether to freeze pre-trained backbone
        device: Device to use ('auto', 'cuda', 'cpu')
        save_features: Whether to save extracted features
        checkpoint_dir: Directory to save model checkpoints
        log_dir: Directory to save logs
        
    Returns:
        Dictionary containing training results
    """
    # Setup logging
    logger = setup_logging(log_dir)
    
    # Device setup
    if device == 'auto':
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(device)
    
    logger.info(f"Using device: {device}")
    
    # Load data based on task type
    logger.info(f"Loading {dataset} dataset for {task_type} task...")
    
    if task_type == 'image':
        if dataset == 'mnist':
            train_loader, test_loader = get_mnist_loaders(batch_size=batch_size)
            num_classes = 10
        elif dataset == 'fashion_mnist':
            train_loader, test_loader = get_fashion_mnist_loaders(batch_size=batch_size)
            num_classes = 10
        elif dataset == 'cifar10':
            train_loader, test_loader = get_cifar10_loaders(batch_size=batch_size)
            num_classes = 10
        else:
            raise ValueError(f"Unsupported image dataset: {dataset}")
        
        # Create image model
        model = ImageTransferLearningModel(
            architecture=pretrained_model,
            num_classes=num_classes,
            feature_dim=feature_dim,
            freeze_backbone=freeze_backbone
        ).to(device)
        
    elif task_type == 'text':
        if dataset == 'cola':
            train_loader, test_loader = get_cola_loaders(
                batch_size=batch_size, model_name=pretrained_model
            )
            num_classes = 2
        elif dataset == 'squad':
            train_loader, test_loader = get_squad_loaders(
                batch_size=batch_size, model_name=pretrained_model
            )
            num_classes = 2
        else:
            raise ValueError(f"Unsupported text dataset: {dataset}")
        
        # Create text model
        model = TextTransferLearningModel(
            model_name=pretrained_model,
            num_classes=num_classes,
            feature_dim=feature_dim,
            freeze_backbone=freeze_backbone
        ).to(device)
        
    else:
        raise ValueError(f"Unsupported task type: {task_type}")
    
    logger.info(f"Dataset loaded: {len(train_loader.dataset)} training samples, "
                f"{len(test_loader.dataset)} test samples")
    logger.info(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Model configuration
    model_config = {
        'task_type': task_type,
        'dataset': dataset,
        'pretrained_model': pretrained_model,
        'num_classes': num_classes,
        'feature_dim': feature_dim,
        'freeze_backbone': freeze_backbone
    }
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    
    # Use different learning rates for backbone and head
    if freeze_backbone:
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    else:
        # Lower learning rate for pre-trained backbone
        backbone_params = []
        head_params = []
        
        for name, param in model.named_parameters():
            if 'backbone' in name:
                backbone_params.append(param)
            else:
                head_params.append(param)
        
        optimizer = optim.Adam([
            {'params': backbone_params, 'lr': learning_rate * 0.1},
            {'params': head_params, 'lr': learning_rate}
        ])
    
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)
    
    # Training history
    train_losses = []
    train_accuracies = []
    val_losses = []
    val_accuracies = []
    val_mcc_scores = [] if task_type == 'text' else []
    
    best_metric = 0.0
    best_model_path = None
    
    logger.info("Starting training...")
    start_time = time.time()
    
    for epoch in range(1, epochs + 1):
        logger.info(f"\nEpoch {epoch}/{epochs}")
        
        # Train
        if task_type == 'image':
            train_loss, train_acc = train_epoch_image(model, train_loader, criterion, optimizer, device, epoch)
            val_loss, val_acc, features, labels = evaluate_image(model, test_loader, criterion, device)
            current_metric = val_acc
            val_mcc = 0.0
        else:  # text
            train_loss, train_acc = train_epoch_text(model, train_loader, criterion, optimizer, device, epoch)
            val_loss, val_acc, val_mcc, features, labels = evaluate_text(
                model, test_loader, criterion, device, use_mcc=(dataset == 'cola')
            )
            current_metric = val_mcc if dataset == 'cola' else val_acc
            val_mcc_scores.append(val_mcc)
        
        train_losses.append(train_loss)
        train_accuracies.append(train_acc)
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)
        
        # Learning rate scheduling
        scheduler.step(val_loss)
        current_lr = optimizer.param_groups[0]['lr']
        
        logger.info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        logger.info(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        if task_type == 'text' and dataset == 'cola':
            logger.info(f"Val MCC: {val_mcc:.4f}")
        logger.info(f"Learning Rate: {current_lr:.6f}")
        
        # Save best model
        if current_metric > best_metric:
            best_metric = current_metric
            best_model_path = save_checkpoint(
                model, optimizer, epoch, val_loss, val_acc, model_config, checkpoint_dir
            )
            logger.info(f"New best model saved: {best_model_path}")
        
        # Save features periodically
        if save_features and epoch % 5 == 0:
            features_dir = os.path.join('results', f'{task_type}_transfer_learning')
            os.makedirs(features_dir, exist_ok=True)
            
            features_path = os.path.join(features_dir, f'features_epoch_{epoch}.npz')
            np.savez(features_path,
                     features=features.numpy() if len(features) > 0 else np.array([]),
                     labels=labels.numpy() if len(labels) > 0 else np.array([]),
                     epoch=epoch,
                     task_type=task_type,
                     dataset=dataset)
            logger.info(f"Features saved: {features_path}")
    
    training_time = time.time() - start_time
    logger.info(f"\nTraining completed in {training_time:.2f} seconds")
    logger.info(f"Best validation {'MCC' if task_type == 'text' and dataset == 'cola' else 'accuracy'}: {best_metric:.4f}")
    
    # Save training curves
    results_dir = os.path.join('results', f'{task_type}_transfer_learning')
    os.makedirs(results_dir, exist_ok=True)
    
    if task_type == 'text' and dataset == 'cola':
        # Plot with MCC
        plot_training_curves(
            train_losses, val_losses, val_mcc_scores, val_accuracies,
            save_path=os.path.join(results_dir, 'training_curves.png'),
            title=f'Transfer Learning ({pretrained_model}) Training Curves',
            metric_names=['MCC', 'Accuracy']
        )
    else:
        plot_training_curves(
            train_losses, val_losses, train_accuracies, val_accuracies,
            save_path=os.path.join(results_dir, 'training_curves.png'),
            title=f'Transfer Learning ({pretrained_model}) Training Curves'
        )
    
    # Final evaluation and feature extraction
    logger.info("Performing final evaluation...")
    model.load_state_dict(torch.load(best_model_path)['model_state_dict'])
    
    if task_type == 'image':
        final_loss, final_acc, final_features, final_labels = evaluate_image(model, test_loader, criterion, device)
        final_mcc = 0.0
    else:
        final_loss, final_acc, final_mcc, final_features, final_labels = evaluate_text(
            model, test_loader, criterion, device, use_mcc=(dataset == 'cola')
        )
    
    logger.info(f"Final Test Accuracy: {final_acc:.2f}%")
    if task_type == 'text' and dataset == 'cola':
        logger.info(f"Final Test MCC: {final_mcc:.4f}")
    
    # Save final features
    if save_features:
        final_features_path = os.path.join(results_dir, 'final_features.npz')
        np.savez(final_features_path,
                 features=final_features.numpy() if len(final_features) > 0 else np.array([]),
                 labels=final_labels.numpy() if len(final_labels) > 0 else np.array([]),
                 task_type=task_type,
                 dataset=dataset,
                 pretrained_model=pretrained_model,
                 accuracy=final_acc,
                 mcc=final_mcc if task_type == 'text' else 0.0)
        logger.info(f"Final features saved: {final_features_path}")
    
    # Save training configuration and results
    results = {
        'model_config': model_config,
        'training_config': {
            'epochs': epochs,
            'batch_size': batch_size,
            'learning_rate': learning_rate,
            'freeze_backbone': freeze_backbone
        },
        'results': {
            'best_metric': best_metric,
            'final_test_accuracy': final_acc,
            'final_test_mcc': final_mcc if task_type == 'text' else 0.0,
            'training_time': training_time,
            'train_losses': train_losses,
            'val_losses': val_losses,
            'train_accuracies': train_accuracies,
            'val_accuracies': val_accuracies,
            'val_mcc_scores': val_mcc_scores if task_type == 'text' else []
        },
        'model_path': best_model_path,
        'features_path': final_features_path if save_features else None
    }
    
    # Save results as JSON
    results_file = os.path.join(results_dir, 'training_results.json')
    with open(results_file, 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        json_results = results.copy()
        for key in ['train_losses', 'val_losses', 'train_accuracies', 'val_accuracies', 'val_mcc_scores']:
            if key in json_results['results']:
                json_results['results'][key] = [float(x) for x in json_results['results'][key]]
        json.dump(json_results, f, indent=2)
    
    logger.info(f"Training results saved: {results_file}")
    
    return results


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description='Transfer Learning for feature extraction')
    
    parser.add_argument('--task', type=str, default='image',
                        choices=['image', 'text'],
                        help='Task type (default: image)')
    
    parser.add_argument('--dataset', type=str, default='mnist',
                        help='Dataset to use (default: mnist)')
    
    parser.add_argument('--architecture', type=str, default='resnet18',
                        help='Pre-trained model architecture (default: resnet18)')
    
    parser.add_argument('--epochs', type=int, default=10,
                        help='Number of training epochs (default: 10)')
    
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size (default: 32)')
    
    parser.add_argument('--lr', type=float, default=0.001,
                        help='Learning rate (default: 0.001)')
    
    parser.add_argument('--feature-dim', type=int, default=512,
                        help='Feature dimension (default: 512)')
    
    parser.add_argument('--no-freeze', action='store_true',
                        help='Do not freeze pre-trained backbone')
    
    parser.add_argument('--device', type=str, default='auto',
                        choices=['auto', 'cuda', 'cpu'],
                        help='Device to use (default: auto)')
    
    parser.add_argument('--no-save-features', action='store_true',
                        help='Do not save extracted features')
    
    parser.add_argument('--checkpoint-dir', type=str, default='models',
                        help='Directory to save checkpoints (default: models)')
    
    parser.add_argument('--log-dir', type=str, default='logs',
                        help='Directory to save logs (default: logs)')
    
    args = parser.parse_args()
    
    # Train model
    results = train_transfer_learning(
        task_type=args.task,
        dataset=args.dataset,
        pretrained_model=args.architecture,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        feature_dim=args.feature_dim,
        freeze_backbone=not args.no_freeze,
        device=args.device,
        save_features=not args.no_save_features,
        checkpoint_dir=args.checkpoint_dir,
        log_dir=args.log_dir
    )
    
    print(f"\nTraining completed!")
    print(f"Final test accuracy: {results['results']['final_test_accuracy']:.2f}%")
    if results['results']['final_test_mcc'] > 0:
        print(f"Final test MCC: {results['results']['final_test_mcc']:.4f}")


if __name__ == '__main__':
    main()
