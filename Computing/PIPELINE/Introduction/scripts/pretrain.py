"""
Pre-training script for the GPT-style language model.

Implements the full next-token prediction (causal language modelling)
pre-training loop:

    1. Load and tokenize the corpus using the trained BPE tokenizer.
    2. Build sliding-window token windows for the causal LM objective.
    3. Initialize the GPT model.
    4. Run the training loop:
           a. Zero gradients
           b. Forward pass
           c. Cross-entropy loss computation
           d. Backward pass (back propagation)
           e. Gradient clipping
           f. Cosine learning-rate schedule update
           g. AdamW optimizer step
    5. Evaluate on a held-out validation split periodically.
    6. Save checkpoints to disk.

Usage:
    Activate the virtual environment first:
        source venv/bin/activate

    Ensure data preparation and tokenizer training are complete:
        python scripts/data_preparation.py
        python scripts/tokenizer_train.py

    Single-GPU training:
        python scripts/pretrain.py

    Multi-GPU training via PyTorch DDP (example: 2 GPUs):
        torchrun --nproc_per_node=2 scripts/pretrain.py

Output:
    checkpoints/checkpoint_step_<N>.pt   Periodic checkpoints.
    checkpoints/checkpoint_final.pt      Final model state.

Dependencies:
    torch, tokenizers, tqdm
    Install via: pip install torch tokenizers tqdm \
        --index-url https://download.pytorch.org/whl/cu121
"""

import math
import os
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tokenizers import Tokenizer
from tqdm import tqdm

# Make the scripts/ directory importable so gpt_model.py can be found
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gpt_model import GPTModel, GPTConfig, GPT_SMALL_CONFIG   # noqa: E402


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TOKENIZER_FILE:       Path  = Path("tokenizer") / "tokenizer.json"
CORPUS_FILE:          Path  = Path("data") / "cleaned" / "corpus.txt"
CHECKPOINT_DIR:       Path  = Path("checkpoints")

# Training hyperparameters
BATCH_SIZE:           int   = 8
CONTEXT_LEN:          int   = 256      # Must match GPTConfig.context_len
MAX_STEPS:            int   = 5_000
EVAL_INTERVAL:        int   = 500      # Evaluate every N steps
CHECKPOINT_INTERVAL:  int   = 1_000   # Save checkpoint every N steps
LEARNING_RATE:        float = 3e-4
WEIGHT_DECAY:         float = 0.1
GRAD_CLIP:            float = 1.0     # Global gradient norm clip threshold
WARMUP_STEPS:         int   = 100     # Linear warm-up steps

DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"


# ---------------------------------------------------------------------------
# Dataset: sliding-window causal language modelling
# ---------------------------------------------------------------------------

class TokenDataset(Dataset):
    """Sliding-window dataset for next-token prediction.

    For a flat sequence of token IDs, each sample is a window of
    (context_len + 1) consecutive tokens.  The input x is the first
    context_len tokens; the target y is the last context_len tokens
    (shifted right by one position).  This implements the standard
    causal language modelling objective:

        loss = cross_entropy(model(x), y)

    Args:
        token_ids:   Flat list of integer token IDs for the full corpus.
        context_len: Number of tokens per training sample.
    """

    def __init__(self, token_ids: list[int], context_len: int) -> None:
        self.data        = torch.tensor(token_ids, dtype=torch.long)
        self.context_len = context_len

    def __len__(self) -> int:
        return max(0, len(self.data) - self.context_len)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        chunk = self.data[idx : idx + self.context_len + 1]
        x = chunk[:-1]   # input tokens
        y = chunk[1:]    # target tokens (shifted by one)
        return x, y


# ---------------------------------------------------------------------------
# Corpus tokenization
# ---------------------------------------------------------------------------

def tokenize_corpus(tokenizer: Tokenizer, corpus_path: Path) -> list[int]:
    """Read the corpus line by line and return a flat list of token IDs.

    Each line in the corpus represents one document.  The
    <|endoftext|> token is appended between documents to signal
    document boundaries to the model.

    Args:
        tokenizer:   A trained Hugging Face Tokenizer.
        corpus_path: Path to the plain-text corpus file.

    Returns:
        A flat Python list of integer token IDs representing the full corpus.
    """
    eot_id = tokenizer.token_to_id("<|endoftext|>")
    ids: list[int] = []

    with open(corpus_path, "r", encoding="utf-8") as fh:
        for line in tqdm(fh, desc="Tokenizing"):
            line = line.strip()
            if line:
                encoded = tokenizer.encode(line)
                ids.extend(encoded.ids)
                if eot_id is not None:
                    ids.append(eot_id)   # mark document boundary

    return ids


