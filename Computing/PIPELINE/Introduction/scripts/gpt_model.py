"""
GPT-style decoder-only Transformer architecture for language model pre-training.

Architecture reference:
    "Attention Is All You Need" (Vaswani et al., 2017)
    https://arxiv.org/html/1706.03762v7

Implementation adapted from:
    Sebastian Raschka, "Build a Large Language Model From Scratch"
    https://github.com/rasbt/LLMs-from-scratch (Apache License 2.0)
    Reference script: https://github.com/rasbt/LLMs-from-scratch/blob/
        28c65cdfbc3338e2e040016eea4b7fdf556e4d57/ch04/01_main-chapter-code/gpt.py

This module defines a configurable GPT-2-style model suitable for pre-training
from scratch on a local GPU or a cloud compute cluster.  The architecture
implements a decoder-only Transformer with:

    - Learned token and positional embeddings
    - Stacked Transformer blocks using the Pre-LayerNorm (Pre-LN) configuration
    - Multi-Head Causal Self-Attention with scaled dot-product
    - Position-wise Feed-Forward Networks with GELU activation
    - Final LayerNorm and a weight-tied vocabulary projection head

Usage:
    Activate the virtual environment first:
        source venv/bin/activate

    Run the module directly to perform a smoke test:
        python scripts/gpt_model.py

Dependencies:
    torch
    Install via: pip install torch --index-url https://download.pytorch.org/whl/cu121
"""

import math
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class GPTConfig:
    """Hyperparameters for the GPT-style Transformer model.

    Attributes:
        vocab_size:   Number of unique token IDs in the tokenizer vocabulary.
        context_len:  Maximum sequence length (context window).
        emb_dim:      Dimensionality of token and positional embeddings.
        n_heads:      Number of attention heads in each Multi-Head Attention block.
        n_layers:     Number of stacked Transformer decoder blocks.
        drop_rate:    Dropout probability applied to embeddings and attention weights.
        qkv_bias:     Whether to include a bias term in Q, K, V projection layers.
    """
    vocab_size:  int   = 50_257   # GPT-2 default vocabulary size
    context_len: int   = 1_024    # GPT-2 default context window
    emb_dim:     int   = 768      # GPT-2 small hidden dimension
    n_heads:     int   = 12       # GPT-2 small attention heads
    n_layers:    int   = 12       # GPT-2 small transformer blocks
    drop_rate:   float = 0.1
    qkv_bias:    bool  = False


# Small model for rapid experimentation on a single GPU (e.g. RTX 3090 / 4090)
GPT_SMALL_CONFIG = GPTConfig(
    vocab_size=50_257,
    context_len=256,
    emb_dim=256,
    n_heads=4,
    n_layers=4,
    drop_rate=0.0,
    qkv_bias=False,
)

# GPT-2 (117 M parameter) configuration
GPT2_CONFIG = GPTConfig(
    vocab_size=50_257,
    context_len=1_024,
    emb_dim=768,
    n_heads=12,
    n_layers=12,
    drop_rate=0.1,
    qkv_bias=True,
)


# ---------------------------------------------------------------------------
# GELU activation function
# ---------------------------------------------------------------------------

class GELU(nn.Module):
    """Gaussian Error Linear Unit (GELU) activation function.

    Defined as GELU(x) = x * Phi(x), where Phi is the standard normal
    cumulative distribution function.  A tanh-based fast approximation is
    used in practice, matching the formulation in the GPT-2 paper.

    GELU replaces the piecewise-linear ReLU in all modern LLMs because it
    provides a smooth, non-zero gradient for negative inputs and empirically
    improves convergence in deep Transformer networks.
    """

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.gelu(x, approximate="tanh")


# ---------------------------------------------------------------------------
# Multi-Head Causal Self-Attention
# ---------------------------------------------------------------------------

