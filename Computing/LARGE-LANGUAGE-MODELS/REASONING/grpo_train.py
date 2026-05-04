"""
grpo_train.py
=============
GRPO (Group Relative Policy Optimization) Training Script with Unsloth
-----------------------------------------------------------------------
This script trains a language model to exhibit chain-of-thought reasoning
on grade school mathematics problems from the GSM8K dataset, using the
GRPO reinforcement learning algorithm via the Unsloth and TRL libraries.

Methodology:
    - The model generates groups of candidate responses for each prompt.
    - Each response is scored by a set of reward functions (correctness,
      format adherence, integer answer detection, XML tag compliance).
    - Group-relative advantages are computed via Z-score normalization
      across the sampled group, eliminating the need for a value/critic model.
    - The policy is updated to reinforce higher-scoring responses relative
      to the group average, guided by a KL divergence penalty to prevent
      excessive deviation from the reference policy.

Reference:
    - Hugging Face LLM Course, Chapter 12:
      https://huggingface.co/learn/llm-course/en/chapter12/6
    - Unsloth R1 Reasoning Blog:
      https://unsloth.ai/blog/r1-reasoning
    - DeepSeekMath GRPO paper:
      https://arxiv.org/abs/2402.03300

Usage:
    Activate the virtual environment, then run:
        source venv/bin/activate
        python grpo_train.py

Hardware requirements:
    - Minimum: 7 GB VRAM (for 1.5B-parameter models with QLoRA 4-bit)
    - Recommended: 15 GB VRAM (for models up to 8B parameters)
    - The script uses 4-bit QLoRA quantization to minimize memory usage.
"""

import re
import os
import torch

# --- Unsloth FastLanguageModel provides memory-efficient model loading
# --- and LoRA adapter application with optimised CUDA kernels.
from unsloth import FastLanguageModel

# --- Hugging Face datasets library for loading the GSM8K benchmark.
from datasets import load_dataset, Dataset

# --- TRL provides the GRPOTrainer and GRPOConfig for RL training.
from trl import GRPOConfig, GRPOTrainer

# --- vLLM SamplingParams for controlling inference during GRPO rollouts.
from vllm import SamplingParams


# =============================================================================
# CONFIGURATION
# =============================================================================

# Maximum sequence length for both training and inference.
# Increase for longer reasoning traces; decrease to reduce VRAM usage.
MAX_SEQ_LENGTH = 1024

# LoRA rank: controls the expressiveness of the LoRA adapters.
# Higher rank = more trainable parameters = better capacity but slower training.
# Recommended values: 8, 16, 32, 64.
LORA_RANK = 16

# Name of the base model to fine-tune.
# Options include: "unsloth/Llama-3.1-8B-Instruct", "unsloth/Qwen2.5-7B-Instruct",
# "unsloth/Phi-4", "google/gemma-3-1b-it"
# For low-VRAM setups, use "unsloth/Qwen2.5-1.5B-Instruct" (requires ~5 GB VRAM).
MODEL_NAME = "google/gemma-3-1b-it"

# Output directory for saving training checkpoints and final LoRA weights.
OUTPUT_DIR = "outputs"

# Number of GRPO training steps.
# Set higher (e.g., 1000-5000) for better results; 250 for a quick test run.
MAX_STEPS = 250

# Number of candidate completions generated per prompt during each GRPO step.
# Higher values give better advantage estimates but require more VRAM.
NUM_GENERATIONS = 6

# Directory name for the saved LoRA adapter after training.
LORA_SAVE_DIR = os.path.join(OUTPUT_DIR, "grpo_saved_lora")


# =============================================================================
# SYSTEM PROMPT AND RESPONSE FORMAT
# =============================================================================

# The system prompt instructs the model to produce responses in a structured
# XML-like format. The <reasoning> block contains the chain-of-thought process,
# and the <answer> block contains only the final numerical result.
# This structured format enables the reward functions to reliably extract
# and evaluate both the reasoning process and the final answer.
SYSTEM_PROMPT = """
Respond in the following format:
<reasoning>
...
</reasoning>
<answer>
...
</answer>
"""

