#!/usr/bin/env python3
"""
Training script for CNN feature learning on image datasets.
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
from typing import Tuple, Dict, List
import logging
from tqdm import tqdm

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models.cnn_models import create_cnn_model
from data.data_loaders import get_mnist_loaders, get_fashion_mnist_loaders
from utils.metrics import calculate_accuracy, plot_training_curves
from utils.visualization import visualize_features


def setup_logging(log_dir: str = 'logs') -> logging.Logger:
    """Setup logging configuration."""
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'cnn_training.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def train_epoch(model: nn.Module, train_loader: DataLoader, criterion: nn.Module,
                optimizer: optim.Optimizer, device: torch.device, epoch: int) -> Tuple[float, float]:
    """Train model for one epoch."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(train_loader, desc=f'Epoch {epoch}')
    for batch_idx, (data, target) in enumerate(pbar):
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        total += target.size(0)
        
        # Update progress bar
        accuracy = 100. * correct / total
        avg_loss = total_loss / (batch_idx + 1)
        pbar.set_postfix({
            'Loss': f'{avg_loss:.4f}',
            'Acc': f'{accuracy:.2f}%'
        })
    
    return total_loss / len(train_loader), 100. * correct / total


def validate_epoch(model: nn.Module, val_loader: DataLoader, criterion: nn.Module,
                   device: torch.device) -> Tuple[float, float]:
    """Validate model for one epoch."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data, target in tqdm(val_loader, desc='Validation'):
            data, target = data.to(device), target.to(device)
            output = model(data)
            loss = criterion(output, target)
            
            total_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
    
    return total_loss / len(val_loader), 100. * correct / total


def extract_and_save_features(model: nn.Module, data_loader: DataLoader, 
                             device: torch.device, save_path: str) -> np.ndarray:
    """Extract features from trained model and save them."""
    model.eval()
    features_list = []
    labels_list = []
    
    with torch.no_grad():
        for data, target in tqdm(data_loader, desc='Extracting features'):
            data = data.to(device)
            if hasattr(model, 'extract_features'):
                features = model.extract_features(data)
            else:
                # Use penultimate layer if extract_features not available
                features = model(data)
            
            features_list.append(features.cpu().numpy())
            labels_list.append(target.numpy())
    
    all_features = np.vstack(features_list)
    all_labels = np.hstack(labels_list)
    
    # Save features
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    np.savez(save_path, features=all_features, labels=all_labels)
    
    return all_features, all_labels


def save_model(model: nn.Module, optimizer: optim.Optimizer, epoch: int,
               loss: float, accuracy: float, save_path: str) -> None:
    """Save model checkpoint."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
        'accuracy': accuracy,
    }, save_path)


