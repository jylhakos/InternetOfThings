"""
Transformer models for feature learning and transfer learning.
"""

import torch
import torch.nn as nn
from typing import Optional, Tuple
import math


class SimpleTransformer(nn.Module):
    """Simple Transformer model for sequence-to-sequence tasks."""
    
    def __init__(self, vocab_size: int, embed_dim: int = 512, num_heads: int = 8,
                 num_layers: int = 6, max_seq_len: int = 512, dropout: float = 0.1,
                 feature_dim: int = 256):
        super(SimpleTransformer, self).__init__()
        
        self.embed_dim = embed_dim
        self.max_seq_len = max_seq_len
        self.feature_dim = feature_dim
        
        # Embedding layers
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        self.position_embedding = nn.Embedding(max_seq_len, embed_dim)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Feature projection layer
        self.feature_projection = nn.Sequential(
            nn.Linear(embed_dim, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )
        
        # Layer normalization
        self.layer_norm = nn.LayerNorm(embed_dim)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass returning features."""
        return self.extract_features(x, attention_mask)
    
    def extract_features(self, x: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Extract transformer features."""
        batch_size, seq_len = x.size()
        
        # Create position indices
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        
        # Embeddings
        token_embeddings = self.token_embedding(x)
        position_embeddings = self.position_embedding(positions)
        
        # Combine embeddings
        embeddings = token_embeddings + position_embeddings
        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)
        
        # Create padding mask if not provided
        if attention_mask is None:
            attention_mask = (x != 0)  # Assume 0 is padding token
        
        # Transformer encoding
        transformer_out = self.transformer_encoder(
            embeddings, 
            src_key_padding_mask=~attention_mask
        )
        
        # Global average pooling with masking
        if attention_mask is not None:
            mask_expanded = attention_mask.unsqueeze(-1).expand_as(transformer_out)
            sum_embeddings = torch.sum(transformer_out * mask_expanded, dim=1)
            sum_mask = torch.sum(mask_expanded, dim=1)
            pooled_output = sum_embeddings / (sum_mask + 1e-8)
        else:
            pooled_output = torch.mean(transformer_out, dim=1)
        
        # Project to feature dimension
        features = self.feature_projection(pooled_output)
        
        return features


