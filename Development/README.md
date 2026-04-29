#  Software Development for the Internet of Things

This repository contains the development environment for IoT, programming language resources, and AI-assisted coding workflows applicable to Internet of Things (IoT) software projects. The content is structured to support both entry-level prototyping and production-grade IoT system development.

---

## Table of Contents

1. [Folder Structure](#1-folder-structure)
2. [Programming Languages Overview](#2-programming-languages-overview)
3. [Virtual Environment Setup (Linux and VS Code)](#3-virtual-environment-setup-linux-and-vs-code)
4. [Vibe Coding Workflow in IoT Software Development](#4-vibe-coding-workflow-in-iot-software-development)
5. [Setting Up the Vibe Coding Environment](#5-setting-up-the-vibe-coding-environment)
6. [Designing the IoT Prompt](#6-designing-the-iot-prompt)
7. [Vibe Coding Examples](#7-vibe-coding-examples)
8. [Executing the Vibe Coding Process](#8-executing-the-vibe-coding-process)
9. [Code Creation: IoT Demo Application](#9-code-creation-iot-demo-application)
10. [Running the Demo Script](#10-running-the-demo-script)
11. [Beyond Vibe Coding: Disciplined AI-Assisted Development](#11-beyond-vibe-coding-disciplined-ai-assisted-development)
12. [References](#12-references)

---

## 1. Folder Structure

The `Development` directory is organized into thematic sub-folders that reflect the principal programming languages and documentation conventions employed across IoT software projects. Each sub-folder is intended to contain source files, configuration artifacts, and associated resources relevant to its designated domain.

```
Development/
├── Python/           # Python-based IoT applications and cloud SDK integrations
│   ├── aws_iot_publisher.py
│   └── requirements.txt
├── C_Cpp/            # C and C++ firmware and embedded system code
├── JavaScript/       # Node.js and JavaScript-based IoT edge and cloud scripts
├── MicroPython/      # MicroPython scripts targeting microcontroller platforms
├── Shell/            # Shell and Bash automation, deployment, and utility scripts
│   └── setup_env.sh
├── Examples/         # Self-contained demonstration projects and reference code
│   └── vibe_iot_demo.py
└── Docs/             # Technical documentation, architecture notes, and guidelines
```

### Sub-folder Descriptions

| Folder         | Purpose                                                                                          |
|----------------|--------------------------------------------------------------------------------------------------|
| `Python/`      | High-level IoT applications, AWS/Azure SDK integrations, data processing pipelines              |
| `C_Cpp/`       | Low-level firmware, real-time operating system (RTOS) code, hardware abstraction layers         |
| `JavaScript/`  | Node.js-based edge computing, MQTT broker clients, REST API consumers                           |
| `MicroPython/` | Lightweight scripts for resource-constrained microcontrollers (ESP32, Raspberry Pi Pico, etc.)  |
| `Shell/`       | Deployment scripts, environment setup, device provisioning automation                           |
| `Examples/`    | Standalone demonstration scripts illustrating specific IoT development patterns                  |
| `Docs/`        | Architecture Decision Records (ADRs), API references, and development guidelines                |

---

## 2. Programming Languages Overview

IoT software development encompasses a spectrum of programming languages, each suited to a different layer of the IoT stack — from firmware running on constrained microcontrollers to cloud-based data pipelines. The following summaries outline the principal characteristics of each language used within this project.

### Python

Python is the dominant high-level language in IoT application development owing to its extensive ecosystem of device SDKs, data processing libraries, and cloud integration packages. Its concise syntax and dynamic type system accelerate prototyping, while frameworks such as the AWS IoT Device SDK for Python and the Azure IoT Hub SDK facilitate secure MQTT-based cloud connectivity. Python is the recommended language for Raspberry Pi applications, edge analytics, and AI/ML inference pipelines.

### C / C++

C and C++ remain the foundational languages for embedded systems and firmware development. C provides direct memory management and low-level hardware access essential for microcontrollers with limited RAM and flash storage. C++ extends this with object-oriented abstractions suitable for more complex firmware architectures. Toolchains such as GCC ARM and frameworks including FreeRTOS, Arduino, and ESP-IDF are standard in this domain.

### JavaScript (Node.js)

Node.js enables event-driven, non-blocking I/O that is well suited to IoT edge gateways where multiple sensor streams must be handled concurrently. The `mqtt.js` and `azure-iot-device` packages provide first-class support for MQTT-based cloud communication. JavaScript is also widely used in web-based IoT dashboards and serverless functions deployed to AWS Lambda or Azure Functions.

### MicroPython

MicroPython is a lean implementation of Python 3 designed to execute on microcontrollers with as little as 16 KB of RAM and 256 KB of flash. It supports platforms such as the ESP32, ESP8266, and Raspberry Pi Pico. MicroPython enables rapid iteration on constrained hardware without requiring a cross-compilation toolchain, making it an effective choice for sensor node prototyping and educational IoT projects.

### Shell (Bash)

Shell scripting is integral to the operational layer of IoT development. Bash scripts automate device provisioning, certificate deployment, environment initialization, over-the-air (OTA) update pipelines, and continuous integration workflows. On Linux-based IoT gateways and single-board computers such as the Raspberry Pi, shell scripting remains indispensable for system-level configuration and task scheduling via `cron`.

---

## 3. Virtual Environment Setup (Linux and VS Code)

A Python virtual environment isolates project dependencies from the system-wide Python installation, preventing version conflicts across different IoT projects. The following instructions describe the complete setup process for a Linux system using both the terminal and Visual Studio Code.

### Prerequisites

- Linux operating system (Ubuntu, Debian, or a Raspberry Pi OS-based distribution)
- Python 3.8 or later installed (`python3 --version`)
- `pip` package manager (`pip3 --version`)
- Visual Studio Code with the **Python** extension installed (identifier: `ms-python.python`)

### Step-by-Step Instructions

#### Step 1: Open the Terminal

Open a terminal in VS Code by navigating to **Terminal > New Terminal** (keyboard shortcut: `` Ctrl+` ``), or use the system terminal application.

#### Step 2: Navigate to the Project Directory

```bash
cd /home/laptop/EXERCISES/IOT/InternetOfThings/Development
```

#### Step 3: Install `venv` (if not already available)

On Debian-based systems, the `venv` module may require explicit installation:

```bash
sudo apt update && sudo apt install python3-venv -y
```

#### Step 4: Create the Virtual Environment

```bash
python3 -m venv .venv
```

This command creates a `.venv` directory within the project folder containing an isolated Python interpreter and `pip` installation.

#### Step 5: Activate the Virtual Environment

```bash
source .venv/bin/activate
```

Upon successful activation, the terminal prompt will be prefixed with `(.venv)`, confirming the environment is active.

#### Step 6: Upgrade `pip` Within the Virtual Environment

```bash
pip install --upgrade pip
```

#### Step 7: Install Project Dependencies

For the IoT demo script, install the required AWS IoT SDK:

```bash
pip install AWSIoTPythonSDK
```

For a broader IoT development environment, a representative set of packages includes:

```bash
pip install AWSIoTPythonSDK azure-iot-device paho-mqtt RPi.GPIO Adafruit-DHT boto3
```

#### Step 8: Select the Virtual Environment in VS Code

1. Open the Command Palette with `Ctrl+Shift+P`.
2. Type and select **Python: Select Interpreter**.
3. Choose the interpreter located at `./.venv/bin/python`.

VS Code will now use the virtual environment for IntelliSense, linting, and terminal sessions opened within the project.

To persist the interpreter selection across VS Code sessions without repeating this step, create a `.vscode/settings.json` file in the project root directory containing the following:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.terminal.activateEnvironment": true
}
```

The `python.defaultInterpreterPath` setting instructs VS Code to use the virtual environment interpreter for all Python operations in the workspace, including IntelliSense, linting, and code execution. The `python.terminal.activateEnvironment` setting causes VS Code to automatically run `source .venv/bin/activate` each time a new integrated terminal is opened, so the environment is always active without manual steps.

To verify that the virtual environment is active in the integrated terminal, open a new terminal with `` Ctrl+` `` and confirm that the shell prompt displays the `(.venv)` prefix before the directory path.

#### Step 9: Deactivate the Virtual Environment

When development is complete, deactivate the environment by running:

```bash
deactivate
```

#### Step 10: (Optional) Export Dependencies to a Requirements File

```bash
pip freeze > requirements.txt
```

To restore the environment on another machine:

```bash
pip install -r requirements.txt
```

---

## 4. Vibe Coding Workflow in IoT Software Development

IoT software development workflows are undergoing a fundamental paradigm shift from manual, syntax-driven coding to a methodology known as "vibe coding" — a practice that employs natural language prompting and agentic AI workflows to accelerate the entire development lifecycle. In this model, AI agents such as Claude autonomously plan, generate, test, and iterate on code, compressing development timelines from months to days.

### 4.1 Conceptual Foundation

"Vibe coding" involves the use of AI models to generate, iterate upon, and execute IoT code without requiring the developer to author the initial implementation. The developer provides a high-level natural language description — a "vibe prompt" — that specifies the system's desired behavior. The AI agent interprets this prompt and produces a functional code framework, including cloud connectivity scripts, sensor abstraction layers, and deployment configurations.

As articulated by Anthropic's Claude Code documentation: engineers who adopt this approach focus on architecture, product thinking, and continuous orchestration — managing multiple agents in parallel, providing strategic direction, and making the decisions that shape what is built, rather than writing individual lines of syntax.

### 4.2 From Syntax to Prompts

The traditional workflow, in which developers write C, C++, or Python code statement by statement, is increasingly supplanted by natural language specification. Rather than authoring a function to initialize an MQTT connection and publish a sensor payload, a developer describes the desired behavior:

> "Create a Python script for a Raspberry Pi that reads temperature from a DHT22 sensor and sends the data to AWS IoT Core every 60 seconds using X.509 certificates for authentication."

AI agents such as Claude Code translate this description into syntactically correct, functionally complete code, including library imports, exception handling, and reconnection logic.

### 4.3 Autonomous Agent Teams

Agentic workflows extend beyond single-prompt code generation to multi-step, multi-file development tasks. An AI agent assigned a task such as "create a sensor data processing pipeline for an ESP32 that aggregates readings and uploads them to Azure IoT Hub" will:

1. Research the relevant SDKs and APIs autonomously.
2. Generate the firmware code and cloud integration scripts across multiple files.
3. Execute unit tests and resolve compilation errors.
4. Iterate on failures, incorporating error output as feedback, until the pipeline is functional.

This capability enables IoT teams to delegate entire development phases to AI agents while maintaining oversight of architectural decisions and system boundaries.

### 4.4 The Traditional V-Model Versus Vibe Coding Loops

The classical V-model of software development — characterized by sequential requirements, design, implementation, verification, and validation phases — is being replaced in the vibe coding paradigm with iterative feedback loops:

1. **Prompt**: Describe the desired IoT feature or system behavior in natural language.
2. **Generate**: The AI agent produces an initial implementation, including cloud resource scripts.
3. **Deploy to Simulation**: Execute the generated script in a test environment or simulator.
4. **Observe**: Monitor outputs, MQTT telemetry, and error logs.
5. **Fix via Chat**: Paste error messages or unexpected outputs directly back into the AI agent's context.
6. **Iterate**: The agent revises the implementation based on the provided feedback.

This loop replaces the traditional debugging workflow, in which developers step through code line by line, with a conversational, feedback-driven correction process.

### 4.5 Error Resolution Without Manual Debugging

Instead of tracing execution paths through an IDE debugger, developers paste compile errors, serial console output, or cloud service error responses directly back into the AI agent's conversation context. The agent analyzes the failure, identifies the root cause, and proposes a corrected implementation. This approach is particularly effective for IoT projects where debugging across hardware, firmware, and cloud layers simultaneously is otherwise time-intensive.

### 4.6 Developer Role in the Vibe Coding Model

The developer's role shifts from code author to system architect and orchestrator. The principal responsibilities become:

- Defining the product vision, functional requirements, and system constraints.
- Composing precise and contextually rich vibe prompts.
- Reviewing AI-generated code for correctness, security, and architectural consistency.
- Managing multiple agents in parallel for concurrent development streams.
- Making final decisions on what is built and how it integrates with existing systems.

---

## 5. Setting Up the Vibe Coding Environment

Two principal cloud platform ecosystems provide first-class tooling for vibe coding in IoT development contexts: Microsoft Azure (via GitHub Copilot in VS Code) and Amazon Web Services (via Amazon Bedrock AgentCore with AWS MCP Servers).

### 5.1 Microsoft: GitHub Copilot in Agent Mode (Visual Studio Code)

GitHub Copilot, integrated into Visual Studio Code, supports an **Agent Mode** that enables the AI to operate autonomously within the development environment. In Agent Mode, GitHub Copilot can create and edit files, execute terminal commands, install dependencies, and debug the development environment without requiring step-by-step instruction.

**Reference**: [GitHub Copilot — Command Your Craft](https://github.com/features/copilot)

**Setup Steps:**

1. Install [Visual Studio Code](https://code.visualstudio.com/) on the development machine.
2. Install the **GitHub Copilot** and **GitHub Copilot Chat** extensions from the VS Code Marketplace.
3. Sign in with a GitHub account that has an active Copilot subscription (a free tier is available).
4. Open the Chat view (`Ctrl+Alt+I`) and select **Agent** from the dropdown to activate Agent Mode.
5. Enter a vibe prompt describing the IoT system, and Copilot will autonomously scaffold files, run terminal commands, and validate the environment.

**Tutorial Reference**: [Work with agents in VS Code](https://code.visualstudio.com/docs/copilot/agents/agents-tutorial)

Key capabilities of GitHub Copilot in Agent Mode relevant to IoT development include:

- Scaffolding complete IoT project structures from a natural language description.
- Executing terminal commands to install SDKs such as `AWSIoTPythonSDK` or `azure-iot-device`.
- Proposing and validating multi-file edits across firmware and cloud integration layers.
- Supporting agentic cloud tasks via Copilot cloud agents that create GitHub branches and pull requests.

### 5.2 Amazon: Amazon Bedrock AgentCore with AWS MCP Servers

Amazon Web Services provides a vibe coding environment through **Amazon Bedrock AgentCore** augmented by specialized **AWS Model Context Protocol (MCP) Servers**. This architecture gives the AI agent direct, structured access to AWS documentation, architecture diagrams, cost analysis tools, and security assessment frameworks, ensuring that AI-generated code follows cloud best practices from the outset.

**Reference**: [Guidance for Vibe Coding with AWS MCP Servers](https://aws.amazon.com/solutions/guidance/vibe-coding-with-aws-mcp-servers/)

The MCP server integration provides the following capabilities:

- **AWS Documentation Access**: The agent queries official AWS documentation in real time, reducing hallucinated or outdated API usage.
- **Architecture Visualization**: Generates architecture diagrams conforming to AWS Well-Architected Framework principles.
- **Cost Analysis**: Evaluates the projected cost of proposed cloud resource configurations before deployment.
- **Security Assessment**: Validates that generated code adheres to AWS security best practices, including IAM policy scoping and certificate management.

**Setup Steps:**

1. Access the AWS Console and navigate to **Amazon Bedrock**.
2. Enable the AgentCore service for the target AWS region.
3. Configure the relevant AWS MCP Servers from the [guidance sample code repository](https://github.com/aws-solutions-library-samples/guidance-for-vibe-coding-with-aws-mcp-servers).
4. Interact with the AI agent via natural language prompts within the Bedrock console or via the Amazon Q Developer IDE plugin.

**Amazon Q Developer Reference**: [Chatting with Amazon Q Developer about code](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/q-in-IDE-chat.html)

Amazon Q Developer (formerly CodeWhisperer) provides agentic chat capabilities directly within supported IDEs, enabling developers to prompt the AI with IoT-specific tasks and receive iterative, context-aware code generation.

### 5.3 Google Cloud: Free AI Tools for IoT Prototyping

Google Cloud offers a suite of free AI tools that can complement IoT development workflows. **Gemini Code Assist for Individuals** provides AI-powered code completions, generation, and debugging assistance directly within VS Code and JetBrains IDEs at no cost, with up to 180,000 code completions per month. **Google AI Studio** enables free experimentation with Gemini models via an API key, supporting rapid prototyping of AI-enhanced IoT features such as natural language sensor query interfaces.

**Reference**: [Free AI Tools from Google Cloud](https://cloud.google.com/use-cases/free-ai-tools)

---

## 6. Designing the IoT Prompt

The quality of a vibe coding session is directly determined by the quality of the initial prompt. Rather than writing syntax, the developer describes the identity and operational requirements of the IoT system in natural language. A well-structured IoT vibe prompt comprises three essential components:

### 6.1 The Device Context

Specify the hardware platform, sensor configuration, and connectivity constraints with precision. The AI agent uses this information to select appropriate libraries, GPIO pin assignments, and communication protocols.

**Example:**
> "I have a Raspberry Pi 4 with a DHT22 temperature and humidity sensor connected to GPIO pin 4, and a reliable Wi-Fi connection."

### 6.2 The Cloud Destination

Identify the target cloud platform and the communication protocol, including the topic structure, data format, and transmission interval.

**Example:**
> "Send the sensor readings every 60 seconds to AWS IoT Core on the topic `raspberrypi/environment`, formatted as JSON, or to an Azure IoT Hub via MQTT."

### 6.3 Security Requirements

Specify the authentication mechanism and any compliance or data protection constraints. For production IoT systems, X.509 certificate-based mutual authentication is the industry standard.

**Example:**
> "Use X.509 certificates stored on the device for mutual TLS authentication. Do not hardcode credentials in the source code."

### 6.4 Constructing an Effective Prompt

Drawing on the Microsoft Learn guidance for creating effective GitHub Copilot prompts, the following principles apply to IoT vibe coding:

- **Start general, then add specifics**: Begin with the overall system goal, then layer in hardware details, cloud configuration, and security requirements.
- **Provide concrete examples**: Include example JSON payloads, topic names, or expected output formats.
- **Break complex tasks into phases**: Decompose a full IoT pipeline (sensor reading, local buffering, MQTT publish, cloud ingestion, database storage) into sequential prompts.
- **Eliminate ambiguity**: Reference specific library names, SDK versions, and API endpoints rather than generic descriptions.
- **Iterate on the response**: If the initial output does not meet requirements, refine the prompt with additional context rather than manually editing the generated code.

**References**: 
- [Examine the vibe coding process — Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/introduction-vibe-coding/3-examine-vibe-coding-process)
- [Create effective prompts for GitHub Copilot — Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/introduction-vibe-coding/4-create-effective-prompts-github-copilot)
- [Identify product requirements and coding guidelines — Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/introduction-vibe-coding/5-identify-product-requirements-guidelines)

---

## 7. Vibe Coding Examples

### 7.1 Amazon (AWS) IoT Vibe Coding

**Tool**: Amazon Q Developer (within the IDE) or AWS Cloud9

**Prompt Example:**

> "Write a Python script using the AWS IoT Device SDK v2 to publish sensor data from an ESP32 (running MicroPython) to an AWS IoT Core topic named `iot/topic`. The payload should include a timestamp, temperature, and device ID."

**Key AWS Services:**

| Service         | Role                                                        |
|-----------------|-------------------------------------------------------------|
| AWS IoT Core    | MQTT message broker and device gateway                     |
| AWS Lambda      | Serverless function for event-driven data processing       |
| Amazon DynamoDB | NoSQL database for time-series sensor data storage         |

**Workflow:**

1. Compose the vibe prompt in Amazon Q Developer.
2. Review and test the generated code in AWS Lambda.
3. Integrate with AWS IoT Core rules engine for message routing.

### 7.2 Microsoft Azure IoT Vibe Coding

**Tool**: GitHub Copilot in Agent Mode (VS Code)

**Prompt Example:**

> "Create a Python script for a Raspberry Pi using `azure-iot-device` to read temperature from a DHT22 sensor and send the reading to Azure IoT Hub using MQTT every 10 seconds. Include X.509 certificate authentication and structured JSON telemetry."

**Key Azure Services:**

| Service           | Role                                                              |
|-------------------|-------------------------------------------------------------------|
| Azure IoT Hub     | Cloud gateway for device-to-cloud and cloud-to-device messaging  |
| Azure Functions   | Event-driven serverless processing of incoming telemetry         |
| Azure IoT Edge    | On-device runtime for deploying containerized workloads          |
| Azure Monitor     | End-to-end observability, alerting, and telemetry analytics      |

**Workflow:**

1. Compose the vibe prompt in GitHub Copilot Agent Mode.
2. Push the generated code to a GitHub repository.
3. Deploy to the device via Azure IoT Edge.

**Azure Monitor Reference**: [Azure Monitor — Gain end-to-end observability for IoT applications](https://azure.microsoft.com/en-us/products/monitor)

Azure Monitor provides observability for IoT deployments, including curated insights, near-real-time alerting, and a unified data platform for telemetry analysis across hybrid and multi-cloud IoT infrastructure.

---

## 8. Executing the Vibe Coding Process

The execution of a vibe coding session follows a structured three-step process, as described in the Microsoft Azure Monitor and Microsoft Learn documentation.

### Step 1: Prompt and Generate

Compose the vibe prompt within the chosen AI agent environment (GitHub Copilot Agent Mode or Amazon Q Developer). The agent will:

- Generate the initial Python framework for the IoT device script.
- Produce any necessary cloud resource configuration scripts (e.g., AWS CloudFormation templates, Azure Resource Manager templates, or Azure Monitor alert rules referencing [Azure Monitor](https://azure.microsoft.com/en-us/products/monitor)).
- Install required dependencies if granted terminal access.

### Step 2: Run and Observe

Execute the generated script in the terminal or deploy it to the target device:

```bash
python3 Examples/vibe_iot_demo.py
```

Monitor the console output for telemetry confirmation messages. For cloud deployments:

- **AWS IoT Core**: Navigate to the AWS IoT Console and open the MQTT Test Client. Subscribe to the topic (e.g., `raspberrypi/vibe`) to observe incoming messages.
- **Azure IoT Hub**: Use the Azure CLI command `az iot hub monitor-events` or the Azure IoT Explorer application to view device-to-cloud messages.

If the script encounters an error, do not manually edit the generated code. Proceed to Step 3.

### Step 3: Fix via Feedback Loop

Copy the complete error output from the terminal — including the stack trace, error type, and line references — and paste it directly into the AI agent's chat context. The agent will:

1. Diagnose the root cause of the failure.
2. Propose a corrected implementation with an explanation of the change.
3. Re-execute the corrected script to confirm resolution.

This feedback loop replaces traditional debugging and is particularly effective for API authentication failures, certificate path errors, and SDK compatibility issues common in IoT cloud integrations.

---

## 9. Code Creation: IoT Demo Application

The following script, located at `Examples/vibe_iot_demo.py`, was created using the vibe coding methodology. It was generated by providing a natural language prompt to an AI agent and iteratively refined through the feedback loop described in Section 8.

**Vibe Prompt Used:**
> "Make a script for Raspberry Pi that sends temperature and humidity data to AWS IoT Core every 5 seconds using MQTT and X.509 certificates."

### Script: `Examples/vibe_iot_demo.py`

```python
# vibe_iot_demo.py
# Description:
#   Connects a Raspberry Pi to AWS IoT Core via MQTT and publishes
#   simulated environmental sensor data at a fixed interval.

import time
import json
import random
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# 1. Setup Vibe (Configurations)
ENDPOINT     = "your-iot-endpoint.iot.us-east-1.amazonaws.com"
CLIENT_ID    = "PiVibeCoder"
PATH_TO_CERT = "/home/pi/certs/certificate.pem.crt"
PATH_TO_KEY  = "/home/pi/certs/private.pem.key"
PATH_TO_ROOT = "/home/pi/certs/rootCA.pem"
TOPIC        = "raspberrypi/vibe"

# 2. Vibe Action: Connect to AWS IoT Core
myAWSIoTMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)

myAWSIoTMQTTClient.connect()
print("Vibe Check: Connected to AWS IoT!")

# 3. Vibe Loop: Simulate and Send
while True:
    data = {
        "timestamp":   time.time(),
        "temperature": round(random.uniform(20.0, 30.0), 2),
        "humidity":    round(random.uniform(40.0, 70.0), 2),
        "status":      "vibing"
    }
    myAWSIoTMQTTClient.publish(TOPIC, json.dumps(data), 1)
    print(f"Sent: {data}")
    time.sleep(5)
```

**Design Notes:**

- The script simulates sensor readings using `random.uniform` in place of a physical DHT22 sensor library, enabling development and testing without physical hardware.
- Data payloads are structured as JSON objects to conform to AWS IoT Core message schema expectations.
- The MQTT QoS level is set to 1 (at-least-once delivery) to ensure message reliability.
- X.509 certificate paths must be updated to reflect the actual device certificate deployment location.

---

## 10. Running the Demo Script

### Prerequisites

1. **AWS IoT Thing Setup**: Create an IoT Thing in the AWS Console, attach a policy permitting `iot:Publish` on the target topic, and download the device certificate, private key, and Amazon Root CA.
2. **Certificate Deployment**: Copy the three certificate files to the Raspberry Pi at the paths specified in the `PATH_TO_*` constants in the script, or update the constants to reflect the actual file paths.
3. **Endpoint Configuration**: Replace `your-iot-endpoint.iot.us-east-1.amazonaws.com` with the custom endpoint found in the AWS IoT Console under **Settings > Device data endpoint**.
4. **SDK Installation**: Activate the virtual environment and install the AWS IoT SDK:

```bash
source .venv/bin/activate
pip install AWSIoTPythonSDK
```

### Execution

Navigate to the `Development` directory and execute the script:

```bash
cd /home/laptop/EXERCISES/IOT/InternetOfThings/Development
python3 Examples/vibe_iot_demo.py
```

Expected console output upon successful connection and data transmission:

```
Vibe Check: Connected to AWS IoT!
Sent: {'timestamp': 1714392000.123, 'temperature': 24.57, 'humidity': 55.32, 'status': 'vibing'}
Sent: {'timestamp': 1714392005.456, 'temperature': 27.13, 'humidity': 48.91, 'status': 'vibing'}
```

### Verification

1. Open the **AWS IoT Console**.
2. Navigate to **Test > MQTT Test Client**.
3. Subscribe to the topic `raspberrypi/vibe`.
4. Confirm that JSON payloads arrive every 5 seconds.

### Using Vibe Coding to Extend the Script

To extend this script — for example, to add real DHT22 sensor readings or to forward data to a DynamoDB table — compose an extension prompt in the AI agent:

> "Modify `vibe_iot_demo.py` to read actual temperature and humidity values from a DHT22 sensor connected to GPIO pin 4 using the `Adafruit_DHT` library. Handle sensor read failures gracefully and retry after 2 seconds."

The agent will generate the modified script incorporating the physical sensor library, GPIO configuration, and error handling.

### Files Added to Complete the Vibe Coding Workflow

The following files were added to make `Examples/vibe_iot_demo.py` fully operational as a runnable IoT project:

| File | Purpose |
|------|---------|
| `Python/aws_iot_publisher.py` | Production extension of the demo: env-var config, logging, signal-based graceful shutdown, MQTT reconnection tuning, and a clear substitution point for a real DHT22 sensor |
| `Python/requirements.txt` | Declares `AWSIoTPythonSDK>=1.5.0` for `pip install -r` |
| `Shell/setup_env.sh` | Bash script that creates `.venv`, installs requirements, and prints exact run instructions — one command to get a new machine ready |

### Python Folder Script: aws_iot_publisher.py

The `Python/` folder contains `aws_iot_publisher.py`, a production-ready script that extends `Examples/vibe_iot_demo.py` with the following improvements:

- **Environment variable configuration**: All AWS IoT endpoint and certificate paths are loaded from environment variables via `os.environ.get()`, keeping credentials out of source code and the Git repository.
- **Structured logging**: Uses Python's `logging` module with ISO 8601 timestamps in place of `print()` statements, making output compatible with log aggregation systems.
- **Graceful shutdown**: Registers `SIGINT` and `SIGTERM` signal handlers so the MQTT connection is cleanly disconnected when the process is stopped with `Ctrl+C` or by a process manager.
- **Reconnection configuration**: Explicitly sets MQTT backoff, offline queue, and timeout parameters for reliable operation on unstable Wi-Fi or cellular connections.
- **Substitutable sensor function**: The `read_sensor()` function is isolated from the publish loop with inline comments explaining exactly how to replace the simulated data with a real DHT22 sensor via the `Adafruit_DHT` library.

| Aspect              | `Examples/vibe_iot_demo.py`        | `Python/aws_iot_publisher.py`             |
|---------------------|-------------------------------------|-------------------------------------------|
| Purpose             | Illustrative vibe coding demo       | Ready-to-deploy production script         |
| Configuration       | Hardcoded constants                 | Environment variables                     |
| Logging             | `print()` statements                | `logging` module with timestamps          |
| Shutdown            | Ctrl+C (abrupt)                     | Signal handlers with clean disconnect     |
| Reconnection        | Default SDK settings                | Explicit backoff and queue configuration  |
| Sensor data         | Simulated via `random`              | Simulated with clear substitution point   |

#### Running aws_iot_publisher.py

Step 1: Set the required environment variables.

```bash
export AWS_IOT_ENDPOINT="your-endpoint.iot.us-east-1.amazonaws.com"
export AWS_IOT_CERT="/home/pi/certs/certificate.pem.crt"
export AWS_IOT_KEY="/home/pi/certs/private.pem.key"
export AWS_IOT_ROOT_CA="/home/pi/certs/rootCA.pem"
```

Step 2: Activate the virtual environment.

```bash
source .venv/bin/activate
```

Step 3: Run the script.

```bash
python3 Python/aws_iot_publisher.py
```

Expected output:

```
2026-04-29T14:00:00 [INFO] Connecting to AWS IoT Core at your-endpoint.iot.us-east-1.amazonaws.com ...
2026-04-29T14:00:01 [INFO] Connected. Publishing to topic 'raspberrypi/vibe' every 5 s.
2026-04-29T14:00:01 [INFO] Published: {'timestamp': 1714392001.0, 'device_id': 'PiVibeCoder', 'temperature': 24.57, 'humidity': 55.32, 'status': 'vibing'}
```

Step 4: Stop the script cleanly with `Ctrl+C`. The signal handler logs a shutdown message and disconnects from AWS IoT Core before the process exits.

### Shell Folder Script: setup_env.sh

The `Shell/` folder contains `setup_env.sh`, a Bash automation script that handles the complete environment setup sequence in a single command. It is the recommended starting point when cloning the repository on a new Raspberry Pi or Linux development machine.

#### What the Script Does

1. Checks whether `python3-venv` is installed; installs it via `apt-get` if absent.
2. Creates the `.venv` virtual environment in the project root if it does not already exist.
3. Activates the virtual environment within the current shell session.
4. Upgrades `pip` to the latest available version.
5. Installs all packages listed in `Python/requirements.txt`.
6. Prints the environment variable export commands and the command to run the IoT publisher.

#### Usage

Run from the `Development` directory:

```bash
cd /home/laptop/EXERCISES/IOT/InternetOfThings/Development
bash Shell/setup_env.sh
```

After the script completes, the virtual environment is active in the current terminal session and all dependencies are installed. Set the environment variables printed by the script, then run the IoT publisher immediately. To use a new terminal, activate the environment manually first:

```bash
source .venv/bin/activate
```

### Caution Regarding Production Use

While vibe coding is highly effective for rapid prototyping, IoT systems deployed in production contexts — particularly those involving safety-critical automation, medical monitoring, or industrial control — require systematic human review of AI-generated code. Engineers must validate that authentication logic, error recovery mechanisms, data validation routines, and resource cleanup procedures meet the reliability and security requirements of the operational environment.

---

## 11. Beyond Vibe Coding: Disciplined AI-Assisted Development

The "Beyond Vibe-Coding" article by Daniel Steegmuller at InnoGames describes a mature, structured approach to AI-assisted development that extends pure vibe coding with systematic quality assurance and planning rigor. This methodology, termed "gate-coding," is applicable to IoT projects of sufficient complexity that require architectural integrity and automated verification.

**Reference**: [Beyond Vibe-Coding: A Disciplined Workflow for AI-Assisted Software Development with Claude Code — InnoGames Blog](https://blog.innogames.com/beyond-vibe-coding-a-disciplined-workflow-for-ai-assisted-software-development-with-claude-code/)

### 11.1 Claude Code Skills

Claude Code supports user-defined "skills": Markdown files that act as structured prompt templates invoked via slash commands. Each skill encodes a specific workflow step — what context to gather, what actions to take, what quality standards to enforce, and what artifacts to produce. Applied to IoT development, skills can encode:

- Firmware compilation and test verification sequences.
- MQTT connectivity validation against a test broker.
- Certificate deployment and permission verification procedures.
- IoT integration test patterns against AWS IoT Core or Azure IoT Hub.

**Reference**: [Claude Code by Anthropic](https://www.anthropic.com/product/claude-code)

### 11.2 The Disciplined Development Pipeline

For complex IoT systems, the following pipeline is recommended over ad-hoc vibe prompting:

1. **Research**: Analyze the existing codebase, hardware constraints, and cloud platform documentation.
2. **High-Level Plan**: Define the architecture, data flow, and component interfaces.
3. **Detailed Plan**: Break each implementation phase into step-by-step instructions with acceptance criteria.
4. **Human Review**: Examine the plan for architectural blind spots, security gaps, and constraint violations before implementation begins.
5. **Implement**: Execute the implementation phase with automated quality gates.
6. **Verify**: Run compilation checks, unit tests, and integration tests against simulated or physical hardware.
7. **Review**: Conduct automated and human code review against project standards.

### 11.3 Context Management

A critical operational principle in AI-assisted development is disciplined context management. As the AI agent's context window accumulates conversation history and generated code, its ability to remain focused and produce correct output degrades — a phenomenon described as "context rot." For IoT projects:

- Begin a fresh agent session for each distinct development phase.
- Reference specific plan documents and architecture decision records rather than relying on conversational history.
- Clear context between firmware and cloud integration phases.

### 11.4 Architectural Practices That Support AI Development

The following software engineering practices significantly improve the reliability of AI-generated IoT code:

- **Single Responsibility Principle**: Small, focused modules with clear responsibilities allow the AI to trace execution paths without contextual overload.
- **Interface Definitions**: Defining explicit interfaces between the sensor abstraction layer, protocol layer, and cloud SDK layer enables the AI to reason about system contracts independently of implementation details.
- **Architecture Decision Records (ADRs)**: Short Markdown documents recording architectural decisions and their rationale prevent the AI from "improving" design choices that were made deliberately.
- **Data-Driven Configuration**: Keeping all endpoint URLs, topic names, intervals, and thresholds in configuration files rather than hardcoded in source enables the AI to modify behavior without touching business logic.

---

## 12. References

The following resources were consulted in the preparation of this documentation and are referenced throughout the content:

| Source | URL |
|--------|-----|
| GitHub Copilot | [https://github.com/features/copilot](https://github.com/features/copilot) |
| Guidance for Vibe Coding with AWS MCP Servers | [https://aws.amazon.com/solutions/guidance/vibe-coding-with-aws-mcp-servers/](https://aws.amazon.com/solutions/guidance/vibe-coding-with-aws-mcp-servers/) |
| Azure Monitor | [https://azure.microsoft.com/en-us/products/monitor](https://azure.microsoft.com/en-us/products/monitor) |
| Claude Code by Anthropic | [https://www.anthropic.com/product/claude-code](https://www.anthropic.com/product/claude-code) |
| Beyond Vibe-Coding: A Disciplined Workflow (InnoGames) | [https://blog.innogames.com/beyond-vibe-coding-a-disciplined-workflow-for-ai-assisted-software-development-with-claude-code/](https://blog.innogames.com/beyond-vibe-coding-a-disciplined-workflow-for-ai-assisted-software-development-with-claude-code/) |
| Tutorial: Work with agents in VS Code | [https://code.visualstudio.com/docs/copilot/agents/agents-tutorial](https://code.visualstudio.com/docs/copilot/agents/agents-tutorial) |
| Identify product requirements and coding guidelines (Microsoft Learn) | [https://learn.microsoft.com/en-us/training/modules/introduction-vibe-coding/5-identify-product-requirements-guidelines](https://learn.microsoft.com/en-us/training/modules/introduction-vibe-coding/5-identify-product-requirements-guidelines) |
| Examine the vibe coding process (Microsoft Learn) | [https://learn.microsoft.com/en-us/training/modules/introduction-vibe-coding/3-examine-vibe-coding-process](https://learn.microsoft.com/en-us/training/modules/introduction-vibe-coding/3-examine-vibe-coding-process) |
| Create effective prompts for GitHub Copilot (Microsoft Learn) | [https://learn.microsoft.com/en-us/training/modules/introduction-vibe-coding/4-create-effective-prompts-github-copilot](https://learn.microsoft.com/en-us/training/modules/introduction-vibe-coding/4-create-effective-prompts-github-copilot) |
| Chatting with Amazon Q Developer about code | [https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/q-in-IDE-chat.html](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/q-in-IDE-chat.html) |
| Free AI tools from Google Cloud | [https://cloud.google.com/use-cases/free-ai-tools](https://cloud.google.com/use-cases/free-ai-tools) |
