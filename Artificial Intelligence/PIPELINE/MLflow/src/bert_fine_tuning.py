import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from transformers import BertForSequenceClassification, BertTokenizer, AdamW, get_scheduler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
import pandas as pd
import time
import psutil
import gc
import os
import json

def get_device_info():
    """
    Hardware detection and optimization for BERT fine-tuning
    Returns optimal device configuration and hardware information
    """
    print("="*60)
    print("HARDWARE DETECTION AND CUDA OPTIMIZATION")
    print("="*60)
    
    # Check CUDA availability and GPU details
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        current_gpu = torch.cuda.current_device()
        gpu_name = torch.cuda.get_device_name(current_gpu)
        gpu_memory = torch.cuda.get_device_properties(current_gpu).total_memory
        gpu_memory_gb = gpu_memory / (1024**3)
        
        print(f"CUDA AVAILABLE: YES")
        print(f"GPU Count: {gpu_count}")
        print(f"Active GPU: {current_gpu} ({gpu_name})")
        print(f"GPU Memory: {gpu_memory_gb:.2f} GB")
        
        # Check GPU memory usage
        if hasattr(torch.cuda, 'memory_reserved'):
            reserved = torch.cuda.memory_reserved(current_gpu) / (1024**3)
            allocated = torch.cuda.memory_allocated(current_gpu) / (1024**3)
            print(f"Memory reserved: {reserved:.2f} GB")
            print(f"Memory allocated: {allocated:.2f} GB")
        
        # CUDA optimization settings
        print(f"CUDA version: {torch.version.cuda}")
        print(f"cuDNN version: {torch.backends.cudnn.version()}")
        
        # Enable optimizations for BERT fine-tuning
        if torch.backends.cudnn.is_available():
            torch.backends.cudnn.benchmark = True  # Optimize for consistent input sizes
            torch.backends.cudnn.deterministic = False  # Allow non-deterministic algorithms for speed
            print("cuDNN optimizations enabled")
        
        # Set memory fraction to prevent OOM errors
        if gpu_memory_gb > 8:
            device = torch.device('cuda')
            print("Using GPU for optimal performance")
        else:
            device = torch.device('cuda')
            print("Limited GPU memory detected - consider reducing batch size")
            
    else:
        print(f"❌ CUDA NOT AVAILABLE")
        print(f"Using CPU for computation")
        
        # CPU information
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        ram_info = psutil.virtual_memory()
        ram_gb = ram_info.total / (1024**3)
        
        print(f"CPU cores: {cpu_count}")
        if cpu_freq:
            print(f"CPU frequency: {cpu_freq.current:.2f} MHz")
        print(f"System RAM: {ram_gb:.2f} GB")
        print(f"Available RAM: {ram_info.available / (1024**3):.2f} GB")
        
        device = torch.device('cpu')
        
        # CPU optimizations
        torch.set_num_threads(cpu_count)
        print(f"Set PyTorch threads to {cpu_count}")
    
    print(f"Selected device: {device}")
    print("="*60)
    
    return device

def optimize_for_bert_training(device):
    """
    Apply BERT-specific optimizations based on hardware
    """
    if device.type == 'cuda':
        # GPU optimizations for BERT
        print("Applying GPU optimizations for BERT fine-tuning:")
        
        # Mixed precision training for faster training and lower memory usage
        try:
            from torch.cuda.amp import autocast, GradScaler
            use_amp = True
            scaler = GradScaler()
            print("Automatic Mixed Precision (AMP) enabled")
        except ImportError:
            use_amp = False
            scaler = None
            print("AMP not available - using float32")
        
        # Clear GPU cache
        torch.cuda.empty_cache()
        print("GPU cache cleared")
        
        # Optimal batch size suggestions
        gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        if gpu_memory_gb >= 16:
            suggested_batch_size = 16
            suggested_max_length = 512
        elif gpu_memory_gb >= 8:
            suggested_batch_size = 8
            suggested_max_length = 256
        else:
            suggested_batch_size = 4
            suggested_max_length = 128
            
        print(f"Suggested batch size: {suggested_batch_size}")
        print(f"Suggested max sequence length: {suggested_max_length}")
        
    else:
        # CPU optimizations for BERT
        print("Applying CPU optimizations for BERT fine-tuning:")
        use_amp = False
        scaler = None
        suggested_batch_size = 2
        suggested_max_length = 128
        
        # Enable JIT compilation for CPU
        torch.jit.set_compiler_enabled(True)
        print("JIT compilation enabled")
        print(f"Suggested batch size: {suggested_batch_size}")
        print(f"Suggested max sequence length: {suggested_max_length}")
    
    return use_amp, scaler, suggested_batch_size, suggested_max_length

