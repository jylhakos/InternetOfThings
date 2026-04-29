import torch
import torch.nn.functional as F
import pickle
import argparse
from model import create_model
from data_utils import Vocabulary


class TextGenerator:
    """
    Text generation class for language models.
    """
    
    def __init__(self, model, vocab, device):
        self.model = model
        self.vocab = vocab
        self.device = device
        self.model.eval()
    
    def generate_text(self, prompt="", max_length=100, temperature=1.0, top_k=50, top_p=0.95):
        """
        Generate text using the trained model.
        
        Args:
            prompt: Starting text prompt
            max_length: Maximum length of generated text
            temperature: Temperature for sampling (higher = more random)
            top_k: Consider only top k most likely tokens
            top_p: Nucleus sampling threshold
        
        Returns:
            Generated text as string
        """
        self.model.eval()
        
        with torch.no_grad():
            # Tokenize prompt
            if prompt:
                tokens = self.vocab.tokenize(prompt)
                input_ids = [self.vocab(token) for token in tokens]
            else:
                input_ids = [self.vocab('<sos>')]  # Start with SOS token
            
            input_ids = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0).to(self.device)
            generated = input_ids.clone()
            
            # Initialize hidden state for RNN models
            hidden = None
            if hasattr(self.model, 'init_hidden'):
                hidden = self.model.init_hidden(1, self.device)
            
            for _ in range(max_length):
                # Get model predictions
                if hasattr(self.model, 'init_hidden'):  # RNN model
                    outputs, hidden = self.model(input_ids, hidden)
                    logits = outputs[:, -1, :]  # Get last time step
                else:  # Transformer or Hybrid model
                    outputs = self.model(input_ids)
                    logits = outputs[:, -1, :]  # Get last time step
                
                # Apply temperature
                logits = logits / temperature
                
                # Apply top-k filtering
                if top_k > 0:
                    top_k_logits, top_k_indices = torch.topk(logits, top_k)
                    logits = torch.full_like(logits, float('-inf'))
                    logits.scatter_(1, top_k_indices, top_k_logits)
                
                # Apply top-p (nucleus) filtering
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                    
                    # Remove tokens with cumulative probability above the threshold
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    
                    indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                    logits[indices_to_remove] = float('-inf')
                
                # Sample next token
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # Check for end of sequence
                if next_token.item() == self.vocab('<eos>'):
                    break
                
                # Append to generated sequence
                generated = torch.cat([generated, next_token], dim=-1)
                
                # Prepare input for next iteration
                if hasattr(self.model, 'init_hidden'):  # RNN model
                    input_ids = next_token
                else:  # Transformer or Hybrid model
                    input_ids = generated  # Use full sequence for attention
                    
                    # Limit context window for efficiency
                    if input_ids.size(1) > 512:
                        input_ids = input_ids[:, -512:]
            
            # Decode generated tokens
            generated_tokens = generated.squeeze().cpu().tolist()
            generated_text = []
            
            for token_id in generated_tokens:
                word = self.vocab.decode(token_id)
                if word not in ['<pad>', '<sos>', '<eos>', '<unk>']:
                    generated_text.append(word)
            
            return ' '.join(generated_text)
    
    def interactive_generation(self):
        """Interactive text generation loop."""
        print("Interactive Text Generation")
        print("=" * 40)
        print("Enter prompts to generate text. Type 'quit' to exit.")
        print("Parameters: max_length=100, temperature=0.8, top_k=50\n")
        
        while True:
            try:
                prompt = input("Enter prompt: ").strip()
                
                if prompt.lower() == 'quit':
                    break
                
                print("\nGenerating text...")
                generated_text = self.generate_text(
                    prompt=prompt,
                    max_length=100,
                    temperature=0.8,
                    top_k=50
                )
                
                print(f"\nGenerated text:\n{generated_text}\n")
                print("-" * 40)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


