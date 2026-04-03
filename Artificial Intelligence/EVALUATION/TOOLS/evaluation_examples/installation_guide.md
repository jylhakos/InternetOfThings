# LLM Evaluation Tools Installation Guide

## 🛠️ Quick Installation

### Core Dependencies
```bash
# Basic evaluation tools (always recommended)
pip install bert-score rouge-score sacrebleu

# Scientific computing
pip install numpy pandas matplotlib scikit-learn
```

### Framework-Specific Installation

#### 1. 🔧 DeepEval
```bash
pip install deepeval
```

#### 2. 🧠 G-Eval 
```bash
pip install openai
export OPENAI_API_KEY="your-api-key-here"
```

#### 3. 🏆 LLMeBench
```bash
git clone https://github.com/qcri/LLMeBench.git
cd LLMeBench
pip install -r requirements.txt
pip install -e .
```

#### 4. 🔍 LangSmith
```bash
pip install langsmith
export LANGCHAIN_API_KEY="your-api-key-here"
```

#### 5. 📊 Ragas
```bash
pip install ragas datasets
```

## 🚀 AWS Deployment

### Prerequisites
```bash
pip install boto3 awscli
aws configure
```

### Deploy All Tools
```bash
bash evaluation_examples/deploy_deepeval_aws.sh
bash evaluation_examples/deploy_geval_aws.sh
bash evaluation_examples/deploy_llmebench_aws.sh
bash evaluation_examples/deploy_langsmith_aws.sh
bash evaluation_examples/deploy_ragas_aws.sh
```

## 🎯 Usage Examples

### Run Individual Tools
```bash
python evaluation_examples/deepeval_example.py
python evaluation_examples/geval_example.py
python evaluation_examples/llmebench_example.py
python evaluation_examples/langsmith_example.py
python evaluation_examples/ragas_example.py
```

### Run Comprehensive Evaluation
```bash
python evaluation_examples/evaluation_demo.py
```

## 📚 Documentation Links

- 🔧 DeepEval: https://deepeval.com/docs/metrics-llm-evals
- 🧠 G-Eval: https://github.com/nlpyang/geval  
- 🏆 LLMeBench: https://github.com/qcri/LLMeBench
- 🔍 LangSmith: https://docs.smith.langchain.com/evaluation
- 📊 Ragas: https://docs.ragas.io/en/stable/

## ⚠️ API Keys Required

- OpenAI API Key for G-Eval: https://platform.openai.com/api-keys
- LangChain API Key for LangSmith: https://www.langchain.com/langsmith

