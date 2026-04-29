"""
Visualization utilities for feature learning experiments.
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from typing import Tuple, Optional, List
import os


def visualize_features(features: np.ndarray, labels: np.ndarray = None, 
                      method: str = 'tsne', save_path: Optional[str] = None,
                      title: str = 'Feature Visualization') -> None:
    """
    Visualize high-dimensional features in 2D.
    
    Args:
        features: Feature vectors (n_samples, n_features)
        labels: Optional labels for coloring points
        method: Dimensionality reduction method ('tsne', 'pca')
        save_path: Path to save the plot
        title: Plot title
    """
    if method == 'tsne':
        reducer = TSNE(n_components=2, random_state=42, perplexity=30)
        features_2d = reducer.fit_transform(features)
    elif method == 'pca':
        reducer = PCA(n_components=2, random_state=42)
        features_2d = reducer.fit_transform(features)
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    plt.figure(figsize=(10, 8))
    
    if labels is not None:
        unique_labels = np.unique(labels)
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))
        
        for i, label in enumerate(unique_labels):
            mask = labels == label
            plt.scatter(features_2d[mask, 0], features_2d[mask, 1], 
                       c=[colors[i]], label=f'Class {label}', alpha=0.7, s=20)
        plt.legend()
    else:
        plt.scatter(features_2d[:, 0], features_2d[:, 1], alpha=0.7, s=20)
    
    plt.title(title)
    plt.xlabel(f'{method.upper()} Component 1')
    plt.ylabel(f'{method.upper()} Component 2')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def visualize_reconstructions(original: torch.Tensor, reconstructed: torch.Tensor,
                             save_path: Optional[str] = None, title: str = 'Reconstructions',
                             num_samples: int = 10) -> None:
    """
    Visualize original vs reconstructed images.
    
    Args:
        original: Original images
        reconstructed: Reconstructed images
        save_path: Path to save the plot
        title: Plot title
        num_samples: Number of samples to display
    """
    num_samples = min(num_samples, original.shape[0])
    
    fig, axes = plt.subplots(2, num_samples, figsize=(num_samples * 2, 4))
    
    for i in range(num_samples):
        # Original
        axes[0, i].imshow(original[i].squeeze(), cmap='gray')
        axes[0, i].set_title('Original')
        axes[0, i].axis('off')
        
        # Reconstructed
        axes[1, i].imshow(reconstructed[i].squeeze(), cmap='gray')
        axes[1, i].set_title('Reconstructed')
        axes[1, i].axis('off')
    
    plt.suptitle(title)
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_latent_space(features: np.ndarray, labels: np.ndarray = None,
                     save_path: Optional[str] = None, title: str = 'Latent Space') -> None:
    """
    Plot 2D latent space (for autoencoders with 2D latent dimension).
    
    Args:
        features: 2D latent features
        labels: Optional labels for coloring
        save_path: Path to save the plot
        title: Plot title
    """
    if features.shape[1] != 2:
        # Use PCA to reduce to 2D if not already 2D
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        features = pca.fit_transform(features)
    
    plt.figure(figsize=(10, 8))
    
    if labels is not None:
        unique_labels = np.unique(labels)
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))
        
        for i, label in enumerate(unique_labels):
            mask = labels == label
            plt.scatter(features[mask, 0], features[mask, 1], 
                       c=[colors[i]], label=f'Class {label}', alpha=0.7, s=30)
        plt.legend()
    else:
        plt.scatter(features[:, 0], features[:, 1], alpha=0.7, s=30)
    
    plt.title(title)
    plt.xlabel('Latent Dimension 1')
    plt.ylabel('Latent Dimension 2')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def visualize_attention_weights(attention_weights: torch.Tensor, tokens: List[str],
                               save_path: Optional[str] = None, title: str = 'Attention Weights') -> None:
    """
    Visualize attention weights as a heatmap.
    
    Args:
        attention_weights: Attention weight matrix (seq_len, seq_len)
        tokens: List of tokens corresponding to sequence
        save_path: Path to save the plot
        title: Plot title
    """
    plt.figure(figsize=(12, 10))
    
    # Create heatmap
    sns.heatmap(attention_weights.detach().cpu().numpy(), 
                xticklabels=tokens, yticklabels=tokens,
                cmap='Blues', annot=False, fmt='.2f',
                cbar_kws={'label': 'Attention Weight'})
    
    plt.title(title)
    plt.xlabel('Key Tokens')
    plt.ylabel('Query Tokens')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_feature_maps(feature_maps: torch.Tensor, save_path: Optional[str] = None,
                     title: str = 'Feature Maps', num_maps: int = 16) -> None:
    """
    Visualize CNN feature maps.
    
    Args:
        feature_maps: Feature maps tensor (batch, channels, height, width)
        save_path: Path to save the plot
        title: Plot title
        num_maps: Number of feature maps to display
    """
    # Take first sample and limit number of maps
    if len(feature_maps.shape) == 4:
        feature_maps = feature_maps[0]  # Take first sample
    
    num_maps = min(num_maps, feature_maps.shape[0])
    
    # Calculate grid dimensions
    cols = 4
    rows = (num_maps + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2, rows * 2))
    axes = axes.flatten() if rows > 1 else [axes] if rows == 1 else axes
    
    for i in range(num_maps):
        axes[i].imshow(feature_maps[i].detach().cpu().numpy(), cmap='viridis')
        axes[i].set_title(f'Map {i}')
        axes[i].axis('off')
    
    # Hide empty subplots
    for i in range(num_maps, len(axes)):
        axes[i].axis('off')
    
    plt.suptitle(title)
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_training_history(history: dict, save_path: Optional[str] = None,
                         title: str = 'Training History') -> None:
    """
    Plot training history with multiple metrics.
    
    Args:
        history: Dictionary with training history
        save_path: Path to save the plot
        title: Plot title
    """
    metrics = list(history.keys())
    num_metrics = len(metrics)
    
    # Determine subplot layout
    if num_metrics <= 2:
        rows, cols = 1, num_metrics
    elif num_metrics <= 4:
        rows, cols = 2, 2
    else:
        rows, cols = (num_metrics + 2) // 3, 3
    
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3))
    axes = axes.flatten() if num_metrics > 1 else [axes]
    
    for i, (metric_name, values) in enumerate(history.items()):
        axes[i].plot(values, label=metric_name, linewidth=2)
        axes[i].set_title(metric_name.replace('_', ' ').title())
        axes[i].set_xlabel('Epoch')
        axes[i].set_ylabel(metric_name.replace('_', ' ').title())
        axes[i].grid(True, alpha=0.3)
        axes[i].legend()
    
    # Hide empty subplots
    for i in range(num_metrics, len(axes)):
        axes[i].axis('off')
    
    plt.suptitle(title)
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def visualize_embedding_space(embeddings: np.ndarray, words: List[str],
                             save_path: Optional[str] = None, title: str = 'Embedding Space',
                             method: str = 'tsne', num_words: int = 100) -> None:
    """
    Visualize word embeddings in 2D space.
    
    Args:
        embeddings: Word embeddings matrix
        words: List of words corresponding to embeddings
        save_path: Path to save the plot
        title: Plot title
        method: Dimensionality reduction method
        num_words: Number of words to display
    """
    # Limit number of words for readability
    num_words = min(num_words, len(words))
    embeddings = embeddings[:num_words]
    words = words[:num_words]
    
    # Reduce dimensionality
    if method == 'tsne':
        reducer = TSNE(n_components=2, random_state=42, perplexity=min(30, num_words-1))
        embeddings_2d = reducer.fit_transform(embeddings)
    elif method == 'pca':
        reducer = PCA(n_components=2, random_state=42)
        embeddings_2d = reducer.fit_transform(embeddings)
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    plt.figure(figsize=(12, 10))
    plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], alpha=0.7, s=50)
    
    # Add word labels
    for i, word in enumerate(words):
        plt.annotate(word, (embeddings_2d[i, 0], embeddings_2d[i, 1]),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, alpha=0.8)
    
    plt.title(title)
    plt.xlabel(f'{method.upper()} Component 1')
    plt.ylabel(f'{method.upper()} Component 2')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, 
                         class_names: List[str] = None,
                         save_path: Optional[str] = None,
                         title: str = 'Confusion Matrix') -> None:
    """
    Plot confusion matrix.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        class_names: Names of classes
        save_path: Path to save the plot
        title: Plot title
    """
    from sklearn.metrics import confusion_matrix
    
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.title(title)
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
