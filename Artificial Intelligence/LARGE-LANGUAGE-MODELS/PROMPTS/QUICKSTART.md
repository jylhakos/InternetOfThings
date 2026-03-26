# Quick Start

## Setup Instructions

### 1. Activate Virtual Environment

**On Linux/macOS:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 2. Verify Installation

```bash
pip list
```

You should see packages like `langchain`, `langchain-community`, `langchain-core`, and `pydantic`.

### 3. Install Ollama (Required for Local LLM)

1. Visit [https://ollama.ai](https://ollama.ai) and download Ollama for your OS
2. Install Ollama
3. Pull a model (e.g., llama2):
   ```bash
   ollama pull llama2
   ```
4. Verify Ollama is running:
   ```bash
   ollama list
   ```

### 4. Run the Example

```bash
python prompt_template_example.py
```

## VS Code Integration

### Select Python Interpreter

1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type: "Python: Select Interpreter"
3. Choose the interpreter from `./venv/bin/python`

### Create VS Code Settings (Optional)

Create `.vscode/settings.json` in the workspace:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black"
}
```

## Troubleshooting

### Ollama Connection Issues

If you get connection errors:
1. Check if Ollama is running: `ollama list`
2. Start Ollama service if needed
3. Verify model is downloaded: `ollama pull llama2`

### Module Not Found Errors

If you get import errors:
1. Ensure virtual environment is activated (you should see `(venv)` in terminal)
2. Reinstall packages: `pip install -r requirements.txt`
3. Verify Python interpreter in VS Code is set to the virtual environment

### Permission Issues

If you get permission errors on Linux:
```bash
chmod +x venv/bin/activate
```

## Additional Models

You can use other models with Ollama:

```bash
# Mistral
ollama pull mistral

# Llama 3
ollama pull llama3

# Code Llama
ollama pull codellama
```

Then update the example code to use the desired model:
```python
llm = Ollama(model="mistral")  # or "llama3", "codellama", etc.
```

## Learning Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
