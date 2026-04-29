"""
Training Configuration Templates
=================================
This file contains example configurations for different training scenarios.
Copy and modify these for your specific use case.
"""

# =============================================================================
# Configuration 1: Small Model on Consumer GPU (7B model on RTX 4090)
# =============================================================================

SMALL_MODEL_CONFIG = {
    "model_name": "meta-llama/Llama-3.2-7B",
    
    # SFT Configuration
    "sft": {
        "dataset": "yahma/alpaca-cleaned",
        "max_samples": 10000,
        "num_epochs": 3,
        "batch_size": 4,
        "gradient_accumulation_steps": 4,
        "learning_rate": 2e-4,
        "max_seq_length": 512,
        "output_dir": "./models/sft_7b",
        
        # LoRA config
        "lora_r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.05,
        
        # Quantization
        "use_4bit": True,
        "use_double_quant": True,
    },
    
    # Reward Model Configuration
    "reward_model": {
        "dataset": "Anthropic/hh-rlhf",
        "subset": "harmless-base",
        "num_epochs": 1,
        "batch_size": 2,
        "gradient_accumulation_steps": 8,
        "learning_rate": 1e-5,
        "output_dir": "./models/reward_7b",
    },
    
    # PPO Configuration
    "ppo": {
        "learning_rate": 1.41e-5,
        "batch_size": 4,
        "mini_batch_size": 1,
        "ppo_epochs": 4,
        "max_grad_norm": 0.5,
        "init_kl_coef": 0.2,
        "target_kl": 6.0,
        "num_iterations": 50,
        "output_dir": "./models/ppo_7b",
    },
    
    # DPO Configuration (alternative to PPO)
    "dpo": {
        "dataset": "Anthropic/hh-rlhf",
        "num_epochs": 1,
        "batch_size": 2,
        "gradient_accumulation_steps": 4,
        "learning_rate": 5e-7,
        "beta": 0.1,
        "max_prompt_length": 512,
        "max_length": 1024,
        "output_dir": "./models/dpo_7b",
    },
}

# =============================================================================
# Configuration 2: Medium Model on Professional GPU (13B on A100)
# =============================================================================

MEDIUM_MODEL_CONFIG = {
    "model_name": "meta-llama/Llama-3.2-13B",
    
    "sft": {
        "dataset": "yahma/alpaca-cleaned",
        "max_samples": 50000,
        "num_epochs": 3,
        "batch_size": 8,
        "gradient_accumulation_steps": 2,
        "learning_rate": 2e-4,
        "max_seq_length": 1024,
        "output_dir": "./models/sft_13b",
        
        "lora_r": 32,
        "lora_alpha": 64,
        "lora_dropout": 0.05,
        
        "use_4bit": True,
        "use_double_quant": True,
    },
    
    "reward_model": {
        "dataset": "Anthropic/hh-rlhf",
        "subset": "helpful-base",
        "num_epochs": 2,
        "batch_size": 4,
        "gradient_accumulation_steps": 4,
        "learning_rate": 1e-5,
        "output_dir": "./models/reward_13b",
    },
    
    "ppo": {
        "learning_rate": 1.41e-5,
        "batch_size": 8,
        "mini_batch_size": 2,
        "ppo_epochs": 4,
        "max_grad_norm": 0.5,
        "init_kl_coef": 0.2,
        "target_kl": 6.0,
        "num_iterations": 100,
        "output_dir": "./models/ppo_13b",
    },
    
    "dpo": {
        "dataset": "Anthropic/hh-rlhf",
        "num_epochs": 2,
        "batch_size": 4,
        "gradient_accumulation_steps": 2,
        "learning_rate": 5e-7,
        "beta": 0.1,
        "max_prompt_length": 512,
        "max_length": 1024,
        "output_dir": "./models/dpo_13b",
    },
}

# =============================================================================
# Configuration 3: Large Model on Multi-GPU Setup (70B on 4x A100)
# =============================================================================

LARGE_MODEL_CONFIG = {
    "model_name": "meta-llama/Llama-3.1-70B",
    
    "sft": {
        "dataset": "yahma/alpaca-cleaned",
        "max_samples": None,  # Use full dataset
        "num_epochs": 2,
        "batch_size": 16,
        "gradient_accumulation_steps": 1,
        "learning_rate": 1e-4,
        "max_seq_length": 2048,
        "output_dir": "./models/sft_70b",
        
        "lora_r": 64,
        "lora_alpha": 128,
        "lora_dropout": 0.05,
        
        "use_4bit": True,
        "use_double_quant": True,
    },
    
    "reward_model": {
        "dataset": "Anthropic/hh-rlhf",
        "subset": "helpful-base",
        "num_epochs": 2,
        "batch_size": 8,
        "gradient_accumulation_steps": 2,
        "learning_rate": 5e-6,
        "output_dir": "./models/reward_70b",
    },
    
    "ppo": {
        "learning_rate": 1e-5,
        "batch_size": 16,
        "mini_batch_size": 4,
        "ppo_epochs": 4,
        "max_grad_norm": 0.5,
        "init_kl_coef": 0.2,
        "target_kl": 6.0,
        "num_iterations": 200,
        "output_dir": "./models/ppo_70b",
    },
}

# =============================================================================
# Configuration 4: Code Generation Specialist
# =============================================================================

