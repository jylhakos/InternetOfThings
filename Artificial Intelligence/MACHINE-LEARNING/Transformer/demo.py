#!/usr/bin/env python3
"""
Demo script showing the progression from RNN to Transformer models.
This script demonstrates the capabilities and differences between different architectures.
"""

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import time
from model import create_model, count_parameters
from data_utils import load_wikitext_dataset, Vocabulary, create_data_loaders
from train import LanguageModelTrainer


def demo_model_architectures():
    """
    Demonstrate the different model architectures and their characteristics.
    """
    print("=" * 80)
    print("DEMO: RNN vs Transformer vs Hybrid Models")
    print("=" * 80)
    
    # Set up device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create a small vocabulary for demo
    vocab_size = 1000
    seq_length = 64
    batch_size = 4
    
    # Model configurations
    models_config = {
        'RNN (LSTM)': {
            'type': 'rnn',
            'params': {
                'embed_size': 128,
                'hidden_size': 256,
                'num_layers': 2,
                'dropout': 0.1
            }
        },
        'Transformer': {
            'type': 'transformer',
            'params': {
                'd_model': 256,
                'nhead': 8,
                'num_layers': 4,
                'dropout': 0.1
            }
        },
        'Hybrid (RNN + Transformer)': {
            'type': 'hybrid',
            'params': {
                'embed_size': 128,
                'hidden_size': 128,
                'd_model': 256,
                'nhead': 8,
                'num_transformer_layers': 2,
                'num_rnn_layers': 1,
                'dropout': 0.1
            }
        }
    }
    
    # Create and analyze models
    models = {}
    model_stats = {}
    
    for model_name, config in models_config.items():
        print(f"\n{'-' * 60}")
        print(f"Creating {model_name} Model")
        print(f"{'-' * 60}")
        
        # Create model
        model = create_model(config['type'], vocab_size, **config['params'])
        model = model.to(device)
        models[model_name] = model
        
        # Count parameters
        param_count = count_parameters(model)
        print(f"Parameters: {param_count:,}")
        
        # Measure inference time
        dummy_input = torch.randint(0, vocab_size, (batch_size, seq_length)).to(device)
        
        # Warm up
        with torch.no_grad():
            for _ in range(5):
                if hasattr(model, 'init_hidden'):
                    hidden = model.init_hidden(batch_size, device)
                    _ = model(dummy_input, hidden)
                else:
                    _ = model(dummy_input)
        
        # Time inference
        torch.cuda.synchronize() if device.type == 'cuda' else None
        start_time = time.time()
        
        with torch.no_grad():
            for _ in range(100):
                if hasattr(model, 'init_hidden'):
                    hidden = model.init_hidden(batch_size, device)
                    outputs = model(dummy_input, hidden)[0]
                else:
                    outputs = model(dummy_input)
        
        torch.cuda.synchronize() if device.type == 'cuda' else None
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100 * 1000  # Convert to ms
        
        model_stats[model_name] = {
            'parameters': param_count,
            'inference_time_ms': avg_time,
            'output_shape': outputs.shape
        }
        
        print(f"Average inference time: {avg_time:.2f} ms")
        print(f"Output shape: {outputs.shape}")
        print(f"Memory usage: ~{param_count * 4 / 1024 / 1024:.1f} MB (FP32)")
    
    # Create comparison visualization
    create_model_comparison_plot(model_stats)
    
    return models, model_stats