class BERTFeatureExtractor(nn.Module):
    """BERT-like feature extractor for transfer learning."""
    
    def __init__(self, vocab_size: int = 30522, embed_dim: int = 768, 
                 num_heads: int = 12, num_layers: int = 12, max_seq_len: int = 512,
                 dropout: float = 0.1, feature_dim: int = 256):
        super(BERTFeatureExtractor, self).__init__()
        
        self.embed_dim = embed_dim
        self.max_seq_len = max_seq_len
        self.feature_dim = feature_dim
        
        # Embedding layers
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        self.position_embedding = nn.Embedding(max_seq_len, embed_dim)
        self.token_type_embedding = nn.Embedding(2, embed_dim)  # For sentence A/B
        
        # Layer normalization and dropout
        self.embed_layer_norm = nn.LayerNorm(embed_dim)
        self.embed_dropout = nn.Dropout(dropout)
        
        # Transformer encoder (BERT-like)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=dropout,
            batch_first=True,
            activation='gelu'  # BERT uses GELU
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Pooler (for [CLS] token)
        self.pooler = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.Tanh()
        )
        
        # Feature projection
        self.feature_projection = nn.Sequential(
            nn.Linear(embed_dim, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )
    
    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None,
                token_type_ids: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass returning features."""
        return self.extract_features(input_ids, attention_mask, token_type_ids)
    
    def extract_features(self, input_ids: torch.Tensor, 
                        attention_mask: Optional[torch.Tensor] = None,
                        token_type_ids: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Extract BERT-like features."""
        batch_size, seq_len = input_ids.size()
        
        # Create default inputs if not provided
        if attention_mask is None:
            attention_mask = (input_ids != 0)
        
        if token_type_ids is None:
            token_type_ids = torch.zeros_like(input_ids)
        
        # Position indices
        position_ids = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, -1)
        
        # Embeddings
        token_embeddings = self.token_embedding(input_ids)
        position_embeddings = self.position_embedding(position_ids)
        token_type_embeddings = self.token_type_embedding(token_type_ids)
        
        # Sum all embeddings
        embeddings = token_embeddings + position_embeddings + token_type_embeddings
        embeddings = self.embed_layer_norm(embeddings)
        embeddings = self.embed_dropout(embeddings)
        
        # Transformer encoding
        encoded = self.transformer_encoder(
            embeddings,
            src_key_padding_mask=~attention_mask
        )
        
        # Use [CLS] token (first token) for sequence representation
        cls_output = encoded[:, 0, :]  # [CLS] token
        pooled_output = self.pooler(cls_output)
        
        # Project to feature dimension
        features = self.feature_projection(pooled_output)
        
        return features
    
    def get_all_hidden_states(self, input_ids: torch.Tensor, 
                             attention_mask: Optional[torch.Tensor] = None,
                             token_type_ids: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Get all hidden states from the transformer."""
        batch_size, seq_len = input_ids.size()
        
        if attention_mask is None:
            attention_mask = (input_ids != 0)
        
        if token_type_ids is None:
            token_type_ids = torch.zeros_like(input_ids)
        
        position_ids = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, -1)
        
        # Embeddings
        token_embeddings = self.token_embedding(input_ids)
        position_embeddings = self.position_embedding(position_ids)
        token_type_embeddings = self.token_type_embedding(token_type_ids)
        
        embeddings = token_embeddings + position_embeddings + token_type_embeddings
        embeddings = self.embed_layer_norm(embeddings)
        embeddings = self.embed_dropout(embeddings)
        
        # Get all hidden states
        encoded = self.transformer_encoder(
            embeddings,
            src_key_padding_mask=~attention_mask
        )
        
        return encoded


class GPTFeatureExtractor(nn.Module):
    """GPT-like feature extractor for causal language modeling."""
    
    def __init__(self, vocab_size: int, embed_dim: int = 768, num_heads: int = 12,
                 num_layers: int = 12, max_seq_len: int = 1024, dropout: float = 0.1,
                 feature_dim: int = 256):
        super(GPTFeatureExtractor, self).__init__()
        
        self.embed_dim = embed_dim
        self.max_seq_len = max_seq_len
        self.feature_dim = feature_dim
        
        # Embeddings
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        self.position_embedding = nn.Embedding(max_seq_len, embed_dim)
        
        # Transformer decoder layers (causal)
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_decoder = nn.TransformerDecoder(decoder_layer, num_layers)
        
        # Layer normalization
        self.layer_norm = nn.LayerNorm(embed_dim)
        self.dropout = nn.Dropout(dropout)
        
        # Feature projection
        self.feature_projection = nn.Sequential(
            nn.Linear(embed_dim, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning features."""
        return self.extract_features(x)
    
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract GPT-like features."""
        batch_size, seq_len = x.size()
        
        # Position indices
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        
        # Embeddings
        token_embeddings = self.token_embedding(x)
        position_embeddings = self.position_embedding(positions)
        
        # Combine embeddings
        embeddings = token_embeddings + position_embeddings
        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)
        
        # Create causal mask
        causal_mask = torch.triu(torch.ones(seq_len, seq_len, device=x.device) * float('-inf'), diagonal=1)
        
        # Transformer decoding (using embeddings as both memory and target)
        decoded = self.transformer_decoder(
            embeddings,
            embeddings,  # Self-attention
            tgt_mask=causal_mask
        )
        
        # Use last token for feature extraction
        last_token_features = decoded[:, -1, :]
        
        # Project to feature dimension
        features = self.feature_projection(last_token_features)
        
        return features


class MultiModalTransformer(nn.Module):
    """Multi-modal transformer for combining text and image features."""
    
    def __init__(self, text_vocab_size: int, image_feature_dim: int = 2048,
                 embed_dim: int = 512, num_heads: int = 8, num_layers: int = 6,
                 feature_dim: int = 256, dropout: float = 0.1):
        super(MultiModalTransformer, self).__init__()
        
        self.embed_dim = embed_dim
        self.feature_dim = feature_dim
        
        # Text embedding
        self.text_embedding = nn.Embedding(text_vocab_size, embed_dim)
        
        # Image feature projection
        self.image_projection = nn.Linear(image_feature_dim, embed_dim)
        
        # Positional encoding
        self.pos_encoding = PositionalEncoding(embed_dim, dropout)
        
        # Cross-modal transformer
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
    
    def forward(self, text_input: torch.Tensor, image_features: torch.Tensor) -> torch.Tensor:
        """Forward pass with text and image inputs."""
        return self.extract_features(text_input, image_features)
    
    def extract_features(self, text_input: torch.Tensor, image_features: torch.Tensor) -> torch.Tensor:
        """Extract multi-modal features."""
        batch_size = text_input.size(0)
        
        # Text embeddings
        text_embedded = self.text_embedding(text_input)
        
        # Image features projection
        image_projected = self.image_projection(image_features).unsqueeze(1)  # Add sequence dimension
        
        # Concatenate text and image features
        combined_features = torch.cat([image_projected, text_embedded], dim=1)
        
        # Add positional encoding
        combined_features = self.pos_encoding(combined_features)
        
        # Transformer encoding
        encoded = self.transformer_encoder(combined_features)
        
        # Global average pooling
        pooled = torch.mean(encoded, dim=1)
        
        # Project to feature dimension
        features = self.feature_projection(pooled)
        
        return features


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer models."""
    
    def __init__(self, embed_dim: int, dropout: float = 0.1, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        
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


def create_transformer_model(model_type: str, **kwargs) -> nn.Module:
    """
    Factory function to create transformer models.
    
    Args:
        model_type: Type of model ('simple', 'bert', 'gpt', 'multimodal')
        **kwargs: Additional arguments for model initialization
        
    Returns:
        Transformer model instance
    """
    if model_type == 'simple':
        return SimpleTransformer(**kwargs)
    elif model_type == 'bert':
        return BERTFeatureExtractor(**kwargs)
    elif model_type == 'gpt':
        return GPTFeatureExtractor(**kwargs)
    elif model_type == 'multimodal':
        return MultiModalTransformer(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def create_transfer_learning_model(model_type: str = 'bert', vocab_size: int = 10000,
                                  embed_dim: int = 512, num_heads: int = 8,
                                  num_layers: int = 6, feature_dim: int = 256,
                                  max_seq_len: int = 512, dropout: float = 0.1) -> torch.nn.Module:
    """
    Factory function to create transformer models for transfer learning.
    
    Args:
        model_type: Type of transformer ('bert', 'gpt', 'transformer')
        vocab_size: Vocabulary size
        embed_dim: Embedding dimension
        num_heads: Number of attention heads
        num_layers: Number of transformer layers
        feature_dim: Feature dimension
        max_seq_len: Maximum sequence length
        dropout: Dropout rate
        
    Returns:
        Transformer model instance
    """
    if model_type == 'bert':
        return BERTFeatureExtractor(vocab_size, embed_dim, num_heads, num_layers, feature_dim, max_seq_len, dropout)
    elif model_type == 'gpt':
        return GPTFeatureExtractor(vocab_size, embed_dim, num_heads, num_layers, feature_dim, max_seq_len, dropout)
    elif model_type == 'transformer':
        return SimpleTransformer(vocab_size, embed_dim, num_heads, num_layers, max_seq_len, dropout, feature_dim)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")


if __name__ == "__main__":
    """Test transformer models."""
    print("Testing transformer models...")
    
    vocab_size = 1000
    seq_len = 64
    batch_size = 4
    
    # Test SimpleTransformer
    model = SimpleTransformer(vocab_size=vocab_size, embed_dim=256, feature_dim=128)
    x = torch.randint(0, vocab_size, (batch_size, seq_len))
    features = model(x)
    print(f"SimpleTransformer - Features shape: {features.shape}")
    
    # Test BERTFeatureExtractor
    model = BERTFeatureExtractor(vocab_size=vocab_size, embed_dim=256, feature_dim=128)
    features = model(x)
    print(f"BERTFeatureExtractor - Features shape: {features.shape}")
    
    # Test GPTFeatureExtractor
    model = GPTFeatureExtractor(vocab_size=vocab_size, embed_dim=256, feature_dim=128)
    features = model(x)
    print(f"GPTFeatureExtractor - Features shape: {features.shape}")
    
    print("Transformer models test completed!")