CODE_MODEL_CONFIG = {
    "model_name": "Qwen/Qwen2.5-Coder-7B",
    
    "sft": {
        "dataset": "iamtarun/python_code_instructions_18k_alpaca",
        "max_samples": None,
        "num_epochs": 3,
        "batch_size": 4,
        "gradient_accumulation_steps": 4,
        "learning_rate": 2e-4,
        "max_seq_length": 1024,
        "output_dir": "./models/code_sft",
        
        "lora_r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.05,
        
        "use_4bit": True,
    },
    
    "reward_model": {
        # Custom reward based on code correctness
        "dataset": "custom_code_preferences",
        "num_epochs": 2,
        "batch_size": 2,
        "learning_rate": 1e-5,
        "output_dir": "./models/code_reward",
    },
    
    "dpo": {
        "dataset": "custom_code_preferences",
        "num_epochs": 1,
        "batch_size": 2,
        "gradient_accumulation_steps": 4,
        "learning_rate": 5e-7,
        "beta": 0.1,
        "output_dir": "./models/code_dpo",
    },
}

# =============================================================================
# Configuration 5: Customer Support Chatbot
# =============================================================================

SUPPORT_MODEL_CONFIG = {
    "model_name": "mistralai/Mistral-7B-v0.1",
    
    "sft": {
        "dataset": "custom_support_conversations",
        "max_samples": 20000,
        "num_epochs": 5,
        "batch_size": 4,
        "gradient_accumulation_steps": 4,
        "learning_rate": 2e-4,
        "max_seq_length": 512,
        "output_dir": "./models/support_sft",
        
        "lora_r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.05,
    },
    
    "reward_model": {
        # Reward based on helpfulness and customer satisfaction
        "dataset": "custom_support_preferences",
        "metrics": ["helpfulness", "clarity", "politeness"],
        "num_epochs": 2,
        "output_dir": "./models/support_reward",
    },
    
    "dpo": {
        "dataset": "custom_support_preferences",
        "num_epochs": 2,
        "batch_size": 4,
        "learning_rate": 5e-7,
        "beta": 0.1,
        "output_dir": "./models/support_dpo",
    },
}

# =============================================================================
# Configuration 6: Minimal/Fast Training (for testing)
# =============================================================================

MINIMAL_CONFIG = {
    "model_name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    
    "sft": {
        "dataset": "yahma/alpaca-cleaned",
        "max_samples": 1000,
        "num_epochs": 1,
        "batch_size": 4,
        "gradient_accumulation_steps": 2,
        "learning_rate": 2e-4,
        "max_seq_length": 256,
        "output_dir": "./models/test_sft",
        
        "lora_r": 8,
        "lora_alpha": 16,
        "use_4bit": False,  # Small model, no quantization needed
    },
    
    "reward_model": {
        "dataset": "demo",  # Use demo dataset
        "num_epochs": 1,
        "batch_size": 2,
        "output_dir": "./models/test_reward",
    },
    
    "dpo": {
        "dataset": "demo",
        "num_epochs": 1,
        "batch_size": 2,
        "learning_rate": 5e-7,
        "output_dir": "./models/test_dpo",
    },
}

# =============================================================================
# Hardware Requirements Reference
# =============================================================================

HARDWARE_REQUIREMENTS = {
    "1B-3B models": {
        "min_vram": "8GB",
        "recommended_vram": "12GB",
        "example_gpus": ["RTX 3060", "RTX 4060 Ti"],
        "batch_size": 2-4,
        "training_time": "2-6 hours (SFT)",
    },
    
    "7B models": {
        "min_vram": "12GB (with QLoRA)",
        "recommended_vram": "24GB",
        "example_gpus": ["RTX 3090", "RTX 4090", "A5000"],
        "batch_size": 4-8,
        "training_time": "6-24 hours (SFT)",
    },
    
    "13B models": {
        "min_vram": "24GB (with QLoRA)",
        "recommended_vram": "40GB",
        "example_gpus": ["RTX 4090", "A100 40GB"],
        "batch_size": 4-8,
        "training_time": "12-48 hours (SFT)",
    },
    
    "30B-70B models": {
        "min_vram": "40GB (with QLoRA)",
        "recommended_vram": "80GB or multi-GPU",
        "example_gpus": ["A100 80GB", "4x A100 40GB"],
        "batch_size": 8-16,
        "training_time": "24-72+ hours (SFT)",
    },
}

# =============================================================================
# Usage Example
# =============================================================================

if __name__ == "__main__":
    import json
    
    print("Available Configurations:")
    print("=" * 60)
    
    configs = {
        "small": SMALL_MODEL_CONFIG,
        "medium": MEDIUM_MODEL_CONFIG,
        "large": LARGE_MODEL_CONFIG,
        "code": CODE_MODEL_CONFIG,
        "support": SUPPORT_MODEL_CONFIG,
        "minimal": MINIMAL_CONFIG,
    }
    
    for name, config in configs.items():
        print(f"\n{name.upper()} Configuration:")
        print(f"  Model: {config['model_name']}")
        print(f"  SFT Batch Size: {config['sft']['batch_size']}")
        print(f"  SFT Epochs: {config['sft']['num_epochs']}")
        print(f"  Output: {config['sft']['output_dir']}")
    
    print("\n" + "=" * 60)
    print("\nTo use a configuration in your training script:")
    print("  from config import SMALL_MODEL_CONFIG")
    print("  config = SMALL_MODEL_CONFIG")
    print("  # Then use config parameters in your training code")
    
    # Save configs to JSON files
    print("\nSaving configurations to JSON files...")
    for name, config in configs.items():
        filename = f"config_{name}.json"
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"  Saved: {filename}")
