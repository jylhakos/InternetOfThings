#!/usr/bin/env python3
"""
Training script for Autoencoder feature learning on various datasets.
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
import matplotlib.pyplot as plt

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models.autoencoder_models import (
    SimpleAutoencoder, ConvAutoencoder, VariationalAutoencoder, 
    create_autoencoder_model
)
from data.data_loaders import get_mnist_loaders, get_fashion_mnist_loaders
from utils.metrics import calculate_reconstruction_loss, plot_training_curves
from utils.visualization import visualize_reconstructions, plot_latent_space


def setup_logging(log_dir: str = 'logs') -> logging.Logger:
    """Setup logging configuration."""
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'autoencoder_training.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def vae_loss(recon_x: torch.Tensor, x: torch.Tensor, mu: torch.Tensor, 
             logvar: torch.Tensor, beta: float = 1.0) -> torch.Tensor:
    """Compute VAE loss (reconstruction + KL divergence)."""
    # Reconstruction loss
    recon_loss = nn.functional.mse_loss(recon_x, x, reduction='sum')
    
    # KL divergence
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    
    # Total loss
    total_loss = recon_loss + beta * kl_loss
    
    return total_loss, recon_loss, kl_loss


def train_epoch(model: nn.Module, train_loader: DataLoader, optimizer: optim.Optimizer,
                device: torch.device, epoch: int, model_type: str = 'standard',
                beta: float = 1.0) -> Tuple[float, float, float]:
    """Train model for one epoch."""
    model.train()
    total_loss = 0.0
    total_recon_loss = 0.0
    total_kl_loss = 0.0
    
    progress_bar = tqdm(train_loader, desc=f'Epoch {epoch}')
    
    for batch_idx, (data, _) in enumerate(progress_bar):
        data = data.to(device)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        if model_type == 'vae':
            recon_data, mu, logvar = model(data)
            loss, recon_loss, kl_loss = vae_loss(recon_data, data, mu, logvar, beta)
            total_kl_loss += kl_loss.item()
        else:
            recon_data = model(data)
            loss = nn.functional.mse_loss(recon_data, data, reduction='sum')
            recon_loss = loss
            kl_loss = torch.tensor(0.0)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Statistics
        total_loss += loss.item()
        total_recon_loss += recon_loss.item()
        
        # Update progress bar
        progress_bar.set_postfix({
            'Loss': f'{total_loss / (batch_idx + 1):.4f}',
            'Recon': f'{total_recon_loss / (batch_idx + 1):.4f}',
            'KL': f'{total_kl_loss / (batch_idx + 1):.4f}' if model_type == 'vae' else '0.0'
        })
    
    avg_loss = total_loss / len(train_loader.dataset)
    avg_recon_loss = total_recon_loss / len(train_loader.dataset)
    avg_kl_loss = total_kl_loss / len(train_loader.dataset) if model_type == 'vae' else 0.0
    
    return avg_loss, avg_recon_loss, avg_kl_loss


def evaluate(model: nn.Module, test_loader: DataLoader, device: torch.device,
             model_type: str = 'standard', beta: float = 1.0) -> Tuple[float, float, float, torch.Tensor, torch.Tensor]:
    """Evaluate model on test set."""
    model.eval()
    total_loss = 0.0
    total_recon_loss = 0.0
    total_kl_loss = 0.0
    
    all_features = []
    all_reconstructions = []
    
    with torch.no_grad():
        for data, _ in tqdm(test_loader, desc='Evaluating'):
            data = data.to(device)
            
            # Forward pass
            if model_type == 'vae':
                recon_data, mu, logvar = model(data)
                loss, recon_loss, kl_loss = vae_loss(recon_data, data, mu, logvar, beta)
                total_kl_loss += kl_loss.item()
                
                # Use mu as features for VAE
                features = mu
            else:
                recon_data = model(data)
                loss = nn.functional.mse_loss(recon_data, data, reduction='sum')
                recon_loss = loss
                
                # Extract features from encoder
                if hasattr(model, 'encode'):
                    features = model.encode(data)
                else:
                    # For simple autoencoders, get the bottleneck representation
                    features = model.encoder(data.view(data.size(0), -1))
            
            total_loss += loss.item()
            total_recon_loss += recon_loss.item()
            
            # Store features and reconstructions for analysis
            all_features.append(features.cpu())
            all_reconstructions.append(recon_data.cpu())
    
    avg_loss = total_loss / len(test_loader.dataset)
    avg_recon_loss = total_recon_loss / len(test_loader.dataset)
    avg_kl_loss = total_kl_loss / len(test_loader.dataset) if model_type == 'vae' else 0.0
    
    # Concatenate features and reconstructions
    features_tensor = torch.cat(all_features, dim=0)
    reconstructions_tensor = torch.cat(all_reconstructions, dim=0)
    
    return avg_loss, avg_recon_loss, avg_kl_loss, features_tensor, reconstructions_tensor


def save_checkpoint(model: nn.Module, optimizer: optim.Optimizer, epoch: int,
                   loss: float, model_config: Dict, checkpoint_dir: str = 'models') -> str:
    """Save model checkpoint."""
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
        'model_config': model_config
    }
    
    checkpoint_path = os.path.join(checkpoint_dir, f'autoencoder_model_epoch_{epoch}.pth')
    torch.save(checkpoint, checkpoint_path)
    
    return checkpoint_path


def generate_samples(model: nn.Module, device: torch.device, num_samples: int = 10,
                    latent_dim: int = 64) -> Optional[torch.Tensor]:
    """Generate samples from VAE."""
    if not hasattr(model, 'decode'):
        return None
    
    model.eval()
    with torch.no_grad():
        # Sample from standard normal distribution
        z = torch.randn(num_samples, latent_dim).to(device)
        samples = model.decode(z)
        return samples.cpu()


def interpolate_latent_space(model: nn.Module, start_data: torch.Tensor, 
                           end_data: torch.Tensor, device: torch.device,
                           num_steps: int = 10) -> Optional[torch.Tensor]:
    """Interpolate in latent space between two data points."""
    if not hasattr(model, 'encode') or not hasattr(model, 'decode'):
        return None
    
    model.eval()
    with torch.no_grad():
        start_data = start_data.to(device)
        end_data = end_data.to(device)
        
        # Encode data points
        if hasattr(model, 'reparameterize'):  # VAE
            start_mu, start_logvar = model.encode(start_data)
            end_mu, end_logvar = model.encode(end_data)
            start_z = start_mu
            end_z = end_mu
        else:  # Standard autoencoder
            start_z = model.encode(start_data)
            end_z = model.encode(end_data)
        
        # Interpolate
        interpolations = []
        for i in range(num_steps):
            alpha = i / (num_steps - 1)
            z_interp = (1 - alpha) * start_z + alpha * end_z
            x_interp = model.decode(z_interp)
            interpolations.append(x_interp.cpu())
        
        return torch.stack(interpolations)


def train_autoencoder(dataset: str = 'mnist', model_type: str = 'standard',
                     epochs: int = 50, batch_size: int = 64, learning_rate: float = 0.001,
                     latent_dim: int = 64, hidden_dims: List[int] = [512, 256, 128],
                     beta: float = 1.0, device: str = 'auto', save_features: bool = True,
                     checkpoint_dir: str = 'models', log_dir: str = 'logs') -> Dict:
    """
    Main training function for Autoencoder models.
    
    Args:
        dataset: Dataset to use ('mnist', 'fashion_mnist')
        model_type: Type of autoencoder ('standard', 'conv', 'vae')
        epochs: Number of training epochs
        batch_size: Batch size
        learning_rate: Learning rate
        latent_dim: Latent space dimension
        hidden_dims: List of hidden layer dimensions
        beta: Beta parameter for VAE (controls KL weight)
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
    if dataset == 'mnist':
        train_loader, test_loader = get_mnist_loaders(batch_size=batch_size)
        input_dim = 28 * 28  # For fully connected autoencoder
        input_channels = 1   # For convolutional autoencoder
    elif dataset == 'fashion_mnist':
        train_loader, test_loader = get_fashion_mnist_loaders(batch_size=batch_size)
        input_dim = 28 * 28
        input_channels = 1
    else:
        raise ValueError(f"Unsupported dataset: {dataset}")
    
    logger.info(f"Dataset loaded: {len(train_loader.dataset)} training samples, "
                f"{len(test_loader.dataset)} test samples")
    
    # Model configuration
    model_config = {
        'model_type': model_type,
        'input_dim': input_dim,
        'input_channels': input_channels,
        'latent_dim': latent_dim,
        'hidden_dims': hidden_dims,
        'beta': beta,
        'dataset': dataset
    }
    
    # Create model
    logger.info(f"Creating {model_type} autoencoder...")
    model = create_autoencoder_model(
        model_type=model_type,
        input_dim=input_dim,
        input_channels=input_channels,
        latent_dim=latent_dim,
        hidden_dims=hidden_dims
    ).to(device)
    
    logger.info(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Optimizer
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
    
    # Training history
    train_losses = []
    train_recon_losses = []
    train_kl_losses = []
    val_losses = []
    val_recon_losses = []
    val_kl_losses = []
    
    best_val_loss = float('inf')
    best_model_path = None
    
    logger.info("Starting training...")
    start_time = time.time()
    
    for epoch in range(1, epochs + 1):
        logger.info(f"\nEpoch {epoch}/{epochs}")
        
        # Train
        train_loss, train_recon_loss, train_kl_loss = train_epoch(
            model, train_loader, optimizer, device, epoch, model_type, beta
        )
        train_losses.append(train_loss)
        train_recon_losses.append(train_recon_loss)
        train_kl_losses.append(train_kl_loss)
        
        # Evaluate
        val_loss, val_recon_loss, val_kl_loss, features, reconstructions = evaluate(
            model, test_loader, device, model_type, beta
        )
        val_losses.append(val_loss)
        val_recon_losses.append(val_recon_loss)
        val_kl_losses.append(val_kl_loss)
        
        # Learning rate scheduling
        scheduler.step(val_loss)
        current_lr = optimizer.param_groups[0]['lr']
        
        logger.info(f"Train Loss: {train_loss:.4f} (Recon: {train_recon_loss:.4f}, KL: {train_kl_loss:.4f})")
        logger.info(f"Val Loss: {val_loss:.4f} (Recon: {val_recon_loss:.4f}, KL: {val_kl_loss:.4f})")
        logger.info(f"Learning Rate: {current_lr:.6f}")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_path = save_checkpoint(
                model, optimizer, epoch, val_loss, model_config, checkpoint_dir
            )
            logger.info(f"New best model saved: {best_model_path}")
        
        # Save features and visualizations periodically
        if epoch % 10 == 0:
            results_dir = os.path.join('results', 'autoencoder')
            os.makedirs(results_dir, exist_ok=True)
            
            # Save features
            if save_features:
                features_path = os.path.join(results_dir, f'features_epoch_{epoch}.npz')
                np.savez(features_path,
                         features=features.numpy(),
                         reconstructions=reconstructions.numpy(),
                         epoch=epoch,
                         model_type=model_type)
                logger.info(f"Features saved: {features_path}")
            
            # Generate visualizations
            try:
                # Sample some test data for visualization
                test_data = next(iter(test_loader))[0][:10]
                
                # Visualize reconstructions
                model.eval()
                with torch.no_grad():
                    test_data_device = test_data.to(device)
                    if model_type == 'vae':
                        test_recon, _, _ = model(test_data_device)
                    else:
                        test_recon = model(test_data_device)
                
                visualize_reconstructions(
                    test_data, test_recon.cpu(),
                    save_path=os.path.join(results_dir, f'reconstructions_epoch_{epoch}.png'),
                    title=f'Reconstructions - Epoch {epoch}'
                )
                
                # Generate samples for VAE
                if model_type == 'vae':
                    samples = generate_samples(model, device, num_samples=10, latent_dim=latent_dim)
                    if samples is not None:
                        plt.figure(figsize=(12, 3))
                        for i in range(10):
                            plt.subplot(1, 10, i + 1)
                            if dataset in ['mnist', 'fashion_mnist']:
                                plt.imshow(samples[i].view(28, 28), cmap='gray')
                            plt.axis('off')
                        plt.suptitle(f'Generated Samples - Epoch {epoch}')
                        plt.tight_layout()
                        plt.savefig(os.path.join(results_dir, f'generated_samples_epoch_{epoch}.png'))
                        plt.close()
                
                # Latent space visualization for 2D latent space
                if latent_dim == 2:
                    plot_latent_space(
                        features.numpy(), 
                        save_path=os.path.join(results_dir, f'latent_space_epoch_{epoch}.png'),
                        title=f'Latent Space - Epoch {epoch}'
                    )
                
            except Exception as e:
                logger.warning(f"Visualization failed: {e}")
    
    training_time = time.time() - start_time
    logger.info(f"\nTraining completed in {training_time:.2f} seconds")
    logger.info(f"Best validation loss: {best_val_loss:.4f}")
    
    # Save training curves
    results_dir = os.path.join('results', 'autoencoder')
    os.makedirs(results_dir, exist_ok=True)
    
    # Plot losses
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.plot(train_losses, label='Train')
    plt.plot(val_losses, label='Validation')
    plt.title('Total Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.subplot(1, 3, 2)
    plt.plot(train_recon_losses, label='Train')
    plt.plot(val_recon_losses, label='Validation')
    plt.title('Reconstruction Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    if model_type == 'vae':
        plt.subplot(1, 3, 3)
        plt.plot(train_kl_losses, label='Train')
        plt.plot(val_kl_losses, label='Validation')
        plt.title('KL Divergence')
        plt.xlabel('Epoch')
        plt.ylabel('KL Loss')
        plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'training_curves.png'))
    plt.close()
    
    # Final evaluation and feature extraction
    logger.info("Performing final evaluation...")
    model.load_state_dict(torch.load(best_model_path)['model_state_dict'])
    final_loss, final_recon_loss, final_kl_loss, final_features, final_reconstructions = evaluate(
        model, test_loader, device, model_type, beta
    )
    
    logger.info(f"Final Test Loss: {final_loss:.4f}")
    logger.info(f"Final Reconstruction Loss: {final_recon_loss:.4f}")
    if model_type == 'vae':
        logger.info(f"Final KL Loss: {final_kl_loss:.4f}")
    
    # Save final features
    if save_features:
        final_features_path = os.path.join(results_dir, 'final_features.npz')
        np.savez(final_features_path,
                 features=final_features.numpy(),
                 reconstructions=final_reconstructions.numpy(),
                 model_type=model_type,
                 dataset=dataset,
                 final_loss=final_loss)
        logger.info(f"Final features saved: {final_features_path}")
    
    # Save training configuration and results
    results = {
        'model_config': model_config,
        'training_config': {
            'epochs': epochs,
            'batch_size': batch_size,
            'learning_rate': learning_rate,
            'dataset': dataset,
            'beta': beta if model_type == 'vae' else None
        },
        'results': {
            'best_val_loss': best_val_loss,
            'final_test_loss': final_loss,
            'final_recon_loss': final_recon_loss,
            'final_kl_loss': final_kl_loss if model_type == 'vae' else None,
            'training_time': training_time,
            'train_losses': train_losses,
            'val_losses': val_losses,
            'train_recon_losses': train_recon_losses,
            'val_recon_losses': val_recon_losses,
            'train_kl_losses': train_kl_losses if model_type == 'vae' else [],
            'val_kl_losses': val_kl_losses if model_type == 'vae' else []
        },
        'model_path': best_model_path,
        'features_path': final_features_path if save_features else None
    }
    
    # Save results as JSON
    results_file = os.path.join(results_dir, 'training_results.json')
    with open(results_file, 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        json_results = results.copy()
        for key in ['train_losses', 'val_losses', 'train_recon_losses', 'val_recon_losses', 
                   'train_kl_losses', 'val_kl_losses']:
            if key in json_results['results']:
                json_results['results'][key] = [float(x) for x in json_results['results'][key]]
        json.dump(json_results, f, indent=2)
    
    logger.info(f"Training results saved: {results_file}")
    
    return results


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description='Train Autoencoder for feature learning')
    
    parser.add_argument('--dataset', type=str, default='mnist',
                        choices=['mnist', 'fashion_mnist'],
                        help='Dataset to use (default: mnist)')
    
    parser.add_argument('--model', type=str, default='standard',
                        choices=['standard', 'conv', 'vae'],
                        help='Autoencoder model type (default: standard)')
    
    parser.add_argument('--epochs', type=int, default=50,
                        help='Number of training epochs (default: 50)')
    
    parser.add_argument('--batch-size', type=int, default=64,
                        help='Batch size (default: 64)')
    
    parser.add_argument('--lr', type=float, default=0.001,
                        help='Learning rate (default: 0.001)')
    
    parser.add_argument('--latent-dim', type=int, default=64,
                        help='Latent space dimension (default: 64)')
    
    parser.add_argument('--hidden-dims', type=int, nargs='+', default=[512, 256, 128],
                        help='Hidden layer dimensions (default: [512, 256, 128])')
    
    parser.add_argument('--beta', type=float, default=1.0,
                        help='Beta parameter for VAE (default: 1.0)')
    
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
    results = train_autoencoder(
        dataset=args.dataset,
        model_type=args.model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        latent_dim=args.latent_dim,
        hidden_dims=args.hidden_dims,
        beta=args.beta,
        device=args.device,
        save_features=not args.no_save_features,
        checkpoint_dir=args.checkpoint_dir,
        log_dir=args.log_dir
    )
    
    print(f"\nTraining completed!")
    print(f"Best validation loss: {results['results']['best_val_loss']:.4f}")
    print(f"Final test loss: {results['results']['final_test_loss']:.4f}")
    print(f"Final reconstruction loss: {results['results']['final_recon_loss']:.4f}")


if __name__ == '__main__':
    main()