# ---------------------------------------------------------------------------
# Learning rate schedule: linear warm-up + cosine decay
# ---------------------------------------------------------------------------

def get_lr(
    step:         int,
    max_steps:    int,
    warmup_steps: int,
    base_lr:      float,
) -> float:
    """Cosine learning rate schedule with a linear warm-up phase.

    During warm-up (steps 0 to warmup_steps), the learning rate increases
    linearly from 0 to base_lr.  After warm-up, it follows a half-cosine
    decay from base_lr to 0 over the remaining steps.

    Args:
        step:         Current training step (0-indexed).
        max_steps:    Total number of training steps.
        warmup_steps: Number of linear warm-up steps.
        base_lr:      Peak learning rate after warm-up.

    Returns:
        Learning rate value for the current step.
    """
    if step < warmup_steps:
        return base_lr * step / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(max_steps - warmup_steps, 1)
    return base_lr * 0.5 * (1.0 + math.cos(math.pi * progress))


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

@torch.no_grad()
def evaluate(
    model:        GPTModel,
    data_loader:  DataLoader,
    eval_batches: int = 20,
) -> dict[str, float]:
    """Estimate validation loss and perplexity.

    Temporarily switches the model to eval mode to disable dropout, and
    disables gradient computation to reduce memory usage.  After evaluation,
    restores the model to training mode.

    Args:
        model:        The GPTModel instance.
        data_loader:  DataLoader yielding (x, y) validation batches.
        eval_batches: Number of batches to average over.

    Returns:
        Dictionary with keys 'loss' (average cross-entropy) and
        'perplexity' (exp(loss)).
    """
    model.eval()
    total_loss = 0.0
    count = 0

    for x, y in data_loader:
        if count >= eval_batches:
            break
        x, y = x.to(DEVICE), y.to(DEVICE)
        _, loss = model(x, targets=y)
        total_loss += loss.item()
        count += 1

    model.train()
    avg_loss = total_loss / max(count, 1)
    return {"loss": avg_loss, "perplexity": math.exp(avg_loss)}


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

