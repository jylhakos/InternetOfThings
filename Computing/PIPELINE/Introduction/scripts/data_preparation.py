"""
Data preparation script for LLM pre-training.

Downloads and preprocesses a text dataset from Hugging Face using streaming
mode (no full dataset download required) and saves a cleaned plain-text
corpus file suitable for tokenizer training and model pre-training.

Dataset used: FineWeb-Edu (HuggingFaceFW/fineweb-edu)
    A high-quality educational subset of Common Crawl.
    Source: https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu

Usage:
    Activate the virtual environment first:
        source venv/bin/activate

    Then run:
        python scripts/data_preparation.py

Output:
    data/cleaned/corpus.txt   One cleaned document per line.

Dependencies:
    datasets, tqdm
    Install via: pip install datasets tqdm
"""

import os
import re
import unicodedata
from pathlib import Path

from datasets import load_dataset
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Number of documents to download from the streaming dataset.
# 100,000 documents from FineWeb-Edu yields approximately 50-100 MB of text,
# which is sufficient for training a small tokenizer and running short
# pre-training experiments.  Scale this up for production runs.
NUM_SAMPLES: int = 100_000

# Discard documents shorter than this character count after cleaning.
MIN_CHARS: int = 100

OUTPUT_DIR:  Path = Path("data") / "cleaned"
CORPUS_FILE: Path = OUTPUT_DIR / "corpus.txt"


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Apply a sequence of normalization steps to a raw text document.

    Cleaning steps:
        1. Unicode NFC normalization — canonicalizes character representations
           (e.g., composed vs. decomposed accented characters).
        2. Whitespace normalization — collapses runs of spaces, tabs, and
           non-breaking spaces into a single ASCII space.
        3. Control character removal — strips null bytes and other ASCII
           control characters that are artifacts of web crawl extraction.
        4. Strip leading and trailing whitespace.

    Args:
        text: Raw string from the dataset sample.

    Returns:
        Cleaned string.  Empty string if the input is None or empty.
    """
    if not text:
        return ""

    # NFC normalization
    text = unicodedata.normalize("NFC", text)

    # Collapse whitespace variants to a single space
    text = re.sub(r"[ \t\u00a0\u200b\u200c\u200d\ufeff]+", " ", text)

    # Remove ASCII control characters except newline (0x0a) and carriage return
    text = re.sub(r"[\x00-\x09\x0b\x0c\x0e-\x1f\x7f]", "", text)

    return text.strip()


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading FineWeb-Edu dataset (streaming, {NUM_SAMPLES:,} samples)...")
    print("Streaming mode avoids downloading the full dataset.\n")

    dataset = load_dataset(
        "HuggingFaceFW/fineweb-edu",
        name="sample-10BT",
        split="train",
        streaming=True,
        trust_remote_code=True,
    )

    # --- Stage 1: Download ---
    raw_texts: list[str] = []
    for i, sample in enumerate(tqdm(dataset, total=NUM_SAMPLES, desc="Downloading")):
        if i >= NUM_SAMPLES:
            break
        raw_texts.append(sample["text"])

    total_raw_chars = sum(len(t) for t in raw_texts)
    print(f"\nDownloaded  : {len(raw_texts):,} samples")
    print(f"Raw chars   : {total_raw_chars:,}")

    # --- Stage 2: Clean and filter ---
    cleaned: list[str] = []
    for text in tqdm(raw_texts, desc="Cleaning "):
        text = clean_text(text)
        if len(text) >= MIN_CHARS:
            cleaned.append(text)

    print(f"Retained    : {len(cleaned):,} documents after length filtering")
    print(f"Discarded   : {len(raw_texts) - len(cleaned):,} documents (< {MIN_CHARS} chars)")

    # --- Stage 3: Write corpus ---
    # Each document is written as a single line.
    # Internal newlines are collapsed to spaces to maintain the one-document-
    # per-line format required by the tokenizer trainer.
    with open(CORPUS_FILE, "w", encoding="utf-8") as fh:
        for doc in tqdm(cleaned, desc="Writing  "):
            fh.write(doc.replace("\n", " ") + "\n")

    size_mb = os.path.getsize(CORPUS_FILE) / 1024 / 1024
    print(f"\nCorpus written to : {CORPUS_FILE}")
    print(f"Corpus size       : {size_mb:.1f} MB")
    print(f"\nFirst 500 characters of corpus:")
    print(cleaned[0][:500] if cleaned else "(empty corpus)")
    print("\nData preparation complete. Next step: python scripts/tokenizer_train.py")


if __name__ == "__main__":
    main()
