"""
Text generation utilities for RNN language models.
"""

import torch
import torch.nn.functional as F
import pickle
import argparse
import os

from models.rnn_model import get_model
from src.data_preprocessing import Vocabulary


def load_model_and_vocab(checkpoint_path, vocab_path=None):
    """
    Load trained model and vocabulary.
    
    Args:
        checkpoint_path (str): Path to model checkpoint
        vocab_path (str): Path to vocabulary file (optional)
        
    Returns:
        tuple: (model, vocab, device)
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model_config = checkpoint['model_config']
    vocab_size = checkpoint['vocab_size']
    
    # Create model
    model = get_model(
        model_config['model_type'],
        vocab_size=vocab_size,
        embed_size=model_config['embed_size'],
        hidden_size=model_config['hidden_size'],
        num_layers=model_config['num_layers'],
        dropout=0.0,  # No dropout during inference
        tie_weights=model_config.get('tie_weights', False)
    )
    
    # Load model state
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    # Load vocabulary
    if vocab_path and os.path.exists(vocab_path):
        vocab = Vocabulary()
        vocab.load(vocab_path)
    else:
        # Try to load from checkpoint directory
        checkpoint_dir = os.path.dirname(checkpoint_path)
        vocab_path = os.path.join(checkpoint_dir, '..', 'data', 'vocab.pkl')
        
        if os.path.exists(vocab_path):
            vocab = Vocabulary()
            vocab.load(vocab_path)
        else:
            raise FileNotFoundError("Vocabulary file not found. Please provide vocab_path.")
    
    print(f"Model loaded from {checkpoint_path}")
    print(f"Vocabulary size: {len(vocab)}")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    return model, vocab, device


def generate_text(model, vocab, prompt, max_length=50, temperature=1.0, top_k=None, device='cpu'):
    """
    Generate text using the trained RNN model.
    
    Args:
        model: Trained RNN model
        vocab: Vocabulary object
        prompt (str): Starting text prompt
        max_length (int): Maximum number of tokens to generate
        temperature (float): Temperature for sampling (higher = more random)
        top_k (int): Only sample from top-k most likely tokens
        device: Device to run inference on
        
    Returns:
        str: Generated text
    """
    model.eval()
    
    # Encode prompt
    tokens = vocab.encode(prompt)
    if not tokens:
        # Use BOS token if prompt is empty
        tokens = [vocab.token2idx[vocab.bos_token]]
    
    generated_tokens = tokens.copy()
    
    with torch.no_grad():
        # Initialize hidden state
        if hasattr(model, 'init_hidden'):
            hidden = model.init_hidden(1, device)
        else:
            hidden = None
        
        # Process prompt tokens (except last one)
        for i in range(len(tokens) - 1):
            input_tensor = torch.tensor([[tokens[i]]], device=device)
            
            if hasattr(model, 'init_hidden'):
                output, hidden = model(input_tensor, hidden)
            else:
                output = model(input_tensor)
        
        # Generate new tokens
        current_token = tokens[-1] if tokens else vocab.token2idx[vocab.bos_token]
        
        for _ in range(max_length):
            input_tensor = torch.tensor([[current_token]], device=device)
            
            # Forward pass
            if hasattr(model, 'init_hidden'):
                output, hidden = model(input_tensor, hidden)
            else:
                output = model(input_tensor)
            
            # Get logits for next token prediction
            logits = output[0, -1, :] / temperature
            
            # Apply top-k filtering if specified
            if top_k is not None:
                # Get top-k indices
                top_k_logits, top_k_indices = torch.topk(logits, min(top_k, logits.size(-1)))
                
                # Create mask for non-top-k tokens
                logits_filtered = torch.full_like(logits, float('-inf'))
                logits_filtered[top_k_indices] = top_k_logits
                logits = logits_filtered
            
            # Sample next token
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1).item()
            
            # Add to generated sequence
            generated_tokens.append(next_token)
            current_token = next_token
            
            # Stop if EOS token is generated
            if next_token == vocab.token2idx[vocab.eos_token]:
                break
    
    # Decode generated tokens
    generated_text = vocab.decode(generated_tokens)
    return generated_text


def generate_multiple_samples(model, vocab, prompt, num_samples=3, max_length=50, 
                            temperature=1.0, top_k=None, device='cpu'):
    """
    Generate multiple text samples.
    
    Args:
        model: Trained RNN model
        vocab: Vocabulary object
        prompt (str): Starting text prompt
        num_samples (int): Number of samples to generate
        max_length (int): Maximum length for each sample
        temperature (float): Temperature for sampling
        top_k (int): Top-k sampling parameter
        device: Device to run on
        
    Returns:
        list: List of generated text samples
    """
    samples = []
    
    for i in range(num_samples):
        print(f"Generating sample {i+1}/{num_samples}...")
        
        sample = generate_text(
            model, vocab, prompt, max_length, temperature, top_k, device
        )
        samples.append(sample)
    
    return samples


def interactive_generation(model, vocab, device):
    """
    Interactive text generation mode.
    
    Args:
        model: Trained RNN model
        vocab: Vocabulary object
        device: Device to run on
    """
    print("\n=== Interactive Text Generation ===")
    print("Enter prompts to generate text. Type 'quit' to exit.")
    print("Commands:")
    print("  'quit' - Exit interactive mode")
    print("  'temp X' - Set temperature to X (e.g., 'temp 0.8')")
    print("  'topk X' - Set top-k to X (e.g., 'topk 40')")
    print("  'length X' - Set max length to X (e.g., 'length 100')")
    print()
    
    # Default parameters
    temperature = 0.8
    top_k = 40
    max_length = 50
    
    while True:
        try:
            prompt = input("\nPrompt: ").strip()
            
            if prompt.lower() == 'quit':
                break
            elif prompt.startswith('temp '):
                try:
                    temperature = float(prompt.split()[1])
                    print(f"Temperature set to {temperature}")
                    continue
                except (IndexError, ValueError):
                    print("Invalid temperature. Use format: temp 0.8")
                    continue
            elif prompt.startswith('topk '):
                try:
                    top_k = int(prompt.split()[1])
                    print(f"Top-k set to {top_k}")
                    continue
                except (IndexError, ValueError):
                    print("Invalid top-k. Use format: topk 40")
                    continue
            elif prompt.startswith('length '):
                try:
                    max_length = int(prompt.split()[1])
                    print(f"Max length set to {max_length}")
                    continue
                except (IndexError, ValueError):
                    print("Invalid length. Use format: length 100")
                    continue
            
            # Generate text
            print("\nGenerating...")
            generated = generate_text(
                model, vocab, prompt, max_length, temperature, top_k, device
            )
            
            print(f"\nGenerated text:")
            print(f"{'='*50}")
            print(generated)
            print(f"{'='*50}")
            
            # Show parameters used
            print(f"\nParameters: temp={temperature}, top_k={top_k}, max_length={max_length}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description='Generate text with trained RNN model')
    
    # Model and data arguments
    parser.add_argument('--checkpoint', type=str, required=True,
                        help='Path to model checkpoint')
    parser.add_argument('--vocab', type=str, default=None,
                        help='Path to vocabulary file')
    
    # Generation arguments
    parser.add_argument('--prompt', type=str, default='The quick brown fox',
                        help='Text prompt for generation')
    parser.add_argument('--max-length', type=int, default=50,
                        help='Maximum length of generated text')
    parser.add_argument('--temperature', type=float, default=0.8,
                        help='Temperature for sampling')
    parser.add_argument('--top-k', type=int, default=40,
                        help='Top-k sampling parameter')
    parser.add_argument('--num-samples', type=int, default=1,
                        help='Number of samples to generate')
    
    # Mode arguments
    parser.add_argument('--interactive', action='store_true',
                        help='Enter interactive mode')
    
    args = parser.parse_args()
    
    # Load model and vocabulary
    print("Loading model and vocabulary...")
    model, vocab, device = load_model_and_vocab(args.checkpoint, args.vocab)
    
    if args.interactive:
        # Interactive mode
        interactive_generation(model, vocab, device)
    else:
        # Single generation mode
        print(f"\nPrompt: {args.prompt}")
        print(f"Parameters: temperature={args.temperature}, top_k={args.top_k}, max_length={args.max_length}")
        print()
        
        if args.num_samples == 1:
            generated = generate_text(
                model, vocab, args.prompt, args.max_length, 
                args.temperature, args.top_k, device
            )
            print("Generated text:")
            print("="*50)
            print(generated)
            print("="*50)
        else:
            samples = generate_multiple_samples(
                model, vocab, args.prompt, args.num_samples,
                args.max_length, args.temperature, args.top_k, device
            )
            
            print(f"Generated {len(samples)} samples:")
            for i, sample in enumerate(samples, 1):
                print(f"\nSample {i}:")
                print("="*30)
                print(sample)
                print("="*30)


if __name__ == '__main__':
    main()
