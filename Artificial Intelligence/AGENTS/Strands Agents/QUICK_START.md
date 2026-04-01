# Quick Start - Strands Agents

Get started with Strands Agents in 5 minutes!

## Quick Setup (Linux)

### 1. Create and Activate Virtual Environment

```bash
# Navigate to project directory
cd "/home/laptop/EXERCISES/IOT/InternetOfThings/Artificial Intelligence/CODING-AND-DEVELOPMENT/Strands Agents"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install Strands Agents and dependencies
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-west-2)
# - Output format (json)
```

### 4. Enable Bedrock Model Access

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to **Model access** in the left sidebar
3. Click **Manage model access**
4. Select **Anthropic Claude 3.7 Sonnet** (or Claude 3.5 Sonnet)
5. Click **Request model access**
6. Wait for approval (usually instant)

### 5. Test Your Setup

```bash
# Create a simple test
cat > test_agent.py << 'EOF'
from strands import Agent

# Create a simple agent
agent = Agent(
    system_prompt="You are a helpful AI assistant."
)

# Test the agent
print("Testing Strands Agent...")
response = agent("Say hello and confirm that Strands Agents is working!")
print(f"\nAgent Response:\n{response}\n")
print("✅ Success! Strands Agents is working correctly.")
EOF

# Run the test
python test_agent.py
```

## Run Your First Example

### Weather Forecaster

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the weather forecaster
python examples/weather_forecaster.py

# Try asking:
# - What's the weather like in Seattle?
# - Will it rain tomorrow in Miami?
```

## 🔧 VS Code Integration

### 1. Select Python Interpreter

1. Open VS Code in project directory: `code .`
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type: **"Python: Select Interpreter"**
4. Select: `./venv/bin/python`

### 2. Configure Terminal to Auto-Activate

Add to `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true
}
```

### 3. Run Examples from VS Code

- Open any `.py` file
- Click the **Run** button (▶️) in the top right
- Or press `F5` to debug

## Environment Variables (Optional)

For examples requiring additional APIs:

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env

# Add your tokens:
# GITHUB_TOKEN=your_github_token
# ANTHROPIC_API_KEY=your_anthropic_key (if not using Bedrock)
```

## ⚡ Automated Setup

Use the setup script for one-command installation:

```bash
# Make executable
chmod +x scripts/setup_env.sh

# Run setup
./scripts/setup_env.sh

# Follow the prompts
```

## Troubleshooting

### Common Issues

#### 1. "No module named 'strands'" error

**Solution:**

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. AWS credentials not found

**Solution:**

```bash
# Configure AWS CLI
aws configure

# Verify credentials
aws sts get-caller-identity
```

#### 3. Bedrock model access denied

**Solution:**

- Go to [Bedrock Console](https://console.aws.amazon.com/bedrock/)
- Request model access for Claude models
- Wait a few minutes for approval

#### 4. "Region not supported" error

**Solution:**

```bash
# Use a region with Bedrock support (e.g., us-west-2)
export AWS_REGION=us-west-2

# Or update AWS config
aws configure set region us-west-2
```

## Build Your Own Agent (Template)

```python
from strands import Agent
from strands_tools import http_request

# Define what your agent should do
SYSTEM_PROMPT = """
You are a [YOUR AGENT DESCRIPTION].

You can:
1. [CAPABILITY 1]
2. [CAPABILITY 2]
3. [CAPABILITY 3]

[ADDITIONAL INSTRUCTIONS]
"""

# Create agent with tools
my_agent = Agent(
    system_prompt=SYSTEM_PROMPT,
    tools=[http_request]  # Add tools as needed
)

# Use your agent
def main():
    user_query = input("Ask your agent: ")
    response = my_agent(user_query)
    print(f"\nAgent: {response}\n")

if __name__ == "__main__":
    main()
```

## Resources

- **Documentation**: https://strandsagents.com/
- **Examples**: https://strandsagents.com/docs/examples/
- **API Reference**: https://strandsagents.com/docs/api/python/
- **GitHub**: https://github.com/strands-agents

---

**Need help?** Check the [README.md](README.md) or [GitHub](https://github.com/strands-agents).
