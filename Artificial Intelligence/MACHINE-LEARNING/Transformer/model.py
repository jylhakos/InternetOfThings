import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class PositionalEncoding(nn.Module):
    """
    Positional encoding for Transformer model.
    Adds positional information to embeddings.
    """
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)


class RNNLanguageModel(nn.Module):
    """
    Basic RNN language model for comparison.
    """
    def __init__(self, vocab_size, embed_size=128, hidden_size=256, num_layers=2, dropout=0.2):
        super(RNNLanguageModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.rnn = nn.LSTM(embed_size, hidden_size, num_layers, dropout=dropout, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, x, hidden=None):
        embedded = self.dropout(self.embedding(x))
        output, hidden = self.rnn(embedded, hidden)
        output = self.dropout(output)
        output = self.fc(output)
        return output, hidden

    def init_hidden(self, batch_size, device):
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        return (h0, c0)


class TransformerLanguageModel(nn.Module):
    """
    Transformer-based language model.
    """
    def __init__(self, vocab_size, d_model=512, nhead=8, num_layers=6, dropout=0.1):
        super(TransformerLanguageModel, self).__init__()
        self.d_model = d_model
        
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=2048,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.fc = nn.Linear(d_model, vocab_size)
        
        self.init_weights()

    def init_weights(self):
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()
        self.fc.weight.data.uniform_(-initrange, initrange)

    def forward(self, src, src_mask=None):
        # Scale embeddings by sqrt(d_model)
        src = self.embedding(src) * math.sqrt(self.d_model)
        src = self.pos_encoder(src)
        
        if src_mask is None:
            src_mask = self.generate_square_subsequent_mask(src.size(1)).to(src.device)
            
        output = self.transformer(src, mask=src_mask)
        output = self.fc(output)
        return output

    @staticmethod
    def generate_square_subsequent_mask(sz):
        """Generate a square mask for the sequence."""
        mask = torch.triu(torch.ones(sz, sz), diagonal=1)
        mask = mask.masked_fill(mask == 1, float('-inf'))
        return mask


class HybridRNNTransformer(nn.Module):
    """
    Hybrid model combining RNN and Transformer architectures.
    RNN processes initial context, Transformer handles attention-based modeling.
    """
    def __init__(self, vocab_size, embed_size=256, hidden_size=256, d_model=512, 
                 nhead=8, num_transformer_layers=3, num_rnn_layers=2, dropout=0.1):
        super(HybridRNNTransformer, self).__init__()
        
        self.embed_size = embed_size
        self.hidden_size = hidden_size
        self.d_model = d_model
        
        # Shared embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_size)
        
        # RNN component for sequential processing
        self.rnn = nn.LSTM(embed_size, hidden_size, num_rnn_layers, 
                          dropout=dropout, batch_first=True)
        
        # Project RNN output to transformer dimension
        self.rnn_to_transformer = nn.Linear(hidden_size, d_model)
        
        # Positional encoding for transformer
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        
        # Transformer component for attention-based modeling
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=2048,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_transformer_layers)
        
        # Output projection
        self.fc = nn.Linear(d_model, vocab_size)
        
        self.dropout = nn.Dropout(dropout)
        self.init_weights()

    def init_weights(self):
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()
        self.fc.weight.data.uniform_(-initrange, initrange)

    def forward(self, x, src_mask=None):
        # Embed input tokens
        embedded = self.dropout(self.embedding(x))
        
        # Process through RNN for sequential understanding
        rnn_out, _ = self.rnn(embedded)
        rnn_out = self.dropout(rnn_out)
        
        # Project RNN output to transformer dimension
        transformer_input = self.rnn_to_transformer(rnn_out)
        transformer_input = transformer_input * math.sqrt(self.d_model)
        
        # Add positional encoding
        transformer_input = self.pos_encoder(transformer_input)
        
        # Generate causal mask if not provided
        if src_mask is None:
            src_mask = self.generate_square_subsequent_mask(x.size(1)).to(x.device)
        
        # Process through transformer for attention-based modeling
        transformer_out = self.transformer(transformer_input, mask=src_mask)
        
        # Final projection to vocabulary
        output = self.fc(transformer_out)
        
        return output

    @staticmethod
    def generate_square_subsequent_mask(sz):
        """Generate a square mask for the sequence."""
        mask = torch.triu(torch.ones(sz, sz), diagonal=1)
        mask = mask.masked_fill(mask == 1, float('-inf'))
        return mask


def count_parameters(model):
    """Count the number of trainable parameters in a model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def create_model(model_type, vocab_size, **kwargs):
    """
    Factory function to create different types of language models.
    
    Args:
        model_type: 'rnn', 'transformer', or 'hybrid'
        vocab_size: Size of vocabulary
        **kwargs: Additional model parameters
    
    Returns:
        PyTorch model instance
    """
    if model_type == 'rnn':
        return RNNLanguageModel(vocab_size, **kwargs)
    elif model_type == 'transformer':
        return TransformerLanguageModel(vocab_size, **kwargs)
    elif model_type == 'hybrid':
        return HybridRNNTransformer(vocab_size, **kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
