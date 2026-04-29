#!/usr/bin/env python3
"""
Training script for RNN feature learning on text datasets.
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

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models.rnn_models import SimpleLSTM, FeatureLSTM, create_rnn_model
from data.data_loaders import get_wikitext2_loaders, get_imdb_loaders
from utils.metrics import calculate_accuracy, plot_training_curves
from utils.visualization import visualize_attention_weights


def setup_logging(log_dir: str = 'logs') -> logging.Logger:
    """Setup logging configuration."""
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'rnn_training.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def collate_fn(batch):
    """Custom collate function for variable length sequences."""
    sequences, labels = zip(*batch)
    
    # Convert sequences to tensors and pad them
    max_len = max(len(seq) for seq in sequences)
    padded_sequences = []
    
    for seq in sequences:
        if len(seq) < max_len:
            # Pad with zeros
            padded = seq + [0] * (max_len - len(seq))
        else:
            padded = seq
        padded_sequences.append(padded)
    
    return torch.tensor(padded_sequences), torch.tensor(labels)


def train_epoch(model: nn.Module, train_loader: DataLoader, criterion: nn.Module,
                optimizer: optim.Optimizer, device: torch.device, epoch: int) -> Tuple[float, float]:
    """Train model for one epoch."""
    model.train()
    total_loss = 0.0
    correct = 0
    total_samples = 0
    
    progress_bar = tqdm(train_loader, desc=f'Epoch {epoch}')
    
    for batch_idx, (sequences, labels) in enumerate(progress_bar):
        sequences, labels = sequences.to(device), labels.to(device)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        outputs = model(sequences)
        loss = criterion(outputs, labels)
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping to prevent exploding gradients
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
        
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


def evaluate(model: nn.Module, test_loader: DataLoader, criterion: nn.Module,
             device: torch.device) -> Tuple[float, float, torch.Tensor, torch.Tensor]:
    """Evaluate model on test set."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total_samples = 0
    
    all_features = []
    all_labels = []
    
    with torch.no_grad():
        for sequences, labels in tqdm(test_loader, desc='Evaluating'):
            sequences, labels = sequences.to(device), labels.to(device)
            
            # Forward pass
            outputs = model(sequences)
            loss = criterion(outputs, labels)
            
            # Statistics
            total_loss += loss.item()
            predictions = outputs.argmax(dim=1)
            correct += (predictions == labels).sum().item()
            total_samples += labels.size(0)
            
            # Extract features if model supports it
            if hasattr(model, 'extract_features'):
                features = model.extract_features(sequences)
                all_features.append(features.cpu())
                all_labels.append(labels.cpu())
    
    avg_loss = total_loss / len(test_loader)
    accuracy = 100.0 * correct / total_samples
    
    # Concatenate features
    features_tensor = torch.cat(all_features, dim=0) if all_features else torch.empty(0)
    labels_tensor = torch.cat(all_labels, dim=0) if all_labels else torch.empty(0)
    
    return avg_loss, accuracy, features_tensor, labels_tensor


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
    
    checkpoint_path = os.path.join(checkpoint_dir, f'rnn_model_epoch_{epoch}.pth')
    torch.save(checkpoint, checkpoint_path)
    
    return checkpoint_path


def build_vocab(train_loader: DataLoader, min_freq: int = 2) -> Dict[str, int]:
    """Build vocabulary from training data."""
    word_freq = {}
    
    # Count word frequencies
    for sequences, _ in train_loader:
        for seq in sequences:
            for word_id in seq:
                if word_id.item() not in word_freq:
                    word_freq[word_id.item()] = 0
                word_freq[word_id.item()] += 1
    
    # Build vocabulary
    vocab = {'<PAD>': 0, '<UNK>': 1}
    vocab_size = 2
    
    for word_id, freq in word_freq.items():
        if freq >= min_freq and word_id not in vocab:
            vocab[str(word_id)] = vocab_size
            vocab_size += 1
    
    return vocab


