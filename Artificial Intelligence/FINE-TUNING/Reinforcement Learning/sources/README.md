# RLHF Training Source Code

This directory contains complete, working examples for the entire RLHF (Reinforcement Learning from Human Feedback) pipeline.

## 📁 Files Overview

### Training Scripts

1. **`1_supervised_fine_tuning.py`**
   - **Stage 1 of RLHF**: Supervised Fine-Tuning (SFT)
   - Fine-tune a base LLM on instruction-following data
   - Uses LoRA/QLoRA for parameter-efficient training
   - Output: SFT model ready for reward modeling or RLHF

2. **`2_reward_model_training.py`**
   - **Stage 2 of RLHF**: Train a reward model
   - Learns to predict human preferences from comparison data
   - Takes pairs of (chosen, rejected) responses
   - Output: Reward model for scoring model outputs

3. **`3_ppo_rlhf_training.py`**
   - **Stage 3 of RLHF**: PPO-based optimization
   - Uses Proximal Policy Optimization to align model with rewards
   - Requires both SFT model and reward model
   - Output: RLHF-trained model aligned with human preferences

4. **`4_dpo_training.py`**
   - **Alternative to PPO**: Direct Preference Optimization
   - Simpler alternative that doesn't need a separate reward model
   - Directly optimizes on preference data
   - Often more stable and easier to train than PPO

### Utilities

5. **`5_model_inference.py`**
   - Test and compare trained models
   - Interactive chat interface
   - Batch inference
   - Model comparison utilities

6. **`utils.py`**
   - Common utility functions
   - Data formatting (Alpaca, chat formats)
   - Training helpers
   - Metrics computation
   - GPU memory management

7. **`requirements.txt`**
   - All required Python packages
   - Includes versions and installation notes

8. **`config.py`**
   - Pre-configured training scenarios
   - Multiple model size configurations
   - Hardware requirements reference

9. **`run_rlhf_pipeline.sh`**
   - Automated pipeline execution script
   - Multiple training modes
   - GPU checking and error handling

## Quick Start

**Always activate the virtual environment before running any commands**

### Step 1: Activate Virtual Environment

```bash
# Navigate to the project root directory
cd "/home/laptop/EXERCISES/IOT/InternetOfThings/Artificial Intelligence/FINE-TUNING/Reinforcement Learning"

# Activate virtual environment (REQUIRED)
source venv/bin/activate

# Verify activation - you should see (venv) in your prompt
# Example: (venv) user@hostname:~/path/to/project$
```

### Step 2: Install Dependencies

**Ensure virtual environment is activated (you should see `(venv)` in your terminal prompt)**

```bash
# Install all required packages
pip install -r requirements.txt

# For CUDA 11.8 (recommended):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Step 3: Run the Complete Pipeline

#### Option A: Full RLHF Pipeline (3 Stages)

```bash
# Stage 1: Supervised Fine-Tuning
python 1_supervised_fine_tuning.py

# Stage 2: Reward Model Training
python 2_reward_model_training.py

# Stage 3: PPO-based RLHF
python 3_ppo_rlhf_training.py
```

#### Option B: DPO (Simpler Alternative)

```bash
# Stage 1: SFT (same as above)
python 1_supervised_fine_tuning.py

# Stage 2: DPO (replaces reward model + PPO)
python 4_dpo_training.py
```

### Step 4: Test Your Model

**Ensure virtual environment is active**

```bash
# Interactive chat
python 5_model_inference.py --model ./sft_model --mode interactive

# Test with predefined prompts
python 5_model_inference.py --model ./ppo_model --mode test

# Compare models
python 5_model_inference.py --model ./sft_model --mode compare --compare-with ./dpo_model ./ppo_model
```

## Training Pipeline Comparison

### Full RLHF (PPO)
- **Stages**: SFT → Reward Model → PPO
- **Complexity**: High (3 models to train)
- **Stability**: Can be unstable
- **Quality**: Excellent when tuned properly
- **Use when**: You need maximum control and have resources

### DPO
- **Stages**: SFT → DPO
- **Complexity**: Medium (2 stages)
- **Stability**: More stable than PPO
- **Quality**: Comparable to RLHF
- **Use when**: You want simplicity and stability

## Key Concepts Implemented

### Parameter-Efficient Fine-Tuning (PEFT)
- **LoRA**: Low-Rank Adaptation - trains only ~1% of parameters
- **QLoRA**: Quantized LoRA - combines LoRA with 4-bit quantization
- Reduces memory usage by 75%+

### Supervised Fine-Tuning (SFT)
- Teaches the model to follow instructions
- Uses prompt-response pairs
- Foundation for RLHF or DPO

### Reward Modeling
- Learns human preferences from comparisons
- Predicts which response is better
- Essential for PPO-based RLHF

### PPO (Proximal Policy Optimization)
- Reinforcement learning algorithm
- Optimizes model to maximize rewards
- Uses KL divergence penalty to prevent drift

### DPO (Direct Preference Optimization)
- Direct optimization on preferences
- No separate reward model needed
- Simpler and often more stable

## Example Use Cases

Each script includes practical examples for:

1. **Customer Support Chatbots**
   - Fine-tune on support conversations
   - Align with helpfulness preferences

2. **Code Generation**
   - Train on code examples
   - Optimize for correctness and style

3. **Content Creation**
   - Fine-tune on writing samples
   - Align with quality preferences

4. **Educational Tutoring**
   - Train on educational content
   - Optimize for clarity and pedagogical quality

## Customization

### Changing the Base Model

Edit the `model_name` parameter in any script:

```python
# Use a different model
model_name = "mistralai/Mistral-7B-v0.1"
# or
model_name = "meta-llama/Llama-3.1-8B"
```

### Using Your Own Dataset

```python
# Load custom dataset
from datasets import load_dataset

