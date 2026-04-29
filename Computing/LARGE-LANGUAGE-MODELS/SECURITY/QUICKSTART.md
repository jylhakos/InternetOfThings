# Prompt Injection Demo

## Prerequisites Check

Before starting, ensure you have:

- Python 3.8 or higher installed
- Git installed
- Docker installed (optional)
- At least 8GB of free disk space (for LLM models)

## Quick Setup

### 1. Setup Virtual Environment

```bash
# Run the setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
pip install -r requirements.txt
```

### 2. Install Ollama

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Mac:**
```bash
brew install ollama
```

**Windows:**
Download from https://ollama.ai/download

### 3. Start Ollama and Download Model

```bash
# Start Ollama server (in a new terminal)
ollama serve

# Download Llama 2 model (in another terminal)
ollama pull llama2
```

### 4. Run the Demo

```bash
# Activate virtual environment
source venv/bin/activate

# Run demonstration
python src/prompt_injection_demo.py
```

### 5. Run Tests

```bash
# Quick test run
./run_tests.sh

# Or manually
pytest tests/ -v -s
```

## Common Issues and Solutions

### Issue: "Virtual environment not found"
**Solution:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Issue: "Ollama connection refused"
**Solution:**
Ensure Ollama server is running:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Issue: "Model not found"
**Solution:**
```bash
ollama pull llama2
ollama list  # Verify model is downloaded
```

### Issue: "pytest not found"
**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Project Structure Overview

```
SECURITY/
├── README.md              # Full documentation
├── QUICKSTART.md         # This file
├── src/                  # Python source code
│   └── prompt_injection_demo.py
├── tests/                # Test cases
│   └── test_prompt_injection.py
├── setup.sh              # Automated setup
└── run_tests.sh          # Automated testing
```

## What the Demo Shows

The demo demonstrates three main attack types:

1. **Direct Prompt Injection**: User directly sends malicious prompts
2. **Indirect Prompt Injection**: Malicious instructions hidden in external content
3. **Jailbreak Attempts**: Bypassing safety guardrails

## Next Steps

1. Read the full [README.md](README.md) for comprehensive information
2. Explore the source code in `src/prompt_injection_demo.py`
3. Examine test cases in `tests/test_prompt_injection.py`
4. Experiment with your own prompt injection examples

## Docker Alternative

If you prefer using Docker:

```bash
# Start all services
docker-compose up -d

# Download model in container
docker exec -it ollama-server ollama pull llama2

# Run demo
docker exec -it prompt-injection-demo python src/prompt_injection_demo.py

# Run tests
docker exec -it prompt-injection-demo pytest tests/ -v
```

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review test cases for example usage
- Check Ollama documentation: https://ollama.ai
- Check LangChain documentation: https://www.langchain.com

## Safety Reminder

This demo is for educational purposes only. Use responsibly:
- Only test on your own systems
- Never use against production services without authorization
- Understand the ethical implications

---

**Ready to start?** Run `./setup.sh` and follow the prompts!