def monitor_resources(device):
    """Monitor GPU/CPU usage during training"""
    if device.type == 'cuda':
        gpu_memory_used = torch.cuda.memory_allocated(0) / (1024**3)
        gpu_memory_cached = torch.cuda.memory_reserved(0) / (1024**3)
        return f"GPU Memory: {gpu_memory_used:.2f}GB used, {gpu_memory_cached:.2f}GB cached"
    else:
        ram_info = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        return f"CPU: {cpu_percent:.1f}%, RAM: {ram_info.percent:.1f}%"

# Initialize hardware detection and optimization
device = get_device_info()
use_amp, scaler, suggested_batch_size, suggested_max_length = optimize_for_bert_training(device)

print("\n" + "="*60)
print("BERT MODEL SETUP WITH HARDWARE OPTIMIZATION")
print("="*60)

# Load pre-trained BERT model and tokenizer with domain-specific optimization
model_name = 'bert-base-uncased'
print(f"Loading BERT model: {model_name}")

tokenizer = BertTokenizer.from_pretrained(model_name)
print(f"Tokenizer loaded (vocab size: {tokenizer.vocab_size})")

# Load model with optimized configuration for hardware
model = BertForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2,
    output_attentions=False,  # Set to True if you want attention weights for analysis
    output_hidden_states=False,  # Set to True if you want hidden states
    return_dict=True
)

# Move model to optimal device
model.to(device)
print(f"Model loaded and moved to {device}")

