"""
Training scripts for feature learning experiments.
"""

from .train_cnn import train_cnn, main as train_cnn_main
from .train_rnn import train_rnn, main as train_rnn_main
from .train_autoencoder import train_autoencoder, main as train_autoencoder_main
from .train_transfer_learning import train_transfer_learning, main as train_transfer_main

__all__ = [
    "train_cnn",
    "train_rnn", 
    "train_autoencoder",
    "train_transfer_learning",
    "train_cnn_main",
    "train_rnn_main",
    "train_autoencoder_main", 
    "train_transfer_main",
]
