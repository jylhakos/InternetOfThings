# Pipeline for training, pre-training, and deployment of Large Language Models

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Pipeline Architecture](#pipeline-architecture)
4. [Pipeline Steps](#pipeline-steps)
5. [Local Pipeline: Docker and Linux](#local-pipeline-docker-and-linux)
6. [Cloud Pipeline: Microsoft Azure](#cloud-pipeline-microsoft-azure)
7. [Comparison: Local versus Cloud Pipeline](#comparison-local-versus-cloud-pipeline)
8. [Open Source Tools for Pre-Training](#open-source-tools-for-pre-training)
9. [Python Virtual Environment Setup](#python-virtual-environment-setup)
10. [Practical Pre-Training Pipeline on Local Linux with GPU](#practical-pre-training-pipeline-on-local-linux-with-gpu)
11. [Inference Testing: Ollama and Open WebUI](#inference-testing-ollama-and-open-webui)
12. [References and External Resources](#references-and-external-resources)

---

## Overview

A **pipeline** in the context of large language model (LLM) development refers to a structured sequence of automated, reproducible stages that transform raw data into a trained, evaluated, and deployed model. The pipeline encompasses every phase from data ingestion and tokenization through model architecture definition, distributed training, evaluation, checkpointing, and ultimately deployment into a production environment.

Designing an LLM pipeline requires decisions at multiple levels: the choice of compute infrastructure, the distributed training strategy, the model architecture, the tokenizer, and the serving framework. These decisions differ significantly depending on whether the pipeline runs in a local virtualized environment — such as a workstation or a small cluster running Docker on Linux — or on a cloud provider such as Microsoft Azure, which furnishes elastic, high-performance computing clusters and managed machine-learning services.

This document describes both scenarios. It first defines the fundamental concepts underlying LLM training. It then describes a general pipeline applicable to both environments, followed by environment-specific guidance for local deployments and for Azure-based deployments. A comparative summary highlights the trade-offs between the two approaches.

For foundational reading on implementing a GPT-style model from scratch, the following resources are recommended:

- [Build a Large Language Model (from Scratch)](https://github.com/rasbt/LLMs-from-scratch) — Sebastian Raschka
- [Implementing a GPT Model from Scratch To Generate Text](https://github.com/rasbt/LLMs-from-scratch/blob/main/ch04/01_main-chapter-code/ch04.ipynb) — Jupyter Notebook, Chapter 4
- [From GPT-2 to gpt-oss: Analyzing the Architectural Advances](https://magazine.sebastianraschka.com/p/from-gpt-2-to-gpt-oss-analyzing-the) — Sebastian Raschka
- [The Big LLM Architecture Comparison](https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison) — Sebastian Raschka

---

## Core Concepts

The following section provides working definitions for the principal concepts referenced throughout this document. These definitions are intended as concise technical summaries suitable for practitioners entering the field of large-scale language model development.

### Transformer

The Transformer is a neural network architecture introduced by Vaswani et al. (2017) in "Attention Is All You Need." It replaces recurrent connections with self-attention mechanisms, enabling parallelized processing of sequences. All modern large language models, including the GPT and LLaMA families, are built on the Transformer architecture or direct derivatives thereof.

### Multi-Head Attention (MHA)

Multi-Head Attention is the core computational block of the Transformer. The mechanism projects the input sequence into multiple sets of query, key, and value vectors — each set called an "attention head" — computes scaled dot-product attention independently for each head, and concatenates the results. This allows the model to attend jointly to information from different representation subspaces at different positions within the sequence.

### Query Attention

In the attention mechanism, each token in the sequence generates a **query** vector that is compared against the **key** vectors of all other tokens. The similarity scores between the query and the keys determine the weighted combination of **value** vectors that forms the output. Query attention is the operation by which a given token retrieves contextually relevant information from the sequence.

### Grouped Query Attention (GQA)

Grouped Query Attention is an architectural variant in which multiple query heads share a single key-value head, rather than maintaining one key-value pair per query head as in standard MHA. GQA reduces memory bandwidth requirements during inference while preserving most of the representational power of full MHA. It is used in several recent open-weight models, including LLaMA 2 and Mistral.

### Dot-Product Attention

Dot-product attention, specifically **scaled dot-product attention**, computes the compatibility between queries and keys as the dot product of their vector representations, scaled by the square root of the key dimension to prevent gradient saturation in softmax. Formally:

$$\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

where $Q$, $K$, and $V$ are the query, key, and value matrices, and $d_k$ is the dimensionality of the key vectors.

### Tokenization

Tokenization is the process of converting raw text into a discrete sequence of integer identifiers (**tokens**) that serve as the input to a language model. Modern LLMs typically use subword tokenization algorithms — most commonly Byte-Pair Encoding (BPE) — which balance vocabulary size against the ability to represent rare or novel words. The tokenizer is trained on the same corpus as the model and its vocabulary is fixed before model training begins.

Widely used tokenizer implementations include:

- [tiktoken](https://github.com/openai/tiktoken) — A fast BPE tokenizer for use with OpenAI models.
- [SentencePiece](https://github.com/google/sentencepiece) — An unsupervised text tokenizer for neural network-based text generation, developed by Google.

### Positional Encoding

Because the Transformer has no inherent notion of sequence order, positional information must be injected into the token representations. **Positional encoding** assigns a unique vector to each position in the sequence and adds it to the corresponding token embedding. Early models used fixed sinusoidal encodings; contemporary models increasingly use learned absolute or relative encodings, including Rotary Position Embedding (RoPE) and ALiBi.

### GELU

The **Gaussian Error Linear Unit** (GELU) is a smooth, differentiable activation function defined as:

$$\text{GELU}(x) = x \cdot \Phi(x)$$

where $\Phi(x)$ is the standard normal cumulative distribution function. GELU is the standard activation function in GPT-style models, replacing the piecewise-linear ReLU. It tends to produce better empirical performance in deep Transformer networks due to its stochastic gating behavior.

### Back Propagation

Back propagation is the algorithm by which the gradients of the loss function with respect to every parameter in the network are computed via the chain rule of calculus, propagating error signals from the output layer backwards through all intermediate layers. Back propagation underlies all gradient-based optimization of neural networks.

### LayerNorm

**Layer Normalization** (Ba et al., 2016) normalizes the activations within a single layer across the feature dimension — rather than across the batch dimension as in Batch Normalization — to produce zero-mean, unit-variance representations. LayerNorm stabilizes training and reduces sensitivity to learning-rate choice. In most GPT-style models, LayerNorm is applied before each sub-layer (Pre-LN configuration).

### RMSNorm

**Root Mean Square Layer Normalization** (RMSNorm) is a computationally efficient simplification of LayerNorm that omits the mean-centering step and normalizes activations solely by their root mean square:

$$\text{RMSNorm}(x) = \frac{x}{\sqrt{\frac{1}{n}\sum_{i=1}^{n} x_i^2 + \epsilon}} \cdot g$$

where $g$ is a learned gain parameter. RMSNorm is used in LLaMA and related architectures because it achieves training stability comparable to LayerNorm at lower computational cost.

### Weights

In the context of neural networks, **weights** (also called **parameters**) are the learnable real-valued scalars organized into matrices and vectors throughout the network. Weights encode the knowledge acquired during training. The primary goal of the training pipeline is to find a configuration of weights that minimizes the training objective on the target dataset.

### Activation Function

An **activation function** is a nonlinear transformation applied element-wise to the output of a linear projection, enabling the network to model nonlinear relationships in the data. Without activation functions, arbitrary compositions of linear layers remain linear. Common activation functions in modern LLMs include GELU, SwiGLU, and SiLU.

### Loss

The **loss** (or **loss function**) is a scalar value that quantifies the discrepancy between the model's predictions and the target outputs for a given batch. It serves as the objective that the optimizer minimizes during training. In language modeling, the standard loss is the cross-entropy between the predicted token probability distribution and the true next token.

### Zero Gradient

**Zeroing the gradient** refers to the operation of resetting accumulated gradient tensors to zero before each forward-backward pass. In frameworks such as PyTorch, gradients accumulate by default across backward passes; calling `optimizer.zero_grad()` (or equivalent) prior to each training step ensures that gradient accumulation from previous steps does not corrupt the current update.

### Optimizer

An **optimizer** is an algorithm that updates model weights based on the computed gradients in order to minimize the loss. The optimizer implements a specific rule for translating raw gradients into weight updates, potentially incorporating momentum, adaptive learning rates, or weight decay. The choice of optimizer significantly affects both training stability and final model quality.

### Cross-Entropy Loss

**Cross-entropy loss** measures the divergence between two probability distributions — here, the model's predicted distribution over vocabulary tokens and the true one-hot distribution of the target token. For a predicted probability $p$ assigned to the correct token:

$$\mathcal{L} = -\log p$$

Averaged over a sequence and a batch, cross-entropy loss is equivalent to the negative log-likelihood of the target token sequence under the model, and its minimization drives the model to assign high probability to correct next tokens.

### AdamW

**AdamW** is the optimizer of choice for training nearly all modern large language models. It extends the Adam optimizer (which uses first- and second-moment estimates of the gradient to compute adaptive per-parameter learning rates) by applying **weight decay** directly to the parameters rather than to the gradient update, as originally proposed by Loshchilov and Hutter (2019). This correction prevents adaptive methods from conflating regularization with gradient adaptation, and generally improves generalization.

### Dropout

**Dropout** (Srivastava et al., 2014) is a regularization technique in which a randomly selected subset of neurons is set to zero during each training step with probability $p$ (the dropout rate). This prevents neurons from co-adapting and reduces overfitting. At inference time, dropout is disabled and activations are scaled by $1 - p$. In large pre-training runs, dropout is often set to zero or a very small value, as the data volume itself provides sufficient regularization.

### LoRA

**Low-Rank Adaptation** (LoRA; Hu et al., 2021) is a parameter-efficient fine-tuning (PEFT) technique. Rather than updating all weights of a pre-trained model, LoRA freezes the original weight matrices and injects small trainable low-rank decomposition matrices into the attention projection layers:

$$W' = W + \Delta W = W + BA$$

where $B \in \mathbb{R}^{d \times r}$ and $A \in \mathbb{R}^{r \times k}$ with rank $r \ll \min(d, k)$. This reduces the number of trainable parameters by orders of magnitude, enabling fine-tuning of billion-parameter models on modest hardware. **QLoRA** extends LoRA by additionally quantizing the frozen base model weights to 4-bit precision.

---

## Pipeline Architecture

A complete LLM training and deployment pipeline consists of two broad phases: the **training pipeline** and the **deployment pipeline**.

The **training pipeline** transforms raw text data into a trained model artifact. It encompasses data collection, preprocessing, tokenizer training, model initialization, distributed training, evaluation, and checkpointing.

The **deployment pipeline** packages and serves the trained model artifact in a target environment for inference. It encompasses model export or quantization, containerization, infrastructure provisioning, and serving framework configuration.

Although the logical steps of both pipelines remain consistent across environments, their implementation differs substantially between a local virtualized environment (Docker on Linux) and a cloud provider such as Microsoft Azure.

---

## Pipeline Steps

The following steps constitute a canonical LLM training and deployment pipeline. They apply to both local and cloud environments; environment-specific differences are noted in subsequent sections.

### 1. Data Collection and Preprocessing

Large-scale corpora — typically comprising terabytes of text — are collected from diverse sources (web crawls, books, code repositories, scientific papers). Raw data is deduplicated, quality-filtered, and normalized. The resulting text is segmented into documents and serialized into a format suitable for streaming during tokenization (e.g., Apache Parquet or line-delimited JSON).

### 2. Tokenizer Training

A subword tokenizer is trained on a representative sample of the preprocessed corpus to produce a domain-specific vocabulary. BPE-based tokenizers (e.g., tiktoken) and unigram language model-based tokenizers (e.g., SentencePiece) are the two most common choices. The tokenizer vocabulary size is a hyperparameter that balances compression efficiency against model embedding table size.

### 3. Model Architecture Definition

The Transformer architecture is configured by specifying the number of layers, the hidden dimension, the number of attention heads, the feed-forward intermediate dimension, the positional encoding scheme, and the activation function. Pre-training typically targets established architectures (e.g., GPT-3, BLOOM, LLaMA) or their derivatives to leverage existing hyperparameter search results and infrastructure support.

### 4. Distributed Training

Training is executed across multiple GPU or TPU devices. For large models that do not fit within the memory of a single device, model parallelism strategies are required:

- **Data Parallel (DP)**: Replicates the model across devices; each device processes a different data shard and gradients are synchronized after each step.
- **Tensor Parallel (TP)**: Partitions individual weight matrices across devices.
- **Pipeline Parallel (PP)**: Partitions the model by layers across devices.
- **Fully Sharded Data Parallel (FSDP)**: Shards optimizer states, gradients, and parameters across all data-parallel workers; implemented in PyTorch natively.
- **DeepSpeed ZeRO**: A Microsoft Research technique that stages the sharding of optimizer states, gradients, and parameters to minimize redundant memory usage.

### 5. Evaluation and Checkpointing

Model checkpoints are saved periodically (e.g., every N training steps) to enable recovery from hardware failures and to facilitate comparison across training runs. Standard evaluation metrics include **perplexity** on held-out validation data and benchmark scores on standardized downstream tasks (e.g., MMLU, HellaSwag). Learning rate schedules, gradient norms, and hardware utilization are monitored continuously.

### 6. Deployment

After training, the model is exported (optionally quantized to INT8 or INT4 precision), containerized, and deployed behind an inference server. Common serving frameworks include vLLM, TGI (Text Generation Inference by Hugging Face), and ONNX Runtime. The deployment target may be a local Docker container, a Kubernetes cluster, or a managed cloud inference endpoint.

---

## Local Pipeline: Docker and Linux

In a local environment, the training and deployment pipeline is executed on a single machine or a small cluster of machines running Linux, with Docker used to provide reproducible, isolated runtime environments.

### Environment Setup

The training environment is defined in a `Dockerfile` that specifies the base CUDA image, PyTorch version, and all Python dependencies (transformers, accelerate, deepspeed, datasets, etc.). Docker Compose or Kubernetes (via k3s or minikube) may be used to orchestrate multi-container deployments. Volume mounts provide the container with access to the host filesystem for datasets and checkpoints.

### Memory Management

On a single machine or a small node cluster, GPU memory is the primary constraint. The Hugging Face `accelerate` library abstracts away the complexity of mixed-precision training, gradient checkpointing, and CPU offloading, enabling models larger than the available GPU memory to be trained through systematic offloading of activations and optimizer states to CPU RAM or NVMe storage.

### Training Execution

Training is launched via the `accelerate launch` command or `torchrun` for PyTorch Distributed Data Parallel (DDP) configurations. For single-node multi-GPU setups, FSDP or DeepSpeed ZeRO Stage 2/3 provides the most practical path to training billion-scale models.

### Inference and Deployment

Locally trained models are served using containerized inference servers. A typical deployment packages the model weights and a serving framework such as vLLM or Hugging Face TGI into a Docker image, which is run with GPU passthrough via the NVIDIA Container Toolkit. The inference endpoint is exposed over HTTP using a REST or OpenAI-compatible API.

---

## Cloud Pipeline: Microsoft Azure

Microsoft Azure provides managed infrastructure and machine learning services that substantially simplify the orchestration of large-scale LLM training and deployment. The primary service is **Azure Machine Learning** (Azure ML), which offers job scheduling, experiment tracking, a model registry, and managed inference endpoints.

- [Azure Machine Learning Documentation](https://learn.microsoft.com/en-us/azure/machine-learning/?view=azureml-api-2)
- [LLM Fundamentals — Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/journey/llm-fundamentals)

### Model Catalog and Foundation Models

Azure ML provides a **Model Catalog** that hosts a curated collection of open-weight foundation models — including Llama, Phi, Falcon, and Mistral — that are pre-trained and prepared for fine-tuning on custom datasets. Selecting a foundation model from the catalog as the starting point for fine-tuning is the recommended approach when training data is insufficient to justify pre-training from scratch.

- [Explore Microsoft Foundry Models in Azure Machine Learning](https://learn.microsoft.com/en-us/azure/machine-learning/foundry-models-overview?view=azureml-api-2)

### Compute Infrastructure

Azure ML provisions high-performance GPU compute clusters (NC- and ND-series virtual machines equipped with NVIDIA A100 or H100 GPUs). Infrastructure as Code (IaC) tools — Azure Bicep, ARM templates, or Terraform — are used to define and version the cluster configuration, enabling reproducible environment provisioning. Compute clusters scale to zero when idle, providing cost efficiency for intermittent training workloads.

### Submitting a Training Job

Training jobs are submitted to Azure ML using the Python SDK v2 `command()` function, which specifies the training script, the compute target, the environment (either a curated Azure ML environment or a custom Docker image), and the data inputs. Distributed training is configured through the `distribution` parameter (PyTorch DDP, FSDP, or DeepSpeed).

- [Tutorial: Train a Model in Azure Machine Learning](https://learn.microsoft.com/en-us/azure/machine-learning/tutorial-train-model?view=azureml-api-2)
- [Training a Model in Azure Machine Learning — Concepts](https://learn.microsoft.com/en-us/azure/machine-learning/concept-train-machine-learning-model?view=azureml-api-2)

### Fine-Tuning on Azure

For fine-tuning workloads, Azure ML supports **LoRA** and **QLoRA** via the Hugging Face PEFT library, enabling fine-tuning of large foundation models on single or multi-GPU nodes with substantially reduced memory requirements. The Microsoft Foundry platform provides additional tooling for supervised fine-tuning workflows.

- [Beyond the Prompt — Why and How to Fine-tune Your Own Models](https://devblogs.microsoft.com/foundry/beyond-the-prompt-why-and-how-to-fine-tune-your-own-models/)
- [Fine-tune Models with Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry-classic/concepts/fine-tuning-overview?view=foundry-classic)

### Distributed Training Strategies on Azure

For models too large to fit on a single GPU node, Azure ML supports:

- **Fully Sharded Data Parallel (FSDP)**: Shards model parameters, gradients, and optimizer states across all participating GPUs in the cluster.
- **DeepSpeed ZeRO**: Integrates with the Azure ML training job configuration to distribute optimizer state and gradient storage across nodes, enabling training of models with hundreds of billions of parameters.

### Deployment and Inference

Trained models are registered in the Azure ML **Model Registry** and deployed to **Managed Online Endpoints** for real-time inference or **Batch Endpoints** for high-throughput offline inference. Each endpoint is backed by a configurable compute instance and can be version-controlled to support canary deployments and A/B testing.

---

## Comparison: Local versus Cloud Pipeline

The table below summarizes the principal differences between a local Docker/Linux-based pipeline and a Microsoft Azure cloud pipeline.

| Dimension | Local (Docker / Linux) | Cloud (Microsoft Azure) |
|---|---|---|
| **Infrastructure provisioning** | Manual; managed via Docker Compose or Kubernetes on-premises | Automated; defined via Azure ML SDK, Bicep, or Terraform |
| **Compute scalability** | Bounded by available hardware; scaling requires physical procurement | Elastic; GPU clusters scale on demand to hundreds of nodes |
| **Distributed training** | PyTorch DDP or FSDP on single node or small cluster; `accelerate` or `torchrun` | Azure ML managed distributed jobs; FSDP, DeepSpeed ZeRO supported natively |
| **Memory management** | Gradient checkpointing, CPU offloading via `accelerate`; constrained by node RAM | DeepSpeed ZeRO offload to NVMe; sufficient GPU memory typically available at scale |
| **Data storage** | Local filesystem or NFS mounts | Azure Blob Storage, Azure Data Lake; mounted as datastores in Azure ML |
| **Experiment tracking** | MLflow, Weights & Biases (self-hosted or SaaS) | Azure ML Experiments (built-in); integrates with MLflow |
| **Checkpointing** | Manual; stored to local disk or NFS | Automatic checkpointing to Azure Blob Storage; integrated with Model Registry |
| **Model serving** | vLLM or TGI in Docker container; exposed via custom API | Azure ML Managed Online Endpoints; versioned, monitored, auto-scaled |
| **Cost model** | Fixed capital expenditure; underutilized capacity incurs opportunity cost | Pay-per-use; idle clusters scale to zero; large jobs may incur significant expense |
| **Reproducibility** | Dockerfile provides environment reproducibility; hardware variability possible | Curated environments and versioned compute clusters provide high reproducibility |
| **Operational complexity** | Lower for small teams with hardware already available | Lower for large-scale workloads; managed services reduce infrastructure overhead |

**Summary.** A local pipeline is appropriate for research-scale experiments, prototyping, and fine-tuning of small to medium models where the team has access to suitable GPU hardware and wishes to maintain full control over the environment. A cloud pipeline becomes advantageous — and often necessary — when pre-training models from scratch, when model size exceeds the memory of local hardware, or when time-to-result is constrained by the need for large-scale distributed training.

---

## Open Source Tools for Pre-Training

This section catalogs the principal open-source frameworks, libraries, and datasets that constitute a practical pre-training stack. All tools listed here are freely available under permissive open-source licenses and are in widespread use across academic and industrial LLM research.

### Hugging Face Ecosystem

The Hugging Face organization maintains several libraries that together cover the full pre-training pipeline:

- **[Transformers](https://github.com/huggingface/transformers)** — Model definitions, training utilities, and a pre-trained model hub hosting hundreds of architectures including GPT-2, LLaMA, Mistral, and Falcon.
- **[Tokenizers](https://github.com/huggingface/tokenizers)** — A fast, Rust-backed tokenizer library supporting BPE, WordPiece, and Unigram tokenization. Used in `scripts/tokenizer_train.py` to train the domain-specific vocabulary.
- **[Datasets](https://github.com/huggingface/datasets)** — Efficient data loading with streaming support for multi-terabyte corpora. Streaming mode avoids downloading the entire dataset and is used in `scripts/data_preparation.py`.
- **[Accelerate](https://github.com/huggingface/accelerate)** — A minimal abstraction layer over PyTorch distributed training (DDP, FSDP) and mixed-precision. Requires minimal changes to convert a single-GPU training script to a multi-GPU or multi-node configuration.
- **[PEFT](https://github.com/huggingface/peft)** — Parameter-Efficient Fine-Tuning library providing LoRA and QLoRA implementations for memory-efficient fine-tuning of large foundation models.

An introductory curriculum covering the complete LLM development workflow is available at the [Hugging Face LLM Course](https://huggingface.co/learn/llm-course/chapter1/1).

### PyTorch

[PyTorch](https://pytorch.org/) is the primary deep learning framework used in all scripts in this project. The key components used in the pre-training pipeline are:

- `torch.nn` — Module system for defining the Transformer architecture.
- `torch.optim.AdamW` — Weight-decay-corrected adaptive optimizer.
- `torch.utils.data.Dataset` and `DataLoader` — Batched, shuffled data loading.
- `torch.distributed` — Backend for multi-GPU distributed training via DDP or FSDP.

### Open-Llama Pre-Training Framework

[Open-Llama](https://github.com/s-JoL/Open-Llama) is an open-source project that provides a complete end-to-end training pipeline for large language models, encompassing dataset preparation, tokenization, pre-training, prompt tuning, LoRA fine-tuning, and reinforcement learning from human feedback (RLHF). It serves as a practical reference implementation for the full pre-training workflow described in this document.

### Reference Implementation: LLMs-from-Scratch

Sebastian Raschka's [LLMs-from-Scratch](https://github.com/rasbt/LLMs-from-scratch) provides a pedagogically oriented, step-by-step implementation of a GPT-style language model. The GPT model architecture in `scripts/gpt_model.py` is adapted from the reference script [gpt.py](https://github.com/rasbt/LLMs-from-scratch/blob/28c65cdfbc3338e2e040016eea4b7fdf556e4d57/ch04/01_main-chapter-code/gpt.py) (Apache License 2.0).

### Foundational Research Paper

The Transformer architecture underlying all modern LLMs is introduced in:

- [Attention Is All You Need — Vaswani et al. (2017)](https://arxiv.org/html/1706.03762v7)

### Open Pre-Training Datasets

The following publicly available datasets are suitable for LLM pre-training at various scales:

| Dataset | Size | Description | Source |
|---|---|---|---|
| FineWeb-Edu | 1.3 TB | High-quality educational subset of Common Crawl | [huggingface.co](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu) |
| The Pile | 825 GB | Diverse English text corpus from 22 sources (EleutherAI) | [pile.eleuther.ai](https://pile.eleuther.ai/) |
| Common Crawl | Multi-TB | Raw web crawl data requiring substantial filtering | [commoncrawl.org](https://commoncrawl.org/) |
| OpenWebText | 40 GB | Reddit-curated web text, GPT-2 training data replica | [github.com/jcpeterson/openwebtext](https://github.com/jcpeterson/openwebtext) |

The `scripts/data_preparation.py` script in this project uses FineWeb-Edu via the Hugging Face `datasets` library in streaming mode, making it practical to begin without downloading the full dataset.

---

## Python Virtual Environment Setup

A virtual environment isolates project dependencies from the system Python installation, ensures reproducibility, and prevents version conflicts. All scripts in this project must be executed within the activated virtual environment.

### Creating the Virtual Environment

The following commands apply to a Linux system with Python 3.10 or later installed:

```bash
# Navigate to the project directory
cd /path/to/Introduction

# Create the virtual environment in a folder named venv/
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Confirm the active interpreter
which python
# Expected: /path/to/Introduction/venv/bin/python
```

The convenience script `scripts/setup_venv.sh` automates the above and installs all required dependencies in a single step:

```bash
bash scripts/setup_venv.sh
```

To override the CUDA version (default is CUDA 12.1):

```bash
CUDA_VERSION=cu118 bash scripts/setup_venv.sh
```

### Installing Dependencies Manually

After activating the virtual environment, the required packages can also be installed individually:

```bash
# PyTorch with CUDA 12.1 support
pip install torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu121

# Hugging Face ecosystem
pip install transformers tokenizers datasets accelerate peft

# Training utilities
pip install tqdm wandb

# Inference server (for local deployment)
pip install vllm
```

Check the installed CUDA version on the host system with:

```bash
nvcc --version
```

Replace `cu121` with the appropriate suffix for the installed CUDA version (e.g., `cu118` for CUDA 11.8, `cpu` for CPU-only environments without NVIDIA hardware).

### Configuring VS Code to Use the Virtual Environment

1. Open the project folder in VS Code.
2. Open the Command Palette with `Ctrl+Shift+P`.
3. Select **Python: Select Interpreter**.
4. Choose the interpreter located at `./venv/bin/python`.

VS Code will automatically activate the virtual environment in all integrated terminals opened within the project workspace and provide IntelliSense completions for installed packages.

### Activating the Virtual Environment for Script Execution

The virtual environment must be activated at the start of every new terminal session before running scripts or installing packages:

```bash
# Activate (required at the start of each new terminal session)
source venv/bin/activate

# Confirm activation
python --version       # should show 3.10+
pip list | grep torch  # should show the installed torch version
```

The `venv/` directory is excluded from version control by the `.gitignore` file in this project.

---

## Practical Pre-Training Pipeline on Local Linux with GPU

This section provides a hands-on walkthrough of the pre-training pipeline using the scripts in the `scripts/` directory. The pipeline targets a single Linux workstation equipped with at least one NVIDIA GPU (an RTX 3090 or RTX 4090 with 24 GB VRAM is sufficient for the small configuration; larger configurations require A100 or H100 hardware).

### Hardware Requirements

| Component | Minimum (small model) | Recommended (GPT-2 scale) |
|---|---|---|
| GPU | NVIDIA RTX 3090 / 4090 (24 GB VRAM) | NVIDIA A100 (40 GB or 80 GB) |
| System RAM | 32 GB | 128 GB |
| Storage | 200 GB NVMe SSD | 2 TB NVMe SSD |
| CUDA | 11.8 or later | 12.1 or later |

### Script Directory Structure

```
scripts/
├── setup_venv.sh         Shell script to create and configure the virtual environment
├── gpt_model.py          GPT-style Transformer architecture (model definition)
├── data_preparation.py   Data download, cleaning, and corpus creation
├── tokenizer_train.py    BPE tokenizer training on the corpus
└── pretrain.py           Pre-training loop with checkpointing and evaluation
```

### Stage 1: Data Preparation

The script `scripts/data_preparation.py` downloads a streaming subset of the [FineWeb-Edu](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu) dataset and writes a cleaned plain-text corpus to `data/cleaned/corpus.txt`. Using streaming mode means only the requested number of samples (`NUM_SAMPLES = 100,000` by default) is transferred, rather than the full 1.3 TB dataset.

The preprocessing steps applied to each document are:

1. **Unicode NFC normalization** — Canonicalizes character representations.
2. **Whitespace normalization** — Collapses tabs, non-breaking spaces, and zero-width characters into single ASCII spaces.
3. **Control character removal** — Strips null bytes and other ASCII control characters that are artifacts of web-crawl text extraction.
4. **Length filtering** — Discards documents shorter than 100 characters after cleaning.

Run data preparation:

```bash
source venv/bin/activate
python scripts/data_preparation.py
```

Output: `data/cleaned/corpus.txt`

### Stage 2: Tokenization

Tokenization converts raw text into a sequence of integer token IDs that the model processes numerically. There are three principal tokenization approaches for language models:

**Approach 1 — Character-level tokenization.** Each character in the text is a separate token. This produces a very small vocabulary (typically 100–300 tokens for English) but generates extremely long sequences. Because the computational complexity of self-attention scales quadratically with sequence length, character-level tokenization is prohibitively expensive for Transformer models operating on long documents.

**Approach 2 — Word-level tokenization.** The text is split on whitespace boundaries, treating each distinct word as a token. This produces compact sequences but results in a large vocabulary and cannot represent words absent from the training corpus (the out-of-vocabulary problem). Morphological variants of a word (e.g., "train", "trains", "training") each consume a separate vocabulary slot.

**Approach 3 — Subword BPE tokenization (industry standard).** The tokenizer learns frequent character sequences (subwords) from the corpus itself. This approach is used by GPT, LLaMA, Mistral, Falcon, and most modern LLMs. It balances vocabulary size (typically 32,000–100,000 tokens) against sequence length and handles out-of-vocabulary words by decomposing them into known subword units.

The script `scripts/tokenizer_train.py` trains a BPE tokenizer using the Hugging Face `tokenizers` library (Approach 3) and saves the vocabulary and merge rules to `tokenizer/tokenizer.json`. The following special tokens are added to provide structural information for training and inference:

| Token | Purpose |
|---|---|
| `<\|endoftext\|>` | Marks the end of a document; used as a document separator during training |
| `<\|bos\|>` | Beginning-of-sequence marker |
| `<\|eos\|>` | End-of-sequence marker |
| `<\|pad\|>` | Padding token for batched inference with variable-length inputs |
| `<\|unk\|>` | Unknown token fallback (rarely triggered by byte-level BPE) |

Run tokenizer training:

```bash
source venv/bin/activate
python scripts/tokenizer_train.py
```

Output: `tokenizer/tokenizer.json`

### Stage 3: GPT-Style Model Architecture

The model architecture is defined in `scripts/gpt_model.py`. It implements a decoder-only Transformer following the design described in "Attention Is All You Need" (Vaswani et al., 2017) adapted to the autoregressive (causal) language modelling objective used in GPT-2 and GPT-3. The implementation is adapted from Sebastian Raschka's [gpt.py](https://github.com/rasbt/LLMs-from-scratch/blob/28c65cdfbc3338e2e040016eea4b7fdf556e4d57/ch04/01_main-chapter-code/gpt.py) (Apache License 2.0).

The architecture stacks the following components in order:

1. **Token embedding** — Maps each integer token ID to a dense vector of dimension `emb_dim`.
2. **Positional embedding** — Maps each sequence position to a learned vector that is added to the token embedding to inject positional information.
3. **Dropout** — Applied to the combined embedding for regularization during training.
4. **N Transformer blocks**, each containing:
   - Pre-LayerNorm
   - Multi-Head Causal Self-Attention (with a causal mask preventing each token from attending to future positions)
   - Residual connection
   - Pre-LayerNorm
   - Position-wise Feed-Forward Network (two linear layers with GELU activation, inner dimension 4 × `emb_dim`)
   - Residual connection
5. **Final LayerNorm**
6. **Linear projection head** — Projects from `emb_dim` to `vocab_size` to produce vocabulary logits. Its weights are tied to the token embedding matrix, which reduces the parameter count and consistently improves perplexity (Press and Wolf, 2017).

The following named configurations are provided in `gpt_model.py`:

| Configuration | Parameters | `emb_dim` | Layers | Heads | `context_len` |
|---|---|---|---|---|---|
| `GPT_SMALL_CONFIG` | ~7 M | 256 | 4 | 4 | 256 |
| `GPT2_CONFIG` | ~117 M | 768 | 12 | 12 | 1,024 |

Run the architecture smoke test:

```bash
source venv/bin/activate
python scripts/gpt_model.py
```

### Stage 4: The Pre-Training Loop

The script `scripts/pretrain.py` implements the full training loop. The data pipeline uses `torch.utils.data.Dataset` and `DataLoader` with a sliding-window approach: each training sample is a window of `context_len` token IDs from the corpus, and the target is the same window shifted right by one position — the standard next-token prediction (causal language modelling) objective.

For each training step the loop performs the following operations in sequence:

1. **Zero gradients** — `optimizer.zero_grad()` resets accumulated gradients from the previous step. PyTorch accumulates gradients by default; resetting them before each step prevents contamination from prior batches.
2. **Forward pass** — The batch of token sequences is passed through the model. Each Transformer block applies causal self-attention and a feed-forward network, producing logits over the vocabulary.
3. **Loss calculation** — Cross-entropy loss is computed between the predicted next-token distribution (logits) and the actual next tokens (targets). This is the primary training signal.
4. **Backward pass (back propagation)** — `loss.backward()` traverses the computation graph in reverse, computing the gradient of the loss with respect to every trainable parameter via the chain rule.
5. **Gradient clipping** — The global gradient norm is clipped to 1.0. This prevents gradient explosion, which is common in the early stages of training for large models.
6. **Learning rate update** — A cosine schedule with linear warm-up adjusts the learning rate. During the warm-up phase the learning rate rises linearly from zero to the peak value; afterwards it decays following a half-cosine curve to zero.
7. **AdamW optimizer step** — The optimizer updates all trainable parameters using first-moment (momentum) and second-moment (adaptive scaling) gradient estimates, with weight decay applied directly to the parameter values (not to the gradient).

Run pre-training (single GPU):

```bash
source venv/bin/activate
python scripts/pretrain.py
```

For multi-GPU training on a single machine using PyTorch Distributed Data Parallel (DDP):

```bash
source venv/bin/activate
torchrun --nproc_per_node=2 scripts/pretrain.py
```

Checkpoints are saved to `checkpoints/` at intervals defined by `CHECKPOINT_INTERVAL` in the script. Each checkpoint stores the model state dictionary, optimizer state, current training step, and configuration, enabling training to resume after interruption.

### Stage 5: Evaluation

During training the script evaluates the model on a held-out validation split (10% of the corpus) every `EVAL_INTERVAL` steps and reports:

- **Validation loss** — Average cross-entropy loss on the validation set. Lower values indicate better next-token prediction.
- **Perplexity** — $e^{\text{loss}}$. A lower value indicates better language modelling quality. State-of-the-art LLMs achieve perplexities below 10 on standard benchmarks. Early in training, perplexity will be close to the vocabulary size (random chance); it should decrease steadily as training progresses.

For downstream task benchmarking, the [Language Model Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness) by EleutherAI provides a standardized framework for running tasks from the [Hugging Face Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) locally against a trained checkpoint.

---

## Inference Testing: Ollama and Open WebUI

After training, the model checkpoint must be converted to a format compatible with an inference server before it can be used interactively. This section describes how to use [Ollama](https://ollama.com/) for local GGUF-based inference and [Open WebUI](https://github.com/open-webui/open-webui) as a browser-based interface for testing the model.

### Converting the Model to GGUF Format

Ollama and other llama.cpp-based inference servers require models in the **GGUF** (GGML Unified Format). The conversion uses [llama.cpp](https://github.com/ggerganov/llama.cpp).

Step 1: Build llama.cpp from source:

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j$(nproc)
pip install -r requirements.txt
```

Step 2: Export the PyTorch checkpoint to Hugging Face format (if not already in that format), then convert to GGUF:

```bash
# Convert to GGUF using float16 precision
python convert_hf_to_gguf.py /path/to/hf_model \
    --outfile model.gguf \
    --outtype f16
```

Step 3 (optional): Apply quantization to reduce model size and memory footprint:

```bash
# 4-bit quantization — reduces memory by approximately 4x at modest quality cost
./llama-quantize model.gguf model-q4_k_m.gguf Q4_K_M
```

### Installing Ollama on Linux

[Ollama](https://ollama.com/) is an open-source tool that simplifies running GGUF-format language models locally on Linux, macOS, and Windows. Install it on Linux with the official installer:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify the installation:

```bash
ollama --version
```

Ollama starts an HTTP server on port 11434 by default. Check that the service is running:

```bash
systemctl status ollama
```

### Creating a Modelfile

An Ollama `Modelfile` defines the model configuration including the GGUF file path, system prompt, and inference parameters. Create a file named `Modelfile` in the project directory:

```
# Modelfile for the locally trained language model

FROM ./model-q4_k_m.gguf

PARAMETER temperature 0.7
PARAMETER top_k 40
PARAMETER top_p 0.9
PARAMETER num_ctx 2048
PARAMETER repeat_penalty 1.1

SYSTEM "You are a helpful assistant trained from scratch."
```

Register the model with Ollama:

```bash
ollama create my-llm -f Modelfile
```

Verify the model is registered:

```bash
ollama list
```

### Running Inference with Ollama

Start an interactive chat session in the terminal:

```bash
ollama run my-llm "Explain the concept of self-attention in a Transformer model."
```

Query the model programmatically via the REST API:

```bash
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "my-llm",
    "prompt": "What is the purpose of positional encoding in a Transformer?",
    "stream": false
  }'
```

The response will include the generated text along with token usage statistics and timing information.

### Open WebUI: Browser-Based Interface

[Open WebUI](https://github.com/open-webui/open-webui) provides a ChatGPT-style web interface that connects to Ollama as its backend. It requires Docker. Install and start Open WebUI with:

```bash
docker run -d \
  --network=host \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://127.0.0.1:11434 \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

Open a browser and navigate to `http://localhost:8080`. Create an account on first launch; all credentials are stored locally in the Docker volume. The model registered with Ollama (`my-llm`) will appear in the model selector dropdown.

To upload a new model through the interface:

1. Navigate to **Settings** → **Models**.
2. Use the **Pull a model from Ollama.com** field to pull a community model, or use the **Upload a model** option to import a GGUF file directly from the local filesystem.

### Verifying That the Model Works Correctly

The following checklist confirms that the inference pipeline is functioning correctly:

1. The model produces coherent text continuations given a natural-language prompt.
2. Generation terminates at the `<|endoftext|>` or `<|eos|>` special token rather than running indefinitely.
3. The perplexity of the model on a sample of held-out text is comparable to the final training validation perplexity recorded during `pretrain.py`.
4. Response latency is within an acceptable range for the selected quantization level (Q4_K_M typically achieves 20–50 tokens/second on a modern CPU; GPU inference is significantly faster).

---

## References and External Resources

### Foundational Research Papers

- [Attention Is All You Need — Vaswani et al. (2017)](https://arxiv.org/html/1706.03762v7)

### Tokenization

- [tiktoken — Fast BPE Tokenizer (OpenAI)](https://github.com/openai/tiktoken)
- [SentencePiece — Unsupervised Text Tokenizer (Google)](https://github.com/google/sentencepiece)
- [Hugging Face Tokenizers Library](https://github.com/huggingface/tokenizers)

### Architecture and Model Analysis

- [From GPT-2 to gpt-oss: Analyzing the Architectural Advances](https://magazine.sebastianraschka.com/p/from-gpt-2-to-gpt-oss-analyzing-the)
- [The Big LLM Architecture Comparison](https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison)

### Practical Implementation

- [Build a Large Language Model (from Scratch) — Sebastian Raschka](https://github.com/rasbt/LLMs-from-scratch)
- [Implementing a GPT Model from Scratch To Generate Text — Chapter 4 Notebook](https://github.com/rasbt/LLMs-from-scratch/blob/main/ch04/01_main-chapter-code/ch04.ipynb)
- [Reference GPT Architecture Script (gpt.py, Apache License 2.0)](https://github.com/rasbt/LLMs-from-scratch/blob/28c65cdfbc3338e2e040016eea4b7fdf556e4d57/ch04/01_main-chapter-code/gpt.py)
- [Open-Llama: Open-Source End-to-End Pre-Training Pipeline](https://github.com/s-JoL/Open-Llama)

### Hugging Face Resources

- [Hugging Face LLM Course — Introduction](https://huggingface.co/learn/llm-course/chapter1/1)
- [Hugging Face Transformers Library](https://github.com/huggingface/transformers)
- [FineWeb-Edu Dataset](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu)
- [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)

### Evaluation

- [Language Model Evaluation Harness (EleutherAI)](https://github.com/EleutherAI/lm-evaluation-harness)

### Inference and Deployment Tools

- [Ollama — Run LLMs Locally](https://ollama.com/)
- [Open WebUI — Browser Interface for Ollama](https://github.com/open-webui/open-webui)
- [llama.cpp — GGUF Inference and Quantization](https://github.com/ggerganov/llama.cpp)

### Cloud Training Guides

- [Training Large Language Models on Amazon SageMaker](https://aws.amazon.com/blogs/machine-learning/training-large-language-models-on-amazon-sagemaker-best-practices/)
- [Fine-Tuning Large Language Models: How Vertex AI Takes LLMs to the Next Level](https://codelabs.developers.google.com/llm-finetuning-supervised#0)

### Microsoft Azure and Foundry

- [LLM Fundamentals — Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/journey/llm-fundamentals)
- [Beyond the Prompt — Why and How to Fine-tune Your Own Models](https://devblogs.microsoft.com/foundry/beyond-the-prompt-why-and-how-to-fine-tune-your-own-models/)
- [Fine-tune Models with Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry-classic/concepts/fine-tuning-overview?view=foundry-classic)
- [Azure Machine Learning Documentation](https://learn.microsoft.com/en-us/azure/machine-learning/?view=azureml-api-2)
- [Explore Microsoft Foundry Models in Azure Machine Learning](https://learn.microsoft.com/en-us/azure/machine-learning/foundry-models-overview?view=azureml-api-2)
- [Tutorial: Train a Model in Azure Machine Learning](https://learn.microsoft.com/en-us/azure/machine-learning/tutorial-train-model?view=azureml-api-2)
- [Training a Model in Azure Machine Learning — Concepts](https://learn.microsoft.com/en-us/azure/machine-learning/concept-train-machine-learning-model?view=azureml-api-2)
