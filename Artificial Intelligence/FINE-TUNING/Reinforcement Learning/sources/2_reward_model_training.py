"""
Reward Model Training - Stage 2 of RLHF Pipeline
=================================================
This script demonstrates how to train a reward model that predicts human preferences.
The reward model learns to score model outputs based on human preference data.

Key Concepts:
- Training a model to predict preference rankings
- Using paired comparison data (chosen vs rejected responses)
- Creating a scalar reward for any model output
"""

import torch
import torch.nn as nn
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding
)
from datasets import load_dataset
from typing import Dict, List


class RewardModelTrainer:
    """
    Trainer class for reward models used in RLHF.
    
    The reward model learns to predict human preferences by training on
    comparison data where each example has a preferred (chosen) and
    non-preferred (rejected) response.
    """
    
    def __init__(self, model_name="meta-llama/Llama-3.2-1B"):
        """
        Initialize the reward model trainer.
        
        Args:
            model_name: Base model to use for the reward model
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.dataset = None
        
    def load_model_and_tokenizer(self):
        """
        Load the model with a classification head for reward prediction.
        The model outputs a single scalar value (the reward score).
        """
        print(f"Loading model: {self.model_name}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model with sequence classification head (1 output = reward score)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=1,                          # Single output for reward score
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        
        # Configure model for reward modeling
        self.model.config.pad_token_id = self.tokenizer.pad_token_id
        
        print(f"Model loaded with {self.model.num_parameters():,} parameters")
        
    def load_preference_dataset(self, dataset_name="Anthropic/hh-rlhf", subset="harmless-base"):
        """
        Load a preference dataset with chosen/rejected pairs.
        
        The dataset format:
        {
            "chosen": "Human: ... Assistant: [better response]",
            "rejected": "Human: ... Assistant: [worse response]"
        }
        
        Args:
            dataset_name: HuggingFace dataset identifier
            subset: Dataset subset to use
        """
        print(f"Loading preference dataset: {dataset_name}")
        
        # Load the dataset
        try:
            self.dataset = load_dataset(dataset_name, subset, split="train")
            print(f"Dataset loaded: {len(self.dataset)} preference pairs")
        except Exception as e:
            print(f"Error loading dataset: {e}")
            print("Using a smaller sample dataset for demonstration")
            # Create a small synthetic dataset for demonstration
            self.dataset = self._create_demo_dataset()
    
    def _create_demo_dataset(self):
        """
        Create a small demonstration dataset for testing.
        """
        from datasets import Dataset
        
        demo_data = {
            "chosen": [
                "Human: What is the capital of France?\n\nAssistant: The capital of France is Paris. It's a beautiful city known for its art, culture, and iconic landmarks like the Eiffel Tower.",
                "Human: How do I make coffee?\n\nAssistant: To make coffee, you'll need coffee grounds and hot water. For a simple method: 1) Use 1-2 tablespoons of coffee per 6 oz of water. 2) Heat water to about 195-205°F. 3) Pour water over grounds and let steep for 4-5 minutes. 4) Strain and enjoy!",
            ],
            "rejected": [
                "Human: What is the capital of France?\n\nAssistant: I don't know.",
                "Human: How do I make coffee?\n\nAssistant: Just buy it from Starbucks.",
            ]
        }
        return Dataset.from_dict(demo_data)
    
    def preprocess_function(self, examples: Dict) -> Dict:
        """
        Tokenize and prepare the preference data.
        
        For each pair, we need to:
        1. Tokenize both chosen and rejected responses
        2. Create labels: chosen=1, rejected=0
        
        Args:
            examples: Batch of examples with 'chosen' and 'rejected' keys
        
        Returns:
            Tokenized examples with labels
        """
        # Tokenize chosen responses
        chosen_encodings = self.tokenizer(
            examples["chosen"],
            truncation=True,
            max_length=512,
            padding="max_length"
        )
        
        # Tokenize rejected responses
        rejected_encodings = self.tokenizer(
            examples["rejected"],
            truncation=True,
            max_length=512,
            padding="max_length"
        )
        
        # Combine both into a single batch
        # We'll process them separately in the compute_loss method
        return {
            "input_ids_chosen": chosen_encodings["input_ids"],
            "attention_mask_chosen": chosen_encodings["attention_mask"],
            "input_ids_rejected": rejected_encodings["input_ids"],
            "attention_mask_rejected": rejected_encodings["attention_mask"],
        }
    
    def compute_loss(self, model, inputs, return_outputs=False):
        """
        Custom loss function for reward model training.
        
        The loss encourages the model to assign higher rewards to chosen
        responses than to rejected responses.
        
        Loss = -log(sigmoid(reward_chosen - reward_rejected))
        
        This is equivalent to maximizing the probability that the chosen
        response has a higher reward than the rejected response.
        """
        # Get rewards for chosen responses
        rewards_chosen = model(
            input_ids=inputs["input_ids_chosen"],
            attention_mask=inputs["attention_mask_chosen"]
        ).logits
        
        # Get rewards for rejected responses
        rewards_rejected = model(
            input_ids=inputs["input_ids_rejected"],
            attention_mask=inputs["attention_mask_rejected"]
        ).logits
        
        # Compute ranking loss
        # We want: reward_chosen > reward_rejected
        loss = -nn.functional.logsigmoid(rewards_chosen - rewards_rejected).mean()
        
        if return_outputs:
            return loss, {"rewards_chosen": rewards_chosen, "rewards_rejected": rewards_rejected}
        return loss
    
    def train(self, output_dir="./reward_model", num_epochs=1):
        """
        Train the reward model.
        
        Args:
            output_dir: Directory to save the trained model
            num_epochs: Number of training epochs
        """
        print("\nPreparing dataset...")
        
        # Preprocess dataset
        tokenized_dataset = self.dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=self.dataset.column_names
        )
        
        # Setup training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=8,
            learning_rate=1e-5,
            lr_scheduler_type="cosine",
            warmup_ratio=0.1,
            logging_steps=10,
            save_strategy="epoch",
            bf16=True,
            remove_unused_columns=False,          # Keep our custom columns
            report_to="tensorboard",
        )
        
        # Custom Trainer with our loss function
        class RewardTrainer(Trainer):
            def compute_loss(self, model, inputs, return_outputs=False):
                return self.compute_loss(model, inputs, return_outputs)
        
        # Initialize trainer
        trainer = RewardTrainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
        )
        
        # Bind our custom loss function
        trainer.compute_loss = lambda model, inputs, return_outputs=False: self.compute_loss(model, inputs, return_outputs)
        
        print("\nStarting training...")
        trainer.train()
        
        # Save the model
        print(f"\nSaving reward model to {output_dir}")
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        return trainer
    
    def test_reward_model(self, model_path="./reward_model"):
        """
        Test the trained reward model with sample inputs.
        
        Args:
            model_path: Path to the saved reward model
        """
        print("\n" + "=" * 80)
        print("Testing Reward Model")
        print("=" * 80)
        
        # Load the trained model
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Test examples
        test_cases = [
            ("Human: What is 2+2?\n\nAssistant: 2+2 equals 4.", "Good answer"),
            ("Human: What is 2+2?\n\nAssistant: I don't know.", "Bad answer"),
            ("Human: Tell me about AI.\n\nAssistant: Artificial Intelligence (AI) refers to computer systems designed to perform tasks that typically require human intelligence.", "Informative"),
            ("Human: Tell me about AI.\n\nAssistant: AI is stuff.", "Vague"),
        ]
        
        model.eval()
        with torch.no_grad():
            for text, description in test_cases:
                inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                reward = model(**inputs).logits.item()
                print(f"\n{description}:")
                print(f"Text: {text[:100]}...")
                print(f"Reward Score: {reward:.4f}")


def main():
    """
    Main pipeline for reward model training.
    """
    print("=" * 80)
    print("Reward Model Training - Stage 2 of RLHF")
    print("=" * 80)
    
    # Initialize trainer
    rm_trainer = RewardModelTrainer()
    
    # Load model and tokenizer
    rm_trainer.load_model_and_tokenizer()
    
    # Load preference dataset
    rm_trainer.load_preference_dataset()
    
    # Train the reward model
    rm_trainer.train(num_epochs=1)
    
    # Test the model
    rm_trainer.test_reward_model()
    
    print("\n" + "=" * 80)
    print("Reward model training completed!")
    print("=" * 80)


if __name__ == "__main__":
    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("WARNING: CUDA not available. Training will be slow.")
    
    main()
