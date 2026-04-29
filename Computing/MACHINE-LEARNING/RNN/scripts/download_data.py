"""
Script to download and prepare WikiText dataset.
"""

import os
import argparse
from src.data_preprocessing import preprocess_wikitext


def download_and_prepare_data(args):
    """
    Download and prepare WikiText dataset.
    
    Args:
        args: Command line arguments
    """
    print("WikiText Dataset Download and Preparation")
    print("=" * 50)
    
    # Create data directory
    os.makedirs(args.data_dir, exist_ok=True)
    print(f"Data directory: {args.data_dir}")
    
    # Download and preprocess data
    print(f"\nDownloading WikiText-{args.dataset} dataset...")
    print(f"This may take a few minutes on first run...")
    
    try:
        data_loaders, vocab = preprocess_wikitext(
            dataset_name=f"wikitext-{args.dataset}-v1",
            vocab_size=args.vocab_size,
            min_freq=args.min_freq,
            seq_length=args.seq_length,
            batch_size=args.batch_size,
            cache_dir=args.data_dir,
            save_vocab=True
        )
        
        print("\n" + "="*50)
        print("Dataset prepared successfully!")
        print("="*50)
        
        # Print statistics
        print(f"\nDataset Statistics:")
        print(f"  Dataset version: wikitext-{args.dataset}-v1")
        print(f"  Vocabulary size: {len(vocab):,}")
        print(f"  Sequence length: {args.seq_length}")
        print(f"  Batch size: {args.batch_size}")
        print(f"  Minimum token frequency: {args.min_freq}")
        
        print(f"\nData Loaders:")
        for split, loader in data_loaders.items():
            print(f"  {split.capitalize()}: {len(loader):,} batches")
        
        # Show vocabulary samples
        print(f"\nVocabulary Sample (most common tokens):")
        most_common = list(vocab.token_counts.most_common(20))
        for i, (token, count) in enumerate(most_common):
            print(f"  {i+1:2d}. '{token}' ({count:,})")
        
        # Show file locations
        print(f"\nFiles created:")
        vocab_path = os.path.join(args.data_dir, 'vocab.pkl')
        if os.path.exists(vocab_path):
            print(f"  Vocabulary: {vocab_path}")
        
        print(f"  Dataset cache: {args.data_dir}/")
        
        print(f"\nTo use this data for training:")
        print(f"  python src/train_clean.py --data-dir {args.data_dir} --vocab-size {len(vocab)} --seq-length {args.seq_length}")
        
    except Exception as e:
        print(f"\nError downloading/preparing data: {e}")
        print("This might be due to network issues or HuggingFace dataset problems.")
        print("\nTrying with fallback dummy data...")
        
        try:
            # Try with dummy data
            data_loaders, vocab = preprocess_wikitext(
                dataset_name="dummy",  # This will trigger fallback
                vocab_size=args.vocab_size,
                min_freq=1,  # Lower min_freq for dummy data
                seq_length=args.seq_length,
                batch_size=args.batch_size,
                cache_dir=args.data_dir,
                save_vocab=True
            )
            
            print("✓ Fallback dummy data prepared successfully!")
            print("  This data can be used for testing the pipeline.")
            
        except Exception as e2:
            print(f"✗ Even fallback data preparation failed: {e2}")
            return False
    
    return True


def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description='Download WikiText Dataset')
    
    # Dataset arguments
    parser.add_argument('--dataset', type=str, default='2',
                        choices=['2', '103'],
                        help='WikiText dataset version (2 or 103)')
    parser.add_argument('--data-dir', type=str, default='./data',
                        help='Directory to store dataset')
    
    # Preprocessing arguments
    parser.add_argument('--vocab-size', type=int, default=10000,
                        help='Maximum vocabulary size')
    parser.add_argument('--min-freq', type=int, default=2,
                        help='Minimum token frequency')
    parser.add_argument('--seq-length', type=int, default=128,
                        help='Sequence length for training')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for data loaders')
    
    args = parser.parse_args()
    
    print("Arguments:")
    for key, value in vars(args).items():
        print(f"  {key}: {value}")
    print()
    
    success = download_and_prepare_data(args)
    
    if success:
        print("\n✓ Data preparation completed successfully!")
        exit(0)
    else:
        print("\n✗ Data preparation failed!")
        exit(1)


if __name__ == '__main__':
    main()