def train_cnn(dataset: str = 'mnist', model_type: str = 'simple', epochs: int = 10,
              batch_size: int = 64, learning_rate: float = 0.001, device: str = 'auto',
              save_model_path: str = 'models/cnn_model.pth',
              save_features_path: str = 'results/cnn_features.npz',
              test_mode: bool = False) -> Dict:
    """
    Train CNN model for feature learning.
    
    Args:
        dataset: Dataset to use ('mnist', 'fashion_mnist')
        model_type: Type of CNN model ('simple', 'feature', 'resnet', 'attention')
        epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Learning rate for optimizer
        device: Device to use for training ('auto', 'cpu', 'cuda')
        save_model_path: Path to save trained model
        save_features_path: Path to save extracted features
        test_mode: Whether running in test mode (fewer epochs, smaller batches)
        
    Returns:
        Dictionary containing training results
    """
    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting CNN training with dataset={dataset}, model_type={model_type}")
    
    # Adjust parameters for test mode
    if test_mode:
        epochs = min(epochs, 2)
        batch_size = min(batch_size, 32)
        logger.info("Running in test mode")
    
    # Setup device
    if device == 'auto':
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(device)
    logger.info(f"Using device: {device}")
    
    # Load data
    logger.info("Loading dataset...")
    if dataset == 'mnist':
        train_loader, test_loader = get_mnist_loaders(batch_size, batch_size)
        num_classes = 10
        input_channels = 1
    elif dataset == 'fashion_mnist':
        train_loader, test_loader = get_fashion_mnist_loaders(batch_size, batch_size)
        num_classes = 10
        input_channels = 1
    else:
        raise ValueError(f"Unknown dataset: {dataset}")
    
    logger.info(f"Dataset loaded: {len(train_loader.dataset)} training samples, {len(test_loader.dataset)} test samples")
    
    # Create model
    logger.info(f"Creating {model_type} model...")
    if model_type in ['simple', 'attention']:
        model = create_cnn_model(model_type, num_classes=num_classes, num_channels=input_channels)
    elif model_type == 'feature':
        model = create_cnn_model(model_type, input_channels=input_channels, feature_dim=256)
    elif model_type == 'resnet':
        model = create_cnn_model(model_type, feature_dim=512, freeze_backbone=False)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model = model.to(device)
    logger.info(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=epochs//3, gamma=0.1)
    
    # Training loop
    logger.info("Starting training...")
    train_losses = []
    train_accuracies = []
    val_losses = []
    val_accuracies = []
    
    best_accuracy = 0.0
    start_time = time.time()
    
    for epoch in range(1, epochs + 1):
        # Train
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device, epoch)
        train_losses.append(train_loss)
        train_accuracies.append(train_acc)
        
        # Validate
        val_loss, val_acc = validate_epoch(model, test_loader, criterion, device)
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)
        
        # Update learning rate
        scheduler.step()
        
        # Log progress
        logger.info(f'Epoch {epoch}/{epochs}:')
        logger.info(f'  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
        logger.info(f'  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
        logger.info(f'  LR: {scheduler.get_last_lr()[0]:.6f}')
        
        # Save best model
        if val_acc > best_accuracy:
            best_accuracy = val_acc
            save_model(model, optimizer, epoch, val_loss, val_acc, save_model_path)
            logger.info(f'New best model saved with accuracy: {val_acc:.2f}%')
    
    # Training completed
    total_time = time.time() - start_time
    logger.info(f"Training completed in {total_time:.2f} seconds")
    logger.info(f"Best validation accuracy: {best_accuracy:.2f}%")
    
    # Extract and save features
    logger.info("Extracting features from trained model...")
    features, labels = extract_and_save_features(model, test_loader, device, save_features_path)
    logger.info(f"Features saved to {save_features_path}")
    
    # Plot training curves
    if not test_mode:
        try:
            plot_training_curves(train_losses, val_losses, train_accuracies, val_accuracies,
                                'results/cnn_training_curves.png')
            logger.info("Training curves saved")
        except Exception as e:
            logger.warning(f"Could not save training curves: {e}")
    
    # Return results
    results = {
        'best_accuracy': best_accuracy,
        'train_losses': train_losses,
        'val_losses': val_losses,
        'train_accuracies': train_accuracies,
        'val_accuracies': val_accuracies,
        'training_time': total_time,
        'model_path': save_model_path,
        'features_path': save_features_path,
        'num_features': features.shape[1] if features is not None else 0
    }
    
    return results


def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description='Train CNN for feature learning')
    parser.add_argument('--dataset', type=str, default='mnist', 
                       choices=['mnist', 'fashion_mnist'],
                       help='Dataset to use for training')
    parser.add_argument('--model-type', type=str, default='simple',
                       choices=['simple', 'feature', 'resnet', 'attention'],
                       help='Type of CNN model to use')
    parser.add_argument('--epochs', type=int, default=10,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=64,
                       help='Training batch size')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate for optimizer')
    parser.add_argument('--device', type=str, default='auto',
                       choices=['auto', 'cpu', 'cuda'],
                       help='Device to use for training')
    parser.add_argument('--save-model', type=str, default='models/cnn_model.pth',
                       help='Path to save trained model')
    parser.add_argument('--save-features', type=str, default='results/cnn_features.npz',
                       help='Path to save extracted features')
    parser.add_argument('--test-mode', action='store_true',
                       help='Run in test mode (reduced epochs and batch size)')
    
    args = parser.parse_args()
    
    # Train model
    results = train_cnn(
        dataset=args.dataset,
        model_type=args.model_type,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        device=args.device,
        save_model_path=args.save_model,
        save_features_path=args.save_features,
        test_mode=args.test_mode
    )
    
    # Print summary
    print("\n" + "="*50)
    print("CNN TRAINING SUMMARY")
    print("="*50)
    print(f"Best Validation Accuracy: {results['best_accuracy']:.2f}%")
    print(f"Training Time: {results['training_time']:.2f} seconds")
    print(f"Number of Features: {results['num_features']}")
    print(f"Model saved to: {results['model_path']}")
    print(f"Features saved to: {results['features_path']}")
    print("="*50)


if __name__ == '__main__':
    main()
