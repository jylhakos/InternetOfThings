# Internet of Things

Internet of Things (IoT) consists of several layers which play a role in the route from connecting things to IoT applications. This repository contains documents, examples, and implementations covering various aspects of IoT development, from AI integration to deployment strategies.

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/iot.png?raw=true)

Figure: [Reference model](https://www.itu.int/rec/T-REC-Y.2060-201206-I)

## Table of Contents

- [How does Artificial Intelligence for IoT work?](#how-does-artificial-intelligence-for-iot-work)
- [Challenges of IoT](#challenges-of-iot)
- [Examples of IoT](#examples-of-iot)
- [How do IoT Software Development Workflows Change with Vibe Coding and Agentic Agents?](#how-do-iot-software-development-workflows-change-with-vibe-coding-and-agentic-agents)
- [Folder Structure](#folder-structure)
- [References](#references)

## How does Artificial Intelligence for IoT work?

Artificial Intelligence for IoT stands for the integration of AI and IoT. Artificial Intelligence for IoT helps to enhance connectivity, automation, and data analysis. IoT devices and systems leverage AI to analyze data, make intelligent decisions, and communicate effectively with other devices.

Artificial Intelligence for IoT enables devices to learn from data, adapt to dynamic environments, and autonomously perform tasks. Artificial Intelligence for Internet of Things (IoT) combines IoT sensors that collect data with AI to analyze it, enabling devices to learn, make decisions, and take autonomous action without human intervention.

By processing data at the edge or in the cloud, Artificial Intelligence for IoT reduces latency, improves predictive maintenance, and automates processes for increased efficiency.

## Challenges of IoT

### Core Challenges

**Security & Privacy**: Securing a vast number of connected devices, especially with sensitive data.

**Latency**: Ensuring AI processing happens fast enough for real-time control.

**Interoperability**: Getting devices from different manufacturers to communicate effectively.

### Challenges with Processing IoT Data on Cloud Platforms

1. **Latency** When IoT data is sent to the cloud, there is a delay between data generation and processing because of network latency.

2. **Network Failure** Timely action is not initiated in case the network is down and the digital twin cannot reach the IoT endpoints.

3. **Data Breaches** Possibility of data breach at the server farm or the cloud.

4. **Size of Data** Directly proportional to the number of sensors generating data.

5. **Power Consumption** Energy requirements and battery capacity define when and how often to send/receive information from the cloud.

## Examples of IoT

### Use Cases

**Smart Cities**: Optimizing traffic flow, smart lighting, and energy management systems that adapt to real-time conditions and reduce energy consumption while improving urban livability.

**Industrial Automation (IIoT)**: Automated, self-adjusting manufacturing lines that use sensors and AI to optimize production processes, perform predictive maintenance, and reduce downtime.

**Smart Homes**: Devices that learn user habits to save energy and increase comfort, such as thermostats that adjust based on occupancy patterns and lighting systems that adapt to daily routines.

### Programming Languages

[Go](https://github.com/golang/go) is an open source programming language suitable for IoT applications, offering excellent concurrency support and low-level system access.

## Folder Structure

### Computing/
Computing resources for IoT applications, consisting agent frameworks, autonomous agent systems, edge computing integration, large language models, machine learning models, and evaluation tooling.
- **AGENTS/** - Agent framework implementations (LangChain, No Framework, Spring AI, Strands Agents)
- **AI-AND-EDGE-COMPUTING/** - Edge AI integration with examples, models, and data pipelines
- **AUTONOMOUS-AGENT-FRAMEWORKS/** - Agno, AutoGen, CrewAI, Embabel, Haystack, OpenClaw, Semantic Kernel
- **CODING-AND-DEVELOPMENT/** - Development tools including Agent Development Kit, Agent2Agent, GitHub Copilot, Langflow, Langfuse, MCP, n8n
- **EVALUATION/** - Benchmarking, metrics, observability, security, and testing tools
- **FINE-TUNING/** - Model fine-tuning with PyTorch, reinforcement learning, and evaluation metrics
- **LARGE-LANGUAGE-MODELS/** - LLM deployment, inference, orchestration, prompts, RAG, security, and vector databases
- **MACHINE-LEARNING/** - CNN, Deep Learning, Feature Learning, RNN, Transformers, Reinforcement Learning, Unsupervised Learning
- **PIPELINE/** - ML pipeline tools (Airflow, Dagster, Kubeflow, MLflow)

### Concurrency/
Concurrent programming patterns and implementations across multiple languages for handling asynchronous IoT data streams.
- **C++/** - Concurrency patterns in C++
- **Go/** - Goroutines, channels, and synchronization primitives
- **Java/** - Java concurrency implementations
- **Javascript/** - Async JavaScript patterns
- **Python/** - asyncio, Celery, Redis Queue

### Databases/
Data storage solutions for IoT applications handling time-series and telemetry data.
- **MongoDB/** - NoSQL document database for IoT data
- **PostgreSQL/** - Relational database with Go examples
- **Redis/** - In-memory data store for caching and real-time applications

### Debugging/
Tools and techniques for debugging IoT applications and systems.
- **GDB/** - GNU Debugger for low-level debugging
- **Sentry/** - Error tracking and monitoring

### Deployment/
Deployment strategies for IoT applications across various platforms.
- **Browser/** - Angular and React frontend deployments
- **Clouds/** - AWS, Azure, GCP cloud deployments
- **Containers/** - Docker containerization for multiple frameworks
- **DevOps/** - CI/CD pipelines and automation tools
- **Native/** - Native application deployments

### Frameworks/
Web and application frameworks for building IoT services.
- **Backend/** - Server-side frameworks
- **Frontend/** - Client-side frameworks

### Languages/
Programming language implementations and examples.
- **C, C++, C#** - System-level and embedded programming
- **Go, Java, Kotlin, Scala** - Backend services
- **Python, Rust** - IoT applications and embedded systems
- **Javascript, Typescript, Dart** - Web and mobile applications
- **Qt** - Cross-platform application framework

### Messaging/
Communication protocols and APIs for IoT device connectivity.
- **GraphQL/** - Query language for APIs
- **gRPC/** - High-performance RPC framework
- **HTTP/REST/** - Traditional web protocols
- **MQTT/** - Lightweight messaging protocol for IoT
- **NATS/** - Cloud-native messaging system
- **OpenAPI/** - API specification and documentation
- **Socket.IO/** - Real-time bidirectional communication
- **TCP/** - Low-level network communication

### Microservices/
Microservices architecture patterns and implementations for scalable IoT systems.
- **infrastructure/** - Infrastructure configuration
- **k8s/** - Kubernetes orchestration
- **services/** - Service implementations

### Security/
Security implementations for protecting IoT devices and data.
- **JWT/** - JSON Web Token authentication
- **TLS/** - Transport Layer Security

## How do IoT Software Development Workflows Change with Vibe Coding and Agentic Agents?

The adoption of vibe coding and agentic agents is transforming IoT software development from a manual, hardware-centric process into an automated, conversational, and high-level architecture design workflow. Developers are increasingly moving away from writing low-level code—historically in C or C++—towards directing AI agents in natural language to handle protocol implementation, device provisioning, sensor data integration, and cloud connectivity.

### Introduction to Vibe Coding and Agentic Coding

The term "vibe coding" was coined by AI researcher Andrej Karpathy in early 2025 to describe a software development practice in which the developer's role shifts from writing code line by line to guiding an AI assistant through natural language prompts to generate, refine, and debug software. Rather than focusing on the details of implementation, the developer specifies desired outcomes and the AI handles the translation into functional code. As Google Cloud summarises: "With traditional programming, you focus on the details of implementation, manually writing the specific commands, keywords, and punctuation a language requires. Vibe coding lets you focus on the desired outcome instead, describing your goal in plain language." ([Google Cloud, 2026](https://cloud.google.com/discover/what-is-vibe-coding))

Agentic coding extends this paradigm further. Whereas vibe coding describes an interactive conversational workflow with an AI assistant, agentic coding refers to the deployment of autonomous AI agents that plan, write, test, and modify code with minimal human intervention. These agents operate through a "reason and act" loop: upon receiving a high-level instruction, the agent decomposes the request into sub-tasks, executes actions such as reading files, running terminal commands, installing dependencies, and verifying outputs, then iterates until the goal is achieved. The defining feature of a coding agent is its iterative feedback loop—it writes a test case, runs the code, observes a failure, and rewrites the code to pass the test, enabling self-correction on complex instructions. ([Google Cloud, 2026](https://cloud.google.com/discover/what-is-agentic-coding))

In practice, vibe coding is applied along two axes: first, a tight conversational loop used to create and refine individual pieces of code; second, a broader application lifecycle that takes a high-level idea from ideation through AI-driven generation, iterative refinement, testing and validation, and finally deployment. This lifecycle maps directly onto IoT development stages from system design through to production operation.

### What Impact Do Vibe Coding and Agentic Agents Have on IoT Software Development Workflows?

The integration of vibe coding and agentic agents into IoT development produces a structural shift in developer roles, tooling, and process. Developers are transitioning from implementers to orchestrators, validating and directing AI-generated outputs rather than authoring every line of code.

**From Manual Coding to Directed Orchestration**

Vibe coding enables a "prompt architect" approach: a developer describes the desired behavior of a sensor or edge device in natural language, and the AI produces the corresponding code. For example, a developer using Amazon Q Developer might instruct the tool: "Set up an MQTT client to publish temperature data every 10 seconds," and receive functional firmware code without consulting hardware reference manuals or protocol specifications. ([AWS, 2025](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-q-developer-agentic-coding-experience-ide/)) AI tools can likewise generate boilerplate code to read data from sensors—temperature sensors, accelerometers, gas sensors—and transmit it to cloud services such as AWS IoT Core, reducing the time required for routine device integration tasks.

Generative AI is accelerating code generation for embedded systems, automating sensor data integration, and expediting debugging of complex Linux-based edge devices. The developer's role evolves from manual implementer to "editor-in-chief," reviewing, testing, and taking ownership of AI-generated outputs.

**Multi-Agent Coordination for Complex IoT Systems**

Complex IoT architectures are increasingly developed through multi-agent coordination, where specialized agents—one responsible for connectivity, another for sensor data processing, another for security configuration—are orchestrated by a supervising agent. Frameworks such as CrewAI, Amazon Bedrock Agents, and Google's Agent Development Kit (ADK) support this model. Within these multi-agent systems, each agent contributes domain-specific knowledge, enabling more sophisticated decision-making and removing routine tasks from human workloads. Gartner predicts that over 33 percent of enterprise applications will employ AI agents by 2028. ([AWS, 2025](https://aws.amazon.com/isv/resources/how-agentic-ai-is-transforming-software-development/))

Agentic AI transforms the "unit of software delivery" from a discrete feature or user story into a complete workflow—an end-to-end business process that agents can plan, implement, test, and deploy as a unified unit. Each agent automates a bounded workflow, bringing the technical implementation closer to the underlying business process. ([AWS Enterprise Strategy, 2025](https://aws.amazon.com/blogs/enterprise-strategy/the-new-unit-of-software-delivery-the-workflow/))

**Automated Testing and Debugging**

Agentic workflows enable automated testing in which agents identify, diagnose, and propose fixes for bugs in device code without human intervention. An agent writes a test case, executes it, observes a failure, revises the implementation, and re-runs verification autonomously. Amazon's internal deployment of AI-assisted development demonstrated a reduction in time spent waiting for technical answers by over 450,000 developer hours; equivalent productivity gains are anticipated for IoT engineering teams managing heterogeneous hardware environments. ([AWS DevOps Blog, 2025](https://aws.amazon.com/blogs/devops/how-generative-ai-is-transforming-developer-workflows-at-amazon/))

### How Are IoT Software Development Workflows Evolving with Vibe Coding and Agentic Agents?

The evolution of IoT development workflows under vibe coding and agentic agents can be characterised across the standard software development lifecycle.

**System Design and Prototyping**

Developers act as architects, articulating high-level goals through natural language while AI generates initial boilerplate and configuration code. Vibe coding enables rapid creation of minimum viable prototypes, allowing developers to test concepts in simulated environments before committing to hardware deployment. The application lifecycle follows an iterative pattern: ideation via a high-level prompt, AI-driven generation of an initial code structure, iterative refinement through conversational feedback, testing and validation by a human expert, and deployment with a final prompt or a single automated action. ([Google Cloud, 2026](https://cloud.google.com/discover/what-is-vibe-coding))

AI software development—defined as the use of AI technologies to create, enhance, and optimise software applications—moves software production from pure automation towards augmentation, transforming development into a more adaptive, human-guided process. The user guides the AI but retains responsibility for reviewing, testing, and understanding the code generated, taking full ownership of the final product.

**Development and Integration**

Agents handle routine coding, debugging, and API integration—for example, connecting sensors to cloud services such as AWS IoT Core or Azure IoT Hub. Microsoft's Azure IoT Edge platform supports the deployment of AI-enabled modules for edge inference, and the .NET IoT Libraries enable C# development for sensors and controllers running on Raspberry Pi, HummingBoard, and comparable hardware. The libraries provide full support for GPIO, SPI, I2C, PWM, and serial port interfaces, covering temperature and humidity sensors, accelerometers, gas sensors, and RFID modules. ([Microsoft, 2026](https://dotnet.microsoft.com/en-us/apps/iot))

**Testing and Debugging**

Agentic coding agents autonomously manage multi-step testing workflows: executing firmware test suites, comparing outputs against expected behaviour, logging discrepancies, and applying corrective changes. The iterative self-correction mechanism inherent in agentic coding is particularly valuable in IoT environments where debugging interactions between firmware and heterogeneous hardware is time-intensive and expertise-dependent.

**Deployment and Maintenance**

Agents manage edge-to-cloud firmware updates, security patch deployment, and anomaly detection, optimising operational performance at scale. Agentic systems can monitor device fleets, detect behavioural anomalies, and trigger remediation workflows autonomously, reducing the need for manual oversight of large-scale IoT deployments.

### IoT Workflow Stages

The following table contrasts traditional IoT development with the vibe coding and agentic approach across each major stage of the development lifecycle.

| Stage | Traditional Approach | Vibe Coding and Agentic Approach |
|---|---|---|
| System Design | Manual architecture documentation; deep hardware-specific knowledge required | Developer specifies goals in natural language; AI generates architecture proposals and boilerplate |
| Development | Line-by-line implementation in C/C++, Python, or Java | AI generates sensor drivers, protocol implementations, and cloud integrations from prompts |
| Testing | Manual test case authoring; hardware-in-the-loop testing cycles | Agents write, execute, and iterate test cases autonomously; continuous self-correction |
| Deployment | Manual firmware flashing; scripted OTA update pipelines | Agent-managed firmware deployment, OTA updates, and cloud connectivity configuration |
| Maintenance | Manual monitoring; issue escalation to engineering teams | Agentic anomaly detection, automated remediation, continuous optimisation |

### Risks of Workflow Changes in IoT Development

The transition to vibe coding and agentic development in IoT systems introduces a distinct set of risks that require careful evaluation.

**Security Vulnerabilities in AI-Generated Code**

AI-generated code may contain security vulnerabilities that are non-obvious to a developer who does not thoroughly review the output. In IoT systems, where devices operate within trusted networks and may handle sensitive sensor data or control physical infrastructure, unvetted AI-generated code presents a significant attack surface. Without rigorous code review, AI-generated firmware may introduce weaknesses such as hard-coded credentials, insecure communication protocols, or insufficiently validated inputs. This risk is amplified by the fact that vibe coding, in its less disciplined form, can encourage developers to accept AI output without deep scrutiny. Security review and validation by a qualified engineer remains essential, particularly for devices deployed in safety-critical or industrial environments.

**Over-Provisioning and Resource Exhaustion**

Without proper constraints, agentic agents may over-provision cloud resources, exceed API rate limits, or generate device telemetry at volumes that exceed network or processing capacity. IoT deployments frequently involve hardware operating under strict bandwidth, memory, and energy budgets; an agent that is not configured with awareness of these constraints may generate code that exhausts device resources or degrades network performance across a deployed fleet.

**Real-Time and Timing Constraints**

IoT systems, particularly in industrial (IIoT) contexts, require precise timing for interrupt handlers, hardware timers, and time-sensitive control loops. Current AI code generation models may not reliably produce code that satisfies exact timing requirements for industrial-grade applications, where deviations of microseconds can affect process correctness or operational safety. The probabilistic nature of large language model code generation is not inherently suited to deterministic real-time requirements; explicit constraints, formal verification, and hardware-in-the-loop testing remain necessary.

**Erosion of Embedded Systems Expertise**

A structural shift towards vibe coding as the primary development paradigm may reduce the depth of embedded systems expertise within development teams over time. If developers rely predominantly on AI-generated code without developing a corresponding understanding of the underlying hardware interfaces, the capacity to diagnose novel hardware failures, optimise for constrained environments, or design safety-critical systems may diminish progressively.

**Data Privacy and Intellectual Property**

Transmitting proprietary device specifications, firmware source code, or sensor data to cloud-hosted AI services during development raises data privacy and intellectual property concerns. Organisations developing commercially sensitive IoT products must evaluate the data governance implications of AI tool usage within their development pipelines, including where data is processed, retained, and whether it is used for model training.

**Vendor Dependency and Model Reliability**

Dependence on commercial AI tools for core development tasks introduces vendor lock-in and exposure to model deprecation, rate limiting, or service disruptions. Agentic workflows that rely on external API endpoints for code generation or testing may become inoperable during service outages or under pricing model changes, creating continuity risks for development and operational pipelines.

## References

- [HPE - What is AI IoT?](https://www.hpe.com/us/en/what-is/ai-iot.html)
- [ITU-T Reference Model Y.2060](https://www.itu.int/rec/T-REC-Y.2060-201206-I)
- [Go Programming Language](https://github.com/golang/go)
- [What is vibe coding? - Google Cloud](https://cloud.google.com/discover/what-is-vibe-coding)
- [What is agentic coding? - Google Cloud](https://cloud.google.com/discover/what-is-agentic-coding)
- [AWS Internet of Things](https://aws.amazon.com/iot/)
- [Amazon Q Developer agentic coding experience in the IDE](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-q-developer-agentic-coding-experience-ide/)
- [Chatting with Amazon Q Developer about code](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/q-in-IDE-chat.html#ide-agentic)
- [Prepare your development and test environment for IoT Edge - Microsoft](https://learn.microsoft.com/en-us/azure/iot-edge/development-environment)
- [Build IoT applications with .NET - Microsoft](https://dotnet.microsoft.com/en-us/apps/iot)
- [Agentic AI 101: How autonomous systems are driving software breakthroughs - AWS](https://aws.amazon.com/isv/resources/how-agentic-ai-is-transforming-software-development/)
- [The New Unit of Software Delivery: The Workflow - AWS Enterprise Strategy](https://aws.amazon.com/blogs/enterprise-strategy/the-new-unit-of-software-delivery-the-workflow/)
- [How generative AI is transforming developer workflows at Amazon - AWS DevOps Blog](https://aws.amazon.com/blogs/devops/how-generative-ai-is-transforming-developer-workflows-at-amazon/)
- [Introduction to vibe coding - Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/introduction-vibe-coding/)
- [What is AI software development? - Microsoft Copilot 101](https://www.microsoft.com/en-us/microsoft-copilot/copilot-101/ai-software-development)
- [The future of AI software development - Microsoft](https://www.microsoft.com/en-us/software-development-companies/resources/articles/future-of-ai-software-development)