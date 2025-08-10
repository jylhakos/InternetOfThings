"""
Recurrent Neural Network models for sequential feature learning.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional
import math


class SimpleRNN(nn.Module):
    """Simple RNN for sequence processing."""
    
    def __init__(self, vocab_size: int, embed_dim: int = 128, hidden_dim: int = 256, 
                 num_layers: int = 2, num_classes: int = 10, dropout: float = 0.3):
        super(SimpleRNN, self).__init__()
        
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # RNN layer
        self.rnn = nn.RNN(embed_dim, hidden_dim, num_layers, 
                         batch_first=True, dropout=dropout if num_layers > 1 else 0)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes)
        )
    
    def forward(self, x: torch.Tensor, hidden: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_size = x.size(0)
        
        # Embedding
        embedded = self.embedding(x)
        
        # RNN forward pass
        if hidden is None:
            hidden = self.init_hidden(batch_size, x.device)
        
        rnn_out, hidden = self.rnn(embedded, hidden)
        
        # Use the last time step output for classification
        last_output = rnn_out[:, -1, :]
        
        # Classification
        output = self.classifier(last_output)
        
        return output, hidden
    
    def init_hidden(self, batch_size: int, device: torch.device) -> torch.Tensor:
        """Initialize hidden state."""
        return torch.zeros(self.num_layers, batch_size, self.hidden_dim, device=device)
    
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract features from the RNN."""
        batch_size = x.size(0)
        embedded = self.embedding(x)
        hidden = self.init_hidden(batch_size, x.device)
        rnn_out, _ = self.rnn(embedded, hidden)
        return rnn_out[:, -1, :]  # Return last hidden state as features


