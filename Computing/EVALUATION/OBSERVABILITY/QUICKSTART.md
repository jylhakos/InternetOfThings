# Quick Start Guide

Get up and running with AI Agent Observability.

## Prerequisites

- Linux operating system (Ubuntu 20.04+ recommended)
- Python 3.9 or higher
- Git
- (Optional) Docker and Docker Compose for local Langfuse deployment

## Step 1: Setup Virtual Environment

Run the automated setup script:

```bash
# Make script executable (if not already)
chmod +x setup.sh

# Run setup
./setup.sh
```

This will:
- Create a virtual environment in `venv/`
- Install all required Python packages
- Create necessary directories
- Copy `.env.example` to `.env`

## Step 2: Configure Environment Variables

Edit the `.env` file and add your API keys:

```bash
nano .env
```

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key from [platform.openai.com](https://platform.openai.com)
- `LANGFUSE_PUBLIC_KEY` - Get from [cloud.langfuse.com](https://cloud.langfuse.com) or local deployment
- `LANGFUSE_SECRET_KEY` - Get from [cloud.langfuse.com](https://cloud.langfuse.com) or local deployment

**Optional (for cloud deployment):**
- Update `LANGFUSE_HOST` if using cloud Langfuse

## Step 3: (Optional) Deploy Langfuse Locally

If you want to run Langfuse locally instead of using the cloud version:

```bash
cd docker
docker-compose up -d
```

Access Langfuse at: [http://localhost:3000](http://localhost:3000)

Create an account and get your API keys from the settings page.

Update `.env`:
```bash
LANGFUSE_HOST=http://localhost:3000
```

## Step 4: Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## Step 5: Verify Installation

```bash
python sources/test_installation.py
```

This will check:
- Python version
- All dependencies
- Environment variables
- Package versions

## Step 6: Run Your First Agent Evaluation

### Option A: Single Query Example

```bash
python sources/agent_evaluation.py
```

This will:
- Run a LangGraph agent on sample queries
- Send traces to Langfuse
- Display results in terminal

### Option B: Batch Evaluation

```bash
python sources/run_evaluation.py --dataset fallback --num-samples 5
```

This will:
- Run evaluation on 5 test cases
- Calculate accuracy metrics
- Save results to `results/evaluation_report.json`

## Step 7: View Results in Langfuse

Open your Langfuse dashboard:
- **Cloud**: [https://cloud.langfuse.com](https://cloud.langfuse.com)
- **Local**: [http://localhost:3000](http://localhost:3000)

You'll see:
- Detailed traces of agent execution
- Step-by-step reasoning
- Tool calls and responses
- Performance metrics

## Step 8: (Optional) Run LLM-as-a-Judge Evaluation

```bash
python sources/llm_judge_evaluator.py
```

This demonstrates automated quality evaluation using an LLM as a judge.

---

## Common Commands

### Activate Virtual Environment
```bash
source venv/bin/activate
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Run Batch Evaluation
```bash
# Using fallback dataset
python sources/run_evaluation.py --dataset fallback --num-samples 10

# Using HotpotQA dataset from Hugging Face
python sources/run_evaluation.py --dataset hotpot_qa --num-samples 20
```

### Check Quality Thresholds
```bash
python sources/check_thresholds.py \
  --results results/evaluation_report.json \
  --min-accuracy 0.8 \
  --verbose
```

### Using Custom Threshold Config
```bash
python sources/check_thresholds.py \
  --results results/evaluation_report.json \
  --config configs/thresholds.json \
  --verbose
```

---

## Project Structure Overview

```
OBSERVABILITY/
├── README.md              # Comprehensive documentation
├── QUICKSTART.md          # This file
├── setup.sh               # Automated setup script
├── requirements.txt       # Python dependencies
├── .env                   # Your API keys (not in Git)
├── .env.example           # Template for .env
├── .gitignore            # Git ignore rules
│
├── sources/              # Python source code
│   ├── agent_evaluation.py
│   ├── run_evaluation.py
│   ├── check_thresholds.py
│   ├── llm_judge_evaluator.py
│   └── test_installation.py
│
├── configs/              # Configuration files
│   └── thresholds.json
│
├── docker/               # Docker configuration
│   └── docker-compose.yml
│
└── results/              # Evaluation results (auto-generated)
    └── evaluation_report.json
```

---

## Troubleshooting

### Missing API Keys Error

**Problem:** `Error: Missing required environment variables`

**Solution:** 
1. Ensure `.env` file exists
2. Add your API keys to `.env`
3. Make sure keys are valid

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'langfuse'`

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Langfuse Connection Error

**Problem:** Cannot connect to Langfuse

**Solution:**
- **Cloud users**: Check if `LANGFUSE_HOST=https://cloud.langfuse.com`
- **Local users**: Ensure Docker containers are running:
  ```bash
  cd docker
  docker-compose ps
  ```

### Docker Issues

**Problem:** Docker not found or permission denied

**Solution:**
```bash
# Install Docker
sudo apt update
sudo apt install docker.io docker-compose

# Add user to docker group (logout/login required)
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

---

## Next Steps

1. Read the full [README.md](README.md) for comprehensive documentation
2. Explore different evaluation metrics
3. Set up CI/CD with GitHub Actions (see `.github/workflows/evaluation.yml`)
4. Try different LLM models and compare performance
5. Create custom evaluation datasets
6. Experiment with LLM-as-a-Judge evaluators

---

## Useful Links

- **Langfuse Documentation**: [https://langfuse.com/docs](https://langfuse.com/docs)
- **LangChain Documentation**: [https://python.langchain.com/docs](https://python.langchain.com/docs)
- **OpenAI Platform**: [https://platform.openai.com](https://platform.openai.com)
- **Hugging Face Hub**: [https://huggingface.co](https://huggingface.co)

---

## Support

For issues or questions:
1. Check the [README.md](README.md) for detailed documentation
2. Review the troubleshooting section above
3. Check Langfuse documentation
4. Review example code in `sources/` directory

---