def train() -> None:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Training device : {DEVICE}")
    if DEVICE == "cuda":
        print(f"GPU             : {torch.cuda.get_device_name(0)}")
        print(f"VRAM            : {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    # --- Load tokenizer ---
    assert TOKENIZER_FILE.exists(), (
        f"Tokenizer not found at '{TOKENIZER_FILE}'.\n"
        f"Run 'python scripts/tokenizer_train.py' first."
    )
    print(f"\nLoading tokenizer from : {TOKENIZER_FILE}")
    tokenizer = Tokenizer.from_file(str(TOKENIZER_FILE))
    vocab_size = tokenizer.get_vocab_size()
    print(f"Vocabulary size        : {vocab_size:,}")

    # --- Tokenize corpus ---
    assert CORPUS_FILE.exists(), (
        f"Corpus not found at '{CORPUS_FILE}'.\n"
        f"Run 'python scripts/data_preparation.py' first."
    )
    token_ids = tokenize_corpus(tokenizer, CORPUS_FILE)
    print(f"Total tokens in corpus : {len(token_ids):,}")

    # --- Train / validation split (90% / 10%) ---
    split      = int(0.9 * len(token_ids))
    train_ids  = token_ids[:split]
    val_ids    = token_ids[split:]

    train_ds = TokenDataset(train_ids, CONTEXT_LEN)
    val_ds   = TokenDataset(val_ids,   CONTEXT_LEN)

    train_loader = DataLoader(
        train_ds, batch_size=BATCH_SIZE, shuffle=True,  pin_memory=(DEVICE == "cuda")
    )
    val_loader = DataLoader(
        val_ds,   batch_size=BATCH_SIZE, shuffle=False, pin_memory=(DEVICE == "cuda")
    )

    # --- Initialise model ---
    # Override vocab_size to match the trained tokenizer.
    base = GPT_SMALL_CONFIG
    cfg  = GPTConfig(
        vocab_size  = vocab_size,
        context_len = CONTEXT_LEN,
        emb_dim     = base.emb_dim,
        n_heads     = base.n_heads,
        n_layers    = base.n_layers,
        drop_rate   = base.drop_rate,
        qkv_bias    = base.qkv_bias,
    )
    model = GPTModel(cfg).to(DEVICE)
    print(f"Model parameters       : {model.count_parameters():,}")

    # --- AdamW optimizer ---
    # Weight decay is applied only to weight matrices (dim >= 2).
    # Bias vectors and LayerNorm parameters are excluded from weight decay
    # because regularizing them provides no benefit and can harm convergence.
    decay_params    = [p for n, p in model.named_parameters()
                       if p.requires_grad and p.dim() >= 2]
    no_decay_params = [p for n, p in model.named_parameters()
                       if p.requires_grad and p.dim() < 2]

    optimizer = torch.optim.AdamW(
        [
            {"params": decay_params,    "weight_decay": WEIGHT_DECAY},
            {"params": no_decay_params, "weight_decay": 0.0},
        ],
        lr=LEARNING_RATE,
        betas=(0.9, 0.95),
        eps=1e-8,
    )

    # --- Training loop ---
    model.train()
    data_iter = iter(train_loader)
    step      = 0
    t0        = time.time()

    print(f"\nStarting pre-training: {MAX_STEPS:,} steps, batch size {BATCH_SIZE}\n")

    while step < MAX_STEPS:
        # Refresh data iterator when the epoch ends
        try:
            x, y = next(data_iter)
        except StopIteration:
            data_iter = iter(train_loader)
            x, y = next(data_iter)

        x, y = x.to(DEVICE), y.to(DEVICE)

        # Step 1: Zero gradients
        # Prevents gradient accumulation from the previous training step.
        optimizer.zero_grad()

        # Step 2: Forward pass
        # Pass token sequences through the model to obtain logits.
        logits, loss = model(x, targets=y)

        # Step 3: Backward pass (back propagation)
        # Compute gradients of the loss with respect to all parameters.
        loss.backward()

        # Step 4: Gradient clipping
        # Clips the global gradient norm to GRAD_CLIP to prevent gradient
        # explosion, which is common early in training of large models.
        grad_norm = nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)

        # Step 5: Update learning rate (cosine schedule with linear warm-up)
        lr = get_lr(step, MAX_STEPS, WARMUP_STEPS, LEARNING_RATE)
        for param_group in optimizer.param_groups:
            param_group["lr"] = lr

        # Step 6: AdamW optimizer step
        # Updates all trainable parameters using first/second moment estimates
        # and applies weight decay directly to the parameter values.
        optimizer.step()

        step += 1

        # --- Logging ---
        if step % 50 == 0:
            elapsed = time.time() - t0
            print(
                f"step {step:>5d}/{MAX_STEPS}  "
                f"loss {loss.item():.4f}  "
                f"ppl {math.exp(loss.item()):.2f}  "
                f"lr {lr:.2e}  "
                f"grad_norm {grad_norm:.3f}  "
                f"elapsed {elapsed:.1f}s"
            )

        # --- Periodic evaluation on validation set ---
        if step % EVAL_INTERVAL == 0:
            metrics = evaluate(model, val_loader)
            print(
                f"\n[Validation  step={step}]  "
                f"val_loss={metrics['loss']:.4f}  "
                f"perplexity={metrics['perplexity']:.2f}\n"
            )

        # --- Periodic checkpointing ---
        if step % CHECKPOINT_INTERVAL == 0:
            ckpt_path = CHECKPOINT_DIR / f"checkpoint_step_{step:06d}.pt"
            torch.save(
                {
                    "step":                 step,
                    "model_state_dict":     model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "loss":                 loss.item(),
                    "config":               cfg,
                },
                ckpt_path,
            )
            print(f"Checkpoint saved: {ckpt_path}")

    # --- Final checkpoint ---
    final_path = CHECKPOINT_DIR / "checkpoint_final.pt"
    torch.save(
        {
            "step":             step,
            "model_state_dict": model.state_dict(),
            "config":           cfg,
        },
        final_path,
    )
    print(f"\nTraining complete.  Final checkpoint: {final_path}")
    print(
        "Next step: convert the checkpoint to GGUF format for inference "
        "with Ollama.  See the README for instructions."
    )


if __name__ == "__main__":
    train()