def load_model_and_vocab(model_path, vocab_path, model_type='hybrid'):
    """
    Load trained model and vocabulary.
    
    Args:
        model_path: Path to saved model
        vocab_path: Path to saved vocabulary
        model_type: Type of model ('rnn', 'transformer', or 'hybrid')
    
    Returns:
        Loaded model and vocabulary
    """
    # Load vocabulary
    vocab = Vocabulary()
    vocab.load(vocab_path)
    vocab_size = len(vocab)
    
    # Create model with same configuration as training
    model_configs = {
        'rnn': {
            'embed_size': 128,
            'hidden_size': 256,
            'num_layers': 2,
            'dropout': 0.2
        },
        'transformer': {
            'd_model': 512,
            'nhead': 8,
            'num_layers': 6,
            'dropout': 0.1
        },
        'hybrid': {
            'embed_size': 256,
            'hidden_size': 256,
            'd_model': 512,
            'nhead': 8,
            'num_transformer_layers': 3,
            'num_rnn_layers': 2,
            'dropout': 0.1
        }
    }
    
    model = create_model(model_type, vocab_size, **model_configs[model_type])
    
    # Load model weights
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    
    return model, vocab


def demo_generation():
    """
    Demonstration of text generation with different models.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Demo prompts
    prompts = [
        "The future of artificial intelligence",
        "Machine learning has revolutionized",
        "Deep neural networks can",
        "Natural language processing enables",
        "The transformer architecture"
    ]
    
    # Try to load models and generate text
    model_types = ['hybrid', 'transformer', 'rnn']
    
    for model_type in model_types:
        print(f"\n{'='*60}")
        print(f"{model_type.upper()} Model Text Generation")
        print(f"{'='*60}")
        
        try:
            model_path = f'checkpoints_{model_type}/best_model.pt'
            vocab_path = 'vocab.pkl'
            
            model, vocab = load_model_and_vocab(model_path, vocab_path, model_type)
            generator = TextGenerator(model, vocab, device)
            
            for prompt in prompts:
                print(f"\nPrompt: '{prompt}'")
                generated = generator.generate_text(
                    prompt=prompt,
                    max_length=50,
                    temperature=0.8,
                    top_k=50
                )
                print(f"Generated: {generated}")
                
        except FileNotFoundError:
            print(f"Model files not found for {model_type}. Train the model first.")
        except Exception as e:
            print(f"Error loading {model_type} model: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Text Generation with Language Models')
    parser.add_argument('--model_type', type=str, default='hybrid',
                        choices=['rnn', 'transformer', 'hybrid'],
                        help='Type of model to use for generation')
    parser.add_argument('--model_path', type=str, default=None,
                        help='Path to saved model file')
    parser.add_argument('--vocab_path', type=str, default='vocab.pkl',
                        help='Path to saved vocabulary file')
    parser.add_argument('--prompt', type=str, default='',
                        help='Text prompt for generation')
    parser.add_argument('--max_length', type=int, default=100,
                        help='Maximum length of generated text')
    parser.add_argument('--temperature', type=float, default=0.8,
                        help='Sampling temperature')
    parser.add_argument('--top_k', type=int, default=50,
                        help='Top-k sampling parameter')
    parser.add_argument('--interactive', action='store_true',
                        help='Run in interactive mode')
    parser.add_argument('--demo', action='store_true',
                        help='Run demo with multiple models')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_generation()
    elif args.interactive:
        try:
            model_path = args.model_path or f'checkpoints_{args.model_type}/best_model.pt'
            model, vocab = load_model_and_vocab(model_path, args.vocab_path, args.model_type)
            
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            generator = TextGenerator(model, vocab, device)
            generator.interactive_generation()
            
        except FileNotFoundError:
            print(f"Model files not found. Train the model first using: python train.py")
        except Exception as e:
            print(f"Error: {e}")
    else:
        try:
            model_path = args.model_path or f'checkpoints_{args.model_type}/best_model.pt'
            model, vocab = load_model_and_vocab(model_path, args.vocab_path, args.model_type)
            
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            generator = TextGenerator(model, vocab, device)
            
            generated_text = generator.generate_text(
                prompt=args.prompt,
                max_length=args.max_length,
                temperature=args.temperature,
                top_k=args.top_k
            )
            
            print(f"Prompt: '{args.prompt}'")
            print(f"Generated: {generated_text}")
            
        except FileNotFoundError:
            print(f"Model files not found. Train the model first using: python train.py")
        except Exception as e:
            print(f"Error: {e}")