# The XML chain-of-thought format template used for generating training examples
# (not used directly in training; provided for reference).
XML_COT_FORMAT = """\
<reasoning>
{reasoning}
</reasoning>
<answer>
{answer}
</answer>
"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_xml_answer(text: str) -> str:
    """
    Extract the content between <answer> and </answer> tags from model output.

    The GSM8K reward functions compare the extracted answer against the
    ground truth label. This function handles cases where the model produces
    additional content after the closing tag.

    Args:
        text: Raw model output string.

    Returns:
        The extracted answer string, stripped of leading/trailing whitespace.
    """
    answer = text.split("<answer>")[-1]
    answer = answer.split("</answer>")[0]
    return answer.strip()


def extract_hash_answer(text: str) -> str | None:
    """
    Extract the final numerical answer from a GSM8K ground truth string.

    GSM8K answer strings contain a natural language derivation followed
    by the final answer after a '####' delimiter, e.g.:
        "She had 5 apples and bought 3 more. #### 8"

    Args:
        text: Ground truth answer string from the GSM8K dataset.

    Returns:
        The numerical answer as a string, or None if the delimiter is absent.
    """
    if "####" not in text:
        return None
    return text.split("####")[1].strip()


# =============================================================================
# DATASET PREPARATION
# =============================================================================

def get_gsm8k_questions(split: str = "train") -> Dataset:
    """
    Load and format the GSM8K dataset for GRPO training.

    Each example is transformed into a prompt formatted as a two-turn
    conversation: a system message with the response format instructions,
    and a user message with the mathematical problem. The answer field
    is reduced to the final numerical value only.

    Args:
        split: Dataset split to load ("train" or "test").

    Returns:
        A Hugging Face Dataset with "prompt" and "answer" columns.
    """
    # Load the GSM8K dataset from the Hugging Face Hub.
    data = load_dataset("openai/gsm8k", "main")[split]

    # Format each example with the system prompt and extract the numerical answer.
    data = data.map(
        lambda x: {
            "prompt": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": x["question"]},
            ],
            "answer": extract_hash_answer(x["answer"]),
        }
    )
    return data


# =============================================================================
# REWARD FUNCTIONS
# =============================================================================
# Reward functions are the core mechanism of GRPO training. Each function
# receives the model's completions and optional metadata, and returns a list
# of scalar scores. The GRPOTrainer aggregates these scores and computes
# group-relative advantages for policy optimization.

def correctness_reward_func(prompts, completions, answer, **kwargs) -> list[float]:
    """
    Primary reward: assign 2.0 if the extracted answer matches the ground truth.

    This is the most important reward function. It directly measures whether
    the model solved the problem correctly, providing the primary learning signal.

    Args:
        prompts: List of input prompts (used for logging).
        completions: List of model completions (nested list of message dicts).
        answer: List of ground truth answer strings.

    Returns:
        List of reward scores: 2.0 for correct, 0.0 for incorrect.
    """
    responses = [completion[0]["content"] for completion in completions]
    q = prompts[0][-1]["content"]
    extracted_responses = [extract_xml_answer(r) for r in responses]

    # Log the first example in each batch for monitoring training progress.
    print(
        "-" * 40,
        f"\nQuestion:\n{q}",
        f"\nGround truth:\n{answer[0]}",
        f"\nModel response:\n{responses[0]}",
        f"\nExtracted answer:\n{extracted_responses[0]}",
    )

    return [2.0 if r == a else 0.0 for r, a in zip(extracted_responses, answer)]


def int_reward_func(completions, **kwargs) -> list[float]:
    """
    Secondary reward: assign 0.5 if the extracted answer is a valid integer.

    This reward encourages the model to produce numerical answers in the
    expected format, even if the value is not yet correct. It provides a
    weaker signal that helps the model learn the output format early in training.

    Returns:
        List of reward scores: 0.5 if integer, 0.0 otherwise.
    """
    responses = [completion[0]["content"] for completion in completions]
    extracted_responses = [extract_xml_answer(r) for r in responses]
    return [0.5 if r.isdigit() else 0.0 for r in extracted_responses]


def strict_format_reward_func(completions, **kwargs) -> list[float]:
    """
    Format reward: enforce strict adherence to the XML response structure.

    The pattern requires exact newline placement around the XML tags,
    matching the SYSTEM_PROMPT format specification precisely.

    Returns:
        List of reward scores: 0.5 if strictly formatted, 0.0 otherwise.
    """
    pattern = r"^<reasoning>\n.*?\n</reasoning>\n<answer>\n.*?\n</answer>\n$"
    responses = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, r, re.DOTALL) for r in responses]
    return [0.5 if match else 0.0 for match in matches]


def soft_format_reward_func(completions, **kwargs) -> list[float]:
    """
    Format reward: reward approximate adherence to the XML structure.

    This is a relaxed version of strict_format_reward_func that does not
    require exact newline placement. It helps the model learn the overall
    tag structure even when newline placement is inconsistent.

    Returns:
        List of reward scores: 0.5 if loosely formatted, 0.0 otherwise.
    """
    pattern = r"<reasoning>.*?</reasoning>\s*<answer>.*?</answer>"
    responses = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, r, re.DOTALL) for r in responses]
    return [0.5 if match else 0.0 for match in matches]


def count_xml(text: str) -> float:
    """
    Count XML tag occurrences and penalize extraneous trailing content.

    This function awards partial credit for each correctly placed XML tag
    and applies a small penalty for any content that appears after the
    closing </answer> tag, discouraging the model from appending extra
    commentary after the structured response.

    Args:
        text: Model completion string.

    Returns:
        A float reward value between 0.0 and 0.5.
    """
    count = 0.0
    if text.count("<reasoning>\n") == 1:
        count += 0.125
    if text.count("\n</reasoning>\n") == 1:
        count += 0.125
    if text.count("\n<answer>\n") == 1:
        count += 0.125
        # Penalize content after the closing answer tag.
        count -= len(text.split("\n</answer>\n")[-1]) * 0.001
    if text.count("\n</answer>") == 1:
        count += 0.125
        count -= (len(text.split("\n</answer>")[-1]) - 1) * 0.001
    return count


def xmlcount_reward_func(completions, **kwargs) -> list[float]:
    """
    XML tag compliance reward: delegates to count_xml for each completion.

    Returns:
        List of reward scores from count_xml for each completion.
    """
    contents = [completion[0]["content"] for completion in completions]
    return [count_xml(c) for c in contents]


# =============================================================================
# MODEL LOADING
# =============================================================================

def load_model():
    """
    Load the base model and apply LoRA adapters using Unsloth.

    The model is loaded in 4-bit quantization (QLoRA) to minimise VRAM usage.
    LoRA adapters are applied to the attention projection layers (q_proj,
    k_proj, v_proj, o_proj) and feed-forward layers (gate_proj, up_proj,
    down_proj), which are the standard targets for instruction tuning.

    fast_inference=True enables vLLM-backed generation during GRPO rollouts,
    providing significantly higher throughput compared to standard generation.

    Returns:
        Tuple of (model, tokenizer).
    """
    print(f"Loading model: {MODEL_NAME}")
    print(f"Max sequence length: {MAX_SEQ_LENGTH}")
    print(f"LoRA rank: {LORA_RANK}")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=True,           # 4-bit QLoRA quantization for VRAM efficiency
        fast_inference=True,          # Enable vLLM for faster rollout generation
        max_lora_rank=LORA_RANK,
        gpu_memory_utilization=0.6,  # Fraction of GPU memory to allocate; reduce if OOM
    )

    # Apply LoRA adapters to the model.
    # Only the LoRA parameters (~1-5% of total) are trainable; base weights are frozen.
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_RANK,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",   # Attention layers
            "gate_proj", "up_proj", "down_proj",         # Feed-forward layers
        ],
        lora_alpha=LORA_RANK,
        use_gradient_checkpointing="unsloth",  # Unsloth's memory-efficient checkpointing
        random_state=3407,
    )

    return model, tokenizer


# =============================================================================
# TRAINING CONFIGURATION
# =============================================================================

def get_training_args() -> GRPOConfig:
    """
    Configure the GRPO training hyperparameters.

    Key hyperparameters:
        - learning_rate: Controls the step size for gradient updates.
          Too high causes instability; too low causes slow convergence.
        - num_generations: Number of completions sampled per prompt per step.
          Higher values give better advantage estimates at higher VRAM cost.
        - max_steps: Total training steps. At least 300 steps are needed
          before rewards begin to increase noticeably.
        - max_completion_length: Maximum tokens in each generated response.

    Returns:
        A GRPOConfig instance with all training hyperparameters set.
    """
    max_prompt_length = 256

    return GRPOConfig(
        # Optimizer settings
        learning_rate=5e-6,
        adam_beta1=0.9,
        adam_beta2=0.99,
        weight_decay=0.1,
        warmup_ratio=0.1,
        lr_scheduler_type="cosine",
        optim="paged_adamw_8bit",     # Memory-efficient paged AdamW

        # Batch and generation settings
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,  # Increase to 4 for smoother gradients
        num_generations=NUM_GENERATIONS,
        max_prompt_length=max_prompt_length,
        max_completion_length=MAX_SEQ_LENGTH - max_prompt_length,

        # Training duration and checkpointing
        max_steps=MAX_STEPS,
        save_steps=MAX_STEPS,         # Save a checkpoint at the final step

        # Gradient clipping and logging
        max_grad_norm=0.1,            # Clip gradients to prevent instability
        logging_steps=1,              # Log metrics at every step
        report_to="none",             # Disable external reporting (Weights & Biases etc.)

        output_dir=OUTPUT_DIR,
    )


# =============================================================================
# INFERENCE (TESTING THE TRAINED MODEL)
# =============================================================================

def run_inference(model, tokenizer, question: str) -> str:
    """
    Run inference with the trained model and the saved LoRA adapter.

    This function demonstrates how to use the fine-tuned model for inference
    after training. The LoRA adapter is loaded from disk and applied to the
    base model for generation.

    Args:
        model: The Unsloth FastLanguageModel instance.
        tokenizer: The corresponding tokenizer.
        question: The mathematical question to pose to the model.

    Returns:
        The model's full response string (including reasoning tags).
    """
    # Format the input as a chat conversation with the system prompt.
    text = tokenizer.apply_chat_template(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        tokenize=False,
        add_generation_prompt=True,
    )

    # Configure sampling parameters for inference.
    # temperature=0.8 introduces some variability; lower values are more deterministic.
    sampling_params = SamplingParams(
        temperature=0.8,
        top_p=0.95,
        max_tokens=1024,
    )

    # Generate using the trained LoRA adapter.
    output = (
        model.fast_generate(
            text,
            sampling_params=sampling_params,
            lora_request=model.load_lora(LORA_SAVE_DIR),
        )[0]
        .outputs[0]
        .text
    )

    return output


# =============================================================================
# MAIN TRAINING LOOP
# =============================================================================

def main():
    """
    Main entry point: orchestrates model loading, dataset preparation,
    GRPO training, model saving, and a demonstration inference call.
    """

    # 1. Load the model and tokenizer with LoRA adapters applied.
    model, tokenizer = load_model()

    # 2. Load and format the GSM8K training dataset.
    print("Loading GSM8K dataset...")
    dataset = get_gsm8k_questions(split="train")
    print(f"Dataset size: {len(dataset)} examples")

    # 3. Configure GRPO training hyperparameters.
    training_args = get_training_args()

    # 4. Instantiate the GRPO trainer with all reward functions.
    #    The trainer will:
    #    a) Sample num_generations completions per prompt at each step.
    #    b) Score each completion with all provided reward functions.
    #    c) Compute group-relative advantages via Z-score normalization.
    #    d) Update the policy to maximize expected reward.
    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=[
            xmlcount_reward_func,         # XML tag compliance (partial credit)
            soft_format_reward_func,      # Relaxed format check
            strict_format_reward_func,    # Strict format check
            int_reward_func,              # Integer answer detection
            correctness_reward_func,      # Correct answer (primary signal)
        ],
        args=training_args,
        train_dataset=dataset,
    )

    # 5. Run GRPO training.
    #    Note: rewards typically remain low for the first 150-300 steps.
    #    Be patient and do not terminate training prematurely.
    print(f"\nStarting GRPO training for {MAX_STEPS} steps...")
    print("Tip: Reward increases are typically observed after 150-300 steps.")
    trainer.train()

    # 6. Save the trained LoRA adapter weights.
    print(f"\nSaving LoRA adapter to: {LORA_SAVE_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model.save_lora(LORA_SAVE_DIR)

    # 7. Optionally save the full merged model in 16-bit precision.
    #    Uncomment the following lines to save the merged model:
    # merged_model_dir = os.path.join(OUTPUT_DIR, "model_merged_16bit")
    # print(f"Saving merged model to: {merged_model_dir}")
    # model.save_pretrained_merged(merged_model_dir, tokenizer, save_method="merged_16bit")

    # 8. Demonstrate inference with a sample problem.
    print("\n" + "=" * 60)
    print("INFERENCE DEMONSTRATION")
    print("=" * 60)

    test_question = (
        "A bakery sells muffins in packs of 6. "
        "If a school orders 15 packs and then receives an additional 12 loose muffins "
        "as a bonus, how many muffins does the school have in total?"
    )
    print(f"\nQuestion:\n{test_question}\n")

    response = run_inference(model, tokenizer, test_question)
    print(f"Model response:\n{response}")

    print("\nTraining complete.")


if __name__ == "__main__":
    main()
