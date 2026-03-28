"""
Direct Preference Optimization (DPO) Training
==============================================
This script demonstrates DPO, an alternative to RLHF that directly optimizes
for preferences without needing a separate reward model.

Key Concepts:
- Direct optimization on preference data
- No explicit reward model needed
- Simpler and more stable than PPO-based RLHF
- Implicit reward function learned during training

DPO Loss:
L = -log(σ(β * log(π_θ(y_w|x) / π_ref(y_w|x)) - β * log(π_θ(y_l|x) / π_ref(y_l|x))))

Where:
- y_w: winning (chosen) response
- y_l: losing (rejected) response
- π_θ: current policy
- π_ref: reference policy
- β: temperature parameter
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import DPOTrainer, DPOConfig
from datasets import load_dataset, Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import BitsAndBytesConfig


class DPOTrainingPipeline:
    """
    Complete pipeline for Direct Preference Optimization.
    
    DPO is often preferred over PPO-based RLHF because:
    1. Simpler - no separate reward model needed
    2. More stable - direct optimization is less prone to instability
    3. Faster - fewer models to train and manage
    4. Effective - achieves comparable or better results
    """
    
    def __init__(self, model_name="meta-llama/Llama-3.2-1B"):
        """
        Initialize DPO trainer.
        
        Args:
            model_name: Base model or SFT model to optimize
        """
        self.model_name = model_name
        self.model = None
        self.ref_model = None
        self.tokenizer = None
        
    def setup_quantization(self):
        """
        Setup 4-bit quantization for memory efficiency.
        """
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
    
    def setup_lora(self):
        """
        Setup LoRA configuration for parameter-efficient training.
        """
        return LoraConfig(
            r=16,
            lora_alpha=32,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        )
    
    def load_models(self):
        """
        Load the policy model and reference model.
        
        For DPO, we need:
        1. Policy model (θ) - the model being optimized
        2. Reference model (ref) - frozen copy of initial policy
        """
        print(f"Loading models: {self.model_name}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"  # Left padding for generation
        
        # Load policy model with quantization
        bnb_config = self.setup_quantization()
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )
        
        # Prepare for training
        self.model = prepare_model_for_kbit_training(self.model)
        
        # Apply LoRA
        lora_config = self.setup_lora()
        self.model = get_peft_model(self.model, lora_config)
        
        # Load reference model (no LoRA, frozen)
        self.ref_model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )
        
        print("Models loaded successfully!")
        self.model.print_trainable_parameters()
    
    def load_preference_dataset(self, dataset_name="Anthropic/hh-rlhf", subset="harmless-base"):
        """
        Load preference dataset with chosen/rejected pairs.
        
        DPO expects:
        {
            "prompt": "...",
            "chosen": "...",    # Better response
            "rejected": "..."   # Worse response
        }
        
        Args:
            dataset_name: HuggingFace dataset identifier
            subset: Dataset subset
        
        Returns:
            Dataset object
        """
        print(f"Loading preference dataset: {dataset_name}")
        
        try:
            # Load dataset
            dataset = load_dataset(dataset_name, subset, split="train")
            
            # The hh-rlhf dataset has 'chosen' and 'rejected' fields
            # We need to extract the prompt from the conversation
            def extract_prompt_and_responses(example):
                """
                Extract prompt, chosen, and rejected from the conversation format.
                """
                # Extract the human's last message as the prompt
                chosen_text = example["chosen"]
                rejected_text = example["rejected"]
                
                # Find the last "Human:" part (the prompt)
                prompt_end = chosen_text.rfind("Assistant:")
                if prompt_end == -1:
                    prompt = chosen_text
                    chosen_response = ""
                    rejected_response = ""
                else:
                    prompt = chosen_text[:prompt_end]
                    chosen_response = chosen_text[prompt_end:]
                    
                    # Extract rejected response
                    rejected_prompt_end = rejected_text.rfind("Assistant:")
                    rejected_response = rejected_text[rejected_prompt_end:] if rejected_prompt_end != -1 else rejected_text
                
                return {
                    "prompt": prompt.strip(),
                    "chosen": chosen_response.strip(),
                    "rejected": rejected_response.strip()
                }
            
            # Process dataset
            dataset = dataset.map(extract_prompt_and_responses)
            
            # Limit size for demonstration
            dataset = dataset.select(range(min(1000, len(dataset))))
            
            print(f"Dataset loaded: {len(dataset)} preference pairs")
            return dataset
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            print("Creating demo dataset...")
            return self._create_demo_dataset()
    
    def _create_demo_dataset(self):
        """
        Create a demonstration preference dataset.
        """
        demo_data = {
            "prompt": [
                "Human: What is the capital of France?",
                "Human: How do you make tea?",
                "Human: Explain quantum physics simply.",
                "Human: What's the best programming language?",
            ],
            "chosen": [
                "Assistant: The capital of France is Paris, a beautiful city known for its art, culture, and the iconic Eiffel Tower.",
                "Assistant: To make tea: 1) Boil water, 2) Place tea bag in cup, 3) Pour hot water, 4) Steep for 3-5 minutes, 5) Remove bag and enjoy. You can add milk or sugar to taste.",
                "Assistant: Quantum physics studies matter and energy at atomic scales. At this level, particles behave differently than everyday objects - they can exist in multiple states simultaneously until observed. This is called superposition.",
                "Assistant: There's no single 'best' programming language - it depends on your goals. Python is great for beginners and data science, JavaScript for web development, C++ for performance-critical applications, and so on. Choose based on your specific needs.",
            ],
            "rejected": [
                "Assistant: I'm not sure.",
                "Assistant: Just buy tea from a store.",
                "Assistant: It's really complicated stuff with particles and waves.",
                "Assistant: Python is definitely the best language for everything.",
            ]
        }
        return Dataset.from_dict(demo_data)
    
    def setup_training_config(self, output_dir="./dpo_model"):
        """
        Configure DPO training parameters.
        
        Args:
            output_dir: Directory to save model checkpoints
        
        Returns:
            DPOConfig object
        """
        config = DPOConfig(
            output_dir=output_dir,
            
            # Training parameters
            num_train_epochs=1,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            gradient_checkpointing=True,
            
            # Optimization
            learning_rate=5e-7,
            lr_scheduler_type="cosine",
            warmup_ratio=0.1,
            optim="paged_adamw_8bit",
            
            # DPO-specific parameters
            beta=0.1,                          # Temperature parameter for DPO
            max_prompt_length=512,             # Maximum prompt length
            max_length=1024,                   # Maximum total length
            
            # Mixed precision
            bf16=True,
            
            # Logging and saving
            logging_steps=10,
            save_strategy="epoch",
            save_total_limit=2,
            report_to="tensorboard",
            
            # Memory optimization
            max_grad_norm=0.3,
        )
        return config
    
    def train(self, output_dir="./dpo_model"):
        """
        Run DPO training.
        
        Args:
            output_dir: Directory to save the trained model
        """
        # Load preference dataset
        dataset = self.load_preference_dataset()
        
        # Setup training config
        training_args = self.setup_training_config(output_dir)
        
        # Initialize DPO Trainer
        print("\nInitializing DPO Trainer...")
        trainer = DPOTrainer(
            model=self.model,
            ref_model=self.ref_model,
            args=training_args,
            train_dataset=dataset,
            tokenizer=self.tokenizer,
        )
        
        # Train
        print("\n" + "=" * 80)
        print("Starting DPO Training")
        print("=" * 80)
        
        trainer.train()
        
        # Save model
        print(f"\nSaving model to {output_dir}")
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        print("\n" + "=" * 80)
        print("DPO Training Completed!")
        print("=" * 80)
    
    def test_model(self, model_path="./dpo_model"):
        """
        Test the DPO-trained model with sample prompts.
        
        Args:
            model_path: Path to the trained model
        """
        print("\n" + "=" * 80)
        print("Testing DPO-Trained Model")
        print("=" * 80)
        
        # Load the trained model
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype=torch.bfloat16
        )
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Test prompts
        test_prompts = [
            "Human: What is machine learning?\n\nAssistant:",
            "Human: How can I improve my coding skills?\n\nAssistant:",
            "Human: Explain the importance of testing in software development.\n\nAssistant:",
        ]
        
        model.eval()
        for prompt in test_prompts:
            print(f"\nPrompt: {prompt}")
            
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=128,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=tokenizer.pad_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Response:\n{response}\n")
            print("-" * 80)


def main():
    """
    Main pipeline for DPO training.
    """
    print("=" * 80)
    print("Direct Preference Optimization (DPO) Training")
    print("=" * 80)
    
    # Initialize pipeline
    dpo_pipeline = DPOTrainingPipeline()
    
    # Load models
    dpo_pipeline.load_models()
    
    # Train with DPO
    dpo_pipeline.train()
    
    # Test the model
    dpo_pipeline.test_model()


if __name__ == "__main__":
    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB\n")
    else:
        print("WARNING: CUDA not available. Training will be very slow.\n")
    
    main()
