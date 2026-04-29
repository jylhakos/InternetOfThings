"""
Training script for RNN language models.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR, ReduceLROnPlateau
import time
import math
import os
import json
from datetime import datetime
import argparse

from models.rnn_model import get_model, count_parameters
from src.data_preprocessing import preprocess_wikitext, Vocabulary


def train_epoch(model, train_loader, optimizer, criterion, device, grad_clip=5.0):
    """
    Train the model for one epoch.
    
    Args:
        model: The neural network model
        train_loader: Training data loader
        optimizer: Optimizer
        criterion: Loss function
        device: Device to run on
        grad_clip: Gradient clipping threshold
        
    Returns:
        float: Average training loss
    """
    model.train()
    total_loss = 0
    num_batches = len(train_loader)
    
    for batch_idx, (input_seq, target_seq) in enumerate(train_loader):
        input_seq, target_seq = input_seq.to(device), target_seq.to(device)
        batch_size = input_seq.size(0)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        if hasattr(model, 'init_hidden'):
            # RNN-based model
            hidden = model.init_hidden(batch_size, device)
            output, hidden = model(input_seq, hidden)
        else:
            # Transformer model
            output = model(input_seq)
        
        # Calculate loss
        loss = criterion(output.view(-1, output.size(-1)), target_seq.view(-1))
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping
        if grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        
        # Update parameters
        optimizer.step()
        
        total_loss += loss.item()
        
        # Print progress
        if batch_idx % 100 == 0:
            print(f'Batch {batch_idx}/{num_batches}, Loss: {loss.item():.4f}')
    
    return total_loss / num_batches


def evaluate(model, data_loader, criterion, device):
    """
    Evaluate the model.
    
    Args:
        model: The neural network model
        data_loader: Data loader for evaluation
        criterion: Loss function
        device: Device to run on
        
    Returns:
        float: Average evaluation loss
        float: Perplexity
    """
    model.eval()
    total_loss = 0
    num_tokens = 0
    
    with torch.no_grad():
        for input_seq, target_seq in data_loader:
            input_seq, target_seq = input_seq.to(device), target_seq.to(device)
            batch_size = input_seq.size(0)
            
            # Forward pass
            if hasattr(model, 'init_hidden'):
                hidden = model.init_hidden(batch_size, device)
                output, hidden = model(input_seq, hidden)
            else:
                output = model(input_seq)
            
            # Calculate loss
            loss = criterion(output.view(-1, output.size(-1)), target_seq.view(-1))
            
            total_loss += loss.item() * target_seq.numel()
            num_tokens += target_seq.numel()
    
    avg_loss = total_loss / num_tokens
    perplexity = math.exp(avg_loss)
    
    return avg_loss, perplexity


def save_checkpoint(model, optimizer, scheduler, epoch, loss, perplexity, 
                   vocab, args, filepath):
    """
    Save model checkpoint.
    
    Args:
        model: The neural network model
        optimizer: Optimizer state
        scheduler: Learning rate scheduler
        epoch: Current epoch
        loss: Current loss
        perplexity: Current perplexity
        vocab: Vocabulary object
        args: Training arguments
        filepath: Path to save checkpoint
    """
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
        'loss': loss,
        'perplexity': perplexity,
        'vocab_size': len(vocab),
        'model_config': {
            'model_type': args.model,
            'embed_size': args.embed_size,
            'hidden_size': args.hidden_size,
            'num_layers': args.num_layers,
            'dropout': args.dropout,
            'tie_weights': args.tie_weights
        },
        'training_config': vars(args)
    }
    
    torch.save(checkpoint, filepath)
    print(f"Checkpoint saved to {filepath}")


def load_checkpoint(filepath, model, optimizer=None, scheduler=None, device='cpu'):
    """
    Load model checkpoint.
    
    Args:
        filepath: Path to checkpoint file
        model: Model to load state into
        optimizer: Optimizer to load state into (optional)
        scheduler: Scheduler to load state into (optional)
        device: Device to load on
        
    Returns:
        int: Epoch number
        float: Best loss
    """
    checkpoint = torch.load(filepath, map_location=device)
    
    model.load_state_dict(checkpoint['model_state_dict'])
    
    if optimizer and 'optimizer_state_dict' in checkpoint:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    
    if scheduler and 'scheduler_state_dict' in checkpoint and checkpoint['scheduler_state_dict']:
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
    
    print(f"Checkpoint loaded from {filepath}")
    print(f"Epoch: {checkpoint['epoch']}, Loss: {checkpoint['loss']:.4f}, "
          f"Perplexity: {checkpoint['perplexity']:.2f}")
    
    return checkpoint['epoch'], checkpoint['loss']


def train_model(args):
    """
    Main training function.
    
    Args:
        args: Training arguments
    """
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() and args.cuda else 'cpu')
    print(f"Using device: {device}")
    
    # Set random seed for reproducibility
    torch.manual_seed(args.seed)
    if device.type == 'cuda':
        torch.cuda.manual_seed(args.seed)
    
    # Load and preprocess data
    print("Loading and preprocessing data...")
    data_loaders, vocab = preprocess_wikitext(
        dataset_name=args.dataset,
        vocab_size=args.vocab_size,
        min_freq=args.min_freq,
        seq_length=args.seq_length,
        batch_size=args.batch_size,
        cache_dir=args.data_dir
    )
    
    train_loader = data_loaders['train']
    val_loader = data_loaders['validation']
    
    # Create model
    print("Creating model...")
    if args.model in ['rnn', 'lstm', 'gru']:
        model = get_model(
            args.model,
            vocab_size=len(vocab),
            embed_size=args.embed_size,
            hidden_size=args.hidden_size,
            num_layers=args.num_layers,
            dropout=args.dropout,
            tie_weights=args.tie_weights
        )
    else:
        raise ValueError(f"Unsupported model type: {args.model}")
    
    model = model.to(device)
    print(f"Model parameters: {count_parameters(model):,}")
    
    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    
    # Learning rate scheduler
    scheduler = None
    if args.scheduler == 'step':
        scheduler = StepLR(optimizer, step_size=args.lr_step, gamma=args.lr_gamma)
    elif args.scheduler == 'plateau':
        scheduler = ReduceLROnPlateau(optimizer, mode='min', patience=args.patience, 
                                    factor=args.lr_gamma, verbose=True)
    
    # Load checkpoint if specified
    start_epoch = 0
    best_val_loss = float('inf')
    
    if args.resume:
        if os.path.exists(args.resume):
            start_epoch, best_val_loss = load_checkpoint(
                args.resume, model, optimizer, scheduler, device
            )
            start_epoch += 1
        else:
            print(f"Checkpoint file not found: {args.resume}")
    
    # Training loop
    print("Starting training...")
    train_losses = []
    val_losses = []
    
    for epoch in range(start_epoch, args.epochs):
        epoch_start_time = time.time()
        
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, criterion, device, args.grad_clip)
        
        # Evaluate
        val_loss, val_perplexity = evaluate(model, val_loader, criterion, device)
        
        # Update learning rate
        if scheduler:
            if args.scheduler == 'plateau':
                scheduler.step(val_loss)
            else:
                scheduler.step()
        
        # Record losses
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        
        # Print progress
        elapsed = time.time() - epoch_start_time
        print(f'Epoch {epoch+1}/{args.epochs} | '
              f'Time: {elapsed:.1f}s | '
              f'Train Loss: {train_loss:.4f} | '
              f'Val Loss: {val_loss:.4f} | '
              f'Val Perplexity: {val_perplexity:.2f} | '
              f'LR: {optimizer.param_groups[0]["lr"]:.2e}')
        
        # Save checkpoint if validation loss improved
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            
            # Save best model
            best_model_path = os.path.join(args.save_dir, 'best_model.pth')
            save_checkpoint(model, optimizer, scheduler, epoch, val_loss, 
                          val_perplexity, vocab, args, best_model_path)
        
        # Save regular checkpoint
        if (epoch + 1) % args.save_every == 0:
            checkpoint_path = os.path.join(args.save_dir, f'checkpoint_epoch_{epoch+1}.pth')
            save_checkpoint(model, optimizer, scheduler, epoch, val_loss, 
                          val_perplexity, vocab, args, checkpoint_path)\n    \n    # Save final model\n    final_model_path = os.path.join(args.save_dir, 'final_model.pth')\n    save_checkpoint(model, optimizer, scheduler, args.epochs-1, val_loss, \n                  val_perplexity, vocab, args, final_model_path)\n    \n    # Save training history\n    history = {\n        'train_losses': train_losses,\n        'val_losses': val_losses,\n        'best_val_loss': best_val_loss\n    }\n    \n    history_path = os.path.join(args.save_dir, 'training_history.json')\n    with open(history_path, 'w') as f:\n        json.dump(history, f, indent=2)\n    \n    print(f\"Training completed! Best validation loss: {best_val_loss:.4f}\")\n    print(f\"Best validation perplexity: {math.exp(best_val_loss):.2f}\")\n\n\ndef main():\n    parser = argparse.ArgumentParser(description='Train RNN Language Model')\n    \n    # Data arguments\n    parser.add_argument('--dataset', type=str, default='wikitext-2-v1',\n                        help='WikiText dataset version')\n    parser.add_argument('--data-dir', type=str, default='./data',\n                        help='Directory to store data')\n    parser.add_argument('--vocab-size', type=int, default=10000,\n                        help='Vocabulary size')\n    parser.add_argument('--min-freq', type=int, default=2,\n                        help='Minimum token frequency')\n    parser.add_argument('--seq-length', type=int, default=128,\n                        help='Sequence length')\n    \n    # Model arguments\n    parser.add_argument('--model', type=str, default='lstm',\n                        choices=['rnn', 'lstm', 'gru'],\n                        help='Model type')\n    parser.add_argument('--embed-size', type=int, default=256,\n                        help='Embedding dimension')\n    parser.add_argument('--hidden-size', type=int, default=512,\n                        help='Hidden state dimension')\n    parser.add_argument('--num-layers', type=int, default=2,\n                        help='Number of RNN layers')\n    parser.add_argument('--dropout', type=float, default=0.2,\n                        help='Dropout probability')\n    parser.add_argument('--tie-weights', action='store_true',\n                        help='Tie input and output embeddings')\n    \n    # Training arguments\n    parser.add_argument('--batch-size', type=int, default=32,\n                        help='Batch size')\n    parser.add_argument('--epochs', type=int, default=20,\n                        help='Number of epochs')\n    parser.add_argument('--lr', type=float, default=0.001,\n                        help='Learning rate')\n    parser.add_argument('--weight-decay', type=float, default=1e-5,\n                        help='Weight decay')\n    parser.add_argument('--grad-clip', type=float, default=5.0,\n                        help='Gradient clipping threshold')\n    \n    # Scheduler arguments\n    parser.add_argument('--scheduler', type=str, default=None,\n                        choices=[None, 'step', 'plateau'],\n                        help='Learning rate scheduler')\n    parser.add_argument('--lr-step', type=int, default=5,\n                        help='Step size for StepLR')\n    parser.add_argument('--lr-gamma', type=float, default=0.5,\n                        help='Gamma for learning rate decay')\n    parser.add_argument('--patience', type=int, default=3,\n                        help='Patience for ReduceLROnPlateau')\n    \n    # Save/load arguments\n    parser.add_argument('--save-dir', type=str, default='./checkpoints',\n                        help='Directory to save checkpoints')\n    parser.add_argument('--save-every', type=int, default=5,\n                        help='Save checkpoint every N epochs')\n    parser.add_argument('--resume', type=str, default=None,\n                        help='Path to checkpoint to resume from')\n    \n    # Other arguments\n    parser.add_argument('--cuda', action='store_true',\n                        help='Use CUDA if available')\n    parser.add_argument('--seed', type=int, default=1234,\n                        help='Random seed')\n    \n    args = parser.parse_args()\n    \n    # Create directories\n    os.makedirs(args.data_dir, exist_ok=True)\n    os.makedirs(args.save_dir, exist_ok=True)\n    \n    # Save arguments\n    args_path = os.path.join(args.save_dir, 'args.json')\n    with open(args_path, 'w') as f:\n        json.dump(vars(args), f, indent=2)\n    \n    print(\"Training Arguments:\")\n    for key, value in vars(args).items():\n        print(f\"  {key}: {value}\")\n    print()\n    \n    # Start training\n    train_model(args)\n\n\nif __name__ == '__main__':\n    main()"
