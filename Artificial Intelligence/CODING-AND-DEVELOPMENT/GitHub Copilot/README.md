# GitHub Copilot

GitHub Copilot is an AI coding assistant developed by GitHub and OpenAI that enhances your development workflow with intelligent code suggestions and chat-based assistance.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step-by-Step Setup](#step-by-step-setup)
  - [1. Open VS Code and Navigate to Extensions](#1-open-vs-code-and-navigate-to-extensions)
  - [2. Install the GitHub Copilot Extension](#2-install-the-github-copilot-extension)
  - [3. Authenticate Your GitHub Account](#3-authenticate-your-github-account)
  - [4. Verify the Setup](#4-verify-the-setup)
- [Using GitHub Copilot](#using-github-copilot)
  - [Chat](#chat)
  - [Agents](#agents)
- [Configuration Settings](#configuration-settings)
  - [Core Settings](#core-settings)
  - [Settings Configuration (JSON)](#settings-configuration-json)
- [Using Python Virtual Environments](#using-python-virtual-environments)
  - [Create a Virtual Environment](#create-a-virtual-environment)
  - [Activate the Virtual Environment](#activate-the-virtual-environment)
  - [Select the Interpreter in VS Code](#select-the-interpreter-in-vs-code)
  - [Install Dependencies](#install-dependencies)
- [Customizing Copilot Behavior](#customizing-copilot-behavior)
- [Troubleshooting](#troubleshooting)
  - [GitHub Copilot Stops Working](#github-copilot-stops-working)
  - [Status Bar Icon Issues](#status-bar-icon-issues)
  - [Authentication Problems](#authentication-problems)
  - [Linux (Ubuntu) Specific Issues](#linux-ubuntu-specific-issues)
- [OpenClaw vs GitHub Copilot](#openclaw-vs-github-copilot)
- [Useful Resources](#useful-resources)

## Overview

GitHub Copilot provides several key features:

- **Code Completions**: Auto-complete-style suggestions for single lines or entire functions as you type, or based on natural language comments describing desired functionality.

- **Chat Assistance**: Interact with a chat interface within your IDE or on GitHub.com to troubleshoot bugs, craft new features, or ask general coding questions.

- **Code Explanation and Refactoring**: Explain existing code snippets or suggest ways to refactor and simplify code without switching context to an external application.

- **Agents**: Advanced agent mode allows for more autonomous actions, such as automatically generating draft pull requests, creating commits, and performing code analysis based on assigned issues.

## Prerequisites

Before setting up GitHub Copilot, ensure you have:

- **Visual Studio Code** installed on your machine (Linux, Windows, or macOS)
- An **active GitHub account** with a GitHub Copilot plan

## Step-by-Step Setup

### 1. Open VS Code and Navigate to Extensions

- Launch Visual Studio Code
- Click on the **Extensions** icon in the Activity Bar on the side (it looks like four squares) or press `Ctrl+Shift+X`

### 2. Install the GitHub Copilot Extension

- In the Extensions search bar, type **GitHub Copilot**
- Locate the official **GitHub Copilot** and **GitHub Copilot Chat** extensions (installing one usually installs both)
- Click the **Install** button for the GitHub Copilot extension

### 3. Authenticate Your GitHub Account

- After installation, a prompt will typically appear in the bottom-right corner or the Status Bar asking you to sign in to GitHub
- Click on **Sign in to use Copilot** or hover over the Copilot icon in the Status Bar and select **Use AI Features**
- Your default web browser will open to a GitHub login page
- Follow the prompts to sign in to your GitHub account. GitHub will request the necessary permissions for Visual Studio Code
- Click **Authorize Visual-Studio-Code** or **Authorize GitHub Copilot Plugin** to approve the permissions

### 4. Verify the Setup

Once authorized, you will be redirected back to VS Code, and the Copilot icon in the bottom-right status bar should be highlighted, indicating it is active and ready to use.

## Using GitHub Copilot

### Chat

Open the Chat view (`Ctrl+Alt+I`) to interact with the AI using natural language prompts, ask questions, or generate code snippets.

### Agents

For more complex tasks, use Copilot agents via the Chat view to plan and implement features across multiple files.

## Configuration Settings

Once installed and authenticated, GitHub Copilot's core features are enabled by default. You can manage its behavior in the VS Code Settings:

- Navigate to **File > Preferences > Settings** (or **Code > Preferences > Settings** on Mac)
- Or press `Ctrl+,` (Windows/Linux) or `Cmd+,` (Mac)

### Core Settings

- **`github.copilot.enable`**: Controls whether inline suggestions are enabled for specific languages. The default is `{"*": true, ...}` (enabled for most languages).

- **`editor.inlineSuggest.enabled`**: General VS Code setting for inline suggestions. Ensure it is not disabled, as Copilot uses this functionality to display its "ghost text" suggestions.

- **`editor.inlineSuggest.showToolbar`**: Set this to `"onHover"` or `"always"` to control the visibility of the toolbar used to accept or navigate suggestions.

- **`editor.autoClosingQuotes`** and **`editor.autoClosingBrackets`**: Some users find that disabling auto-closing quotes/brackets improves the flow of Copilot suggestions, as you don't need to manually delete the auto-inserted closing character to see the suggestion.

- **`chat.disableAIFeatures`**: Can be used to disable all built-in AI features. Should be set to `false` (default) if you want to use Copilot in that workspace.

### Settings Configuration (JSON)

You can also edit settings directly in JSON format. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) and type **Preferences: Open User Settings (JSON)**:

```json
{
  "github.copilot.enable": {
    "*": true,
    "yaml": false,
    "plaintext": false,
    "markdown": false
  },
  "editor.inlineSuggest.enabled": true,
  "editor.inlineSuggest.showToolbar": "onHover",
  "chat.disableAIFeatures": false
}
```

## Using Python Virtual Environments

VS Code integrates seamlessly with virtual environments without requiring special Copilot settings. Copilot automatically analyzes the active project's files and dependencies.

### Create a Virtual Environment

1. Open your project folder in VS Code
2. Open the Integrated Terminal (`Ctrl+` `` `)
3. Run the appropriate command to create a virtual environment:
   ```bash
   # For Python 3
   python3 -m venv venv
   
   # Or simply
   python -m venv venv
   ```

### Activate the Virtual Environment

In the terminal, run the activation command for your operating system:

**Linux/Ubuntu and macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
.\venv\Scripts\activate
```

### Select the Interpreter in VS Code

VS Code should automatically detect your new environment. If not:

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type **Python: Select Interpreter**
3. Choose the Python executable inside your `venv` folder

### Install Dependencies

With the environment active, install necessary packages:

```bash
pip install -r requirements.txt
```

## Customizing Copilot Behavior

You can further customize how Copilot behaves:

1. Go to **File > Preferences > Settings** (or the gear icon in the bottom-left)
2. Search for **GitHub Copilot** to view available settings
3. **Enable/Disable for Languages**: You can enable or disable inline suggestions for specific languages (e.g., set `github.copilot.enable` to `false` for Markdown files)
4. **Add Context**: For better suggestions, you can create a `.github/copilot-instructions.md` file in your project root to provide specific guidelines
5. **Use Chat Commands**: Use the Copilot Chat view to interact with the AI:
   - `/explain` - Ask for explanations
   - `/init` - Set up your project
   - Use `#` mentions to reference specific files or symbols

## Troubleshooting

### GitHub Copilot Stops Working

If GitHub Copilot suddenly stops providing suggestions:

1. **Check the Status Bar Icon**:
   - Look for the Copilot icon in the bottom-right corner of VS Code
   - If it shows an error or warning, click on it for more details

2. **Restart the Copilot Service**:
   - Open Command Palette (`Ctrl+Shift+P`)
   - Type and select **Developer: Reload Window**
   - Or type **GitHub Copilot: Restart**

3. **Re-authenticate**:
   - Open Command Palette (`Ctrl+Shift+P`)
   - Type **GitHub Copilot: Sign Out**
   - Then sign in again by clicking the Copilot icon

4. **Check Your Subscription**:
   - Ensure your GitHub Copilot subscription is active
   - Visit [GitHub Settings](https://github.com/settings/copilot) to verify

5. **Update the Extension**:
   - Go to Extensions (`Ctrl+Shift+X`)
   - Check if GitHub Copilot has updates available
   - Click **Update** if needed

6. **Check Network Connection**:
   - Copilot requires an active internet connection
   - Verify your firewall or proxy settings aren't blocking GitHub services

### Status Bar Icon Issues

If the Copilot icon is missing or inactive:

- Ensure the extension is installed and enabled
- Check if `chat.disableAIFeatures` is set to `true` in settings (should be `false`)
- Restart VS Code

### Authentication Problems

If you encounter authentication issues:

- Clear your GitHub credentials and re-authenticate
- On Linux, you may need to check your keyring settings
- Try signing in through GitHub.com first, then authorize VS Code

### Linux (Ubuntu) Specific Issues

**Keyring Issues:**
If you encounter authentication issues on Ubuntu:

```bash
# Install gnome-keyring if not already installed
sudo apt-get install gnome-keyring

# Or use pass as an alternative credential manager
sudo apt-get install pass
```

**Permission Issues:**
Ensure VS Code has proper permissions:

```bash
# If installed via snap
sudo snap connect code:password-manager-service

# Check VS Code can access the network
ls -la ~/.config/Code/
```

**Extension Installation Issues:**
If extensions fail to install:

```bash
# Clear extension cache
rm -rf ~/.vscode/extensions/github.copilot*

# Reinstall from terminal
code --install-extension GitHub.copilot
```

## OpenClaw vs GitHub Copilot

**OpenClaw** is a self-hosted autonomous AI agent designed for full-task delegation, whereas **GitHub Copilot** is a proprietary, cloud-based coding companion integrated into IDEs to speed up code completion and chatting.

**Use GitHub Copilot:**
- For fast autocomplete and inline suggestions
- Chat-based help directly in the editor
- Zero-config setup with seamless IDE integration
- When you need instant code completions and explanations

**Use OpenClaw:**
- For complex tasks requiring full autonomy
- Autonomous file manipulation and multi-step workflows
- When data privacy and self-hosting are priorities
- For flexibility with different AI models
- When you need full control over the AI agent's behavior

For more details, visit [OpenClaw Documentation](https://docs.openclaw.ai/providers/github-copilot).

## Useful Resources

- [Set up GitHub Copilot in VS Code](https://code.visualstudio.com/docs/copilot/setup)
- [GitHub Copilot Features](https://github.com/features/copilot)
- [Installing the GitHub Copilot Extension](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-extension)
- [Get Started with GitHub Copilot Completions](https://learn.microsoft.com/en-us/visualstudio/ide/visual-studio-github-copilot-extension?view=visualstudio)

---
