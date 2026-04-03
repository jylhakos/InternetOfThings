# Evaluation of Artificial Intelligence (AI) models

This repository contains tools and methodologies for evaluating artificial intelligence models, with a focus on Large Language Models (LLMs), AI agents, security testing, observability, time-series forecasting, and various AI evaluation frameworks.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Project Structure](#-project-structure)
- [Tools & Frameworks](#tools--frameworks)
- [Use Cases](#use-cases)
- [Technologies & Dependencies](#technologies--dependencies)
- [References](#references)
- [Docker Deployment](#docker-deployment)
- [Contributing](#contributing)
- [Project Highlights](#project-highlights)

## Overview

This project provides a complete evaluation ecosystem for AI systems, covering:

- **Performance Benchmarking**: Systematic evaluation of LLM capabilities across diverse tasks
- **Quantitative Metrics**: Time-series forecasting and RNN+LSTM model evaluation
- **Observability**: Real-time monitoring and tracing of AI agent behavior
- **Security Testing**: Prompt injection detection, guardrails, and adversarial testing
- **Production Tools**: REST APIs, Docker deployment, and evaluation frameworks

## Quick Start

### BENCHMARKING
```bash
cd BENCHMARKING
pip install -r requirements.txt
python benchmark_runner.py
```

### METRICS
```bash
cd METRICS
pip install -r src/requirements.txt
python src/train_models.py
```

### OBSERVABILITY
```bash
cd OBSERVABILITY
bash setup.sh
source .venv/bin/activate
python sources/run_evaluation.py
```

### SECURITY
```bash
cd SECURITY
bash scripts/setup_venv.sh
source venv/bin/activate
bash scripts/run_security_tests.sh
```

### TOOLS
```bash
cd TOOLS
source bert_env/bin/activate
python demo_evaluation.py
```

## 📁 Project Structure

```
EVALUATION/
├── 📂 BENCHMARKING/           # LLM Benchmarking Tools & Frameworks
│   ├── 📄 benchmark_runner.py      # Core benchmarking execution engine
│   ├── 📄 enhanced_benchmark_runner.py  # Advanced benchmarking features
│   ├── 📄 docker-compose.yml       # Containerized benchmarking setup
│   ├── 📄 Dockerfile               # Docker environment configuration
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 README.md               # Benchmarking documentation
│   ├── 📄 SETUP_AND_USAGE.md      # Installation & usage guide
│   └── 📂 notebooks/
│       └── 📄 LLM_Benchmark_Tutorial.ipynb  # Interactive tutorial
│
├── 📂 METRICS/                # AI Model Evaluation & Time-Series Analysis
│   ├── 📂 src/                     # Core evaluation modules
│   │   ├── 📄 advanced_evaluation.py     # Advanced metrics & analysis
│   │   ├── 📄 electricity_forecasting.py # Time-series forecasting
│   │   ├── 📄 model_optimization.py      # Model tuning & optimization
│   │   ├── 📄 train_models.py            # Model training pipeline
│   │   ├── 📄 validate_pipeline.py       # Pipeline validation
│   │   ├── 📄 api_server.py              # REST API server
│   │   ├── 📄 weather_service.py         # Weather data integration
│   │   ├── 📄 gpu_cuda_diagnostic.py     # GPU/CUDA diagnostics
│   │   ├── 📄 RNN_LSTM_Electricity_Forecasting.ipynb  # LSTM tutorial
│   │   └── 📂 Dataset/            # Training & evaluation datasets
│   ├── 📄 GPU_CUDA_DIAGNOSIS.md   # GPU setup troubleshooting
│   ├── 📄 README.md               # RNN+LSTM forecasting pipeline
│   └── 📄 SETUP.md               # Environment setup guide
│
├── 📂 OBSERVABILITY/          # AI Agent & LLM Observability
│   ├── 📂 sources/                 # Observability implementations
│   │   ├── 📄 agent_evaluation.py     # Agent evaluation framework
│   │   ├── 📄 llm_judge_evaluator.py  # LLM-as-a-Judge evaluation
│   │   ├── 📄 run_evaluation.py       # Evaluation orchestration
│   │   ├── 📄 check_thresholds.py     # Performance threshold checks
│   │   └── 📄 test_installation.py    # Installation verification
│   ├── 📂 configs/                 # Configuration files
│   │   └── 📄 thresholds.json        # Evaluation thresholds
│   ├── 📂 docker/                  # Docker deployment
│   │   └── 📄 docker-compose.yml     # Container orchestration
│   ├── 📄 README.md               # Observability documentation
│   ├── 📄 QUICKSTART.md           # Quick start guide
│   ├── 📄 CONTRIBUTING.md         # Contribution guidelines
│   ├── 📄 requirements.txt         # Python dependencies
│   └── 📄 setup.sh                # Setup automation script
│
├── 📂 SECURITY/               # LLM Security Testing & Guardrails
│   ├── 📂 src/                     # Security testing modules
│   │   ├── 📄 rag_chatbot.py         # RAG chatbot implementation
│   │   ├── 📄 injection_tests.py     # Prompt injection tests
│   │   ├── 📄 guardrails.py          # Input/output validation
│   │   ├── 📄 metrics.py             # Security metrics
│   │   └── 📄 ollama_client.py       # Ollama API client
│   ├── 📂 tests/                   # Security test suite
│   │   ├── 📄 test_prompt_injection.py    # Direct injection tests
│   │   ├── 📄 test_indirect_injection.py  # Indirect injection tests
│   │   ├── 📄 test_data_exfiltration.py   # Data leakage tests
│   │   └── 📄 test_guardrails.py          # Guardrail validation
│   ├── 📂 data/                    # Test data and documents
│   │   ├── 📂 secure_docs/            # Secure RAG documents
│   │   ├── 📂 malicious_docs/         # Malicious test documents
│   │   └── 📄 test_prompts.json      # Test prompt dataset
│   ├── 📂 config/                  # Configuration files
│   │   ├── 📄 model_parameters.yaml  # Model configuration
│   │   └── 📄 ollama_config.yaml     # Ollama settings
│   ├── 📂 scripts/                 # Automation scripts
│   │   ├── 📄 install_ollama.sh      # Ollama installation
│   │   ├── 📄 run_security_tests.sh  # Test execution
│   │   └── 📄 setup_venv.sh          # Virtual environment setup
│   ├── 📄 README.md               # Security testing documentation
│   ├── 📄 QUICKSTART.md           # Quick start guide
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 Dockerfile               # Docker image definition
│   └── 📄 docker-compose.yml      # Container orchestration
│
├── 📂 TOOLS/                  # Evaluation Tools & Utilities
│   ├── 📂 evaluation_examples/     # Evaluation examples
│   │   ├── 📄 deepeval_example.py     # DeepEval framework demo
│   │   ├── 📄 geval_example.py        # G-Eval implementation
│   │   ├── 📄 langsmith_example.py    # LangSmith integration
│   │   ├── 📄 ragas_example.py        # RAG evaluation toolkit
│   │   ├── 📄 llmebench_example.py    # LLM benchmark example
│   │   ├── 📄 evaluation_demo.py      # Evaluation demo
│   │   ├── 📄 integration_test.py     # Integration testing
│   │   └── 📄 installation_guide.md   # Installation guide
│   ├── 📂 src/                     # Core tool implementations
│   │   ├── 📄 bert_evaluation.py      # BERT model evaluation
│   │   ├── 📄 bert_fine_tuning.py     # BERT fine-tuning utilities
│   │   ├── 📄 geval_integration.py    # G-Eval integration
│   │   └── 📄 minimal_bert.py         # Minimal BERT implementation
│   ├── 📄 api.py                  # REST API for evaluation services
│   ├── 📄 demo_evaluation.py      # Evaluation demonstrations
│   ├── 📄 modern_optimizers_guide.py  # Optimizer implementations
│   ├── 📄 optimizer_demo.py        # Optimizer demonstration
│   ├── 📄 examples.py              # Usage examples
│   ├── 📄 README.md               # Tools documentation
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 docker-compose.yml      # Production deployment setup
│   └── 📄 Dockerfile               # Docker image definition
│
└── 📄 README.md                  # This documentation file
```

Each directory contains specialized tools for different aspects of AI evaluation:

- **BENCHMARKING**: LLM performance benchmarking and comparison using open-source tools
- **METRICS**: Quantitative evaluation metrics, time-series forecasting, and RNN+LSTM models
- **OBSERVABILITY**: AI agent monitoring, tracing, and LLM-as-a-Judge evaluation
- **SECURITY**: LLM security testing, prompt injection detection, and guardrails
- **TOOLS**: Production-ready evaluation frameworks and utilities

## Tools & Frameworks

### BENCHMARKING Tools
- **Benchmark Execution**: Core benchmarking engine and enhanced runner for LLM testing
- **Containerization**: Docker and Docker Compose for isolated benchmarking environments
- **Interactive Tutorial**: Jupyter notebook for hands-on LLM benchmarking practice
- **Evaluation Metrics**: BLEU, ROUGE, METEOR, Perplexity, Exact Match, F1 Score
- **Benchmarks**: ARC, HellaSwag, MMLU, GPQA, WinoGrande, GSM8K, HumanEval

### METRICS & Analysis Tools
- **Time-Series Forecasting**: RNN, LSTM, and Deep LSTM implementations for electricity forecasting
- **Model Optimization**: Grid search, random search, Bayesian optimization, and hyperparameter tuning
- **Evaluation Metrics**: RMSE, MAE, MAPE, R², sMAPE, MASE, statistical tests
- **API Services**: REST API for model predictions and weather data integration
- **GPU/CUDA Support**: CUDA diagnostics and optimization tools

### OBSERVABILITY Platforms
- **Agent Evaluation**: LangGraph-based agent evaluation framework
- **LLM-as-a-Judge**: Automated evaluation using LLM judges
- **Tracing & Monitoring**: Real-time agent behavior tracking and decision logging
- **Performance Metrics**: Task completion, tool invocation accuracy, reasoning quality
- **Threshold Monitoring**: Automated performance threshold validation

### SECURITY Testing Tools
- **Ollama**: Local LLM deployment for secure testing
- **Prompt Injection Testing**: Direct and indirect injection vulnerability detection
- **Guardrails**: Input/output validation and content filtering
- **RAG Security**: Retrieval-augmented generation chatbot security testing
- **Data Exfiltration**: Sensitive data leakage detection and prevention
- **Security Metrics**: Toxicity, hallucination index, adversarial robustness

### EVALUATION Frameworks
- **DeepEval**: Production-ready LLM testing and evaluation framework
- **G-Eval**: LLM-as-a-Judge evaluation with chain-of-thought reasoning
- **LangSmith**: Advanced LLM application monitoring and debugging
- **RAGAS**: RAG system evaluation toolkit
- **LLMeBench**: Large-scale LLM benchmarking platform
- **BERT**: Fine-tuning and evaluation utilities for BERT models

## Use Cases

### When to Use BENCHMARKING
- Compare multiple LLM models on standardized tasks
- Evaluate reasoning capabilities (ARC, HellaSwag, MMLU)
- Assess mathematical and coding proficiency (GSM8K, HumanEval)
- Run systematic benchmarks in containerized environments
- Generate reproducible performance reports

### When to Use METRICS
- Time-series forecasting for electricity consumption or similar sequential data
- Train and optimize RNN/LSTM models with hyperparameter tuning
- Evaluate model performance using RMSE, MAE, MAPE, R²
- Deploy forecasting models via REST API
- Troubleshoot GPU/CUDA setup for deep learning

### When to Use OBSERVABILITY
- Monitor AI agent behavior in real-time
- Trace multi-step reasoning and tool invocations
- Evaluate agent performance using LLM-as-a-Judge
- Track task completion rates and decision quality
- Validate performance against predefined thresholds
- Debug non-deterministic agent behaviors

### When to Use SECURITY
- Test LLM applications for prompt injection vulnerabilities
- Implement input/output guardrails for production systems
- Detect and prevent sensitive data exfiltration
- Evaluate RAG chatbot security and robustness
- Run adversarial testing against local Ollama models
- Assess toxicity and hallucination risks

### When to Use TOOLS
- Integrate production-ready evaluation frameworks (DeepEval, RAGAS)
- Evaluate RAG systems for relevance and groundedness
- Fine-tune and evaluate BERT models for classification
- Deploy evaluation services via REST API
- Run integration tests across multiple frameworks
- Compare optimizer performance (Adam, AdamW, SGD, RMSprop)

## Technologies & Dependencies

### Core Technologies
- **Python**: Primary programming language for all modules
- **PyTorch**: Deep learning framework for model training and evaluation
- **TensorFlow**: Alternative deep learning framework support
- **Docker**: Containerization for isolated and reproducible environments
- **FastAPI**: REST API framework for evaluation services
- **Jupyter**: Interactive notebooks for tutorials and demonstrations

### Machine Learning Libraries
- **Transformers (Hugging Face)**: Pre-trained models and BERT implementations
- **scikit-learn**: Classical machine learning and evaluation metrics
- **NumPy**: Numerical computation and array operations
- **Pandas**: Data manipulation and analysis

### Evaluation Frameworks
- **DeepEval**: LLM-focused evaluation and testing framework
- **RAGAS**: RAG system evaluation and metrics
- **LangChain**: LLM application framework and agent orchestration
- **LangSmith**: LLM application monitoring and debugging
- **LangGraph**: Agent evaluation and workflow management

### Time-Series & Forecasting
- **RNN/LSTM**: Recurrent neural networks for sequential data
- **Optuna**: Hyperparameter optimization framework
- **Matplotlib/Seaborn**: Visualization and plotting

### Security & Testing
- **Ollama**: Local LLM deployment and testing
- **pytest**: Testing framework for unit and integration tests
- **CUDA/cuDNN**: GPU acceleration support

### DevOps & Deployment
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy for production deployments
- **Virtual Environments**: Isolated Python environments (venv, conda)

## References

### BENCHMARKING Resources
- [Open-source Benchmarking Tools for LLMs](./BENCHMARKING/README.md) - A guide to LLM benchmarking frameworks
- [SETUP_AND_USAGE Guide](./BENCHMARKING/SETUP_AND_USAGE.md) - Step-by-step installation instructions
- [LLM Benchmark Tutorial](./BENCHMARKING/notebooks/LLM_Benchmark_Tutorial.ipynb) - Interactive Jupyter notebook tutorial
- [Benchmark Runner](./BENCHMARKING/benchmark_runner.py) - Core benchmarking execution engine
- [Enhanced Benchmark Runner](./BENCHMARKING/enhanced_benchmark_runner.py) - Advanced benchmarking features

### METRICS & Time-Series Analysis
- [RNN+LSTM Time-Series Forecasting](./METRICS/README.md) - Complete pipeline for electricity usage forecasting
- [Advanced Evaluation Methods](./METRICS/src/advanced_evaluation.py) - Sophisticated model evaluation techniques
- [GPU/CUDA Setup Guide](./METRICS/GPU_CUDA_DIAGNOSIS.md) - Troubleshooting GPU environments
- [Electricity Forecasting Notebook](./METRICS/src/RNN_LSTM_Electricity_Forecasting.ipynb) - Hands-on LSTM implementation
- [Model Optimization](./METRICS/src/model_optimization.py) - Hyperparameter tuning and optimization
- [Train Models](./METRICS/src/train_models.py) - Model training pipeline
- [Validate Pipeline](./METRICS/src/validate_pipeline.py) - Pipeline validation and testing
- [Weather Service API](./METRICS/src/weather_service.py) - Weather data integration
- [GPU CUDA Diagnostic](./METRICS/src/gpu_cuda_diagnostic.py) - GPU diagnostics and testing

### OBSERVABILITY & Monitoring
- [AI Agent & LLM Observability Guide](./OBSERVABILITY/README.md) - Observability practices
- [Quick Start Guide](./OBSERVABILITY/QUICKSTART.md) - Quick setup and usage instructions
- [Agent Evaluation Framework](./OBSERVABILITY/sources/agent_evaluation.py) - Agent evaluation implementation
- [LLM Judge Evaluator](./OBSERVABILITY/sources/llm_judge_evaluator.py) - LLM-as-a-Judge evaluation
- [Run Evaluation](./OBSERVABILITY/sources/run_evaluation.py) - Evaluation orchestration
- [Check Thresholds](./OBSERVABILITY/sources/check_thresholds.py) - Performance threshold validation
- [Threshold Configuration](./OBSERVABILITY/configs/thresholds.json) - Evaluation threshold settings

### SECURITY & Testing
- [LLM Security Evaluation Guide](./SECURITY/README.md) - Security testing and guardrails documentation
- [Quick Start Guide](./SECURITY/QUICKSTART.md) - Quick security testing setup
- [RAG Chatbot](./SECURITY/src/rag_chatbot.py) - RAG chatbot implementation
- [Injection Tests](./SECURITY/src/injection_tests.py) - Prompt injection testing
- [Guardrails](./SECURITY/src/guardrails.py) - Input/output validation
- [Security Metrics](./SECURITY/src/metrics.py) - Security metrics calculation
- [Ollama Client](./SECURITY/src/ollama_client.py) - Ollama API client
- [Prompt Injection Tests](./SECURITY/tests/test_prompt_injection.py) - Direct injection testing
- [Indirect Injection Tests](./SECURITY/tests/test_indirect_injection.py) - Indirect injection testing
- [Data Exfiltration Tests](./SECURITY/tests/test_data_exfiltration.py) - Data leakage testing
- [Guardrail Tests](./SECURITY/tests/test_guardrails.py) - Guardrail validation

### TOOLS & Frameworks
- [LLM Evaluation Tools Overview](./TOOLS/README.md) - Open-source evaluation frameworks (2026)
- [DeepEval Framework](./TOOLS/evaluation_examples/deepeval_example.py) - Production LLM testing
- [G-Eval Implementation](./TOOLS/evaluation_examples/geval_example.py) - LLM-as-a-Judge evaluation
- [LangSmith Integration](./TOOLS/evaluation_examples/langsmith_example.py) - Advanced LLM monitoring
- [RAGAS Toolkit](./TOOLS/evaluation_examples/ragas_example.py) - RAG system evaluation
- [LLMeBench Example](./TOOLS/evaluation_examples/llmebench_example.py) - LLM benchmarking
- [Evaluation Demo](./TOOLS/evaluation_examples/evaluation_demo.py) - Full evaluation demo
- [Integration Test](./TOOLS/evaluation_examples/integration_test.py) - Integration testing
- [BERT Evaluation Guide](./TOOLS/src/bert_evaluation.py) - BERT model assessment utilities
- [BERT Fine-Tuning](./TOOLS/src/bert_fine_tuning.py) - BERT fine-tuning utilities
- [G-Eval Integration](./TOOLS/src/geval_integration.py) - G-Eval integration
- [Modern Optimizers Guide](./TOOLS/modern_optimizers_guide.py) - Optimizer implementations
- [Evaluation API](./TOOLS/api.py) - REST API for evaluation services

### External References
- [Confident AI DeepEval](https://github.com/confident-ai/deepeval) - Open-source LLM evaluation framework
- [G-Eval Paper](https://github.com/nlpyang/geval) - Chain-of-thought based LLM evaluation
- [LangSmith Documentation](https://docs.langchain.com/langsmith/) - LLM application monitoring
- [RAGAS Framework](https://github.com/explodinggradients/ragas) - RAG evaluation toolkit
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/) - Pre-trained model library
- [Ollama Documentation](https://ollama.ai/docs) - Local LLM deployment platform
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Agent evaluation framework
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html) - Deep learning framework
- [TensorFlow Documentation](https://www.tensorflow.org/api_docs) - Machine learning platform
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Modern web framework for APIs

## Docker Deployment

All modules support Docker deployment for production environments:

### BENCHMARKING
```bash
cd BENCHMARKING
docker-compose up -d
```

### METRICS
```bash
cd METRICS
docker build -t metrics-api .
docker run -p 8000:8000 metrics-api
```

### OBSERVABILITY
```bash
cd OBSERVABILITY/docker
docker-compose up -d
```

### SECURITY
```bash
cd SECURITY
docker-compose up -d
```

### TOOLS
```bash
cd TOOLS
docker-compose up -d
```

## Contributing

Contributions are welcome to improve evaluation methodologies, add new frameworks, or enhance existing tools. Please refer to the following guidelines:

- [OBSERVABILITY Contributing Guide](./OBSERVABILITY/CONTRIBUTING.md) - Guidelines for observability contributions

### General Contribution Guidelines
1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

## Project Highlights

### Coverage
This repository provides end-to-end AI evaluation solutions, from basic benchmarking to advanced security testing and observability.

### Production-Ready
All modules include Docker support, REST APIs, and documentation for production deployment.

### Open-Source Tools
Leverages industry-standard open-source frameworks (DeepEval, RAGAS, LangChain, Ollama) for reproducible results.

### Multi-Domain Support
Covers LLM evaluation, time-series forecasting, agent monitoring, and security testing in a unified ecosystem.

### Educational Resources
Includes Jupyter notebooks, interactive tutorials, and detailed documentation for learning and experimentation.

---

**Last Updated**: April 2026  
**Maintained by**: IoT & AI Evaluation Team

