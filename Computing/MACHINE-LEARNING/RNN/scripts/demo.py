"""
Demo script for RNN language model with WikiText dataset.
This script demonstrates the complete pipeline from data preprocessing to text generation.
"""

import torch
import os
import time
from datetime import datetime

# Import our modules
from models.rnn_model import RNNLanguageModel, count_parameters
from src.data_preprocessing import preprocess_wikitext
from src.generate import generate_text


def demo_data_preprocessing():
    """
    Demonstrate data preprocessing pipeline.
    """
    print("="*60)
    print("DEMO: Data Preprocessing Pipeline")
    print("="*60)
    
    print("\n1. Loading WikiText dataset...")
    try:
        data_loaders, vocab = preprocess_wikitext(
            dataset_name="wikitext-2-v1",
            vocab_size=5000,  # Smaller vocab for demo
            seq_length=64,    # Shorter sequences for demo
            batch_size=8,     # Smaller batch for demo
            cache_dir="./data"
        )
        
        print(f"✓ Dataset loaded successfully!")
        print(f"  - Vocabulary size: {len(vocab):,}")
        print(f"  - Training batches: {len(data_loaders['train'])}")
        print(f"  - Validation batches: {len(data_loaders['validation'])}")
        print(f"  - Test batches: {len(data_loaders['test'])}")
        
        # Show sample batch
        train_loader = data_loaders['train']
        sample_batch = next(iter(train_loader))
        input_seq, target_seq = sample_batch
        
        print(f"\n2. Sample batch shape:")
        print(f"  - Input sequence: {input_seq.shape}")
        print(f"  - Target sequence: {target_seq.shape}")
        
        # Decode sample text
        sample_text = vocab.decode(input_seq[0].tolist()[:20])  # First 20 tokens
        print(f"\n3. Sample decoded text (first 20 tokens):")
        print(f"  '{sample_text}'")
        
        # Show vocabulary statistics
        print(f"\n4. Vocabulary statistics:")
        print(f"  - Special tokens: {vocab.pad_token}, {vocab.unk_token}, {vocab.eos_token}, {vocab.bos_token}")
        print(f"  - Most common tokens: {list(vocab.token_counts.most_common(10))}")
        
        return data_loaders, vocab
        
    except Exception as e:
        print(f"✗ Error in data preprocessing: {e}")
        return None, None


def demo_model_creation(vocab_size):
    """
    Demonstrate model creation and architecture.
    """
    print("\n" + "="*60)
    print("DEMO: Model Architecture")
    print("="*60)
    
    # Model configurations to demo
    configs = [
        {'name': 'Small LSTM', 'model_type': 'lstm', 'embed_size': 128, 'hidden_size': 256, 'num_layers': 1},
        {'name': 'Medium LSTM', 'model_type': 'lstm', 'embed_size': 256, 'hidden_size': 512, 'num_layers': 2},
        {'name': 'GRU Model', 'model_type': 'gru', 'embed_size': 256, 'hidden_size': 512, 'num_layers': 2},
    ]
    
    models = {}
    
    for config in configs:
        print(f"\n{config['name']} ({config['model_type'].upper()}):")
        
        model = RNNLanguageModel(
            vocab_size=vocab_size,
            embed_size=config['embed_size'],
            hidden_size=config['hidden_size'],
            num_layers=config['num_layers'],
            rnn_type=config['model_type'].upper(),
            dropout=0.2
        )
        
        param_count = count_parameters(model)
        models[config['name']] = model
        
        print(f"  - Parameters: {param_count:,}")
        print(f"  - Embedding: {config['embed_size']} dim")
        print(f"  - Hidden: {config['hidden_size']} dim")
        print(f"  - Layers: {config['num_layers']}")
        
        # Test forward pass
        batch_size, seq_len = 4, 10
        dummy_input = torch.randint(0, vocab_size, (batch_size, seq_len))
        
        with torch.no_grad():
            hidden = model.init_hidden(batch_size)
            output, new_hidden = model(dummy_input, hidden)
            
        print(f"  - Input shape: {dummy_input.shape}")
        print(f"  - Output shape: {output.shape}")
    
    return models['Medium LSTM']  # Return medium model for training demo


def demo_training_step(model, data_loaders, vocab):
    """
    Demonstrate a few training steps.
    """
    print("\n" + "="*60)
    print("DEMO: Training Process")
    print("="*60)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nUsing device: {device}")
    
    model = model.to(device)
    model.train()
    
    # Setup training components
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    train_loader = data_loaders['train']
    
    print(f"\nRunning 5 training steps...")
    start_time = time.time()
    
    for step, (input_seq, target_seq) in enumerate(train_loader):
        if step >= 5:  # Only run 5 steps for demo
            break
            
        input_seq, target_seq = input_seq.to(device), target_seq.to(device)
        batch_size = input_seq.size(0)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        hidden = model.init_hidden(batch_size, device)
        output, hidden = model(input_seq, hidden)
        
        # Calculate loss
        loss = criterion(output.view(-1, output.size(-1)), target_seq.view(-1))
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        
        # Update parameters
        optimizer.step()
        
        print(f"  Step {step+1}: Loss = {loss.item():.4f}")
    
    elapsed = time.time() - start_time
    print(f"\nCompleted 5 training steps in {elapsed:.2f} seconds")
    
    # Quick evaluation
    print(f"\nQuick evaluation on validation set...")
    model.eval()
    val_loader = data_loaders['validation']
    
    total_loss = 0
    num_batches = 0
    
    with torch.no_grad():
        for batch_idx, (input_seq, target_seq) in enumerate(val_loader):
            if batch_idx >= 3:  # Only evaluate on 3 batches
                break
                
            input_seq, target_seq = input_seq.to(device), target_seq.to(device)
            batch_size = input_seq.size(0)
            
            hidden = model.init_hidden(batch_size, device)
            output, hidden = model(input_seq, hidden)
            
            loss = criterion(output.view(-1, output.size(-1)), target_seq.view(-1))
            total_loss += loss.item()
            num_batches += 1
    
    avg_val_loss = total_loss / num_batches
    perplexity = torch.exp(torch.tensor(avg_val_loss))
    
    print(f"  Validation loss: {avg_val_loss:.4f}")
    print(f"  Perplexity: {perplexity:.2f}")
    
    return model


