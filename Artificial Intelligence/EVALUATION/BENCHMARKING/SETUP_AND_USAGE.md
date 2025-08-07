# Large language models (LLMs) Benchmarking Tools - Setup and Usage

## Overview
This scripts provides a toolkit for benchmarking Large Language Models (LLMs) with a focus on comparing BERT, DistilBERT, and ALBERT models across various tasks.

This document covers setup instructions, usage examples, and best practices for using the benchmarking tools.

## Quick Start

### Option 1: Local Installation (Recommended)

1. **Run the installation script:**
   ```bash
   ./install_benchmarking_tools.sh
   ```
   
2. **Activate the environment:**
   ```bash
   cd ~/llm_benchmarking
   ./activate_env.sh
   ```

3. **Test the installation:**
   ```bash
   python scripts/quick_benchmark.py
   ```

4. **Run full benchmarks:**
   ```bash
   python benchmark_runner.py          # Zero-shot testing only
   python enhanced_benchmark_runner.py # All testing approaches
   ```

## Testing Approaches Available

### Enhanced Implementation (`enhanced_benchmark_runner.py`)
- **Zero-shot Testing**: Direct model inference
- **Few-shot Testing**: Examples provided in prompts
- **Fine-tuned Testing**: Task-specific model training

### Usage Examples

**Zero-shot (Current):**
```bash
python benchmark_runner.py
```

**All approaches (Enhanced):**
```bash
# Quick mode (recommended for testing)
python enhanced_benchmark_runner.py
# Select option 1 when prompted

# Full mode (comprehensive evaluation)
python enhanced_benchmark_runner.py  
# Select option 2 when prompted
```

### Option 2: Docker Setup

1. **Build and run with Docker:**
   ```bash
   docker-compose up --build
   ```
   
2. **Access Jupyter notebook:**
   Open your browser to `http://localhost:8888`

3. **Run benchmarks in container:**
   ```bash
   docker-compose run llm-benchmark benchmark
   ```

### Option 3: AWS Setup

1. **Launch EC2 instance:**
   ```bash
   # Modify the script with your AWS credentials
   bash aws_setup.sh
   ```

2. **Connect to instance:**
   ```bash
   ssh -i your-key-pair.pem ubuntu@your-instance-ip
   ```

3. **Run installation script on the instance:**
   ```bash
   curl -O https://raw.githubusercontent.com/your-repo/install_benchmarking_tools.sh
   chmod +x install_benchmarking_tools.sh
   ./install_benchmarking_tools.sh
   ```

## Available Benchmarks

### 1. Text Classification
- Dataset: IMDB movie reviews
- Models: BERT, DistilBERT, ALBERT
- Metrics: Accuracy, F1-score, Precision, Recall

### 2. Question Answering
- Dataset: SQuAD
- Models: BERT, DistilBERT, ALBERT
- Metrics: Exact Match, F1-score

### 3. Mathematical Reasoning
- Custom math word problems
- Models: BERT, DistilBERT, ALBERT
- Metrics: Accuracy, Response time

## Project Structure

```
llm_benchmarking/
├── benchmark_runner.py      # Main benchmarking script
├── requirements.txt         # Python dependencies
├── install_benchmarking_tools.sh  # Installation script
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker compose setup
├── .gitignore             # Git ignore rules
├── configs/
│   └── benchmark_config.yaml
├── scripts/
│   └── quick_benchmark.py
├── notebooks/
│   └── LLM_Benchmark_Tutorial.ipynb
├── data/                  # Datasets
├── models/                # Downloaded models
└── results/              # Benchmark outputs
    ├── benchmark_results.json
    ├── benchmark_summary.csv
    └── benchmark_comparison.png
```

## Understanding Results

### Metrics Explained

- **Accuracy**: Percentage of correct predictions
- **F1-Score**: Harmonic mean of precision and recall
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **Exact Match**: Percentage of exactly correct answers
- **Inference Time**: Average time per prediction

### Expected Results

| Model | Classification Accuracy | QA Exact Match | Math Accuracy | Inference Time (ms) |
|-------|------------------------|----------------|---------------|-------------------|
| BERT | ~85% | ~80% | ~25% | ~150 |
| DistilBERT | ~82% | ~75% | ~20% | ~75 |
| ALBERT | ~84% | ~78% | ~23% | ~90 |

*Note: Actual results may vary based on hardware and specific datasets*

## Troubleshooting

### Issues

1. **Memory Error**: Reduce batch size or number of samples
2. **Model Loading Error**: Check internet connection for model downloads
3. **CUDA Error**: Add `--device cpu` flag or install CUDA drivers
4. **Import Error**: Ensure virtual environment is activated

### Performance

- Use GPU for faster inference (if available)
- Reduce sample sizes for quick testing
- Use DistilBERT for faster experimentation
- Cache models locally to avoid re-downloading

## Customization

### Adding New Models
Edit `benchmark_runner.py` and modify the `models` dictionary:
```python
self.models = {
    'BERT': 'bert-base-uncased',
    'RoBERTa': 'roberta-base',
    'Your-Model': 'your-model-name'
}
```

### Adding New Datasets
Modify the benchmark functions to use different datasets:
```python
dataset = load_dataset('your-dataset-name', split='test')
```

### Custom Metrics
Add custom evaluation functions to the benchmark suite.

## Integration with Other Tools

### Weights & Biases
```python
import wandb
wandb.init(project="llm-benchmark")
wandb.log(results)
```

### MLflow
```python
import mlflow
mlflow.log_metrics(results)
```

## License

This project is open source. See LICENSE file for details.