class MultiHeadCausalAttention(nn.Module):
    """Scaled dot-product multi-head causal self-attention.

    Implements the attention mechanism described in Section 3.2 of
    "Attention Is All You Need" (Vaswani et al., 2017):

        Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) * V

    A causal (autoregressive) mask is applied so that each token can only
    attend to itself and preceding tokens.  This is required for the
    next-token prediction (causal language modelling) objective.

    Args:
        cfg: GPTConfig instance supplying emb_dim, n_heads, drop_rate,
             and qkv_bias.
    """

    def __init__(self, cfg: GPTConfig) -> None:
        super().__init__()
        assert cfg.emb_dim % cfg.n_heads == 0, (
            f"emb_dim ({cfg.emb_dim}) must be divisible by n_heads ({cfg.n_heads})"
        )

        self.n_heads  = cfg.n_heads
        self.head_dim = cfg.emb_dim // cfg.n_heads

        # Combined Q, K, V projection for computational efficiency
        self.W_qkv     = nn.Linear(cfg.emb_dim, 3 * cfg.emb_dim, bias=cfg.qkv_bias)
        self.out_proj  = nn.Linear(cfg.emb_dim, cfg.emb_dim)
        self.attn_drop = nn.Dropout(cfg.drop_rate)
        self.resid_drop = nn.Dropout(cfg.drop_rate)

        # Causal mask: upper-triangular matrix of True values.
        # Registered as a buffer (not a trainable parameter) so it is
        # moved to the correct device automatically via model.to(device).
        self.register_buffer(
            "mask",
            torch.triu(
                torch.ones(cfg.context_len, cfg.context_len), diagonal=1
            ).bool(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C = x.shape  # batch size, sequence length, embedding dimension

        # Project input to Q, K, V and split along the last dimension
        qkv = self.W_qkv(x)                           # (B, T, 3*C)
        q, k, v = qkv.split(C, dim=2)                 # each (B, T, C)

        # Reshape to (B, n_heads, T, head_dim) for batched attention
        q = q.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

        # Scaled dot-product attention scores: (B, n_heads, T, T)
        scale = math.sqrt(self.head_dim)
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) / scale

        # Apply causal mask to prevent attending to future positions
        attn_scores = attn_scores.masked_fill(self.mask[:T, :T], float("-inf"))

        # Normalize scores to probability weights via softmax
        attn_weights = torch.softmax(attn_scores, dim=-1)
        attn_weights = self.attn_drop(attn_weights)

        # Weighted aggregation of value vectors
        context = torch.matmul(attn_weights, v)        # (B, n_heads, T, head_dim)
        context = context.transpose(1, 2).contiguous().view(B, T, C)

        return self.resid_drop(self.out_proj(context))


# ---------------------------------------------------------------------------
# Position-wise Feed-Forward Network
# ---------------------------------------------------------------------------

class FeedForward(nn.Module):
    """Two-layer position-wise feed-forward network with GELU activation.

    As described in "Attention Is All You Need" Section 3.3:
        FFN(x) = GELU(x W_1 + b_1) W_2 + b_2

    The inner dimension is expanded by a factor of 4 relative to emb_dim,
    following the convention established in the original Transformer paper
    and adopted by GPT-2 and GPT-3.

    Args:
        cfg: GPTConfig instance supplying emb_dim and drop_rate.
    """

    def __init__(self, cfg: GPTConfig) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(cfg.emb_dim, 4 * cfg.emb_dim),
            GELU(),
            nn.Linear(4 * cfg.emb_dim, cfg.emb_dim),
            nn.Dropout(cfg.drop_rate),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ---------------------------------------------------------------------------
# Transformer Block
# ---------------------------------------------------------------------------

class TransformerBlock(nn.Module):
    """Single GPT-style Transformer decoder block using Pre-LayerNorm.

    Each block applies the following operations:
        1. LayerNorm
        2. Multi-Head Causal Self-Attention
        3. Residual connection
        4. LayerNorm
        5. Position-wise Feed-Forward Network
        6. Residual connection

    The Pre-LayerNorm (Pre-LN) configuration normalizes inputs before each
    sub-layer rather than after (Post-LN), which stabilizes gradient flow
    in very deep networks (Xiong et al., 2020).

    Args:
        cfg: GPTConfig instance.
    """

    def __init__(self, cfg: GPTConfig) -> None:
        super().__init__()
        self.ln1  = nn.LayerNorm(cfg.emb_dim)
        self.attn = MultiHeadCausalAttention(cfg)
        self.ln2  = nn.LayerNorm(cfg.emb_dim)
        self.ff   = FeedForward(cfg)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Attention sub-layer with residual connection
        x = x + self.attn(self.ln1(x))
        # Feed-forward sub-layer with residual connection
        x = x + self.ff(self.ln2(x))
        return x


# ---------------------------------------------------------------------------
# Full GPT Model
# ---------------------------------------------------------------------------

class GPTModel(nn.Module):
    """Decoder-only GPT-style language model.

    Full architecture:
        1. Token embedding table       (vocab_size  x emb_dim)
        2. Learned positional embedding (context_len x emb_dim)
        3. Dropout on the summed embedding
        4. N stacked TransformerBlock layers
        5. Final LayerNorm
        6. Linear projection head      (emb_dim x vocab_size)
           Weight-tied to the token embedding table.

    The model is trained with a next-token prediction (causal language
    modelling) objective using cross-entropy loss over the full vocabulary.

    Weight tying between the input embedding and output projection reduces
    the parameter count and consistently improves perplexity (Press & Wolf, 2017).

    Args:
        cfg: GPTConfig instance specifying all hyperparameters.
    """

    def __init__(self, cfg: GPTConfig) -> None:
        super().__init__()
        self.cfg = cfg

        self.tok_emb  = nn.Embedding(cfg.vocab_size, cfg.emb_dim)
        self.pos_emb  = nn.Embedding(cfg.context_len, cfg.emb_dim)
        self.emb_drop = nn.Dropout(cfg.drop_rate)

        self.blocks = nn.Sequential(
            *[TransformerBlock(cfg) for _ in range(cfg.n_layers)]
        )
        self.ln_f = nn.LayerNorm(cfg.emb_dim)

        # Language model head: weight-tied with the token embedding.
        self.lm_head = nn.Linear(cfg.emb_dim, cfg.vocab_size, bias=False)
        self.lm_head.weight = self.tok_emb.weight

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module: nn.Module) -> None:
        """Initialize parameters with a scaled normal distribution.

        Follows the GPT-2 initialization scheme: standard deviation of 0.02
        for all weight matrices and embeddings, and zero initialization for
        all bias vectors.
        """
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        if isinstance(module, nn.Linear) and module.bias is not None:
            nn.init.zeros_(module.bias)

    def forward(
        self,
        idx:     torch.Tensor,
        targets: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        """Forward pass through the model.

        Args:
            idx:     Integer token indices of shape (B, T).
            targets: Ground-truth next-token indices of shape (B, T).
                     If provided, the cross-entropy loss is computed and
                     returned.  Pass None during inference.

        Returns:
            logits: Unnormalized log-probabilities of shape (B, T, vocab_size).
            loss:   Scalar cross-entropy loss if targets are provided, else None.
        """
        B, T = idx.shape
        assert T <= self.cfg.context_len, (
            f"Sequence length {T} exceeds the model context length "
            f"{self.cfg.context_len}."
        )

        device    = idx.device
        positions = torch.arange(T, device=device)

        # Sum token and positional embeddings, apply dropout
        x = self.tok_emb(idx) + self.pos_emb(positions)   # (B, T, emb_dim)
        x = self.emb_drop(x)

        # Pass through all Transformer blocks and the final LayerNorm
        x = self.blocks(x)
        x = self.ln_f(x)

        # Project to vocabulary logits
        logits = self.lm_head(x)                           # (B, T, vocab_size)

        loss = None
        if targets is not None:
            # Flatten to (B*T, vocab_size) and (B*T,) for cross-entropy
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1),
            )

        return logits, loss

    def count_parameters(self) -> int:
        """Return the total number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ---------------------------------------------------------------------------
# Text generation utility
# ---------------------------------------------------------------------------

@torch.no_grad()
def generate(
    model:          GPTModel,
    idx:            torch.Tensor,
    max_new_tokens: int,
    temperature:    float       = 1.0,
    top_k:          int | None  = None,
) -> torch.Tensor:
    """Auto-regressive next-token generation via ancestral sampling.

    For each generation step:
        1. Crop the context to the model's maximum context length.
        2. Run a forward pass to obtain logits for the last position.
        3. Apply temperature scaling.
        4. Optionally restrict to the top-k most probable tokens.
        5. Sample one token from the resulting distribution.
        6. Append the sampled token and repeat.

    Args:
        model:          A trained GPTModel placed in eval mode.
        idx:            Prompt token indices of shape (1, T).
        max_new_tokens: Number of new tokens to generate.
        temperature:    Logit scaling factor.  Values < 1.0 make the
                        distribution sharper (more deterministic); values
                        > 1.0 make it flatter (more random).
        top_k:          If set, restrict sampling to the top-k tokens.

    Returns:
        Token index tensor of shape (1, T + max_new_tokens).
    """
    model.eval()
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -model.cfg.context_len:]
        logits, _ = model(idx_cond)
        logits = logits[:, -1, :] / temperature             # (1, vocab_size)

        if top_k is not None:
            top_values, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < top_values[:, [-1]]] = float("-inf")

        probs      = torch.softmax(logits, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)  # (1, 1)
        idx        = torch.cat([idx, next_token], dim=1)

    return idx


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running GPT model smoke test ...")

    cfg   = GPT_SMALL_CONFIG
    model = GPTModel(cfg)
    total = model.count_parameters()

    print(f"Configuration       : {cfg}")
    print(f"Trainable parameters: {total:,}")

    # Test forward pass
    batch  = torch.randint(0, cfg.vocab_size, (2, 64))
    logits, _ = model(batch)
    print(f"Output logits shape : {logits.shape}")   # expect (2, 64, vocab_size)

    # Test generation
    prompt = torch.randint(0, cfg.vocab_size, (1, 5))
    output = generate(model, prompt, max_new_tokens=10, temperature=0.8, top_k=40)
    print(f"Generated sequence  : {output.shape}")   # expect (1, 15)

    print("Smoke test passed.")
