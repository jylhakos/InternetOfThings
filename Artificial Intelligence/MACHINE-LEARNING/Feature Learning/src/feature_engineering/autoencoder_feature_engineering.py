#!/usr/bin/env python3
"""
Autoencoder Feature Engineering with PyTorch

This script demonstrates feature engineering using Autoencoder architectures.
- A fully-connected autoencoders
- Convolutional autoencoders for image data
- Variational autoencoders (VAE) for generative modeling
- Denoising autoencoders for robust feature learning
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, random_split
import torchvision
import torchvision.transforms as transforms
from torchvision import datasets

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import os
import time
import pickle
import argparse
from scipy.stats import multivariate_normal

# Set random seeds
torch.manual_seed(42)
np.random.seed(42)


class SimpleAutoencoder(nn.Module):
    """
    A fully-connected autoencoder for feature learning
    """
    
    def __init__(self, input_dim=784, hidden_dims=[512, 256, 128], latent_dim=64):
        super(SimpleAutoencoder, self).__init__()
        
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        
        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(inplace=True),
                nn.Dropout(0.2)
            ])
            prev_dim = hidden_dim
        
        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Decoder
        decoder_layers = []
        prev_dim = latent_dim
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(inplace=True),
                nn.Dropout(0.2)
            ])
            prev_dim = hidden_dim
        
        decoder_layers.extend([
            nn.Linear(prev_dim, input_dim),
            nn.Sigmoid()  # For normalized input data
        ])
        self.decoder = nn.Sequential(*decoder_layers)
        
    def encode(self, x):
        """Encode input to latent representation"""
        return self.encoder(x)
    
    def decode(self, z):
        """Decode latent representation to reconstruction"""
        return self.decoder(z)
    
    def forward(self, x):
        """Forward pass through autoencoder"""
        z = self.encode(x)
        reconstruction = self.decode(z)
        return reconstruction, z


class ConvAutoencoder(nn.Module):
    """
    Convolutional autoencoder for image data
    """
    
    def __init__(self, input_channels=1, base_channels=32, latent_dim=128):
        super(ConvAutoencoder, self).__init__()
        
        self.latent_dim = latent_dim
        
        # Encoder
        self.encoder = nn.Sequential(
            # 28x28 -> 14x14
            nn.Conv2d(input_channels, base_channels, 4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            
            # 14x14 -> 7x7
            nn.Conv2d(base_channels, base_channels*2, 4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            
            # 7x7 -> 3x3
            nn.Conv2d(base_channels*2, base_channels*4, 4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            
            nn.Flatten(),
            nn.Linear(base_channels*4*3*3, latent_dim)
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, base_channels*4*3*3),
            nn.ReLU(inplace=True),
            nn.Unflatten(1, (base_channels*4, 3, 3)),
            
            # 3x3 -> 7x7
            nn.ConvTranspose2d(base_channels*4, base_channels*2, 4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            
            # 7x7 -> 14x14
            nn.ConvTranspose2d(base_channels*2, base_channels, 4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            
            # 14x14 -> 28x28
            nn.ConvTranspose2d(base_channels, input_channels, 4, stride=2, padding=1),
            nn.Sigmoid()
        )
        
    def encode(self, x):
        """Encode input to latent representation"""
        return self.encoder(x)
    
    def decode(self, z):
        """Decode latent representation to reconstruction"""
        return self.decoder(z)
    
    def forward(self, x):
        """Forward pass through autoencoder"""
        z = self.encode(x)
        reconstruction = self.decode(z)
        return reconstruction, z


class VariationalAutoencoder(nn.Module):
    """
    Variational Autoencoder (VAE) for generative feature learning
    """
    
    def __init__(self, input_dim=784, hidden_dims=[512, 256], latent_dim=64):
        super(VariationalAutoencoder, self).__init__()
        
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        
        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(inplace=True)
            ])
            prev_dim = hidden_dim
        
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Mean and log variance layers
        self.mu_layer = nn.Linear(prev_dim, latent_dim)
        self.logvar_layer = nn.Linear(prev_dim, latent_dim)
        
        # Decoder
        decoder_layers = []
        prev_dim = latent_dim
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(inplace=True)
            ])
            prev_dim = hidden_dim
        
        decoder_layers.extend([
            nn.Linear(prev_dim, input_dim),
            nn.Sigmoid()
        ])
        self.decoder = nn.Sequential(*decoder_layers)
        
    def encode(self, x):
        """Encode input to latent parameters"""
        h = self.encoder(x)
        mu = self.mu_layer(h)
        logvar = self.logvar_layer(h)
        return mu, logvar
    
    def reparameterize(self, mu, logvar):
        """Reparameterization trick for VAE"""
        if self.training:
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            return mu + eps * std
        else:
            return mu
    
    def decode(self, z):
        """Decode latent representation to reconstruction"""
        return self.decoder(z)
    
    def forward(self, x):
        """Forward pass through VAE"""
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        reconstruction = self.decode(z)
        return reconstruction, z, mu, logvar


class DenoisingAutoencoder(nn.Module):
    """
    Denoising autoencoder for robust feature learning
    """
    
    def __init__(self, input_dim=784, hidden_dims=[512, 256, 128], latent_dim=64, noise_factor=0.3):
        super(DenoisingAutoencoder, self).__init__()
        
        self.noise_factor = noise_factor
        
        # Use SimpleAutoencoder architecture
        self.autoencoder = SimpleAutoencoder(input_dim, hidden_dims, latent_dim)
        
    def add_noise(self, x):
        """Add noise to input data"""
        if self.training:
            noise = torch.randn_like(x) * self.noise_factor
            return torch.clamp(x + noise, 0, 1)
        return x
    
    def encode(self, x):
        """Encode input to latent representation"""
        return self.autoencoder.encode(x)
    
    def decode(self, z):
        """Decode latent representation to reconstruction"""
        return self.autoencoder.decode(z)
    
    def forward(self, x):
        """Forward pass through denoising autoencoder"""
        noisy_x = self.add_noise(x)
        reconstruction, z = self.autoencoder(noisy_x)
        return reconstruction, z, noisy_x


class AutoencoderFeatureTrainer:
    """
    Trainer class for autoencoder feature extraction models
    """
    
    def __init__(self, model, model_type='simple', device='cpu'):
        self.model = model.to(device)
        self.model_type = model_type
        self.device = device
        self.train_losses = []
        self.val_losses = []
        
    def compute_loss(self, reconstruction, target, model_output=None):
        """Compute appropriate loss based on model type"""
        recon_loss = F.mse_loss(reconstruction, target, reduction='mean')
        
        if self.model_type == 'vae' and model_output is not None:
            # VAE loss with KL divergence
            _, _, mu, logvar = model_output
            kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
            kl_loss /= target.size(0) * target.size(1)  # Normalize by batch size and input dim
            total_loss = recon_loss + 0.1 * kl_loss  # Beta = 0.1
            return total_loss, recon_loss, kl_loss
        
        return recon_loss, recon_loss, 0.0
    
    def train_epoch(self, train_loader, optimizer):
        """Train for one epoch"""
        self.model.train()
        running_loss = 0.0
        running_recon_loss = 0.0
        running_kl_loss = 0.0
        
        for batch_idx, (data, _) in enumerate(train_loader):
            data = data.to(self.device)
            
            # Flatten data if needed
            if len(data.shape) > 2 and self.model_type in ['simple', 'vae', 'denoising']:
                data = data.view(data.size(0), -1)
            
            optimizer.zero_grad()
            
            # Forward pass
            if self.model_type == 'vae':
                reconstruction, z, mu, logvar = self.model(data)
                model_output = (reconstruction, z, mu, logvar)
                target = data
            elif self.model_type == 'denoising':
                reconstruction, z, noisy_data = self.model(data)
                model_output = (reconstruction, z)
                target = data  # Reconstruct original, not noisy
            else:
                reconstruction, z = self.model(data)
                model_output = (reconstruction, z)
                target = data
            
            # Compute loss
            total_loss, recon_loss, kl_loss = self.compute_loss(
                reconstruction, target, model_output if self.model_type == 'vae' else None
            )
            
            total_loss.backward()
            optimizer.step()
            
            running_loss += total_loss.item()
            running_recon_loss += recon_loss.item()
            running_kl_loss += kl_loss if isinstance(kl_loss, float) else kl_loss.item()
            
            if batch_idx % 100 == 0:
                print(f'Batch {batch_idx}/{len(train_loader)}, '
                      f'Total Loss: {total_loss.item():.6f}, '
                      f'Recon Loss: {recon_loss.item():.6f}')
                
        epoch_loss = running_loss / len(train_loader)
        epoch_recon_loss = running_recon_loss / len(train_loader)
        epoch_kl_loss = running_kl_loss / len(train_loader)
        
        return epoch_loss, epoch_recon_loss, epoch_kl_loss
    
    def validate_epoch(self, val_loader):
        """Validate for one epoch"""
        self.model.eval()
        running_loss = 0.0
        running_recon_loss = 0.0
        running_kl_loss = 0.0
        
        with torch.no_grad():
            for data, _ in val_loader:
                data = data.to(self.device)
                
                if len(data.shape) > 2 and self.model_type in ['simple', 'vae', 'denoising']:
                    data = data.view(data.size(0), -1)
                
                if self.model_type == 'vae':
                    reconstruction, z, mu, logvar = self.model(data)
                    model_output = (reconstruction, z, mu, logvar)
                    target = data
                elif self.model_type == 'denoising':
                    reconstruction, z, noisy_data = self.model(data)
                    model_output = (reconstruction, z)
                    target = data
                else:
                    reconstruction, z = self.model(data)
                    model_output = (reconstruction, z)
                    target = data
                
                total_loss, recon_loss, kl_loss = self.compute_loss(
                    reconstruction, target, model_output if self.model_type == 'vae' else None
                )
                
                running_loss += total_loss.item()
                running_recon_loss += recon_loss.item()
                running_kl_loss += kl_loss if isinstance(kl_loss, float) else kl_loss.item()
                
        epoch_loss = running_loss / len(val_loader)
        epoch_recon_loss = running_recon_loss / len(val_loader)
        epoch_kl_loss = running_kl_loss / len(val_loader)
        
        return epoch_loss, epoch_recon_loss, epoch_kl_loss
    
    def train(self, train_loader, val_loader, epochs=10, lr=0.001):
        """Full training loop"""
        optimizer = optim.Adam(self.model.parameters(), lr=lr, weight_decay=1e-5)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5)
        
        print(f"Starting training for {epochs} epochs...")
        print(f"Model has {sum(p.numel() for p in self.model.parameters()):,} parameters")
        print(f"Model type: {self.model_type}")
        
        for epoch in range(epochs):
            start_time = time.time()
            
            train_loss, train_recon, train_kl = self.train_epoch(train_loader, optimizer)
            val_loss, val_recon, val_kl = self.validate_epoch(val_loader)
            
            scheduler.step(val_loss)
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            
            epoch_time = time.time() - start_time
            print(f'Epoch {epoch+1}/{epochs} ({epoch_time:.1f}s)')
            print(f'Train Loss: {train_loss:.4f} (Recon: {train_recon:.4f}, KL: {train_kl:.4f})')
            print(f'Val Loss: {val_loss:.4f} (Recon: {val_recon:.4f}, KL: {val_kl:.4f})')
            print('-' * 70)
            
        return self.train_losses, self.val_losses


def visualize_reconstructions(model, data_loader, device, num_samples=8, save_path=None):
    """
    Visualize original images and their reconstructions
    """
    model.eval()
    
    # Get a batch of data
    data, _ = next(iter(data_loader))
    data = data[:num_samples].to(device)
    
    with torch.no_grad():
        if hasattr(model, 'model_type') and model.model_type == 'vae':
            reconstruction, _, _, _ = model(data.view(data.size(0), -1))
        elif hasattr(model, 'model_type') and model.model_type == 'denoising':
            reconstruction, _, noisy_data = model(data.view(data.size(0), -1))
        else:
            if len(data.shape) > 2:
                flat_data = data.view(data.size(0), -1)
                reconstruction, _ = model(flat_data)
            else:
                reconstruction, _ = model(data)
    
    # Reshape for visualization
    if len(data.shape) == 4:  # Image data
        original = data.cpu()
        reconstructed = reconstruction.view(data.shape).cpu()
    else:
        original = data.cpu()
        reconstructed = reconstruction.cpu()
    
    # Create visualization
    fig, axes = plt.subplots(2, num_samples, figsize=(num_samples * 2, 4))
    
    for i in range(num_samples):
        # Original
        if len(original.shape) == 4:
            axes[0, i].imshow(original[i].squeeze(), cmap='gray')
        else:
            axes[0, i].imshow(original[i].view(28, 28), cmap='gray')
        axes[0, i].set_title(f'Original {i+1}')
        axes[0, i].axis('off')
        
        # Reconstruction
        if len(reconstructed.shape) == 4:
            axes[1, i].imshow(reconstructed[i].squeeze(), cmap='gray')
        else:
            axes[1, i].imshow(reconstructed[i].view(28, 28), cmap='gray')
        axes[1, i].set_title(f'Reconstructed {i+1}')
        axes[1, i].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Reconstructions saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def visualize_latent_space(model, data_loader, device, num_samples=2000, save_path=None):
    """
    Visualize the learned latent space
    """
    model.eval()
    latent_vectors = []
    labels = []
    
    print("Extracting latent representations...")
    with torch.no_grad():
        for i, (data, target) in enumerate(data_loader):
            if len(latent_vectors) * data_loader.batch_size >= num_samples:
                break
                
            data = data.to(device)
            
            # Flatten data if needed
            if len(data.shape) > 2 and not hasattr(model, 'encoder'):
                data = data.view(data.size(0), -1)
            
            # Extract latent features
            if hasattr(model, 'encode'):
                if isinstance(model, VariationalAutoencoder):
                    mu, logvar = model.encode(data)
                    z = model.reparameterize(mu, logvar)
                else:
                    z = model.encode(data)
            else:
                _, z = model(data)
            
            latent_vectors.append(z.cpu().numpy())
            labels.append(target.numpy())
    
    all_latent = np.concatenate(latent_vectors, axis=0)
    all_labels = np.concatenate(labels, axis=0)
    
    print(f"Visualizing {len(all_latent)} samples with {all_latent.shape[1]} latent dimensions")
    
    # Create visualization
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # PCA visualization
    if all_latent.shape[1] > 2:
        pca = PCA(n_components=2, random_state=42)
        latent_pca = pca.fit_transform(all_latent)
        
        scatter = axes[0].scatter(latent_pca[:, 0], latent_pca[:, 1], 
                                c=all_labels, cmap='tab10', alpha=0.6, s=20)
        axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2f})')
        axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2f})')
        axes[0].set_title('Autoencoder Latent Space - PCA')
        axes[0].grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=axes[0])
    else:
        axes[0].scatter(all_latent[:, 0], all_latent[:, 1] if all_latent.shape[1] > 1 else np.zeros_like(all_latent[:, 0]), 
                       c=all_labels, cmap='tab10', alpha=0.6, s=20)
        axes[0].set_xlabel('Latent Dim 1')
        axes[0].set_ylabel('Latent Dim 2')
        axes[0].set_title('Autoencoder Latent Space')
        axes[0].grid(True, alpha=0.3)
    
    # t-SNE visualization
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    latent_tsne = tsne.fit_transform(all_latent[:min(1000, len(all_latent))])
    labels_tsne = all_labels[:min(1000, len(all_labels))]
    
    scatter2 = axes[1].scatter(latent_tsne[:, 0], latent_tsne[:, 1], 
                             c=labels_tsne, cmap='tab10', alpha=0.6, s=20)
    axes[1].set_xlabel('t-SNE 1')
    axes[1].set_ylabel('t-SNE 2')
    axes[1].set_title('Autoencoder Latent Space - t-SNE')
    axes[1].grid(True, alpha=0.3)
    plt.colorbar(scatter2, ax=axes[1])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Latent space visualization saved to {save_path}")
    else:
        plt.show()
    
    plt.close()
    return all_latent, all_labels


def prepare_datasets(dataset_name='MNIST', batch_size=128):
    """
    Prepare datasets for autoencoder training
    """
    if dataset_name == 'MNIST':
        transform = transforms.Compose([
            transforms.ToTensor()
        ])
        
        full_train_dataset = datasets.MNIST(
            root='../datasets', train=True, download=True, transform=transform
        )
        test_dataset = datasets.MNIST(
            root='../datasets', train=False, download=True, transform=transform
        )
        
        input_dim = 784
        input_channels = 1
        
    elif dataset_name == 'FASHIONMNIST':
        transform = transforms.Compose([
            transforms.ToTensor()
        ])
        
        full_train_dataset = datasets.FashionMNIST(
            root='../datasets', train=True, download=True, transform=transform
        )
        test_dataset = datasets.FashionMNIST(
            root='../datasets', train=False, download=True, transform=transform
        )
        
        input_dim = 784
        input_channels = 1
    
    else:
        raise ValueError(f"Unsupported dataset: {dataset_name}")
    
    # Split training set into train and validation
    train_size = int(0.9 * len(full_train_dataset))
    val_size = len(full_train_dataset) - train_size
    
    train_dataset, val_dataset = random_split(
        full_train_dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    return train_loader, val_loader, test_loader, input_dim, input_channels


def main():
    parser = argparse.ArgumentParser(description='Autoencoder Feature Engineering')
    parser.add_argument('--model', default='simple', 
                      choices=['simple', 'conv', 'vae', 'denoising'],
                      help='Autoencoder model type')
    parser.add_argument('--dataset', default='MNIST', 
                      choices=['MNIST', 'FASHIONMNIST'],
                      help='Dataset to use')
    parser.add_argument('--epochs', type=int, default=20, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=128, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--latent-dim', type=int, default=64, help='Latent dimension')
    parser.add_argument('--no-train', action='store_true', help='Skip training')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    
    args = parser.parse_args()
    
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create output directories
    os.makedirs('../results/autoencoder_features', exist_ok=True)
    os.makedirs('../models', exist_ok=True)
    
    # Prepare datasets
    print(f"Preparing {args.dataset} dataset...")
    train_loader, val_loader, test_loader, input_dim, input_channels = prepare_datasets(
        args.dataset, args.batch_size
    )
    
    # Create model
    if args.model == 'simple':
        model = SimpleAutoencoder(
            input_dim=input_dim,
            latent_dim=args.latent_dim
        )
    elif args.model == 'conv':
        model = ConvAutoencoder(
            input_channels=input_channels,
            latent_dim=args.latent_dim
        )
    elif args.model == 'vae':
        model = VariationalAutoencoder(
            input_dim=input_dim,
            latent_dim=args.latent_dim
        )
    elif args.model == 'denoising':
        model = DenoisingAutoencoder(
            input_dim=input_dim,
            latent_dim=args.latent_dim
        )
    
    print(f"Model: {args.model.upper()} Autoencoder")
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Latent dimension: {args.latent_dim}")
    
    # Training
    if not args.no_train:
        trainer = AutoencoderFeatureTrainer(model, args.model, device)
        train_losses, val_losses = trainer.train(
            train_loader, val_loader, args.epochs, args.lr
        )
        
        # Save model
        model_path = f'../models/autoencoder_features_{args.model}_{args.dataset.lower()}.pth'
        torch.save({
            'model_state_dict': model.state_dict(),
            'train_losses': train_losses,
            'val_losses': val_losses,
            'args': args
        }, model_path)
        print(f"Model saved to {model_path}")
        
        # Plot training curves
        plt.figure(figsize=(10, 4))
        plt.plot(train_losses, label='Train Loss')
        plt.plot(val_losses, label='Val Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title(f'{args.model.upper()} Autoencoder Training Loss')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'../results/autoencoder_features/training_curves_{args.model}_{args.dataset.lower()}.png')
        plt.show()
    
    # Visualizations
    if args.visualize:
        print("Generating visualizations...")
        
        # Visualize reconstructions
        visualize_reconstructions(
            model, test_loader, device, num_samples=8,
            save_path=f'../results/autoencoder_features/reconstructions_{args.model}_{args.dataset.lower()}.png'
        )
        
        # Visualize latent space
        latent_features, labels = visualize_latent_space(
            model, test_loader, device, num_samples=2000,
            save_path=f'../results/autoencoder_features/latent_space_{args.model}_{args.dataset.lower()}.png'
        )
        
        # Save extracted features
        features_path = f'../results/autoencoder_features/extracted_features_{args.model}_{args.dataset.lower()}.pkl'
        with open(features_path, 'wb') as f:
            pickle.dump({'features': latent_features, 'labels': labels}, f)
        print(f"Features saved to {features_path}")
    
    print("Autoencoder Feature Engineering completed!")


if __name__ == '__main__':
    main()
