"""
Supervised Fine-Tuning (SFT) - Stage 1 of RLHF Pipeline
========================================================
This script demonstrates how to perform supervised fine-tuning on a pre-trained LLM
using instruction-following datasets. This is the first step in the RLHF process.

Key Concepts:
- Parameter-Efficient Fine-Tuning (PEFT) with LoRA/QLoRA
- Training on instruction-response pairs
- Memory-efficient training with quantization
"""

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset


def setup_quantization_config():
    """
    Configure 4-bit quantization for memory-efficient training (QLoRA).
    This reduces memory usage by ~75% compared to full precision.
    """
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,                      # Enable 4-bit quantization
        bnb_4bit_quant_type="nf4",              # Use NormalFloat4 quantization
        bnb_4bit_compute_dtype=torch.bfloat16,  # Computation dtype
        bnb_4bit_use_double_quant=True,         # Double quantization for extra memory savings
    )
    return bnb_config


def setup_lora_config():
    """
    Configure LoRA (Low-Rank Adaptation) parameters.
    LoRA adds trainable adapter matrices while freezing the base model,
    training only ~1% of total parameters.
    
    Parameters:
    - r: LoRA rank (higher = more expressive but more memory)
    - lora_alpha: LoRA scaling factor (typically 2*r)
    - lora_dropout: Dropout probability for LoRA layers
    - target_modules: Which model layers to apply LoRA to
    """
    lora_config = LoraConfig(
        r=16,                                   # LoRA rank
        lora_alpha=32,                          # LoRA alpha (scaling factor)
        lora_dropout=0.05,                      # Dropout probability
        bias="none",                            # Don't train bias parameters
        task_type="CAUSAL_LM",                  # Task type: Causal Language Modeling
        target_modules=[                        # Apply LoRA to these attention modules
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )
    return lora_config


def load_model_and_tokenizer(model_name="meta-llama/Llama-3.2-1B"):
    """
    Load a pre-trained model and tokenizer with quantization.
    
    Args:
        model_name: HuggingFace model identifier
    
    Returns:
        tuple: (model, tokenizer)
    """
    print(f"Loading model: {model_name}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token  # Set padding token
    tokenizer.padding_side = "right"           # Pad on the right for causal LM
    
    # Load model with quantization
    bnb_config = setup_quantization_config()
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",                     # Automatically distribute model across devices
        trust_remote_code=True,
    )
    
    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # Apply LoRA
    lora_config = setup_lora_config()
    model = get_peft_model(model, lora_config)
    
    # Print trainable parameters
    model.print_trainable_parameters()
    
    return model, tokenizer


def prepare_dataset(dataset_name="yahma/alpaca-cleaned", max_samples=1000):
    """
    Load and prepare the instruction-following dataset.
    
    The Alpaca format:
    {
        "instruction": "Task description",
        "input": "Optional context",
        "output": "Expected response"
    }
    
    Args:
        dataset_name: HuggingFace dataset identifier
        max_samples: Maximum number of samples to use (set to None for full dataset)
    
    Returns:
        Dataset object
    """
    print(f"Loading dataset: {dataset_name}")
    
    # Load dataset
    dataset = load_dataset(dataset_name, split="train")
    
    # Limit dataset size for faster training (optional)
    if max_samples and len(dataset) > max_samples:
        dataset = dataset.select(range(max_samples))
    
    print(f"Dataset size: {len(dataset)} samples")
    return dataset


def format_instruction(example):
    """
    Format the dataset example into a single text string.
    This function converts the instruction-input-output format into a prompt.
    
    Args:
        example: Dictionary with 'instruction', 'input', 'output' keys
    
    Returns:
        Formatted string
    """
    if example.get("input", "").strip():
        return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""
    else:
        return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{example['instruction']}

### Response:
{example['output']}"""


def setup_training_arguments(output_dir="./sft_model"):
    """
    Configure training hyperparameters.
    
    Args:
        output_dir: Directory to save model checkpoints
    
    Returns:
        TrainingArguments object
    """
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,                    # Number of training epochs
        per_device_train_batch_size=4,         # Batch size per GPU
        gradient_accumulation_steps=4,         # Accumulate gradients for effective batch size of 16
        gradient_checkpointing=True,           # Enable gradient checkpointing to save memory
        optim="paged_adamw_8bit",              # Use 8-bit AdamW optimizer
        learning_rate=2e-4,                    # Learning rate
        lr_scheduler_type="cosine",            # Learning rate schedule
        warmup_ratio=0.03,                     # Warmup 3% of total steps
        logging_steps=10,                      # Log every 10 steps
        save_strategy="epoch",                 # Save checkpoint after each epoch
        save_total_limit=2,                    # Keep only 2 most recent checkpoints
        fp16=False,                            # Disable FP16 (use BF16 instead)
        bf16=True,                             # Enable BF16 mixed precision training
        max_grad_norm=0.3,                     # Gradient clipping
        weight_decay=0.001,                    # Weight decay for regularization
        report_to="tensorboard",               # Report metrics to TensorBoard
    )
    return training_args


def main():
    """
    Main training pipeline for Supervised Fine-Tuning.
    """
    print("=" * 80)
    print("Supervised Fine-Tuning (SFT) - Stage 1 of RLHF")
    print("=" * 80)
    
    # 1. Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer()
    
    # 2. Load and prepare dataset
    dataset = prepare_dataset()
    
    # 3. Setup training arguments
    training_args = setup_training_arguments()
    
    # 4. Initialize SFT Trainer
    print("\nInitializing SFT Trainer...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        tokenizer=tokenizer,
        args=training_args,
        formatting_func=format_instruction,   # Function to format dataset examples
        max_seq_length=512,                   # Maximum sequence length
        packing=False,                        # Don't pack multiple examples in one sequence
    )
    
    # 5. Start training
    print("\nStarting training...")
    trainer.train()
    
    # 6. Save the final model
    print("\nSaving model...")
    trainer.save_model()
    tokenizer.save_pretrained(training_args.output_dir)
    
    print("\n" + "=" * 80)
    print("Training completed successfully!")
    print(f"Model saved to: {training_args.output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    # Check CUDA availability
    if torch.cuda.is_available():
        print(f"CUDA is available. Using GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        print("WARNING: CUDA is not available. Training on CPU will be very slow.")
    
    main()