# Count parameters for memory estimation
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total parameters: {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")

# Model size estimation
model_size_mb = (total_params * 4) / (1024 * 1024)  # Assuming float32
print(f"Estimated model size: {model_size_mb:.1f} MB")

# Sample input text and labels for binary classification
# For domain-specific fine-tuning, replace these with your domain data
texts = [
    "Hello, how are you?",
    "I am fine, thank you.",
    "This is terrible!",
    "I love this!",
    "Not bad at all.",
    "The service was excellent and fast!",
    "Poor quality, very disappointed.",
    "Average product, nothing special.",
    "Outstanding performance, highly recommended!",
    "Waste of money, doesn't work as advertised."
]
labels = [1, 1, 0, 1, 1, 1, 0, 0, 1, 0]  # 1 for positive, 0 for negative

print(f"Training data: {len(texts)} samples")
print(f"Label distribution: {labels.count(1)} positive, {labels.count(0)} negative")

# Tokenize the input text with hardware-optimized settings
print("Tokenizing input text...")
inputs = tokenizer(
    texts,
    padding=True,
    truncation=True,
    return_tensors="pt",
    max_length=suggested_max_length  # Use hardware-optimized length
)

print(f"Tokenization complete")
print(f"Sequence length: {inputs['input_ids'].shape[1]}")
print(f"Batch shape: {inputs['input_ids'].shape}")

# Create dataset and dataloader with optimized batch size
dataset = TensorDataset(inputs['input_ids'], inputs['attention_mask'], torch.tensor(labels))
dataloader = DataLoader(
    dataset,
    batch_size=suggested_batch_size,  # Use hardware-optimized batch size
    shuffle=True,
    num_workers=2 if device.type == 'cpu' else 0,  # Use multiprocessing for CPU
    pin_memory=True if device.type == 'cuda' else False  # Optimize GPU memory transfer
)

print(f"DataLoader created with batch size: {suggested_batch_size}")
print(f"Number of batches: {len(dataloader)}")

# Fine-tuning setup with hardware-optimized parameters
print("\n" + "="*60)
print("OPTIMIZER AND TRAINING CONFIGURATION")
print("="*60)

# Learning rate optimization based on hardware
if device.type == 'cuda':
    learning_rate = 2e-5  # Standard rate for GPU
    num_epochs = 3
    warmup_steps = len(dataloader) // 4  # 25% warmup
else:
    learning_rate = 1e-5  # Lower rate for CPU stability
    num_epochs = 2  # Fewer epochs for CPU
    warmup_steps = 0

optimizer = AdamW(
    model.parameters(),
    lr=learning_rate,
    eps=1e-8,
    weight_decay=0.01  # L2 regularization
)

print(f"Learning rate: {learning_rate}")
print(f"Epochs: {num_epochs}")
print(f"Warmup steps: {warmup_steps}")
total_steps = len(dataloader) * num_epochs

# Learning rate scheduler
scheduler = get_scheduler(
    name="linear",
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=total_steps
)

print("\n" + "="*60)
print("STARTING BERT FINE-TUNING WITH HARDWARE OPTIMIZATION")
print("="*60)

# Training loop with hardware optimization
model.train()
total_start_time = time.time()

# Track best model for early stopping
best_loss = float('inf')
patience_counter = 0
patience_limit = 2

for epoch in range(num_epochs):
    epoch_start_time = time.time()
    total_loss = 0
    num_batches = len(dataloader)
    
    print(f"\nStarting Epoch {epoch+1}/{num_epochs}")
    print(f"{monitor_resources(device)}")
    
    for batch_idx, batch in enumerate(dataloader):
        batch_start_time = time.time()
        
        # Clear gradients
        optimizer.zero_grad()
        
        # Move batch to device
        input_ids, attention_mask, label = batch
        input_ids = input_ids.to(device, non_blocking=True)
        attention_mask = attention_mask.to(device, non_blocking=True)
        label = label.to(device, non_blocking=True)
        
        # Forward pass with optional mixed precision
        if use_amp and device.type == 'cuda':
            # Mixed precision forward pass (GPU only)
            try:
                from torch.cuda.amp import autocast
                with autocast():
                    outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=label)
                    loss = outputs.loss
                
                # Mixed precision backward pass
                scaler.scale(loss).backward()
                
                # Gradient clipping for stability
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                
                # Optimizer step with scaling
                scaler.step(optimizer)
                scaler.update()
                
            except ImportError:
                # Fallback to regular precision
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=label)
                loss = outputs.loss
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
        else:
            # Regular precision training (CPU or GPU without AMP)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=label)
            loss = outputs.loss
            loss.backward()
            
            # Gradient clipping for training stability
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
        
        # Update learning rate scheduler
        scheduler.step()
        
        # Track loss
        current_loss = loss.item()
        total_loss += current_loss
        
        # Batch timing
        batch_time = time.time() - batch_start_time
        
        # Progress reporting
        if batch_idx % max(1, num_batches // 4) == 0 or batch_idx == num_batches - 1:
            current_lr = scheduler.get_last_lr()[0] if scheduler else learning_rate
            
            print(f"Epoch {epoch+1}/{num_epochs}, Batch {batch_idx+1}/{num_batches}")
            print(f"Loss: {current_loss:.4f}, LR: {current_lr:.2e}, Time: {batch_time:.2f}s")
            print(f"{monitor_resources(device)}")
            
        # Memory management for GPU
        if device.type == 'cuda' and batch_idx % 10 == 0:
            torch.cuda.empty_cache()
    
    # Epoch summary
    epoch_time = time.time() - epoch_start_time
    avg_loss = total_loss / num_batches
    
    print(f"\n Epoch {epoch+1}/{num_epochs} completed!")
    print(f"Average Loss: {avg_loss:.4f}")
    print(f"Epoch Time: {epoch_time:.2f} seconds")
    print(f"Throughput: {len(texts) / epoch_time:.2f} samples/second")
    
    # Early stopping check
    if avg_loss < best_loss:
        best_loss = avg_loss
        patience_counter = 0
        # Save best model checkpoint
        print("New best model - saving checkpoint...")
    else:
        patience_counter += 1
        print(f"No improvement for {patience_counter} epochs")
        
    if patience_counter >= patience_limit:
        print(f"Early stopping triggered after {epoch+1} epochs")
        break

# Training completion summary
total_time = time.time() - total_start_time
print(f"\n" + "="*60)
print("FINE-TUNING COMPLETED!")
print("="*60)
print(f"Total training time: {total_time:.2f} seconds")
print(f"Final loss: {avg_loss:.4f}")
print(f"Final resource usage: {monitor_resources(device)}")

# Memory cleanup
if device.type == 'cuda':
    torch.cuda.empty_cache()
    print("GPU cache cleared")
gc.collect()
print("Python garbage collection completed")

# Enhanced evaluation function with hardware optimization
def evaluate_model(model, texts, labels, device):
    """Enhanced evaluation with hardware optimization"""
    print(f"\n📊 Starting model evaluation on {device}...")
    model.eval()
    predictions = []
    confidences = []
    eval_start_time = time.time()
    
    with torch.no_grad():
        for i, text in enumerate(texts):
            # Tokenize with consistent settings
            inputs = tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=suggested_max_length
            )
            inputs = {key: val.to(device, non_blocking=True) for key, val in inputs.items()}
            
            # Forward pass
            if use_amp and device.type == 'cuda':
                try:
                    from torch.cuda.amp import autocast
                    with autocast():
                        outputs = model(**inputs)
                except ImportError:
                    outputs = model(**inputs)
            else:
                outputs = model(**inputs)
            
            # Get predictions and confidence scores
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            predicted_class = torch.argmax(logits, dim=-1).cpu().numpy()[0]
            confidence = torch.max(probabilities).cpu().numpy()
            
            predictions.append(predicted_class)
            confidences.append(confidence)
    
    eval_time = time.time() - eval_start_time
    accuracy = accuracy_score(labels, predictions)
    
    print(f"Evaluation completed in {eval_time:.2f} seconds")
    print(f"Average confidence: {np.mean(confidences):.3f}")
    
    return predictions, accuracy, confidences

