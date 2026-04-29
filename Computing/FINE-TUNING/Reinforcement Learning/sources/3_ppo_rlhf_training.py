"""
PPO-based RLHF Training - Stage 3 of RLHF Pipeline
===================================================
This script demonstrates Proximal Policy Optimization (PPO) for fine-tuning
an LLM using a trained reward model. This is the final stage of RLHF.

Key Concepts:
- PPO algorithm for stable policy updates
- Using reward model to provide feedback
- KL divergence penalty to prevent model drift
- Value function for advantage estimation
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
from datasets import load_dataset
from tqdm import tqdm
import numpy as np


class RLHFTrainer:
    """
    Trainer for Reinforcement Learning from Human Feedback using PPO.
    
    PPO Algorithm Steps:
    1. Generate responses from the current policy (LLM)
    2. Get reward scores from the reward model
    3. Compute advantages using the value function
    4. Update the policy to maximize expected rewards
    5. Apply KL penalty to prevent large deviations from reference model
    """
    
    def __init__(
        self,
        model_name="./sft_model",              # Pre-trained/SFT model
        reward_model_name="./reward_model",    # Trained reward model
        ref_model_name=None                    # Reference model for KL penalty
    ):
        """
        Initialize RLHF trainer.
        
        Args:
            model_name: Path to the SFT model (to be optimized)
            reward_model_name: Path to the reward model
            ref_model_name: Path to reference model (usually same as model_name)
        """
        self.model_name = model_name
        self.reward_model_name = reward_model_name
        self.ref_model_name = ref_model_name or model_name
        
        self.model = None
        self.ref_model = None
        self.reward_model = None
        self.tokenizer = None
        
    def load_models(self):
        """
        Load all required models:
        1. Policy model (the LLM being optimized)
        2. Reference model (frozen, for KL penalty)
        3. Reward model (frozen, for scoring outputs)
        """
        print("Loading models...")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load policy model with value head
        # The value head is used for advantage estimation in PPO
        print(f"Loading policy model: {self.model_name}")
        self.model = AutoModelForCausalLMWithValueHead.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        
        # Load reference model (frozen copy of initial policy)
        # This is used to compute KL divergence penalty
        print(f"Loading reference model: {self.ref_model_name}")
        self.ref_model = AutoModelForCausalLM.from_pretrained(
            self.ref_model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        self.ref_model.eval()  # Set to eval mode (frozen)
        
        # Load reward model
        print(f"Loading reward model: {self.reward_model_name}")
        self.reward_model = AutoModelForSequenceClassification.from_pretrained(
            self.reward_model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        self.reward_model.eval()  # Set to eval mode (frozen)
        
        print("All models loaded successfully!")
    
    def load_prompts_dataset(self, dataset_name="CarperAI/openai_summarize_tldr", max_prompts=100):
        """
        Load a dataset of prompts for the model to respond to.
        
        Args:
            dataset_name: HuggingFace dataset identifier
            max_prompts: Maximum number of prompts to use
        
        Returns:
            List of prompt strings
        """
        print(f"Loading prompts from: {dataset_name}")
        
        try:
            dataset = load_dataset(dataset_name, split="train")
            
            # Extract prompts (adjust based on dataset structure)
            if "prompt" in dataset.column_names:
                prompts = dataset["prompt"][:max_prompts]
            else:
                # Create prompts from the dataset
                prompts = [f"Summarize the following: {item['info']['post'][:200]}" 
                          for item in dataset.select(range(min(max_prompts, len(dataset))))]
        except Exception as e:
            print(f"Error loading dataset: {e}")
            print("Using demo prompts instead")
            prompts = self._create_demo_prompts()
        
        print(f"Loaded {len(prompts)} prompts")
        return prompts
    
    def _create_demo_prompts(self):
        """
        Create demonstration prompts for testing.
        """
        return [
            "Explain what artificial intelligence is in simple terms.",
            "What are the benefits of exercise?",
            "How does photosynthesis work?",
            "Describe the water cycle.",
            "What is the theory of relativity?",
        ]
    
    def setup_ppo_config(self, output_dir="./ppo_model"):
        """
        Configure PPO hyperparameters.
        
        Returns:
            PPOConfig object
        """
        config = PPOConfig(
            model_name=self.model_name,
            learning_rate=1.41e-5,              # PPO learning rate
            batch_size=4,                       # Number of prompts per batch
            mini_batch_size=1,                  # Mini-batch size for PPO updates
            gradient_accumulation_steps=4,      # Gradient accumulation
            ppo_epochs=4,                       # Number of PPO epochs per batch
            max_grad_norm=0.5,                  # Gradient clipping
            
            # Generation parameters
            max_length=512,                     # Maximum generation length
            
            # PPO-specific parameters
            init_kl_coef=0.2,                   # Initial KL penalty coefficient
            target_kl=6.0,                      # Target KL divergence
            adap_kl_ctrl=True,                  # Adaptive KL control
            
            # Optimization
            optimize_cuda_cache=True,
            
            # Logging
            log_with="tensorboard",
            tracker_project_name="ppo-rlhf",
            tracker_kwargs={"logging_dir": f"{output_dir}/logs"},
        )
        return config
    
    def compute_rewards(self, query_tensors, response_tensors):
        """
        Compute rewards for generated responses using the reward model.
        
        Args:
            query_tensors: Input prompts (tokenized)
            response_tensors: Generated responses (tokenized)
        
        Returns:
            List of reward values
        """
        rewards = []
        
        with torch.no_grad():
            for query, response in zip(query_tensors, response_tensors):
                # Combine query and response
                full_text_ids = torch.cat([query, response])
                
                # Decode to text
                text = self.tokenizer.decode(full_text_ids, skip_special_tokens=True)
                
                # Tokenize for reward model
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512
                ).to(self.reward_model.device)
                
                # Get reward score
                reward = self.reward_model(**inputs).logits[0, 0].cpu()
                rewards.append(reward)
        
        return rewards
    
    def train(self, num_iterations=10, output_dir="./ppo_model"):
        """
        Run PPO training loop.
        
        Args:
            num_iterations: Number of training iterations
            output_dir: Directory to save checkpoints
        """
        # Setup PPO config
        ppo_config = self.setup_ppo_config(output_dir)
        
        # Initialize PPO trainer
        ppo_trainer = PPOTrainer(
            config=ppo_config,
            model=self.model,
            ref_model=self.ref_model,
            tokenizer=self.tokenizer,
        )
        
        # Load prompts
        prompts = self.load_prompts_dataset()
        
        # Generation parameters
        generation_kwargs = {
            "max_new_tokens": 128,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "pad_token_id": self.tokenizer.pad_token_id,
        }
        
        print("\n" + "=" * 80)
        print("Starting PPO Training")
        print("=" * 80)
        
        # Training loop
        for iteration in range(num_iterations):
            print(f"\n--- Iteration {iteration + 1}/{num_iterations} ---")
            
            # Sample a batch of prompts
            batch_prompts = np.random.choice(prompts, size=ppo_config.batch_size, replace=False)
            
            # Tokenize prompts
            query_tensors = [
                self.tokenizer.encode(prompt, return_tensors="pt")[0]
                for prompt in batch_prompts
            ]
            
            # Generate responses
            print("Generating responses...")
            response_tensors = []
            for query in query_tensors:
                response = ppo_trainer.generate(
                    query.unsqueeze(0),
                    **generation_kwargs
                )[0]
                response_tensors.append(response.squeeze())
            
            # Compute rewards
            print("Computing rewards...")
            rewards = self.compute_rewards(query_tensors, response_tensors)
            
            # Convert rewards to tensors
            rewards = [torch.tensor(r) for r in rewards]
            
            # PPO update step
            print("Performing PPO update...")
            stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
            
            # Log statistics
            mean_reward = np.mean([r.item() for r in rewards])
            print(f"Mean Reward: {mean_reward:.4f}")
            
            if iteration % 2 == 0 and iteration > 0:
                print(f"\nSample generation at iteration {iteration}:")
                sample_query = query_tensors[0]
                sample_response = response_tensors[0]
                full_text = self.tokenizer.decode(
                    torch.cat([sample_query, sample_response]),
                    skip_special_tokens=True
                )
                print(f"Prompt + Response:\n{full_text}\n")
                print(f"Reward: {rewards[0].item():.4f}")
        
        # Save final model
        print(f"\nSaving final model to {output_dir}")
        ppo_trainer.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        print("\n" + "=" * 80)
        print("PPO Training Completed!")
        print("=" * 80)


def main():
    """
    Main pipeline for PPO-based RLHF training.
    """
    print("=" * 80)
    print("PPO-based RLHF Training - Stage 3 of RLHF")
    print("=" * 80)
    
    # Initialize trainer
    # Note: Update paths to match your saved models from stages 1 and 2
    rlhf_trainer = RLHFTrainer(
        model_name="./sft_model",           # From Stage 1
        reward_model_name="./reward_model"  # From Stage 2
    )
    
    # Load all models
    rlhf_trainer.load_models()
    
    # Train with PPO
    rlhf_trainer.train(num_iterations=10)
    
    print("\nRLHF training pipeline completed!")
    print("Your model is now aligned with human preferences!")


if __name__ == "__main__":
    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        print("WARNING: CUDA not available. Training will be very slow.")
    
    main()