def create_model_comparison_plot(model_stats):
    """Create visualization comparing different models."""
    model_names = list(model_stats.keys())
    parameters = [stats['parameters'] / 1000 for stats in model_stats.values()]  # In thousands
    inference_times = [stats['inference_time_ms'] for stats in model_stats.values()]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Parameters comparison
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    bars1 = ax1.bar(model_names, parameters, color=colors, alpha=0.7)
    ax1.set_ylabel('Parameters (thousands)')
    ax1.set_title('Model Size Comparison')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, param in zip(bars1, parameters):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{param:.0f}K', ha='center', va='bottom')
    
    # Inference time comparison
    bars2 = ax2.bar(model_names, inference_times, color=colors, alpha=0.7)
    ax2.set_ylabel('Inference Time (ms)')
    ax2.set_title('Inference Speed Comparison')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, time_ms in zip(bars2, inference_times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{time_ms:.1f}ms', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('model_comparison.png', dpi=300, bbox_inches='tight')
    print(f"\nModel comparison plot saved to 'model_comparison.png'")
    plt.show()


def demo_attention_vs_recurrence():
    """
    Demonstrate the key differences between attention and recurrence mechanisms.
    """
    print("\n" + "=" * 80)
    print("DEMO: Attention Mechanism vs Recurrent Processing")
    print("=" * 80)
    
    print("\n1. RECURRENT PROCESSING (RNN/LSTM)")
    print("-" * 40)
    print("• Processes sequences step by step")
    print("• Hidden state carries information from previous steps")
    print("• Limited by sequential nature - cannot parallelize")
    print("• May struggle with long-range dependencies")
    print("• Memory efficient for long sequences")
    
    sequence = ["The", "cat", "sat", "on", "the", "mat"]
    print(f"\nExample sequence: {sequence}")
    print("RNN processing:")
    for i, word in enumerate(sequence):
        print(f"  Step {i+1}: Process '{word}' with hidden state from step {i}")
    
    print("\n2. ATTENTION MECHANISM (Transformer)")
    print("-" * 40)
    print("• Processes all positions simultaneously")
    print("• Each position attends to all other positions")
    print("• Fully parallelizable during training")
    print("• Can capture long-range dependencies effectively")
    print("• Memory usage grows quadratically with sequence length")
    
    print(f"\nSame sequence: {sequence}")
    print("Transformer processing:")
    print("  All positions processed simultaneously")
    print("  Attention matrix shows relationships between all word pairs:")
    
    # Create a simple attention visualization
    attention_demo = np.random.rand(len(sequence), len(sequence))
    attention_demo = attention_demo / attention_demo.sum(axis=1, keepdims=True)  # Normalize
    
    print("  Attention weights (simplified):")
    print("       ", "   ".join([f"{w[:3]}" for w in sequence]))
    for i, word in enumerate(sequence):
        weights_str = "  ".join([f"{w:.2f}" for w in attention_demo[i]])
        print(f"  {word[:3]:3s}: {weights_str}")
    
    print("\n3. HYBRID APPROACH (RNN + Transformer)")
    print("-" * 40)
    print("• Combines benefits of both approaches")
    print("• RNN provides sequential inductive bias")
    print("• Transformer adds global attention capabilities")
    print("• Can be more parameter efficient than pure Transformer")
    print("• Suitable for tasks requiring both local and global context")


def demo_transformer_attention():
    """
    Visualize how Transformer attention works.
    """
    print("\n" + "=" * 80)
    print("DEMO: Transformer Attention Mechanism")
    print("=" * 80)
    
    # Create a simple attention example
    sequence_length = 8
    d_model = 64
    
    # Simulate query, key, value matrices
    np.random.seed(42)
    Q = np.random.randn(sequence_length, d_model)
    K = np.random.randn(sequence_length, d_model)
    V = np.random.randn(sequence_length, d_model)
    
    # Compute attention scores
    scores = np.dot(Q, K.T) / np.sqrt(d_model)
    attention_weights = np.exp(scores) / np.exp(scores).sum(axis=1, keepdims=True)
    
    # Create visualization
    plt.figure(figsize=(10, 8))
    plt.imshow(attention_weights, cmap='Blues', aspect='auto')
    plt.colorbar(label='Attention Weight')
    plt.title('Self-Attention Weights Matrix\n(Each row shows where token i attends)')
    plt.xlabel('Key Position')
    plt.ylabel('Query Position')
    
    # Add grid
    plt.grid(True, alpha=0.3)
    plt.xticks(range(sequence_length))
    plt.yticks(range(sequence_length))
    
    plt.tight_layout()
    plt.savefig('attention_weights.png', dpi=300, bbox_inches='tight')
    print("Attention weights visualization saved to 'attention_weights.png'")
    plt.show()
    
    print("\nKey Insights:")
    print("• Darker colors indicate stronger attention")
    print("• Diagonal elements show self-attention")
    print("• Off-diagonal elements show cross-attention between positions")
    print("• Each row sums to 1 (attention is normalized)")


def demo_with_real_data():
    """
    Demonstrate models with real WikiText data.
    """
    print("\n" + "=" * 80)
    print("DEMO: Training Progress with WikiText Dataset")
    print("=" * 80)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load small subset of data for quick demo
    print("Loading WikiText dataset...")
    data = load_wikitext_dataset('wikitext-2-raw-v1')
    
    # Use smaller subset for demo
    data['train'] = data['train'][:100]  # Use only first 100 samples
    data['validation'] = data['validation'][:20]
    
    # Create vocabulary
    vocab = Vocabulary()
    vocab.build_vocab_from_texts(data['train'], min_freq=1)
    vocab_size = len(vocab)
    
    print(f"Vocabulary size: {vocab_size}")
    print(f"Training samples: {len(data['train'])}")
    
    # Create data loaders
    data_loaders = create_data_loaders(
        data, vocab, seq_length=32, batch_size=4, num_workers=0
    )
    
    # Train a small hybrid model for demo
    print("\nTraining small hybrid model (3 epochs)...")
    model = create_model('hybrid', vocab_size,
                        embed_size=64, hidden_size=64, d_model=128,
                        nhead=4, num_transformer_layers=1, num_rnn_layers=1,
                        dropout=0.1)
    model = model.to(device)
    
    trainer = LanguageModelTrainer(
        model, data_loaders['train'], data_loaders['validation'], device, vocab_size
    )
    
    # Quick training
    trainer.train(num_epochs=3, save_dir='demo_checkpoints')
    trainer.plot_training_history('demo_training.png')
    
    print("Demo training completed!")
    print("Check 'demo_training.png' for training progress visualization")


def main():
    """Main demo function."""
    print("RNN + Transformer Language Model Demo")
    print("This demo illustrates the progression from RNN to Transformer architectures")
    print("and shows how they can be combined effectively.")
    
    try:
        # 1. Model architecture comparison
        demo_model_architectures()
        
        # 2. Attention vs Recurrence explanation
        demo_attention_vs_recurrence()
        
        # 3. Transformer attention visualization
        demo_transformer_attention()
        
        # 4. Real data demo (optional - can be slow)
        user_input = input("\nWould you like to run a quick training demo? (y/N): ")
        if user_input.lower().startswith('y'):
            demo_with_real_data()
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nGenerated files:")
        print("• model_comparison.png - Model architecture comparison")
        print("• attention_weights.png - Attention mechanism visualization")
        if user_input.lower().startswith('y'):
            print("• demo_training.png - Training progress")
        
        print("\nNext steps:")
        print("1. Run 'python train.py' to train full models")
        print("2. Run 'python generate.py --demo' to test text generation")
        print("3. Run 'python api.py' to start the inference API")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
