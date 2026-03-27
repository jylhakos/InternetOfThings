# Internet of Things

Internet of Things (IoT) consists of several layers which play a role in the route from connecting things to IoT applications. This repository contains documents, examples, and implementations covering various aspects of IoT development, from AI integration to deployment strategies.

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/iot.png?raw=true)

Figure: [Reference model](https://www.itu.int/rec/T-REC-Y.2060-201206-I)

## Table of Contents

- [How does Artificial Intelligence for IoT work?](#how-does-artificial-intelligence-for-iot-work)
- [Challenges of IoT](#challenges-of-iot)
- [Examples of IoT](#examples-of-iot)
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

### 📁 Artificial Intelligence/
AI resources for IoT applications including agents, autonomous frameworks, edge computing integration, LLMs, machine learning models, and evaluation tools.
- **AGENTS/** - Agent frameworks (LangChain, No Framework implementations)
- **AI-AND-EDGE-COMPUTING/** - Edge AI integration with examples and models
- **AUTONOMOUS-AGENT-FRAMEWORKS/** - Agno, AutoGen, CrewAI, Embabel, Haystack, Semantic Kernel
- **CODING-AND-DEVELOPMENT/** - Development tools including GitHub Copilot, Langflow, MCP, Spring AI
- **EVALUATION/** - Benchmarking, metrics, observability, and testing tools
- **FINE-TUNING/** - Model fine-tuning with PyTorch and evaluation metrics
- **LARGE-LANGUAGE-MODELS/** - LLM deployment, inference, orchestration, RAG, and vector databases
- **MACHINE-LEARNING/** - CNN, Deep Learning, RNN, Transformers, Reinforcement Learning
- **PIPELINE/** - ML pipeline tools (Airflow, Dagster, Kubeflow, MLflow)

### 📁 Concurrency/
Concurrent programming patterns and implementations across multiple languages for handling asynchronous IoT data streams.
- **C++/** - Concurrency patterns in C++
- **Go/** - Goroutines, channels, and synchronization primitives
- **Java/** - Java concurrency implementations
- **Javascript/** - Async JavaScript patterns
- **Python/** - asyncio, Celery, Redis Queue

### 📁 Databases/
Data storage solutions for IoT applications handling time-series and telemetry data.
- **MongoDB/** - NoSQL document database for IoT data
- **PostgreSQL/** - Relational database with Go examples
- **Redis/** - In-memory data store for caching and real-time applications

### 📁 Debugging/
Tools and techniques for debugging IoT applications and systems.
- **GDB/** - GNU Debugger for low-level debugging
- **Sentry/** - Error tracking and monitoring

### 📁 Deployment/
Deployment strategies for IoT applications across various platforms.
- **Browser/** - Angular and React frontend deployments
- **Clouds/** - AWS, Azure, GCP cloud deployments
- **Containers/** - Docker containerization for multiple frameworks
- **DevOps/** - CI/CD pipelines and automation tools
- **Native/** - Native application deployments

### 📁 Frameworks/
Web and application frameworks for building IoT services.
- **Backend/** - Server-side frameworks
- **Frontend/** - Client-side frameworks

### 📁 Languages/
Programming language implementations and examples.
- **C, C++, C#** - System-level programming
- **Go, Java, Kotlin, Scala** - Backend services
- **Python, Rust** - IoT applications and embedded systems
- **Javascript, Typescript, Dart** - Web and mobile applications
- **Qt** - Cross-platform application framework

### 📁 Messaging/
Communication protocols and APIs for IoT device connectivity.
- **GraphQL/** - Query language for APIs
- **gRPC/** - High-performance RPC framework
- **HTTP/REST/** - Traditional web protocols
- **MQTT/** - Lightweight messaging protocol for IoT
- **NATS/** - Cloud-native messaging system
- **Socket.IO/** - Real-time bidirectional communication
- **TCP/** - Low-level network communication

### 📁 Microservices/
Microservices architecture patterns and implementations for scalable IoT systems.
- **infrastructure/** - Infrastructure configuration
- **k8s/** - Kubernetes orchestration
- **services/** - Service implementations

### 📁 Security/
Security implementations for protecting IoT devices and data.
- **JWT/** - JSON Web Token authentication
- **TLS/** - Transport Layer Security

## References

- [HPE - What is AI IoT?](https://www.hpe.com/us/en/what-is/ai-iot.html)
- [ITU-T Reference Model Y.2060](https://www.itu.int/rec/T-REC-Y.2060-201206-I)
- [Go Programming Language](https://github.com/golang/go)