def demo_text_generation(model, vocab):
    """
    Demonstrate text generation with different strategies.
    """
    print("\n" + "="*60)
    print("DEMO: Text Generation")
    print("="*60)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.eval()
    
    # Different prompts to try
    prompts = [
        "The weather today",
        "Machine learning is",
        "In the future",
        "Once upon a time"
    ]
    
    # Different generation strategies
    strategies = [
        {'name': 'Conservative (temp=0.5, top_k=10)', 'temperature': 0.5, 'top_k': 10},
        {'name': 'Balanced (temp=0.8, top_k=40)', 'temperature': 0.8, 'top_k': 40},
        {'name': 'Creative (temp=1.2, top_k=100)', 'temperature': 1.2, 'top_k': 100},
    ]
    
    for prompt in prompts:
        print(f"\n{'='*40}")
        print(f"Prompt: '{prompt}'")
        print(f"{'='*40}")
        
        for strategy in strategies:
            print(f"\n{strategy['name']}:")
            
            try:
                generated = generate_text(
                    model=model,
                    vocab=vocab,
                    prompt=prompt,
                    max_length=30,
                    temperature=strategy['temperature'],
                    top_k=strategy['top_k'],
                    device=device
                )
                
                print(f"  {generated}")
                
            except Exception as e:
                print(f"  Error: {e}")


def demo_autograd():
    """
    Demonstrate PyTorch's autograd functionality.
    """
    print("\n" + "="*60)
    print("DEMO: PyTorch Autograd")
    print("="*60)
    
    print("\n1. Basic autograd example:")
    
    # Create tensors with gradient tracking
    x = torch.randn(3, requires_grad=True)
    y = torch.randn(3, requires_grad=True)
    
    print(f"  x = {x}")
    print(f"  y = {y}")
    
    # Forward pass - builds computational graph
    z = x * y
    loss = z.sum()
    
    print(f"  z = x * y = {z}")
    print(f"  loss = z.sum() = {loss}")
    
    # Backward pass - computes gradients
    loss.backward()
    
    print(f"  x.grad = {x.grad}")
    print(f"  y.grad = {y.grad}")
    
    print("\n2. Neural network autograd example:")
    
    # Simple neural network
    vocab_size, embed_dim, hidden_dim = 100, 8, 16
    
    embedding = torch.nn.Embedding(vocab_size, embed_dim)
    linear = torch.nn.Linear(embed_dim, hidden_dim)
    output = torch.nn.Linear(hidden_dim, vocab_size)
    
    # Forward pass
    input_ids = torch.randint(0, vocab_size, (2, 5))  # batch_size=2, seq_len=5
    targets = torch.randint(0, vocab_size, (2, 5))
    
    print(f"  Input shape: {input_ids.shape}")
    print(f"  Target shape: {targets.shape}")
    
    # Forward
    embedded = embedding(input_ids)
    hidden = torch.relu(linear(embedded))
    logits = output(hidden)
    
    print(f"  Embedded shape: {embedded.shape}")
    print(f"  Logits shape: {logits.shape}")
    
    # Loss
    criterion = torch.nn.CrossEntropyLoss()
    loss = criterion(logits.view(-1, vocab_size), targets.view(-1))
    
    print(f"  Loss: {loss.item():.4f}")
    
    # Backward pass
    loss.backward()
    
    # Show gradients
    print(f"  Embedding grad norm: {embedding.weight.grad.norm():.4f}")
    print(f"  Linear grad norm: {linear.weight.grad.norm():.4f}")
    print(f"  Output grad norm: {output.weight.grad.norm():.4f}")


def main():
    """
    Main demo function.
    """
    print("RNN Language Model Demo")
    print("=" * 60)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name()}")
    print()
    
    try:
        # 1. Data preprocessing demo
        data_loaders, vocab = demo_data_preprocessing()
        
        if data_loaders is None:
            print("Data preprocessing failed. Using dummy data for remaining demos.")
            vocab_size = 1000
            data_loaders = None
            vocab = None
        else:
            vocab_size = len(vocab)
        
        # 2. Model architecture demo
        model = demo_model_creation(vocab_size)
        
        # 3. Training demo (only if data is available)
        if data_loaders is not None:
            model = demo_training_step(model, data_loaders, vocab)
            
            # 4. Text generation demo
            demo_text_generation(model, vocab)
        
        # 5. Autograd demo
        demo_autograd()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext steps:")
        print("1. Train a full model: python src/train_clean.py --epochs 10")
        print("2. Generate text: python src/generate.py --checkpoint checkpoints/best_model.pth")
        print("3. Start API server: python api/app.py --checkpoint checkpoints/best_model.pth")
        print("4. Test with cURL: curl -X POST http://localhost:5000/generate -H 'Content-Type: application/json' -d '{\"prompt\":\"Hello world\", \"max_length\":50}'")
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nDemo finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