class FeatureLSTM(nn.Module):
    """LSTM for sequential feature learning."""
    
    def __init__(self, vocab_size: int, embed_dim: int = 128, hidden_dim: int = 256,
                 num_layers: int = 2, feature_dim: int = 128, dropout: float = 0.3,
                 bidirectional: bool = True):
        super(FeatureLSTM, self).__init__()
        
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # LSTM layer
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers,
                           batch_first=True, dropout=dropout if num_layers > 1 else 0,
                           bidirectional=bidirectional)
        
        # Feature projection layer
        self.feature_projection = nn.Sequential(
            nn.Linear(hidden_dim * self.num_directions, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )
        
        self.feature_dim = feature_dim
    
    def forward(self, x: torch.Tensor, lengths: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass returning features."""
        features = self.extract_features(x, lengths)
        return features
    
    def extract_features(self, x: torch.Tensor, lengths: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Extract sequential features."""
        batch_size = x.size(0)
        
        # Embedding
        embedded = self.embedding(x)
        
        # Pack padded sequences if lengths are provided
        if lengths is not None:
            embedded = nn.utils.rnn.pack_padded_sequence(
                embedded, lengths, batch_first=True, enforce_sorted=False
            )
        
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Unpack if we packed
        if lengths is not None:
            lstm_out, _ = nn.utils.rnn.pad_packed_sequence(lstm_out, batch_first=True)
        
        # Use last hidden state (concatenate forward and backward if bidirectional)
        if self.bidirectional:
            # hidden shape: [num_layers * num_directions, batch, hidden_dim]
            last_hidden = torch.cat([hidden[-2], hidden[-1]], dim=1)  # Concat forward and backward
        else:
            last_hidden = hidden[-1]  # Last layer hidden state
        
        # Project to feature dimension
        features = self.feature_projection(last_hidden)
        
        return features


class TransformerFeatureExtractor(nn.Module):
    """Transformer-based feature extractor."""
    
    def __init__(self, vocab_size: int, embed_dim: int = 512, num_heads: int = 8,
                 num_layers: int = 6, feature_dim: int = 256, max_seq_len: int = 512,
                 dropout: float = 0.1):
        super(TransformerFeatureExtractor, self).__init__()
        
        self.embed_dim = embed_dim
        self.max_seq_len = max_seq_len
        
        # Token embedding
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        
        # Positional encoding
        self.positional_encoding = PositionalEncoding(embed_dim, dropout, max_seq_len)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Feature projection
        self.feature_projection = nn.Sequential(
            nn.Linear(embed_dim, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )
        
        self.feature_dim = feature_dim
    
    def forward(self, x: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass returning features."""
        return self.extract_features(x, attention_mask)
    
    def extract_features(self, x: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Extract transformer features."""
        # Token embedding
        embedded = self.token_embedding(x) * math.sqrt(self.embed_dim)
        
        # Add positional encoding
        embedded = self.positional_encoding(embedded)
        
        # Create padding mask if not provided
        if attention_mask is None:
            attention_mask = (x != 0)  # Assume 0 is padding token
        
        # Transformer encoding
        transformer_out = self.transformer_encoder(embedded, src_key_padding_mask=~attention_mask)
        
        # Global average pooling over sequence length
        if attention_mask is not None:
            # Masked average pooling
            mask_expanded = attention_mask.unsqueeze(-1).expand_as(transformer_out)
            sum_embeddings = torch.sum(transformer_out * mask_expanded, dim=1)
            sum_mask = torch.sum(mask_expanded, dim=1)
            pooled_output = sum_embeddings / (sum_mask + 1e-8)
        else:
            # Simple average pooling
            pooled_output = torch.mean(transformer_out, dim=1)
        
        # Project to feature dimension
        features = self.feature_projection(pooled_output)
        
        return features


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer models."""
    
    def __init__(self, embed_dim: int, dropout: float = 0.1, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, embed_dim)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        div_term = torch.exp(torch.arange(0, embed_dim, 2).float() * 
                           (-math.log(10000.0) / embed_dim))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:x.size(1), :].transpose(0, 1)
        return self.dropout(x)


class GRUFeatureExtractor(nn.Module):
    """GRU-based feature extractor."""
    
    def __init__(self, vocab_size: int, embed_dim: int = 128, hidden_dim: int = 256,
                 num_layers: int = 2, feature_dim: int = 128, dropout: float = 0.3,
                 bidirectional: bool = True):
        super(GRUFeatureExtractor, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # GRU layer
        self.gru = nn.GRU(embed_dim, hidden_dim, num_layers,
                         batch_first=True, dropout=dropout if num_layers > 1 else 0,
                         bidirectional=bidirectional)
        
        # Feature projection layer
        self.feature_projection = nn.Sequential(
            nn.Linear(hidden_dim * self.num_directions, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )
        
        self.feature_dim = feature_dim
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning features."""
        return self.extract_features(x)
    
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract GRU features."""
        # Embedding
        embedded = self.embedding(x)
        
        # GRU forward pass
        gru_out, hidden = self.gru(embedded)
        
        # Use last hidden state
        if self.bidirectional:
            # Concatenate forward and backward hidden states
            last_hidden = torch.cat([hidden[-2], hidden[-1]], dim=1)
        else:
            last_hidden = hidden[-1]
        
        # Project to feature dimension
        features = self.feature_projection(last_hidden)
        
        return features


def create_rnn_model(model_type: str, **kwargs) -> nn.Module:
    """
    Factory function to create RNN models.
    
    Args:
        model_type: Type of model ('simple', 'lstm', 'gru', 'transformer')
        **kwargs: Additional arguments for model initialization
        
    Returns:
        RNN model instance
    """
    if model_type == 'simple':
        return SimpleRNN(**kwargs)
    elif model_type == 'lstm':
        return FeatureLSTM(**kwargs)
    elif model_type == 'gru':
        return GRUFeatureExtractor(**kwargs)
    elif model_type == 'transformer':
        return TransformerFeatureExtractor(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def create_rnn_model(model_type: str = 'lstm', vocab_size: int = 10000,
                     embed_dim: int = 128, hidden_dim: int = 256, 
                     num_layers: int = 2, num_classes: int = 10,
                     dropout: float = 0.3, feature_dim: int = 256) -> torch.nn.Module:
    """
    Factory function to create RNN models.
    
    Args:
        model_type: Type of RNN ('rnn', 'lstm', 'gru', 'feature')
        vocab_size: Vocabulary size
        embed_dim: Embedding dimension
        hidden_dim: Hidden dimension
        num_layers: Number of RNN layers
        num_classes: Number of output classes
        dropout: Dropout rate
        feature_dim: Feature dimension for feature extraction models
        
    Returns:
        RNN model instance
    """
    if model_type == 'rnn':
        return SimpleRNN(vocab_size, embed_dim, hidden_dim, num_layers, num_classes, dropout)
    elif model_type == 'lstm':
        return FeatureLSTM(vocab_size, embed_dim, hidden_dim, num_layers, feature_dim, dropout)
    elif model_type == 'gru':
        return GRUFeatureExtractor(vocab_size, embed_dim, hidden_dim, num_layers, feature_dim, dropout)
    elif model_type == 'feature':
        return FeatureLSTM(vocab_size, embed_dim, hidden_dim, num_layers, feature_dim, dropout)
    elif model_type == 'transformer':
        return TransformerFeatureExtractor(vocab_size, embed_dim, 8, num_layers, 512, dropout, feature_dim)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")


if __name__ == "__main__":
    """Test RNN models."""
    print("Testing RNN models...")
    
    vocab_size = 1000
    seq_len = 32
    batch_size = 16
    
    # Create sample input
    x = torch.randint(0, vocab_size, (batch_size, seq_len))
    
    # Test SimpleRNN
    model = SimpleRNN(vocab_size=vocab_size, num_classes=10)
    output, hidden = model(x)
    features = model.extract_features(x)
    print(f"SimpleRNN - Output shape: {output.shape}, Features shape: {features.shape}")
    
    # Test FeatureLSTM
    model = FeatureLSTM(vocab_size=vocab_size, feature_dim=128)
    features = model(x)
    print(f"FeatureLSTM - Features shape: {features.shape}")
    
    # Test TransformerFeatureExtractor
    model = TransformerFeatureExtractor(vocab_size=vocab_size, embed_dim=128, feature_dim=256)
    features = model(x)
    print(f"TransformerFeatureExtractor - Features shape: {features.shape}")
    
    print("RNN models test completed!")
