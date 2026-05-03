"""
BPE tokenizer training script using the Hugging Face tokenizers library.

Trains a Byte-Pair Encoding (BPE) tokenizer on a plain-text corpus and saves
the resulting vocabulary and merge rules for use during model pre-training.

BPE reference:
    Sennrich et al. (2016), "Neural Machine Translation of Rare Words with
    Subword Units" — https://arxiv.org/abs/1508.07909

There are three principal tokenization approaches for language models:

    Approach 1 — Character-level:
        Every character is a separate token.  Simple to implement but produces
        very long sequences; self-attention complexity scales quadratically
        with sequence length, making this approach prohibitively expensive.

    Approach 2 — Word-level:
        The text is split on whitespace boundaries.  Sequences are compact but
        the vocabulary is large and out-of-vocabulary words cannot be
        represented.

    Approach 3 — Subword BPE (industry standard):
        The tokenizer learns frequent character sequences (subwords) from the
        training corpus.  Used by GPT, LLaMA, Mistral, Falcon, and most
        modern LLMs.  Balances vocabulary size (typically 32,000-100,000
        tokens) against sequence length and handles unseen words by
        decomposing them into known subword units.

This script implements Approach 3.

Library reference:
    Hugging Face tokenizers: https://github.com/huggingface/tokenizers

Usage:
    Activate the virtual environment first:
        source venv/bin/activate

    Ensure data preparation has been run first:
        python scripts/data_preparation.py

    Then run:
        python scripts/tokenizer_train.py

Output:
    tokenizer/tokenizer.json   Trained BPE tokenizer (vocabulary + merges).

Dependencies:
    tokenizers
    Install via: pip install tokenizers
"""

import os
from pathlib import Path

from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, trainers, decoders


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Target vocabulary size.  32,000 is a practical choice for research-scale
# models; GPT-2 uses 50,257 and LLaMA-2 uses 32,000.
VOCAB_SIZE: int = 32_000

# Minimum frequency for a BPE merge to be included in the vocabulary.
MIN_FREQUENCY: int = 2

CORPUS_FILE:    Path = Path("data") / "cleaned" / "corpus.txt"
TOKENIZER_DIR:  Path = Path("tokenizer")
TOKENIZER_FILE: Path = TOKENIZER_DIR / "tokenizer.json"

# Special tokens provide structural information for training and inference.
# Along with BPE merges, these tokens must be added explicitly to the vocabulary.
SPECIAL_TOKENS: list[str] = [
    "<|endoftext|>",   # Marks the end of a document (document separator)
    "<|bos|>",         # Beginning of a sequence
    "<|eos|>",         # End of a sequence
    "<|pad|>",         # Padding token for batched inference
    "<|unk|>",         # Unknown token (rarely triggered by BPE)
]


# ---------------------------------------------------------------------------
# Tokenizer construction and training
# ---------------------------------------------------------------------------

def build_and_train_tokenizer(corpus_path: str) -> Tokenizer:
    """Construct and train a BPE tokenizer on a plain-text corpus.

    The tokenizer pipeline consists of:
        - Model:          BPE (Byte-Pair Encoding) with the unknown token
                          set to <|unk|>.
        - Normalizer:     NFC Unicode normalization only.  Case is preserved
                          to maintain capital-letter distinctions (important
                          for named entities and sentence boundaries).
        - Pre-tokenizer:  ByteLevel pre-tokenization (GPT-2 convention).
                          Maps every byte of the input to a printable
                          character before BPE merging, ensuring that the
                          vocabulary can represent any byte sequence without
                          requiring an explicit unknown token.
        - Decoder:        ByteLevel decoder, which is the inverse of the
                          ByteLevel pre-tokenizer.

    Args:
        corpus_path: Path to the plain-text corpus file (one document per line).

    Returns:
        A trained Tokenizer instance ready for encoding and decoding text.
    """
    # BPE model with unknown token fallback
    tokenizer = Tokenizer(models.BPE(unk_token="<|unk|>"))

    # Unicode NFC normalization (no lowercasing: preserve case)
    tokenizer.normalizer = normalizers.NFC()

    # Byte-level pre-tokenization matches the GPT-2 tokenizer convention
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)

    # Byte-level decoder reconstructs text from token IDs
    tokenizer.decoder = decoders.ByteLevel()

    # BPE trainer configuration
    trainer = trainers.BpeTrainer(
        vocab_size=VOCAB_SIZE,
        min_frequency=MIN_FREQUENCY,
        special_tokens=SPECIAL_TOKENS,
        show_progress=True,
    )

    print(f"Training BPE tokenizer on : {corpus_path}")
    print(f"Target vocabulary size    : {VOCAB_SIZE:,}")
    print(f"Minimum merge frequency   : {MIN_FREQUENCY}")
    print(f"Special tokens            : {SPECIAL_TOKENS}\n")

    tokenizer.train([corpus_path], trainer)

    return tokenizer


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Validate that the corpus exists
    assert CORPUS_FILE.exists(), (
        f"Corpus not found at '{CORPUS_FILE}'.\n"
        f"Run 'python scripts/data_preparation.py' first."
    )

    size_mb = os.path.getsize(CORPUS_FILE) / 1024 / 1024
    print(f"Corpus file : {CORPUS_FILE}  ({size_mb:.1f} MB)\n")

    # Train the tokenizer
    tokenizer = build_and_train_tokenizer(str(CORPUS_FILE))

    # Save vocabulary and merge rules to disk
    TOKENIZER_DIR.mkdir(parents=True, exist_ok=True)
    tokenizer.save(str(TOKENIZER_FILE))

    actual_vocab_size = tokenizer.get_vocab_size()
    print(f"\nTokenizer saved to   : {TOKENIZER_FILE}")
    print(f"Final vocabulary size: {actual_vocab_size:,}")

    # --- Smoke test: encode and decode a sample sentence ---
    sample = (
        "The Transformer architecture introduced self-attention mechanisms "
        "that enable parallel processing of sequences."
    )
    encoding = tokenizer.encode(sample)
    decoded  = tokenizer.decode(encoding.ids)

    print(f"\nSmoke test:")
    print(f"  Input   : {sample!r}")
    print(f"  Tokens  : {encoding.tokens}")
    print(f"  IDs     : {encoding.ids}")
    print(f"  Decoded : {decoded!r}")

    # Verify round-trip consistency
    assert decoded.replace(" ", "") == sample.replace(" ", ""), (
        "WARNING: Decoded text does not match the original input after "
        "whitespace normalization."
    )
    print("\nTokenizer training complete. Next step: python scripts/pretrain.py")


if __name__ == "__main__":
    main()
