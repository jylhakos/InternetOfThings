"""
Utility Functions for RLHF Training
====================================
Common utilities for data processing, model evaluation, and training helpers.
"""

import torch
import json
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np
from transformers import PreTrainedTokenizer
from datasets import Dataset


def format_alpaca_prompt(instruction: str, input_text: str = "", output: str = "") -> str:
    """
    Format data in Alpaca instruction format.
    
    Args:
        instruction: Task description
        input_text: Optional context or input
        output: Expected response
    
    Returns:
        Formatted prompt string
    """
    if input_text.strip():
        prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input_text}

### Response:
{output}"""
    else:
        prompt = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
{output}"""
    
    return prompt


def format_chat_prompt(messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
    """
    Format messages in a chat format.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        system_prompt: Optional system prompt to prepend
    
    Returns:
        Formatted chat string
    """
    prompt = ""
    
    if system_prompt:
        prompt += f"System: {system_prompt}\n\n"
    
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        
        if role == "user":
            prompt += f"Human: {content}\n\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n\n"
        elif role == "system":
            prompt += f"System: {content}\n\n"
    
    # Add Assistant: prefix for generation
    if messages and messages[-1]["role"] != "assistant":
        prompt += "Assistant:"
    
    return prompt


def create_preference_dataset(
    prompts: List[str],
    chosen_responses: List[str],
    rejected_responses: List[str]
) -> Dataset:
    """
    Create a preference dataset from lists of prompts and responses.
    
    Args:
        prompts: List of prompts
        chosen_responses: List of preferred responses
        rejected_responses: List of non-preferred responses
    
    Returns:
        HuggingFace Dataset object
    """
    assert len(prompts) == len(chosen_responses) == len(rejected_responses), \
        "All lists must have the same length"
    
    data = {
        "prompt": prompts,
        "chosen": chosen_responses,
        "rejected": rejected_responses
    }
    
    return Dataset.from_dict(data)


def count_trainable_parameters(model) -> Tuple[int, int]:
    """
    Count trainable and total parameters in a model.
    
    Args:
        model: PyTorch model
    
    Returns:
        Tuple of (trainable_params, total_params)
    """
    trainable_params = 0
    total_params = 0
    
    for param in model.parameters():
        total_params += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    
    return trainable_params, total_params


def print_model_info(model, model_name: str = "Model"):
    """
    Print detailed model information.
    
    Args:
        model: PyTorch model
        model_name: Name to display
    """
    trainable, total = count_trainable_parameters(model)
    
    print(f"\n{model_name} Information:")
    print(f"{'=' * 60}")
    print(f"Total Parameters: {total:,}")
    print(f"Trainable Parameters: {trainable:,}")
    print(f"Trainable %: {100 * trainable / total:.2f}%")
    print(f"Model Memory: {total * 4 / 1e9:.2f} GB (FP32)")
    print(f"Model Memory: {total * 2 / 1e9:.2f} GB (FP16/BF16)")
    print(f"{'=' * 60}")


def estimate_training_time(
    num_samples: int,
    batch_size: int,
    num_epochs: int,
    seconds_per_step: float = 1.0
) -> Dict[str, float]:
    """
    Estimate training time based on dataset size and parameters.
    
    Args:
        num_samples: Number of training samples
        batch_size: Batch size
        num_epochs: Number of epochs
        seconds_per_step: Estimated seconds per training step
    
    Returns:
        Dictionary with time estimates
    """
    steps_per_epoch = num_samples // batch_size
    total_steps = steps_per_epoch * num_epochs
    total_seconds = total_steps * seconds_per_step
    
    hours = total_seconds / 3600
    
    return {
        "steps_per_epoch": steps_per_epoch,
        "total_steps": total_steps,
        "estimated_hours": hours,
        "estimated_days": hours / 24
    }


def save_training_config(config: dict, output_dir: str, filename: str = "training_config.json"):
    """
    Save training configuration to a JSON file.
    
    Args:
        config: Configuration dictionary
        output_dir: Output directory
        filename: Filename for the config
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    # Add timestamp
    config["timestamp"] = datetime.now().isoformat()
    
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Training config saved to: {filepath}")


def load_training_config(filepath: str) -> dict:
    """
    Load training configuration from a JSON file.
    
    Args:
        filepath: Path to config file
    
    Returns:
        Configuration dictionary
    """
    with open(filepath, 'r') as f:
        config = json.load(f)
    return config


def compute_perplexity(model, tokenizer: PreTrainedTokenizer, texts: List[str]) -> float:
    """
    Compute perplexity of a model on given texts.
    
    Perplexity measures how well the model predicts the text.
    Lower perplexity = better performance.
    
    Args:
        model: Language model
        tokenizer: Tokenizer
        texts: List of text strings
    
    Returns:
        Average perplexity
    """
    model.eval()
    total_loss = 0
    total_tokens = 0
    
    with torch.no_grad():
        for text in texts:
            encodings = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            input_ids = encodings.input_ids.to(model.device)
            
            outputs = model(input_ids, labels=input_ids)
            loss = outputs.loss
            
            total_loss += loss.item() * input_ids.size(1)
            total_tokens += input_ids.size(1)
    
    avg_loss = total_loss / total_tokens
    perplexity = torch.exp(torch.tensor(avg_loss)).item()
    
    return perplexity


def log_gpu_memory():
    """
    Log current GPU memory usage.
    """
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            allocated = torch.cuda.memory_allocated(i) / 1e9
            reserved = torch.cuda.memory_reserved(i) / 1e9
            total = torch.cuda.get_device_properties(i).total_memory / 1e9
            
            print(f"\nGPU {i} ({torch.cuda.get_device_name(i)}):")
            print(f"  Allocated: {allocated:.2f} GB")
            print(f"  Reserved: {reserved:.2f} GB")
            print(f"  Total: {total:.2f} GB")
            print(f"  Free: {total - reserved:.2f} GB")


def clear_gpu_cache():
    """
    Clear GPU cache to free up memory.
    """
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        print("GPU cache cleared")


class MetricsLogger:
    """
    Simple metrics logger for tracking training progress.
    """
    
    def __init__(self, log_dir: str = "./logs"):
        """
        Initialize metrics logger.
        
        Args:
            log_dir: Directory to save logs
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        self.metrics = []
        self.start_time = datetime.now()
    
    def log(self, step: int, metrics: dict):
        """
        Log metrics for a training step.
        
        Args:
            step: Training step number
            metrics: Dictionary of metric values
        """
        log_entry = {
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": (datetime.now() - self.start_time).total_seconds(),
            **metrics
        }
        self.metrics.append(log_entry)
    
    def save(self, filename: str = "metrics.json"):
        """
        Save metrics to a JSON file.
        
        Args:
            filename: Output filename
        """
        filepath = os.path.join(self.log_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        print(f"Metrics saved to: {filepath}")
    
    def get_summary(self) -> dict:
        """
        Get a summary of logged metrics.
        
        Returns:
            Dictionary with metric summaries
        """
        if not self.metrics:
            return {}
        
        summary = {"total_steps": len(self.metrics)}
        
        # Calculate averages for numeric metrics
        numeric_keys = [k for k in self.metrics[0].keys() 
                       if isinstance(self.metrics[0][k], (int, float)) and k != "step"]
        
        for key in numeric_keys:
            values = [m[key] for m in self.metrics if key in m]
            summary[f"{key}_mean"] = np.mean(values)
            summary[f"{key}_std"] = np.std(values)
            summary[f"{key}_min"] = np.min(values)
            summary[f"{key}_max"] = np.max(values)
        
        return summary


def generate_sample_outputs(
    model,
    tokenizer: PreTrainedTokenizer,
    prompts: List[str],
    max_new_tokens: int = 128,
    temperature: float = 0.7
) -> List[str]:
    """
    Generate sample outputs from a model for evaluation.
    
    Args:
        model: Language model
        tokenizer: Tokenizer
        prompts: List of prompts
        max_new_tokens: Maximum tokens to generate
        temperature: Sampling temperature
    
    Returns:
        List of generated texts
    """
    model.eval()
    outputs = []
    
    with torch.no_grad():
        for prompt in prompts:
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            
            generated = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id
            )
            
            text = tokenizer.decode(generated[0], skip_special_tokens=True)
            outputs.append(text)
    
    return outputs


if __name__ == "__main__":
    # Example usage
    print("Utility Functions for RLHF Training")
    print("=" * 60)
    
    # Test prompt formatting
    prompt = format_alpaca_prompt(
        instruction="Explain what RLHF is",
        input_text="",
        output="RLHF stands for Reinforcement Learning from Human Feedback..."
    )
    print("\nSample Alpaca Format:")
    print(prompt)
    
    # Test training time estimation
    estimate = estimate_training_time(
        num_samples=10000,
        batch_size=4,
        num_epochs=3,
        seconds_per_step=2.0
    )
    print(f"\nTraining Time Estimate:")
    print(f"  Total Steps: {estimate['total_steps']}")
    print(f"  Estimated Hours: {estimate['estimated_hours']:.2f}")
    print(f"  Estimated Days: {estimate['estimated_days']:.2f}")
