"""
Autoencoder models for unsupervised feature learning.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional
import numpy as np


class SimpleAutoencoder(nn.Module):
    """Simple fully connected autoencoder."""
    
    def __init__(self, input_dim: int, hidden_dims: list = [512, 256, 128], 
                 latent_dim: int = 64, dropout: float = 0.2):
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
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        # Latent layer
        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Decoder
        decoder_layers = []
        prev_dim = latent_dim
        
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        # Output layer
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)
    
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to latent representation."""
        x = x.view(x.size(0), -1)  # Flatten input
        return self.encoder(x)
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent representation to output."""
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass returning reconstruction and latent features."""
        z = self.encode(x)
        x_reconstructed = self.decode(z)
        return x_reconstructed, z
    
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract latent features."""
        return self.encode(x)


class ConvAutoencoder(nn.Module):
    """Convolutional autoencoder for image data."""
    
    def __init__(self, input_channels: int = 1, latent_dim: int = 128):
        super(ConvAutoencoder, self).__init__()
        
        self.input_channels = input_channels
        self.latent_dim = latent_dim
        
        # Encoder
        self.encoder = nn.Sequential(
            # 28x28 -> 14x14
            nn.Conv2d(input_channels, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2),
            
            # 14x14 -> 7x7
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2),
            
            # 7x7 -> 3x3 (approximately)
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2),
        )
        
        # Calculate the flattened size after convolutions
        # For 28x28 input: 28 -> 14 -> 7 -> 3 (with padding and stride)
        self.flattened_size = 128 * 3 * 3
        
        # Latent space
        self.encoder_fc = nn.Linear(self.flattened_size, latent_dim)
        self.decoder_fc = nn.Linear(latent_dim, self.flattened_size)
        
        # Decoder
        self.decoder = nn.Sequential(
            # 3x3 -> 7x7
            nn.ConvTranspose2d(128, 64, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.ReLU(inplace=True),
            
            # 7x7 -> 14x14
            nn.ConvTranspose2d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.ReLU(inplace=True),
            
            # 14x14 -> 28x28
            nn.ConvTranspose2d(32, input_channels, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.Sigmoid()  # Assuming normalized input [0, 1]
        )
    
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to latent representation."""
        # Convolutional encoding
        conv_out = self.encoder(x)
        
        # Flatten and encode to latent space
        flattened = conv_out.view(x.size(0), -1)
        latent = self.encoder_fc(flattened)
        
        return latent
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent representation to output."""
        # Decode from latent space
        decoded = self.decoder_fc(z)
        
        # Reshape for deconvolution
        reshaped = decoded.view(z.size(0), 128, 3, 3)
        
        # Deconvolutional decoding
        output = self.decoder(reshaped)
        
        return output
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass returning reconstruction and latent features."""
        z = self.encode(x)
        x_reconstructed = self.decode(z)
        return x_reconstructed, z
    
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract latent features."""
        return self.encode(x)


class VariationalAutoencoder(nn.Module):
    """Variational Autoencoder (VAE) for probabilistic feature learning."""
    
    def __init__(self, input_dim: int, hidden_dims: list = [512, 256], 
                 latent_dim: int = 64, dropout: float = 0.2):
        super(VariationalAutoencoder, self).__init__()
        
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        
        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Mean and log variance layers
        self.fc_mu = nn.Linear(prev_dim, latent_dim)
        self.fc_logvar = nn.Linear(prev_dim, latent_dim)
        
        # Decoder
        decoder_layers = []
        prev_dim = latent_dim
        
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        # Output layer
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)
    
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode input to mean and log variance."""
        x = x.view(x.size(0), -1)  # Flatten input
        encoded = self.encoder(x)
        
        mu = self.fc_mu(encoded)
        logvar = self.fc_logvar(encoded)
        
        return mu, logvar
    
    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """Reparameterization trick for VAE."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent representation to output."""
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Forward pass returning reconstruction, latent sample, mu, and logvar."""
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        x_reconstructed = self.decode(z)
        
        return x_reconstructed, z, mu, logvar
    
    def extract_features(self, x: torch.Tensor, use_mean: bool = True) -> torch.Tensor:
        """Extract latent features."""
        mu, logvar = self.encode(x)
        
        if use_mean:
            return mu  # Use mean as deterministic features
        else:
            return self.reparameterize(mu, logvar)  # Use sampled features
    
    def sample(self, num_samples: int, device: torch.device) -> torch.Tensor:
        """Generate samples from the learned latent distribution."""
        z = torch.randn(num_samples, self.latent_dim, device=device)
        samples = self.decode(z)
        return samples


class ConvVAE(nn.Module):
    """Convolutional Variational Autoencoder."""
    
    def __init__(self, input_channels: int = 1, latent_dim: int = 128):
        super(ConvVAE, self).__init__()
        
        self.input_channels = input_channels
        self.latent_dim = latent_dim
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2),
            
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2),
            
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2),
        )
        
        self.flattened_size = 128 * 3 * 3
        
        # Mean and log variance layers
        self.fc_mu = nn.Linear(self.flattened_size, latent_dim)
        self.fc_logvar = nn.Linear(self.flattened_size, latent_dim)
        
        # Decoder
        self.decoder_fc = nn.Linear(latent_dim, self.flattened_size)
        
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.ReLU(inplace=True),
            
            nn.ConvTranspose2d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.ReLU(inplace=True),
            
            nn.ConvTranspose2d(32, input_channels, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.Sigmoid()
        )
    
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode input to mean and log variance."""
        conv_out = self.encoder(x)
        flattened = conv_out.view(x.size(0), -1)
        
        mu = self.fc_mu(flattened)
        logvar = self.fc_logvar(flattened)
        
        return mu, logvar
    
    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """Reparameterization trick."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent representation to output."""
        decoded = self.decoder_fc(z)
        reshaped = decoded.view(z.size(0), 128, 3, 3)
        output = self.decoder(reshaped)
        return output
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Forward pass."""
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        x_reconstructed = self.decode(z)
        
        return x_reconstructed, z, mu, logvar
    
    def extract_features(self, x: torch.Tensor, use_mean: bool = True) -> torch.Tensor:
        """Extract latent features."""
        mu, logvar = self.encode(x)
        return mu if use_mean else self.reparameterize(mu, logvar)


def vae_loss(recon_x: torch.Tensor, x: torch.Tensor, mu: torch.Tensor, 
             logvar: torch.Tensor, beta: float = 1.0) -> torch.Tensor:
    """
    VAE loss function combining reconstruction loss and KL divergence.
    
    Args:
        recon_x: Reconstructed input
        x: Original input
        mu: Mean from encoder
        logvar: Log variance from encoder
        beta: Weight for KL divergence term
        
    Returns:
        VAE loss
    """
    # Reconstruction loss (binary cross-entropy or MSE)
    recon_loss = F.mse_loss(recon_x, x.view_as(recon_x), reduction='sum')
    
    # KL divergence loss
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    
    return recon_loss + beta * kl_loss


def create_autoencoder_model(model_type: str, **kwargs) -> nn.Module:
    """
    Factory function to create autoencoder models.
    
    Args:
        model_type: Type of model ('simple', 'conv', 'vae', 'conv_vae')
        **kwargs: Additional arguments for model initialization
        
    Returns:
        Autoencoder model instance
    """
    if model_type == 'simple':
        return SimpleAutoencoder(**kwargs)
    elif model_type == 'conv':
        return ConvAutoencoder(**kwargs)
    elif model_type == 'vae':
        return VariationalAutoencoder(**kwargs)
    elif model_type == 'conv_vae':
        return ConvVAE(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def create_autoencoder_model(model_type: str = 'standard', input_dim: int = 784,
                            input_channels: int = 1, latent_dim: int = 64,
                            hidden_dims: list = [512, 256, 128]) -> torch.nn.Module:
    """
    Factory function to create autoencoder models.
    
    Args:
        model_type: Type of autoencoder ('standard', 'conv', 'vae')
        input_dim: Input dimension for fully connected autoencoders
        input_channels: Number of input channels for convolutional autoencoders
        latent_dim: Latent space dimension
        hidden_dims: List of hidden layer dimensions
        
    Returns:
        Autoencoder model instance
    """
    if model_type == 'standard':
        return SimpleAutoencoder(input_dim=input_dim, hidden_dims=hidden_dims, latent_dim=latent_dim)
    elif model_type == 'conv':
        return ConvAutoencoder(input_channels=input_channels, latent_dim=latent_dim)
    elif model_type == 'vae':
        return VariationalAutoencoder(input_dim=input_dim, hidden_dims=hidden_dims, latent_dim=latent_dim)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")


if __name__ == "__main__":
    """Test autoencoder models."""
    print("Testing autoencoder models...")
    
    batch_size = 4
    input_dim = 28 * 28
    
    # Test SimpleAutoencoder
    model = SimpleAutoencoder(input_dim=input_dim, latent_dim=64)
    x = torch.randn(batch_size, input_dim)
    recon, features = model(x)
    print(f"SimpleAutoencoder - Input: {x.shape}, Reconstruction: {recon.shape}, Features: {features.shape}")
    
    # Test ConvAutoencoder
    model = ConvAutoencoder(input_channels=1, latent_dim=128)
    x = torch.randn(batch_size, 1, 28, 28)
    recon, features = model(x)
    print(f"ConvAutoencoder - Input: {x.shape}, Reconstruction: {recon.shape}, Features: {features.shape}")
    
    # Test VariationalAutoencoder
    model = VariationalAutoencoder(input_dim=input_dim, latent_dim=64)
    x = torch.randn(batch_size, input_dim)
    recon, z, mu, logvar = model(x)
    print(f"VAE - Input: {x.shape}, Reconstruction: {recon.shape}, Latent: {z.shape}")
    
    print("Autoencoder models test completed!")
