# Fine-tuning AI models

Hugging Face provides an ecosystem built on PyTorch for fine-tuning Large Language Models (LLMs) through its transformers and trl libraries.

The primary tool for fine-tuning is the Trainer class from transformers or the SFTTrainer (Supervised Fine-Tuning Trainer) from trl.

## Overview

This repository contains practical implementations and examples for fine-tuning AI models, specifically focusing on Transformer-based architectures like BERT and large language models. The project demonstrates various fine-tuning approaches ranging from traditional supervised learning methods to advanced reinforcement learning techniques. Each subfolder provides complete, working code examples with RESTful APIs, Docker deployment configurations, and documentation.

The implementations cover the full spectrum of model fine-tuning workflows, including data preprocessing, model training, evaluation metrics, and deployment strategies for production environments.

## Project Structure

### 📁 PyTorch
Core implementation of BERT fine-tuning using PyTorch and Hugging Face transformers. This folder demonstrates the fundamentals of fine-tuning pre-trained models for text classification tasks.

**Key Features:**
- BERT architecture and attention mechanism explanations
- Supervised fine-tuning workflow for text classification
- Transfer learning with pre-trained models
- RESTful API for model serving
- Docker containerization and deployment
- Complete examples with minimal dependencies

**Main Components:**
- `src/bert_fine_tuning.py` - Complete BERT fine-tuning implementation
- `api.py` - FastAPI service for model inference
- `docker-compose.yml` - Container orchestration
- Documentation on optimization strategies

### 📁 Evaluation Metrics
Focused implementation for evaluating and fine-tuning BERT models with detailed performance metrics for text classification tasks.

**Key Features:**
- BERT model evaluation framework
- Multiple classification metrics (accuracy, precision, recall, F1-score)
- Validation and testing workflows
- API endpoints for model evaluation
- Docker deployment with Nginx reverse proxy

**Main Components:**
- `src/evaluation_metrics.py` - Metrics calculation and reporting
- `src/bert_fine_tuning.py` - Fine-tuning with metric tracking
- `simple_validation.py` - Streamlined validation utilities
- `test_model_evaluation.py` - Testing suite
- `VALIDATION.md` - Validation methodology documentation

### 📁 Reinforcement Learning
Advanced fine-tuning techniques using Reinforcement Learning from Human Feedback (RLHF) and Direct Preference Optimization (DPO) for aligning LLMs with human preferences.

**Key Features:**
- Complete RLHF pipeline implementation (SFT → Reward Model → PPO)
- Direct Preference Optimization (DPO) as an alternative to PPO
- Parameter-efficient fine-tuning with LoRA/QLoRA
- Multi-stage training workflows
- Interactive model inference and comparison tools

**Main Components:**
- `sources/1_supervised_fine_tuning.py` - Initial instruction-following fine-tuning
- `sources/2_reward_model_training.py` - Human preference learning
- `sources/3_ppo_rlhf_training.py` - PPO-based alignment
- `sources/4_dpo_training.py` - Direct preference optimization
- `sources/5_model_inference.py` - Testing and comparison utilities
- `sources/run_rlhf_pipeline.sh` - Automated pipeline execution

## Example: Fine-tuning provided by Hugging Face

Install libraries:

Install transformers, datasets, trl, and accelerate (for distributed training).

```

    $ pip install transformers datasets trl accelerate bitsandbytes

```
Load model and tokenizer

```

    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    import torch

    model_name = "meta-llama/Llama-2-7b-hf" # Or any other LLM

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=False,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto"
    )
    model.config.use_cache = False # Important for fine-tuning

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token # Or set a specific pad token

```
References

Amazon SageMaker

https://aws.amazon.com/sagemaker/

Fine-Tune Your First LLM

https://docs.pytorch.org/torchtune/0.1/tutorials/first_finetune_tutorial.html

Fine-tuning

https://huggingface.co/docs/transformers/en/training