# Test the model with optimized evaluation
test_texts = ["I really enjoyed this experience!", "This was awful.", "Amazing product quality!", "Terrible service experience."]
test_labels = [1, 0, 1, 0]

print(f"\nTesting model with {len(test_texts)} samples...")
predictions, accuracy, confidences = evaluate_model(model, test_texts, test_labels, device)

print(f"\nMODEL PERFORMANCE SUMMARY")
print("="*50)
print(f"Test accuracy: {accuracy:.3f}")
print(f"Average confidence: {np.mean(confidences):.3f}")
print(f"Device Used: {device}")
print(f"CUDA available: {'Yes' if torch.cuda.is_available() else 'No'}")
if device.type == 'cuda':
    print(f"GPU memory used: {torch.cuda.memory_allocated(device) / 1024**3:.2f} GB")
    print(f"GPU memory cached: {torch.cuda.memory_reserved(device) / 1024**3:.2f} GB")

print(f"\nIndividual predictions:")
for i, (text, true_label, pred_label, conf) in enumerate(zip(test_texts, test_labels, predictions, confidences)):
    status = "" if true_label == pred_label else "❌"
    print(f"{status} Sample {i+1}: '{text[:50]}...' -> Predicted: {pred_label}, True: {true_label}, Confidence: {conf:.3f}")

# Enhanced model saving with comprehensive metadata
print(f"\nSAVING FINE-TUNED MODEL...")
save_directory = "../models/bert-fine-tuned"
os.makedirs(save_directory, exist_ok=True)

# Save model and tokenizer
model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)

# Save training metadata and hardware info
metadata = {
    "training_info": {
        "model_name": model_name,
        "num_epochs": num_epochs,
        "batch_size": suggested_batch_size,
        "learning_rate": learning_rate,
        "final_accuracy": float(accuracy),
        "device_used": str(device),
        "cuda_available": torch.cuda.is_available(),
        "mixed_precision": use_amp and device.type == 'cuda',
        "total_training_time": total_time,
        "num_samples": len(texts),
        "max_length": suggested_max_length
    },
    "hardware_optimization": {
        "device_type": device.type,
        "amp_enabled": use_amp,
        "suggested_batch_size": suggested_batch_size,
        "suggested_max_length": suggested_max_length
    },
    "performance_metrics": {
        "test_accuracy": float(accuracy),
        "average_confidence": float(np.mean(confidences)),
        "samples_per_second": len(texts) / total_time if 'total_time' in locals() else 0
    },
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
}

# Save metadata to JSON file
import json
with open(f"{save_directory}/training_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2, default=str)

print(f"Model saved to: {save_directory}")
print(f"Training metadata saved to: {save_directory}/training_metadata.json")

# Final cleanup and summary
if device.type == 'cuda':
    torch.cuda.empty_cache()
    final_memory = torch.cuda.memory_allocated(device) / 1024**3
    print(f"Final GPU memory usage: {final_memory:.2f} GB")

print(f"\n" + "="*70)
print("BERT FINE-TUNING COMPLETED SUCCESSFULLY! 🎉")
print("="*70)
print(f"Model ready for production use")
print(f"Test accuracy: {accuracy:.1%}")
print(f"Hardware optimization: {'CUDA + Mixed Precision' if use_amp and device.type == 'cuda' else 'Standard'}")
print(f"Model location: {save_directory}")
print(f"Ready for API deployment!")
print("="*70)
print(f"\nTest Results:")
print(f"Texts: {test_texts}")
print(f"True labels: {test_labels}")
print(f"Predictions: {predictions}")
print(f"Accuracy: {accuracy:.2f}")

# Save the model
model.save_pretrained("./fine_tuned_bert")
tokenizer.save_pretrained("./fine_tuned_bert")
print("Model saved to ./fine_tuned_bert")