def train_rnn(dataset: str = 'wikitext2', model_type: str = 'lstm',
              epochs: int = 10, batch_size: int = 32, learning_rate: float = 0.001,
              hidden_dim: int = 256, embed_dim: int = 128, num_layers: int = 2,
              dropout: float = 0.3, device: str = 'auto', save_features: bool = True,
              checkpoint_dir: str = 'models', log_dir: str = 'logs') -> Dict:
    """
    Main training function for RNN models.
    
    Args:
        dataset: Dataset to use ('wikitext2', 'imdb')
        model_type: Type of RNN ('lstm', 'gru', 'rnn', 'feature')
        epochs: Number of training epochs
        batch_size: Batch size
        learning_rate: Learning rate
        hidden_dim: Hidden dimension size
        embed_dim: Embedding dimension size
        num_layers: Number of RNN layers
        dropout: Dropout rate
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
    
    # Load data
    logger.info(f"Loading {dataset} dataset...")
    if dataset == 'wikitext2':
        train_loader, test_loader, vocab_size = get_wikitext2_loaders(
            batch_size=batch_size, test_batch_size=batch_size
        )
    elif dataset == 'imdb':
        train_loader, test_loader, vocab_size = get_imdb_loaders(
            batch_size=batch_size, test_batch_size=batch_size
        )
    else:
        raise ValueError(f"Unsupported dataset: {dataset}")
    
    # Use custom collate function for variable length sequences
    train_loader = DataLoader(
        train_loader.dataset, 
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn
    )
    test_loader = DataLoader(
        test_loader.dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn
    )
    
    logger.info(f"Dataset loaded: {len(train_loader.dataset)} training samples, "
                f"{len(test_loader.dataset)} test samples")
    logger.info(f"Vocabulary size: {vocab_size}")
    
    # Model configuration
    model_config = {
        'model_type': model_type,
        'vocab_size': vocab_size,
        'embed_dim': embed_dim,
        'hidden_dim': hidden_dim,
        'num_layers': num_layers,
        'dropout': dropout,
        'dataset': dataset
    }
    
    # Create model
    logger.info(f"Creating {model_type} model...")
    num_classes = 2 if dataset == 'imdb' else vocab_size  # Binary for IMDB, vocab size for language modeling
    
    model = create_rnn_model(
        model_type=model_type,
        vocab_size=vocab_size,
        embed_dim=embed_dim,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        num_classes=num_classes,
        dropout=dropout
    ).to(device)
    
    logger.info(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)
    
    # Training history
    train_losses = []
    train_accuracies = []
    val_losses = []
    val_accuracies = []
    
    best_val_accuracy = 0.0
    best_model_path = None
    
    logger.info("Starting training...")
    start_time = time.time()
    
    for epoch in range(1, epochs + 1):
        logger.info(f"\nEpoch {epoch}/{epochs}")
        
        # Train
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device, epoch)
        train_losses.append(train_loss)
        train_accuracies.append(train_acc)
        
        # Evaluate
        val_loss, val_acc, features, labels = evaluate(model, test_loader, criterion, device)
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)
        
        # Learning rate scheduling
        scheduler.step(val_loss)
        current_lr = optimizer.param_groups[0]['lr']
        
        logger.info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        logger.info(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        logger.info(f"Learning Rate: {current_lr:.6f}")
        
        # Save best model
        if val_acc > best_val_accuracy:
            best_val_accuracy = val_acc
            best_model_path = save_checkpoint(
                model, optimizer, epoch, val_loss, val_acc, model_config, checkpoint_dir
            )
            logger.info(f"New best model saved: {best_model_path}")
        
        # Save features periodically
        if save_features and epoch % 5 == 0:
            features_dir = os.path.join('results', 'rnn_features')
            os.makedirs(features_dir, exist_ok=True)
            
            features_path = os.path.join(features_dir, f'features_epoch_{epoch}.npz')
            np.savez(features_path, 
                     features=features.numpy(), 
                     labels=labels.numpy(),
                     epoch=epoch,
                     model_type=model_type)
            logger.info(f"Features saved: {features_path}")
    
    training_time = time.time() - start_time
    logger.info(f"\nTraining completed in {training_time:.2f} seconds")
    logger.info(f"Best validation accuracy: {best_val_accuracy:.2f}%")
    
    # Save training curves
    results_dir = os.path.join('results', 'rnn_training')
    os.makedirs(results_dir, exist_ok=True)
    
    plot_training_curves(
        train_losses, val_losses, train_accuracies, val_accuracies,
        save_path=os.path.join(results_dir, 'training_curves.png'),
        title=f'RNN ({model_type}) Training Curves'
    )
    
    # Final evaluation and feature extraction
    logger.info("Performing final evaluation...")
    model.load_state_dict(torch.load(best_model_path)['model_state_dict'])
    final_loss, final_acc, final_features, final_labels = evaluate(model, test_loader, criterion, device)
    
    logger.info(f"Final Test Accuracy: {final_acc:.2f}%")
    
    # Save final features
    if save_features:
        features_dir = os.path.join('results', 'rnn_features')
        os.makedirs(features_dir, exist_ok=True)
        
        final_features_path = os.path.join(features_dir, 'final_features.npz')
        np.savez(final_features_path,
                 features=final_features.numpy(),
                 labels=final_labels.numpy(),
                 model_type=model_type,
                 dataset=dataset,
                 accuracy=final_acc)
        logger.info(f"Final features saved: {final_features_path}")
    
    # Save training configuration and results
    results = {
        'model_config': model_config,
        'training_config': {
            'epochs': epochs,
            'batch_size': batch_size,
            'learning_rate': learning_rate,
            'dataset': dataset
        },
        'results': {
            'best_val_accuracy': best_val_accuracy,
            'final_test_accuracy': final_acc,
            'training_time': training_time,
            'train_losses': train_losses,
            'val_losses': val_losses,
            'train_accuracies': train_accuracies,
            'val_accuracies': val_accuracies
        },
        'model_path': best_model_path,
        'features_path': final_features_path if save_features else None
    }
    
    # Save results as JSON
    results_file = os.path.join(results_dir, 'training_results.json')
    with open(results_file, 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        json_results = results.copy()
        for key in ['train_losses', 'val_losses', 'train_accuracies', 'val_accuracies']:
            if key in json_results['results']:
                json_results['results'][key] = [float(x) for x in json_results['results'][key]]
        json.dump(json_results, f, indent=2)
    
    logger.info(f"Training results saved: {results_file}")
    
    return results


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description='Train RNN for feature learning')
    
    parser.add_argument('--dataset', type=str, default='wikitext2',
                        choices=['wikitext2', 'imdb'],
                        help='Dataset to use (default: wikitext2)')
    
    parser.add_argument('--model', type=str, default='lstm',
                        choices=['lstm', 'gru', 'rnn', 'feature'],
                        help='RNN model type (default: lstm)')
    
    parser.add_argument('--epochs', type=int, default=10,
                        help='Number of training epochs (default: 10)')
    
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size (default: 32)')
    
    parser.add_argument('--lr', type=float, default=0.001,
                        help='Learning rate (default: 0.001)')
    
    parser.add_argument('--hidden-dim', type=int, default=256,
                        help='Hidden dimension size (default: 256)')
    
    parser.add_argument('--embed-dim', type=int, default=128,
                        help='Embedding dimension size (default: 128)')
    
    parser.add_argument('--num-layers', type=int, default=2,
                        help='Number of RNN layers (default: 2)')
    
    parser.add_argument('--dropout', type=float, default=0.3,
                        help='Dropout rate (default: 0.3)')
    
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
    results = train_rnn(
        dataset=args.dataset,
        model_type=args.model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        hidden_dim=args.hidden_dim,
        embed_dim=args.embed_dim,
        num_layers=args.num_layers,
        dropout=args.dropout,
        device=args.device,
        save_features=not args.no_save_features,
        checkpoint_dir=args.checkpoint_dir,
        log_dir=args.log_dir
    )
    
    print(f"\nTraining completed!")
    print(f"Best validation accuracy: {results['results']['best_val_accuracy']:.2f}%")
    print(f"Final test accuracy: {results['results']['final_test_accuracy']:.2f}%")


if __name__ == '__main__':
    main()
