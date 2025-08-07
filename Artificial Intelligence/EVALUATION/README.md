# Evaluation of Artificial Intelligence (AI)

This repository contains tools and methodologies for evaluating artificial intelligence models, with a focus on Large Language Models (LLMs), time-series forecasting, and various AI evaluation frameworks.

## 📁 Project Structure

```
EVALUATION/
├── 📂 BENCHMARKING/           # LLM Benchmarking Tools & Frameworks
│   ├── benchmark_runner.py      # Core benchmarking execution engine
│   ├── enhanced_benchmark_runner.py  # Advanced benchmarking features
│   ├── docker-compose.yml       # Containerized benchmarking setup
│   ├── Dockerfile               # Docker environment configuration
│   ├── requirements.txt         # Python dependencies
│   ├── SETUP_AND_USAGE.md      # Installation & usage guide
│   └── notebooks/
│       └── LLM_Benchmark_Tutorial.ipynb  # Interactive tutorial
│
├── 📂 METRICS/                # AI Model Evaluation & Time-Series Analysis
│   ├── src/                     # Core evaluation modules
│   │   ├── advanced_evaluation.py     # Advanced metrics & analysis
│   │   ├── electricity_forecasting.py # Time-series forecasting
│   │   ├── model_optimization.py      # Model tuning & optimization
│   │   ├── RNN_LSTM_Electricity_Forecasting.ipynb  # LSTM tutorial
│   │   └── Dataset/            # Training & evaluation datasets
│   ├── GPU_CUDA_DIAGNOSIS.md   # GPU setup troubleshooting
│   └── SETUP.md               # Environment setup guide
│
├── 📂 TOOLS/                  # Evaluation Tools & Utilities
│   ├── api.py                  # REST API for evaluation services
│   ├── demo_evaluation.py      # Evaluation demonstrations
│   ├── modern_optimizers_guide.py  # Optimizer implementations
│   ├── docker-compose.yml      # Production deployment setup
│   ├── evaluation_examples/     # Comprehensive evaluation examples
│   │   ├── deepeval_example.py     # DeepEval framework demo
│   │   ├── geval_example.py        # G-Eval implementation
│   │   ├── langsmith_example.py    # LangSmith integration
│   │   └── ragas_example.py        # RAG evaluation toolkit
│   └── src/                    # Core tool implementations
│       ├── bert_evaluation.py      # BERT model evaluation
│       └── bert_fine_tuning.py     # BERT fine-tuning utilities
│
└── README.md                  # This documentation file
```

Each directory contains specialized tools for different aspects of AI evaluation:

- **BENCHMARKING**: Start here for LLM performance benchmarking and comparison
- **METRICS**: Focus on quantitative evaluation metrics and time-series forecasting
- **TOOLS**: Production-ready evaluation tools and frameworks

## References

### BENCHMARKING Resources
- [Open-source Benchmarking Tools for LLMs](./BENCHMARKING/README.md) - Comprehensive guide to LLM benchmarking frameworks
- [SETUP_AND_USAGE Guide](./BENCHMARKING/SETUP_AND_USAGE.md) - Step-by-step installation instructions
- [LLM Benchmark Tutorial](./BENCHMARKING/notebooks/LLM_Benchmark_Tutorial.ipynb) - Interactive Jupyter notebook tutorial

### METRICS & Time-Series Analysis
- [RNN+LSTM Time-Series Forecasting](./METRICS/README.md) - Complete pipeline for electricity usage forecasting
- [Advanced Evaluation Methods](./METRICS/src/advanced_evaluation.py) - Sophisticated model evaluation techniques
- [GPU/CUDA Setup Guide](./METRICS/GPU_CUDA_DIAGNOSIS.md) - Troubleshooting GPU environments
- [Electricity Forecasting Notebook](./METRICS/src/RNN_LSTM_Electricity_Forecasting.ipynb) - Hands-on LSTM implementation

### TOOLS & Frameworks
- [LLM Evaluation Tools Overview](./TOOLS/README.md) - Open-source evaluation frameworks (2025)
- [DeepEval Framework](./TOOLS/evaluation_examples/deepeval_example.py) - Production LLM testing
- [G-Eval Implementation](./TOOLS/evaluation_examples/geval_example.py) - LLM-as-a-Judge evaluation
- [LangSmith Integration](./TOOLS/evaluation_examples/langsmith_example.py) - Advanced LLM monitoring
- [RAGAS Toolkit](./TOOLS/evaluation_examples/ragas_example.py) - RAG system evaluation
- [BERT Evaluation Guide](./TOOLS/src/bert_evaluation.py) - BERT model assessment utilities

### External References
- [Confident AI DeepEval](https://github.com/confident-ai/deepeval) - Open-source LLM evaluation framework
- [G-Eval Paper](https://github.com/nlpyang/geval) - Chain-of-thought based LLM evaluation
- [LangSmith Documentation](https://docs.langchain.com/langsmith/) - LLM application monitoring
- [RAGAS Framework](https://github.com/explodinggradients/ragas) - RAG evaluation toolkit
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/) - Pre-trained model library

