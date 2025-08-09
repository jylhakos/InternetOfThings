import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR
import os
import time
import math
from tqdm import tqdm
import matplotlib.pyplot as plt
from model import create_model, count_parameters
from data_utils import load_wikitext_dataset, Vocabulary, create_data_loaders


class LanguageModelTrainer:
    """
    Trainer class for language models with support for RNN, Transformer, and Hybrid models.
    """
    
    def __init__(self, model, train_loader, val_loader, device, vocab_size):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.vocab_size = vocab_size
        
        # Training components
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(model.parameters(), lr=0.001)
        self.scheduler = StepLR(self.optimizer, step_size=5, gamma=0.8)
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.train_perplexities = []
        self.val_perplexities = []
    
    def train_epoch(self):
        """Train model for one epoch."""
        self.model.train()
        total_loss = 0
        num_batches = len(self.train_loader)
        
        progress_bar = tqdm(self.train_loader, desc="Training", leave=False)
        
        for batch_idx, (inputs, targets) in enumerate(progress_bar):
            inputs, targets = inputs.to(self.device), targets.to(self.device)
            
            self.optimizer.zero_grad()
            
            # Forward pass
            if hasattr(self.model, 'init_hidden'):  # RNN model
                batch_size = inputs.size(0)
                hidden = self.model.init_hidden(batch_size, self.device)
                outputs, _ = self.model(inputs, hidden)
            else:  # Transformer or Hybrid model
                outputs = self.model(inputs)
            
            # Compute loss
            loss = self.criterion(outputs.view(-1, self.vocab_size), targets.view(-1))
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 0.5)
            
            self.optimizer.step()
            
            total_loss += loss.item()
            
            # Update progress bar
            progress_bar.set_postfix({
                'Loss': f'{loss.item():.4f}',
                'PPL': f'{math.exp(loss.item()):.2f}'
            })
        
        avg_loss = total_loss / num_batches
        perplexity = math.exp(avg_loss)
        
        return avg_loss, perplexity
    
    def validate(self):
        """Validate model on validation set."""
        self.model.eval()
        total_loss = 0
        num_batches = len(self.val_loader)
        
        with torch.no_grad():
            for inputs, targets in self.val_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                
                # Forward pass
                if hasattr(self.model, 'init_hidden'):  # RNN model
                    batch_size = inputs.size(0)
                    hidden = self.model.init_hidden(batch_size, self.device)
                    outputs, _ = self.model(inputs, hidden)
                else:  # Transformer or Hybrid model
                    outputs = self.model(inputs)
                
                # Compute loss
                loss = self.criterion(outputs.view(-1, self.vocab_size), targets.view(-1))
                total_loss += loss.item()
        
        avg_loss = total_loss / num_batches
        perplexity = math.exp(avg_loss)
        
        return avg_loss, perplexity
    
    def train(self, num_epochs, save_dir='checkpoints'):
        """
        Train model for specified number of epochs.
        
        Args:
            num_epochs: Number of epochs to train
            save_dir: Directory to save model checkpoints
        """
        os.makedirs(save_dir, exist_ok=True)
        
        print(f"Starting training for {num_epochs} epochs...")
        print(f"Model parameters: {count_parameters(self.model):,}")
        
        best_val_loss = float('inf')
        
        for epoch in range(num_epochs):
            print(f"\nEpoch {epoch + 1}/{num_epochs}")
            print("-" * 50)
            
            start_time = time.time()
            
            # Train
            train_loss, train_ppl = self.train_epoch()
            self.train_losses.append(train_loss)
            self.train_perplexities.append(train_ppl)
            
            # Validate
            val_loss, val_ppl = self.validate()
            self.val_losses.append(val_loss)
            self.val_perplexities.append(val_ppl)
            
            # Update learning rate
            self.scheduler.step()
            
            epoch_time = time.time() - start_time
            
            print(f"Train Loss: {train_loss:.4f}, Train PPL: {train_ppl:.2f}")
            print(f"Val Loss: {val_loss:.4f}, Val PPL: {val_ppl:.2f}")
            print(f"Epoch Time: {epoch_time:.2f}s")
            print(f"Learning Rate: {self.scheduler.get_last_lr()[0]:.6f}")
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self.save_model(os.path.join(save_dir, 'best_model.pt'))
                print("✓ Saved best model")
            
            # Save checkpoint every 5 epochs
            if (epoch + 1) % 5 == 0:
                self.save_checkpoint(os.path.join(save_dir, f'checkpoint_epoch_{epoch+1}.pt'), epoch)
        
        print(f"\nTraining completed!")
        print(f"Best validation loss: {best_val_loss:.4f}")
        print(f"Best validation perplexity: {math.exp(best_val_loss):.2f}")
    
    def save_model(self, filepath):
        """Save model state dict."""
        torch.save(self.model.state_dict(), filepath)
    
    def save_checkpoint(self, filepath, epoch):
        """Save training checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_perplexities': self.train_perplexities,
            'val_perplexities': self.val_perplexities
        }
        torch.save(checkpoint, filepath)
    
    def load_checkpoint(self, filepath):
        """Load training checkpoint."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.train_losses = checkpoint['train_losses']
        self.val_losses = checkpoint['val_losses']
        self.train_perplexities = checkpoint['train_perplexities']
        self.val_perplexities = checkpoint['val_perplexities']
        return checkpoint['epoch']
    
    def plot_training_history(self, save_path=None):
        """Plot training and validation losses and perplexities."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot losses
        epochs = range(1, len(self.train_losses) + 1)
        ax1.plot(epochs, self.train_losses, 'b-', label='Train Loss')
        ax1.plot(epochs, self.val_losses, 'r-', label='Validation Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Plot perplexities
        ax2.plot(epochs, self.train_perplexities, 'b-', label='Train Perplexity')
        ax2.plot(epochs, self.val_perplexities, 'r-', label='Validation Perplexity')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Perplexity')
        ax2.set_title('Training and Validation Perplexity')
        ax2.legend()
        ax2.grid(True)
        ax2.set_yscale('log')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Training history saved to {save_path}")
        
        plt.show()


def train_model(model_type='hybrid', num_epochs=10, batch_size=32, seq_length=128):
    """
    Main training function.
    
    Args:
        model_type: Type of model ('rnn', 'transformer', or 'hybrid')
        num_epochs: Number of training epochs
        batch_size: Batch size for training
        seq_length: Sequence length for training
    """
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load data
    print("Loading WikiText dataset...")
    data = load_wikitext_dataset('wikitext-2-raw-v1')
    
    # Create vocabulary
    print("Building vocabulary...")
    vocab = Vocabulary()
    vocab.build_vocab_from_texts(data['train'], min_freq=2)
    vocab_size = len(vocab)
    print(f"Vocabulary size: {vocab_size}")
    
    # Save vocabulary
    vocab.save('vocab.pkl')
    
    # Create data loaders
    print("Creating data loaders...")
    data_loaders = create_data_loaders(
        data, vocab, seq_length=seq_length, batch_size=batch_size
    )
    
    # Create model
    print(f"Creating {model_type} model...")
    
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
    model = model.to(device)
    
    print(f"Model created with {count_parameters(model):,} parameters")
    
    # Create trainer
    trainer = LanguageModelTrainer(
        model, data_loaders['train'], data_loaders['validation'], device, vocab_size
    )
    
    # Train model
    save_dir = f'checkpoints_{model_type}'
    trainer.train(num_epochs, save_dir)
    
    # Plot training history
    trainer.plot_training_history(f'{save_dir}/training_history.png')
    
    return model, vocab, trainer


if __name__ == "__main__":
    # Example usage - train all three model types
    model_types = ['rnn', 'transformer', 'hybrid']
    
    for model_type in model_types:
        print(f"\n{'='*60}")
        print(f"Training {model_type.upper()} model")
        print(f"{'='*60}")
        
        model, vocab, trainer = train_model(
            model_type=model_type,
            num_epochs=5,  # Reduced for demo
            batch_size=16,  # Smaller batch size for demo
            seq_length=64   # Shorter sequences for demo
        )
        
        print(f"{model_type.upper()} model training completed!\n")
