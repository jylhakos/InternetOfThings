"""
Model Inference and Testing
============================
This script provides utilities for testing fine-tuned models and
comparing outputs from different training stages.

Features:
- Load and test SFT, DPO, or RLHF models
- Interactive chat interface
- Batch inference
- Model comparison
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from typing import List, Optional
import argparse


class ModelInference:
    """
    Utility class for model inference and testing.
    """
    
    def __init__(self, model_path: str, device: str = "auto"):
        """
        Initialize inference pipeline.
        
        Args:
            model_path: Path to the trained model
            device: Device to run inference on ('auto', 'cuda', 'cpu')
        """
        self.model_path = model_path
        self.device = device
        self.model = None
        self.tokenizer = None
        self.generator = None
        
        self.load_model()
    
    def load_model(self):
        """
        Load the model and tokenizer.
        """
        print(f"Loading model from: {self.model_path}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map=self.device,
            torch_dtype=torch.bfloat16,
        )
        
        # Create text generation pipeline
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map=self.device
        )
        
        print("Model loaded successfully!")
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        num_return_sequences: int = 1,
        do_sample: bool = True
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            num_return_sequences: Number of sequences to generate
            do_sample: Whether to use sampling or greedy decoding
        
        Returns:
            Generated text
        """
        outputs = self.generator(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            num_return_sequences=num_return_sequences,
            do_sample=do_sample,
            pad_token_id=self.tokenizer.pad_token_id,
            return_full_text=False  # Only return generated text
        )
        
        if num_return_sequences == 1:
            return outputs[0]['generated_text']
        else:
            return [output['generated_text'] for output in outputs]
    
    def batch_generate(self, prompts: List[str], **generate_kwargs) -> List[str]:
        """
        Generate responses for multiple prompts.
        
        Args:
            prompts: List of input prompts
            **generate_kwargs: Additional arguments for generation
        
        Returns:
            List of generated texts
        """
        results = []
        for prompt in prompts:
            result = self.generate(prompt, **generate_kwargs)
            results.append(result)
        return results
    
    def interactive_chat(self):
        """
        Start an interactive chat session with the model.
        """
        print("\n" + "=" * 80)
        print("Interactive Chat Mode")
        print("=" * 80)
        print("Type 'exit' or 'quit' to end the session")
        print("Type 'clear' to reset the conversation")
        print("-" * 80)
        
        conversation_history = []
        
        while True:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Ending chat session. Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                conversation_history = []
                print("Conversation cleared.")
                continue
            
            if not user_input:
                continue
            
            # Format prompt with conversation history
            prompt = self._format_chat_prompt(conversation_history, user_input)
            
            # Generate response
            print("\nAssistant: ", end="", flush=True)
            response = self.generate(
                prompt,
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            print(response)
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})
    
    def _format_chat_prompt(self, history: List[dict], user_message: str) -> str:
        """
        Format conversation history into a prompt.
        
        Args:
            history: List of conversation turns
            user_message: Current user message
        
        Returns:
            Formatted prompt string
        """
        prompt = ""
        
        # Add conversation history
        for turn in history:
            if turn["role"] == "user":
                prompt += f"Human: {turn['content']}\n\n"
            else:
                prompt += f"Assistant: {turn['content']}\n\n"
        
        # Add current message
        prompt += f"Human: {user_message}\n\nAssistant:"
        
        return prompt


class ModelComparison:
    """
    Compare outputs from multiple models.
    """
    
    def __init__(self, model_paths: dict):
        """
        Initialize model comparison.
        
        Args:
            model_paths: Dictionary mapping model names to paths
                         e.g., {"SFT": "./sft_model", "DPO": "./dpo_model"}
        """
        self.models = {}
        
        for name, path in model_paths.items():
            print(f"\nLoading {name} model...")
            self.models[name] = ModelInference(path)
    
    def compare(self, prompts: List[str], **generate_kwargs):
        """
        Generate responses from all models and compare.
        
        Args:
            prompts: List of test prompts
            **generate_kwargs: Generation parameters
        """
        print("\n" + "=" * 80)
        print("Model Comparison")
        print("=" * 80)
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n{'-' * 80}")
            print(f"Prompt {i}: {prompt}")
            print(f"{'-' * 80}")
            
            for model_name, model in self.models.items():
                print(f"\n[{model_name}]")
                response = model.generate(prompt, **generate_kwargs)
                print(response)
            
            print(f"\n{'-' * 80}")


def main():
    """
    Main function for model inference and testing.
    """
    parser = argparse.ArgumentParser(description="Model Inference and Testing")
    parser.add_argument(
        "--model",
        type=str,
        default="./sft_model",
        help="Path to the model directory"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["interactive", "test", "compare"],
        default="interactive",
        help="Inference mode"
    )
    parser.add_argument(
        "--compare-with",
        type=str,
        nargs="+",
        help="Additional model paths for comparison (space-separated)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        # Interactive chat mode
        model = ModelInference(args.model)
        model.interactive_chat()
    
    elif args.mode == "test":
        # Test mode with predefined prompts
        model = ModelInference(args.model)
        
        test_prompts = [
            "Explain what reinforcement learning is.",
            "What are the benefits of using LoRA for fine-tuning?",
            "How does PPO work in RLHF?",
            "Compare DPO and traditional RLHF.",
            "What are the key components of a reward model?",
        ]
        
        print("\n" + "=" * 80)
        print("Testing Model with Predefined Prompts")
        print("=" * 80)
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n{'-' * 80}")
            print(f"Test {i}: {prompt}")
            print(f"{'-' * 80}")
            response = model.generate(prompt, max_new_tokens=200)
            print(f"\nResponse:\n{response}")
    
    elif args.mode == "compare":
        # Comparison mode
        if not args.compare_with:
            print("Error: --compare-with required for comparison mode")
            return
        
        model_paths = {"Primary": args.model}
        for i, path in enumerate(args.compare_with, 1):
            model_paths[f"Model {i}"] = path
        
        comparison = ModelComparison(model_paths)
        
        test_prompts = [
            "What is artificial intelligence?",
            "Explain the concept of reinforcement learning.",
            "How do neural networks work?",
        ]
        
        comparison.compare(test_prompts, max_new_tokens=150)


if __name__ == "__main__":
    main()
