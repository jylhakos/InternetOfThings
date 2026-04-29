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


def train_model(args):
    """
    Main training function.
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
    model = get_model(
        args.model,
        vocab_size=len(vocab),
        embed_size=args.embed_size,
        hidden_size=args.hidden_size,
        num_layers=args.num_layers,
        dropout=args.dropout,
        tie_weights=args.tie_weights
    )
    
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
    
    # Training loop
    print("Starting training...")
    best_val_loss = float('inf')
    
    for epoch in range(args.epochs):
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
        
        # Print progress
        elapsed = time.time() - epoch_start_time
        print(f'Epoch {epoch+1}/{args.epochs} | '
              f'Time: {elapsed:.1f}s | '
              f'Train Loss: {train_loss:.4f} | '
              f'Val Loss: {val_loss:.4f} | '
              f'Val Perplexity: {val_perplexity:.2f}')
        
        # Save checkpoint if validation loss improved
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_path = os.path.join(args.save_dir, 'best_model.pth')
            save_checkpoint(model, optimizer, scheduler, epoch, val_loss, 
                          val_perplexity, vocab, args, best_model_path)
    
    print(f"Training completed! Best validation loss: {best_val_loss:.4f}")


def main():
    parser = argparse.ArgumentParser(description='Train RNN Language Model')
    
    # Data arguments
    parser.add_argument('--dataset', type=str, default='wikitext-2-v1')
    parser.add_argument('--data-dir', type=str, default='./data')
    parser.add_argument('--vocab-size', type=int, default=10000)
    parser.add_argument('--min-freq', type=int, default=2)
    parser.add_argument('--seq-length', type=int, default=128)
    
    # Model arguments
    parser.add_argument('--model', type=str, default='lstm', choices=['rnn', 'lstm', 'gru'])
    parser.add_argument('--embed-size', type=int, default=256)
    parser.add_argument('--hidden-size', type=int, default=512)
    parser.add_argument('--num-layers', type=int, default=2)
    parser.add_argument('--dropout', type=float, default=0.2)
    parser.add_argument('--tie-weights', action='store_true')
    
    # Training arguments
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--weight-decay', type=float, default=1e-5)
    parser.add_argument('--grad-clip', type=float, default=5.0)
    
    # Scheduler arguments
    parser.add_argument('--scheduler', type=str, default=None, choices=[None, 'step', 'plateau'])
    parser.add_argument('--lr-step', type=int, default=5)
    parser.add_argument('--lr-gamma', type=float, default=0.5)
    parser.add_argument('--patience', type=int, default=3)
    
    # Save/load arguments
    parser.add_argument('--save-dir', type=str, default='./checkpoints')
    parser.add_argument('--cuda', action='store_true')
    parser.add_argument('--seed', type=int, default=1234)
    
    args = parser.parse_args()
    
    # Create directories
    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs(args.save_dir, exist_ok=True)
    
    print("Training Arguments:")
    for key, value in vars(args).items():
        print(f"  {key}: {value}")
    print()
    
    # Start training
    train_model(args)


if __name__ == '__main__':
    main()
