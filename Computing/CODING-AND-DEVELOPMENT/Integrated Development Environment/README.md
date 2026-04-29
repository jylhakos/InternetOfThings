# Integrated Development Environment (IDE)

This document outlines the steps required to set up Python environments, configure GitHub Copilot coding agents, and leverage artificial intelligence features in Visual Studio Code (VS Code).

## Table of Contents

- [A. Python Environments in VS Code](#a-python-environments-in-vs-code)
- [B. GitHub Copilot Coding Agent](#b-github-copilot-coding-agent)
- [C. Copilot CLI Sessions](#c-copilot-cli-sessions)
- [D. Use MCP Servers](#d-use-mcp-servers)
- [E. How to Know if Virtual Environment is Working](#e-how-to-know-if-virtual-environment-is-working)
- [F. Use Tools with Agents](#f-use-tools-with-agents)
- [G. Remote Development](#g-remote-development)
- [H. Monitor Agent Usage with OpenTelemetry](#h-monitor-agent-usage-with-opentelemetry)
- [I. Troubleshooting: Virtual Environment Issues](#i-troubleshooting-virtual-environment-issues)
- [J. Debugging Agents in VS Code](#j-debugging-agents-in-vs-code)
- [K. Building Python-Based AI Coding Agents](#k-building-python-based-ai-coding-agents)
- [L. Tutorial: Work with Agents](#l-tutorial-work-with-agents)

---

## A. Python Environments in VS Code

### Python Extension for Visual Studio Code

The Python extension and Python Environments extension bring environment and package management into Visual Studio Code's UI.

**Documentation**: [Python environments in VS Code](https://code.visualstudio.com/docs/python/environments)

### Prerequisites

Install the Python Environments extension: [ms-python.vscode-python-envs](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs)

The extension automatically discovers your Python environments and uses them when running code.

### Configuration

Enable the Python Environments extension in your `settings.json`:

```json
{
  "python.useEnvironmentsExtension": true,
  "python-envs.terminal.autoActivationType": "shellStartup"
}
```

### Use Active pyenv Python Interpreter (Virtual Environment)

Create or edit `.vscode/settings.json` file with a terminal profile:

**Example Configuration:**

```json
{
  // Core Python interpreter selection (works for Run/Debug & language server)
  "python.defaultInterpreterPath": "/home/andrew/miniforge3/envs/myenv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.terminal.activateEnvInCurrentTerminal": true,
  "python.condaPath": "/home/andrew/miniforge3/bin/conda",
  "terminal.integrated.inheritEnv": true,

  // Prevent auto base activation racing with our profile
  "python.condaAutoActivateBase": false,

  // Terminal profile: launch zsh, suppress base, activate myenv once, stay in same shell
  "terminal.integrated.profiles.linux": {
    "zsh-myenv": {
      "path": "/usr/bin/zsh",
      "args": [
        "-i",
        "-c",
        "export CONDA_AUTO_ACTIVATE_BASE=false; source /home/andrew/miniforge3/etc/profile.d/conda.sh 2>/dev/null || true; conda activate myenv 2>/dev/null || echo '[myenv profile] activation failed'; exec zsh -i"
      ]
    }
  },
  "terminal.integrated.defaultProfile.linux": "zsh-myenv"
}
```

### Environment Discovery

The extension searches your workspace for virtual environments using customizable glob patterns.

**Default Search Pattern**: `./**/.venv` (finds any folder named `.venv` anywhere in your workspace)

**Custom Search Paths**:

```json
{
  "python-envs.workspaceSearchPaths": [
    "./**/.venv",
    "./envs/**",
    "./my-custom-env"
  ]
}
```

**Global Search Paths** (for environments outside your workspace):

```json
{
  "python-envs.globalSearchPaths": ["/Users/yourname/envs", "/opt/shared-envs"]
}
```

**Tips**:

- Use `**` for recursive searches (e.g., `./**/env` finds any folder named `env` at any depth)
- Relative paths resolve from your workspace folder root

### Selecting an Environment

1. **Status Bar**: Click the Python version shown at the bottom of the window
2. **Command Palette**: Run `Python: Select Interpreter` and choose from the list

The selected environment is used for running code and debugging.

### View Discovered Environments

All discovered environments appear in a unified list when selecting an interpreter. The Environment Managers view groups environments by type.

**Troubleshooting**: [View discovered environments](https://code.visualstudio.com/docs/python/environments#_view-discovered-environments)

---

## B. GitHub Copilot Coding Agent

### Overview

GitHub Copilot coding agent is a GitHub-hosted, autonomous AI developer that works independently in the background to complete development tasks. The agent can implement features, fix bugs, and make changes across your repository using its own isolated development environment.

### Key Resources

- **[GitHub Copilot coding agent in VS Code](https://code.visualstudio.com/docs/copilot/copilot-coding-agent)** - Official VS Code documentation
- **[About GitHub Copilot coding agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)** - GitHub documentation
- **[Introducing GitHub Copilot agent mode](https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode)** - VS Code blog announcement
- **[Get started with GitHub Copilot agent mode](https://learn.microsoft.com/en-us/visualstudio/ide/copilot-agent-mode?view=visualstudio)** - Microsoft Learn tutorial

### How It Works

With GitHub Copilot agent mode in Visual Studio, you can use natural language to specify a high-level task. The AI:

1. Creates a plan
2. Makes code edits
3. Runs terminal commands
4. Invokes tools
5. Applies changes across your codebase
6. Monitors outcomes (build results, unit-test failures, tool outputs)
7. Iterates as needed

Unlike ask mode, **agent mode doesn't stop after a single response**. It continues running and refining steps until you reach the goal in your prompt or more input is required.

### Using Agent Mode

In agent mode, Copilot operates autonomously and determines the relevant context for your prompt.

**To invoke the coding agent**:

- Assign a GitHub issue to Copilot, or
- Delegate a task from chat

### Difference from VS Code Agents

This is different from using agents in VS Code, which provide interactive development within the editor and require your active participation during the coding session.

### Settings Reference

**[GitHub Copilot in VS Code settings reference](https://code.visualstudio.com/docs/copilot/reference/copilot-settings)**

**User and workspace settings**: [Configure settings](https://code.visualstudio.com/docs/configure/settings)

User settings are your personal settings for customizing VS Code.

**VS Code Web**: [https://vscode.dev/](https://vscode.dev/)

---

## C. Copilot CLI Sessions

### Overview

Copilot CLI sessions bring the power of GitHub Copilot to your command-line interface, enabling natural language interactions with your terminal.

### Documentation

**[Copilot CLI sessions in Visual Studio Code](https://code.visualstudio.com/docs/copilot/agents/copilot-cli)**

The Copilot CLI integration allows you to:

- Get command suggestions in natural language
- Explain complex commands
- Debug command-line errors
- Generate shell scripts

---

## D. Use MCP Servers

### What is MCP?

**Model Context Protocol (MCP)** is an open standard that enables AI models to interact with external tools and services through a unified interface.

### Documentation

**[Use MCP servers](https://learn.microsoft.com/en-us/visualstudio/ide/mcp-servers?view=visualstudio)**

### How MCP Works

In Visual Studio, MCP support enhances GitHub Copilot agent mode by allowing you to connect any MCP-compatible server to your agentic coding workflow.

**Architecture**:

- **MCP clients** (such as Visual Studio) connect to MCP servers
- **MCP servers** provide tools and services that the AI can use
- The **MCP protocol** defines the message format for communication, including:
  - Tool discovery
  - Invocation
  - Response handling

### Agent Mode Tools

Agent mode can use Model Context Protocol (MCP) tools for responding to requests. This enables the agent to:

- Access external databases
- Call APIs
- Execute specialized operations
- Interact with third-party services

---

## E. How to Know if Virtual Environment is Working

### Quick Check

If you are using venv, the Status Bar in VS Code will show the path to the Python executable inside the venv.

### Activation Commands

**Linux/macOS**:

```bash
source .venv/bin/activate
```

**Absolute path example**:

```bash
source ~/example_folder/.venv/bin/activate
```

**Windows**:

```powershell
.venv\Scripts\activate
```

### AI Agent Monitoring Methods

AI agents can monitor whether a Python virtual environment is active by checking environment variables or the Python interpreter path. **Relying solely on the terminal prompt is not always reliable.**

By focusing on programmatic checks of environment variables and configuration settings, AI agents can reliably determine the virtual environment status, which is more robust than parsing potentially inconsistent terminal prompts.

### Monitoring Methods for AI Agents

#### Method 1: Check the VIRTUAL_ENV Environment Variable

When a virtual environment is active, the `VIRTUAL_ENV` environment variable is set to the environment's directory path.

**In a Python script**:

```python
import os
env_path = os.environ.get('VIRTUAL_ENV')
if env_path:
    print(f"Virtual environment active: {env_path}")
else:
    print("No virtual environment is currently active.")
```

**In the terminal**:

- Unix/macOS: `echo $VIRTUAL_ENV`
- Windows CMD: `echo %VIRTUAL_ENV%`
- Windows PowerShell: `echo $env:VIRTUAL_ENV`

Check if the output is a non-empty path.

#### Method 2: Compare sys.prefix and sys.base_prefix

This is considered a **reliable method** within a running Python script. If the current Python interpreter is running from a virtual environment, `sys.prefix` and `sys.base_prefix` will be different.

**In a Python script**:

```python
import sys
if sys.prefix != sys.base_prefix:
    print(f"Inside a virtual environment: {sys.prefix}")
else:
    print("Not in a virtual environment (using base Python).")
```

#### Method 3: Check the Python Executable Path

Run a command in the terminal to determine the path of the currently used Python executable.

**In the terminal**:

- Unix/macOS: `which python`
- Windows PowerShell: `Get-Command python`

Parse the output to see if the path includes a known virtual environment folder name (e.g., `.venv` or `env`).

### VS Code Integration for AI Agents

For agents operating within the VS Code environment (e.g., as a workspace extension), the most effective approach is to leverage VS Code's settings and APIs:

1. **Monitor the Status Bar**: The VS Code Python extension displays the name of the selected interpreter in the bottom right of the Status Bar
2. **Use the `python.defaultInterpreterPath` setting**: Read the workspace or folder `settings.json` file to identify the configured interpreter path
3. **Utilize the `onDidOpenTerminal` API**: Extension-based agents can use the VS Code API to be notified when a new terminal is opened and monitor terminal output for activation messages

---

## F. Use Tools with Agents

### Overview

Agents in VS Code can use various tools to accomplish tasks more effectively.

### Documentation

**[Use tools with agents](https://code.visualstudio.com/docs/copilot/agents/agent-tools)**

### Types of Tools

Agents can leverage:

- File system operations
- Terminal commands
- Language servers
- Build tools
- Testing frameworks
- MCP servers (external tools via Model Context Protocol)

### Tool Discovery and Invocation

The agent automatically discovers available tools and determines which ones are appropriate for the task at hand. It can:

- Invoke multiple tools in sequence
- Chain tool outputs
- Handle tool failures gracefully
- Request user confirmation for sensitive operations

---

## G. Remote Development

### What is Remote Development?

VS Code Remote Development allows you to use a container, remote machine, or the Windows Subsystem for Linux (WSL) as a full-featured development environment.

### Documentation

- **[VS Code Remote Development Overview](https://code.visualstudio.com/docs/remote/remote-overview)**
- **[Enhance productivity with AI + Remote Dev](https://code.visualstudio.com/blogs/2025/05/27/ai-and-remote)**

### AI-Powered Remote Development

Use chat to set up and troubleshoot your remote environment. GitHub Copilot can:

- Help configure remote connections
- Debug connection issues
- Set up development containers
- Optimize remote workflows

### Benefits

- Develop in the same OS as deployment
- Use specialized hardware or larger machines
- Separate development environments
- Keep source code secure on remote machines
- Access existing development environments from anywhere

---

## H. Monitor Agent Usage with OpenTelemetry

### Overview

Monitor your AI agent usage and performance using OpenTelemetry, the vendor-neutral open standard for observability.

### Documentation

**[Monitor agent usage with OpenTelemetry](https://code.visualstudio.com/docs/copilot/guides/monitoring-agents)**

### What is OpenTelemetry?

**OpenTelemetry (OTel)** is a vendor-neutral open source observability framework for instrumenting, generating, collecting, and exporting telemetry data such as:

- Traces
- Metrics
- Logs

**Resources**:

- **[The open standard for telemetry](https://opentelemetry.io/)**
- **[OpenTelemetry Documentation](https://opentelemetry.io/docs/)**

### Monitoring Capabilities

Track:

- Agent invocations
- Response times
- Success/failure rates
- Resource usage
- Tool invocations
- Context size

### Key Considerations

The monitoring tools focus on **Copilot interactions themselves**, not the specific virtual environment in which they occur. A key challenge is ensuring the agent uses the correct virtual environment in the first place.

Monitoring Copilot and Agent mode usage in a VS Code virtual environment can be done using:

- **Built-in VS Code features** for individual metrics
- **GitHub's organization/enterprise-level analytics** for detailed reporting

The virtual environment itself does not have a dedicated monitoring feature within Copilot's integration, but the usage is captured through the IDE's telemetry.

---

## I. Troubleshooting: Virtual Environment Issues

### Problem: Copilot Agent Mode Ignores Activated Python Virtual Environment

GitHub Copilot Agent Mode in VS Code **does not have a direct, built-in setting** to select a preferred interpreter or automatically activate a virtual environment (venv).

### Why This Happens

Agent Mode operates by launching fresh, non-interactive terminal sessions that often do not inherit:

- The active terminal's state
- The Python extension's auto-activation behavior

This means it often defaults to the **system Python** rather than the venv chosen in VS Code.

### Workarounds to Make Agent Mode Use venv

#### 1. Manual Activation

Before giving complex tasks, open the integrated terminal and run the activation script:

- Linux/macOS: `source .venv/bin/activate`
- Windows: `.venv\Scripts\Activate.ps1`

Once active, subsequent Agent terminal commands usually inherit this state.

#### 2. Explicit Initial Command

Start your prompt by explicitly telling the agent to activate the environment:

```
"Using the .venv in this folder, run [task]"
```

#### 3. VS Code Settings Fix

Explicitly configure the Python path in your `.vscode/settings.json` file:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false
}
```

### Copilot Agent Has No Access to uv

**Problem**: Copilot Agent always opens its own terminal and does not have access to `uv`. Copilot Agent has no access to run code through `uv run python main.py`.

**Root Cause**: Copilot Agent launches a **non-interactive zsh shell** by default.

#### Solution: Configure PATH in VS Code Settings

Use the `terminal.integrated.env.<platform>` setting to append custom directories to the PATH environment variable specifically for the integrated terminal.

**Linux/macOS**:

```json
{
  "terminal.integrated.env.osx": {
    "PATH": "/path/to/uv/bin:${env:PATH}"
  },
  "terminal.integrated.env.linux": {
    "PATH": "/path/to/uv/bin:${env:PATH}"
  }
}
```

**Windows**:

```json
{
  "terminal.integrated.env.windows": {
    "PATH": "C:\\path\\to\\uv\\bin;${env:PATH}"
  }
}
```

Replace `/path/to/uv/bin` with the actual directory containing the `uv` executable.

**Restart VS Code** or reload the terminal for changes to take effect.

#### Python Extension Settings

For managing Python virtual environments, the Python extension for VS Code automatically handles activation in most cases:

1. Use `Python: Select Interpreter` from the Command Palette (Ctrl+Shift+P)
2. Ensure this setting in `settings.json`:

```json
{
  "python.terminal.activateEnvironment": true
}
```

#### Workaround: Launch from Activated Environment

```bash
# Navigate to your workspace
cd <your workspace>

# Activate your venv (example for Unix-like shells)
. venv/bin/activate

# Launch VS Code from the activated environment
code .
```

### Activate uv venv Automatically

If you're using **uv** to manage virtual environments:

```bash
uv venv
source .venv/bin/activate
```

**Auto-activation on terminal launch**: Add this snippet to your `.bashrc` or `.zshrc`:

```bash
if [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
fi
```

---

## J. Debugging Agents in VS Code

### Overview

Debugging agents requires understanding their execution flow, tool invocations, and decision-making process.

### Best Practices

1. **Enable verbose logging**: Configure your agent to output detailed logs
2. **Track tool invocations**: Monitor which tools the agent calls and in what order
3. **Inspect prompts and responses**: Review the context provided to the agent
4. **Use breakpoints in custom agents**: If building custom agents, use standard debugging techniques
5. **Check environment variables**: Ensure the agent has access to required configurations

### Common Issues

- Agent not using the correct Python environment
- Tool invocations failing silently
- Insufficient context for decision-making
- Rate limiting or quota issues
- Network connectivity problems

---

## K. Building Python-Based AI Coding Agents

### Overview

Build custom AI coding agents for VS Code using Anthropic's Claude models via the Python SDK.

### Resources

- **[Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)**
- **[Anthropic Python SDK Examples](https://github.com/anthropics/anthropic-sdk-python/tree/main/examples)**

### Recommended Model

Use models optimized for coding, such as **Anthropic's Claude 3.5 Sonnet**.

### Basic Example

```python
import anthropic

# Initialize the Anthropic client
anthropic_client = anthropic.Anthropic(api_key="your-api-key")

# Create a message request
message = anthropic_client.messages.create(
    model="claude-3-5-sonnet-latest",
    messages=[{
        "role": "user",
        "content": "Please write a Python function that checks if a string is a palindrome."
    }],
    max_tokens=1024
)

print(message.content)
```

### Building an Agent

Key components for a Python-based AI coding agent:

1. **Context gathering**: Read workspace files, analyze code structure
2. **Tool integration**: Execute terminal commands, file operations
3. **State management**: Track progress across multiple interactions
4. **Error handling**: Gracefully handle failures and retry logic
5. **Environment awareness**: Detect and use correct Python environments

### Environment Detection in Agents

Your agent should programmatically check the environment:

```python
import sys
import os

def get_venv_status():
    """Check if running in a virtual environment"""
    in_venv = sys.prefix != sys.base_prefix
    venv_path = os.environ.get('VIRTUAL_ENV', 'Not set')

    return {
        'in_venv': in_venv,
        'venv_path': venv_path,
        'python_path': sys.executable
    }

status = get_venv_status()
print(f"In virtual environment: {status['in_venv']}")
print(f"Virtual environment path: {status['venv_path']}")
print(f"Python executable: {status['python_path']}")
```

---

## L. Tutorial: Work with Agents

### Overview

A tutorial for working with agents in VS Code.

### Documentation

**[Tutorial: Work with agents in VS Code](https://code.visualstudio.com/docs/copilot/agents/agents-tutorial)**

### Example Agent Session with Claude Sonnet 4.5

Here's an example of a conversational agent session in VS Code showing how an AI agent works through a task:

**User Request**: "Set up a Python project with pytest and run tests"

**Agent Response**:

> Let me start by examining the files to understand the structure and requirements.
>
> Tasks:
>
> 1. Activate the virtual environment and install pytest
> 2. Configure VS Code to use this virtual environment
> 3. Run the tests to make sure everything works

**Chat from Copilot**:

> Now I'll create a Python virtual environment.

```bash
python3 -m venv venv
```

> The virtual environment is created.
>
> Now I need to configure VS Code to use this virtual environment.
>
> Then I'll activate the virtual environment.

> Now let me activate the virtual environment, install dependencies, and run the tests:

```bash
source venv/bin/activate && pip install -r requirements.txt
```

> Now let me configure VS Code to use this virtual environment.
>
> I need to create a .vscode folder with a settings.json file to specify the Python interpreter.

```bash
mkdir -p .vscode
```

> Now let me create a settings.json file to configure VS Code to use the virtual environment.

**Creating `.vscode/settings.json`**:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": ["."]
}
```

> Now let me run the main program to see the output, and then run the tests to verify everything works correctly.

```bash
python directory_structure.py
```

> Running tests:

```bash
pytest
```

**Result**: The agent autonomously:

- Created a Python virtual environment
- Configured VS Code settings
- Activated the environment and installed dependencies
- Ran the application and tests
- Verified the complete setup

---

## Additional Resources

### VS Code Documentation

- [Python in Visual Studio Code](https://code.visualstudio.com/docs/python/python-tutorial)
- [GitHub Copilot Overview](https://code.visualstudio.com/docs/copilot/overview)
- [VS Code Terminal](https://code.visualstudio.com/docs/terminal/basics)

### GitHub Copilot

- [GitHub Copilot Documentation](https://docs.github.com/copilot)
- [Copilot Trust Center](https://resources.github.com/copilot-trust-center/)

### Model Context Protocol

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)

### Python Tools

- [uv - Python package manager](https://github.com/astral-sh/uv)
- [pytest Documentation](https://docs.pytest.org/)
- [Python venv Documentation](https://docs.python.org/3/library/venv.html)

---

## Reference

### Example Configuration Files

This repository includes example configuration files:

- **[.vscode/settings.json](.vscode/settings.json)** - Complete VS Code settings for Python development with AI agents
- **[.gitignore](.gitignore)** - A gitignore to exclude binary files and build artifacts

### Essential Settings for Python Environments in VS Code:

```json
{
  "python.useEnvironmentsExtension": true,
  "python-envs.terminal.autoActivationType": "shellStartup",
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "terminal.integrated.inheritEnv": true
}
```

### Check Virtual Environment Status

```bash
# Print virtual environment path (Unix/macOS)
echo $VIRTUAL_ENV

# Print virtual environment path (Windows PowerShell)
echo $env:VIRTUAL_ENV

# Check Python location
which python  # Unix/macOS
Get-Command python  # Windows PowerShell
```

### Activate Virtual Environment

```bash
# Unix/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat
```

---

**Last Updated**: March 29, 2026