# For SFT - instruction format
dataset = load_dataset("your-username/your-dataset")

# For DPO/Reward Model - preference format
dataset = load_dataset("your-username/preference-dataset")
```

### Adjusting Memory Usage

For limited VRAM:

```python
# Reduce batch size
per_device_train_batch_size = 1

# Increase gradient accumulation
gradient_accumulation_steps = 16

# Use more aggressive quantization
load_in_4bit = True
```

## Monitoring Training

### TensorBoard

```bash
# Start TensorBoard
tensorboard --logdir ./logs

# Open in browser: http://localhost:6006
```

### Weights & Biases (W&B)

```python
# Enable W&B logging
import wandb
wandb.init(project="rlhf-training")

# In TrainingArguments
report_to = "wandb"
```

## Troubleshooting

### CUDA Out of Memory

1. Reduce batch size: `per_device_train_batch_size = 1`
2. Enable gradient checkpointing: `gradient_checkpointing = True`
3. Use QLoRA: Already enabled by default
4. Reduce sequence length: `max_seq_length = 256`

### Slow Training

1. Check GPU utilization: `nvidia-smi`
2. Increase batch size (if memory allows)
3. Use mixed precision: `bf16 = True` (default)
4. Enable `torch.compile()` for PyTorch 2.0+

### Model Not Learning

1. Check learning rate (try 1e-5 to 5e-5)
2. Verify dataset format
3. Increase training epochs
4. Check for data quality issues

## Additional Resources

### Documentation
- [Hugging Face TRL](https://huggingface.co/docs/trl/)
- [PEFT Documentation](https://huggingface.co/docs/peft/)
- [Transformers Docs](https://huggingface.co/docs/transformers/)

### Papers
- [InstructGPT Paper (RLHF)](https://arxiv.org/abs/2203.02155)
- [DPO Paper](https://arxiv.org/abs/2305.18290)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [QLoRA Paper](https://arxiv.org/abs/2305.14314)

### Datasets
- [Anthropic HH-RLHF](https://huggingface.co/datasets/Anthropic/hh-rlhf)
- [Alpaca Dataset](https://huggingface.co/datasets/yahma/alpaca-cleaned)
- [OpenAI Summarization](https://huggingface.co/datasets/openai/summarize_from_feedback)

## 📄 License

Please respect the licenses of:
- Base models (e.g., Llama, Mistral)
- Datasets used for training
- Third-party libraries

## Best Practices

1. **Start Small**: Test with small datasets and few epochs
2. **Monitor Closely**: Use TensorBoard or W&B
3. **Save Checkpoints**: Don't lose progress
4. **Document Changes**: Keep notes on what works
5. **Version Control**: Use git for your experiments
6. **Validate Often**: Test on held-out data regularly

## Important Reminders

### Virtual Environment

ALWAYS activate the virtual environment before:
- Installing any packages with pip
- Running any Python scripts
- Starting Jupyter notebooks
- Running the automated pipeline script

```bash
# Activation command (run this first!)
source venv/bin/activate

# You must see (venv) in your prompt before proceeding
# Example: (venv) user@hostname:~/project$
```

To check if virtual environment is active:
```bash
which python
# Should output: /path/to/project/venv/bin/python
# NOT: /usr/bin/python
```

### Mistakes to Avoid

1. **Installing packages without activating venv**
   - Wrong: `pip install transformers` (when venv not active)
   - Right: `source venv/bin/activate` then `pip install transformers`

2. **Running scripts in wrong directory**
   - Scripts expect to be run from project root
   - Always `cd` to project directory first

3. **Forgetting to activate in new terminal**
   - Virtual environment is per-session
   - Must reactivate in every new terminal window

---
