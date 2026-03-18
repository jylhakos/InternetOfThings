# Agents

## Table of Contents

1. [Project Structure](#project-structure)
2. [What are AI Agents?](#what-are-ai-agents)
   - [AI Agents Capabilities](#ai-agents-capabilities)
   - [Use Cases in AI Agent Projects](#use-cases-in-ai-agent-projects)
   - [AI Agent Components](#ai-agent-components)
3. [VS Code and Agents](#vs-code-and-agents)
   - [How AI Agents Function in VS Code](#how-ai-agents-function-in-vs-code)
   - [Key Features and Capabilities](#key-features-and-capabilities)
   - [Tools and Extensions for AI Agent Development](#tools-and-extensions-for-ai-agent-development)
   - [How to Set Up AI Agent-Driven Software Development](#how-to-set-up-ai-agent-driven-software-development)
   - [Best Practices for Working with Agents](#best-practices-for-working-with-agents)
   - [Agent Customization and Configuration](#agent-customization-and-configuration)
4. [Steps to Create an AI Agent](#steps-to-create-an-ai-agent)
   - [Prerequisites](#prerequisites)
   - [Step 1: Task Definition and Scope Analysis](#step-1-task-definition-and-scope-analysis)
   - [Step 2: Tool Repository Development](#step-2-tool-repository-development)
   - [Step 3: Framework Selection and Architecture Design](#step-3-framework-selection-and-architecture-design)
   - [Step 4: Implementation and Integration](#step-4-implementation-and-integration)
5. [Open-Source Tools and Frameworks for AI Agents](#open-source-tools-and-frameworks-for-ai-agents-2025)
   - [Enterprise-Grade Frameworks](#enterprise-grade-frameworks)
   - [Specialized Agent Frameworks](#specialized-agent-frameworks)
   - [No-Framework Approach](#no-framework-approach)
   - [Framework Comparison Matrix](#framework-comparison-matrix)
   - [Selection Criteria of Framework for AI Agents](#selection-criteria-of-framework-for-ai-agents)
6. [References](#references)
   - [Academic and Research](#academic-and-research)
   - [Documentation and Tutorials](#documentation-and-tutorials)
   - [Open Source Repositories](#open-source-repositories)
   - [Reports and Whitepapers](#reports-and-whitepapers)
   - [Online Learning](#online-learning)
   - [Communities](#communities)

## Project Structure *Last Updated: August 2025*

```
AGENTS/
├── README.md
├── Agent Development Kit/
├── Haystack/
├── LangChain/
├── LangGraph/
├── LlamaIndex/
├── No Framework/
└── Semantic Kernel/
```

## What are AI Agents?

An agent is a combination of a model, tools, and a prompt.

An open source AI agents are artificial intelligence tools whose underlying code and algorithms are publicly available.

Artificial Intelligence agents represent autonomous computational entities designed to perceive their environment, make decisions, and execute actions to achieve specific objectives. These sophisticated systems operate independently, utilizing advanced reasoning capabilities to accomplish complex tasks on behalf of users or other systems.

An AI agent functions through a continuous perception-action cycle. The AI agent receives input (user queries, environmental data, or system events), processes this information using its knowledge base and reasoning mechanisms, selects appropriate tools or strategies, executes the chosen actions, and provides feedback or results to the requesting entity.

AI agents excel in scenarios characterized by uncertainty, dynamic environments, and multi-step problem-solving requirements. They are particularly valuable in applications where predetermined workflows are insufficient, such as conversational AI systems, autonomous decision-making platforms, and complex workflow orchestration systems.

AI agents are autonomous software systems that combine Large Language Models (LLMs) with external tools and reasoning capabilities to perform complex, multi-step tasks. As of 2025, AI agents have evolved beyond simple chatbots to become sophisticated problem-solving entities capable of the following.

### AI Agents Capabilities
- **Autonomous Task Decomposition**: Breaking down complex objectives into manageable sub-tasks
- **Dynamic Tool Selection**: Choosing appropriate tools from available resources based on context
- **Multi-modal Reasoning**: Processing and combining information from text, code, images, and structured data
- **Iterative Problem Solving**: Learning from intermediate results to refine approaches
- **Error Recovery**: Detecting failures and implementing alternative strategies

### Use Cases in AI Agent Projects

1. **Code Generation and Software Engineering**
   - Automated code review and refactoring
   - Multi-file project generation with proper architecture
   - Bug detection and automated fixing

2. **Research and Knowledge Synthesis**
   - Automated literature reviews and citation analysis
   - Cross-domain knowledge integration
   - Hypothesis generation and testing

3. **Business Process Automation**
   - Intelligent document processing and analysis
   - Customer service automation with context awareness
   - Supply chain optimization and decision making

4. **Scientific Computing and Data Analysis**
   - Automated experimental design
   - Pattern recognition in complex datasets
   - Model selection and hyperparameter optimization

### AI Agent Components

**Perception Layer**: Environmental sensing and input processing mechanisms
**Reasoning Engine**: Decision-making logic powered by LLMs and specialized algorithms
**Action Interface**: Tool execution and external system integration capabilities
**Memory Systems**: Short-term working memory and long-term knowledge retention
**Communication Protocol**: Inter-agent and human-agent interaction frameworks

## Autonomous Agents & Tools

Auto-GPT: A popular autonomous agent that uses LLMs to perform tasks autonomously, including web browsing and file handling.
Open Interpreter: An agent that runs code (Python, JS, Shell) locally to control the computer and interact with files.
SuperAGI: A full-stack agent infrastructure that includes a GUI and toolkits.
BabyAGI: Focused on task planning, prioritization, and execution loops.

## VS Code and Agents

Visual Studio Code has emerged as a leading platform for AI agent-driven software development, providing an integrated environment where developers can leverage autonomous AI assistants to enhance productivity, code quality, and development workflows. This section explores how to effectively utilize VS Code with AI agents for modern software development.

### How AI Agents Function in VS Code

AI agents in VS Code operate through a sophisticated multi-step process that mirrors human problem-solving approaches:

**Task Decomposition and Planning:**
- Agents analyze complex requests and break them down into manageable, sequential subtasks
- Create execution plans that account for dependencies, file structures, and existing code patterns
- Adapt plans dynamically based on intermediate results and encountered obstacles

**Codebase Interaction and Understanding:**
- Read and analyze entire codebases to understand architecture, patterns, and conventions
- Use semantic search capabilities to locate relevant code sections across multiple files
- Build context from imports, types, documentation, and existing implementations

**Autonomous Execution:**
- Execute tools and commands to modify code, run tests, and validate changes
- Self-correct when errors are detected, attempting alternative approaches
- Provide explanations and reasoning for decisions made during execution

**Iterative Refinement:**
- Monitor test results and compilation errors to identify issues
- Automatically adjust implementations based on feedback
- Request human intervention only when truly necessary or ambiguous

### Key Features and Capabilities

**Automated Feature Implementation:**
- **Issue-to-Code Workflow**: Assign GitHub issues or feature requests directly to agents, which autonomously implement the feature and create draft pull requests
- **Multi-File Coordination**: Agents can create, modify, and refactor code across multiple files while maintaining consistency
- **Architecture Awareness**: Respect existing design patterns, naming conventions, and architectural decisions

**Integrated Testing and Validation:**
- **Unit Test Generation**: Automatically generate comprehensive unit tests for new or modified code
- **Test Execution**: Run test suites and analyze failures to identify and fix issues
- **Frontend Testing**: Use integrated browser tools to interact with running applications, inspect UI elements, and validate user interactions
- **Visual Regression Testing**: Detect unintended UI changes through automated screenshot comparison

**Context-Aware Coding:**
- **Semantic Understanding**: Agents comprehend the purpose and context of code beyond syntax
- **Cross-File Refactoring**: Safely refactor code with automatic updates to all dependent files
- **Documentation Awareness**: Utilize existing documentation, README files, and code comments to inform decisions
- **Type System Integration**: Leverage TypeScript, Python type hints, and other type systems for safer refactoring

**Intelligent Code Review:**
- **Automated Code Analysis**: Identify potential bugs, performance issues, and security vulnerabilities
- **Style Guide Enforcement**: Ensure code adheres to team conventions and industry best practices
- **Optimization Suggestions**: Recommend performance improvements and code simplification opportunities

### Tools and Extensions for AI Agent Development

Several powerful tools and extensions enable AI agent-driven development in VS Code:

**GitHub Copilot:**
- **Agent Mode**: Enables autonomous operation with the ability to understand and implement changes across entire repositories
- **Chat Interface**: Natural language interaction for code generation, explanation, and debugging
- **Inline Suggestions**: Real-time code completion based on context and patterns
- **Command Execution**: Run terminal commands, tests, and build processes through agent directives

**Azure AI Foundry Agent Service:**
- **Cloud-Connected Agents**: Build and test agents connected to Azure services directly within VS Code
- **Custom Tool Integration**: Connect agents to internal APIs, databases, and cloud resources
- **Enterprise Security**: Leverage Azure's security and compliance features for agent operations
- **Scalability**: Deploy agents that can handle enterprise-scale codebases and workflows

**Sourcery:**
- **AI Code Review**: Continuous real-time code review with optimization suggestions
- **Refactoring Automation**: Automated code improvements while maintaining functionality
- **Quality Metrics**: Track code quality trends and identify areas for improvement

**Continue:**
- **Open-Source Alternative**: Free and extensible AI coding assistant
- **Custom Model Support**: Use any LLM backend (OpenAI, Anthropic, local models)
- **Codebase Indexing**: Create embeddings of your entire codebase for enhanced context

**Cursor (VS Code Fork):**
- **Native Agent Integration**: VS Code fork with deeply integrated AI agent capabilities
- **Codebase Chat**: Ask questions about your entire codebase with semantic search
- **Composer Mode**: Multi-file editing with agent assistance

### How to Set Up AI Agent-Driven Software Development

**Step 1: Install and Configure Required Extensions**

1. **Install GitHub Copilot (Recommended)**
   ```bash
   code --install-extension GitHub.copilot
   code --install-extension GitHub.copilot-chat
   ```

2. **Configure Copilot Settings**
   - Open VS Code Settings (Ctrl+, or Cmd+,)
   - Search for "Copilot"
   - Enable "Enable Auto Completions"
   - Configure language-specific settings as needed

3. **Install Additional Agent Tools** (Optional)
   ```bash
   code --install-extension Continue.continue
   code --install-extension sourcery.sourcery
   ```

**Step 2: Activate and Configure Agent Features**

1. **Enable Agent Mode in GitHub Copilot**
   - Open Copilot Chat panel (Ctrl+Shift+I or Cmd+Shift+I)
   - Look for agent selection dropdown
   - Choose from available agents: `@workspace`, `@terminal`, `@vscode`

2. **Configure Agent Behavior**
   - Create `.github/copilot-instructions.md` in your repository root
   - Define project-specific guidelines, patterns, and constraints
   - Example configuration:
     ```markdown
     # Project Guidelines for Copilot
     
     ## Code Style
     - Use functional components in React
     - Prefer async/await over .then() chains
     - Always include error handling
     
     ## Testing
     - Write unit tests for all business logic
     - Use Jest for JavaScript/TypeScript
     - Aim for 80% code coverage
     
     ## Architecture
     - Follow Clean Architecture principles
     - Keep components under 200 lines
     - Use dependency injection
     ```

3. **Set Up Custom Agents** (Advanced)
   - Define agent-specific instructions in `.vscode/agents.json`
   - Configure tool access permissions and capabilities
   - Establish guardrails and validation rules

**Step 3: Connect and Configure Tools**

1. **Integrated Browser for UI Testing**
   - Install browser automation tools (Playwright, Selenium)
   - Configure agents to access the integrated browser
   - Set up visual testing frameworks

2. **MCP Server Integration** (Model Context Protocol)
   - Install and configure MCP server for custom tool access
   - Connect agents to internal APIs, databases, and services
   - Define security boundaries and access controls

3. **Version Control Integration**
   - Configure Git settings for agent commits
   - Set up branch protection rules
   - Enable automated PR creation workflows

**Step 4: Define or Select Appropriate Agents**

VS Code supports various specialized agents for different tasks:

- **@workspace**: For codebase-wide questions and operations
- **@terminal**: For command execution and build operations
- **@vscode**: For VS Code settings and configuration
- **Custom Agents**: Define specialized agents for your domain

**Step 5: Interaction and Task Assignment**

1. **Natural Language Prompts**
   - Use clear, specific instructions: "Implement user authentication with JWT"
   - Provide context: "Following the existing pattern in `auth.service.ts`"
   - Specify constraints: "Ensure all endpoints have rate limiting"

2. **Iterative Refinement**
   - Review agent-generated code
   - Provide feedback: "Make this function more testable"
   - Request explanations: "Explain why you chose this approach"

3. **Multi-Step Workflows**
   - Chain multiple tasks: "Implement feature X, then write tests, then update docs"
   - Monitor progress through agent status indicators
   - Intervene when necessary to guide direction

### Best Practices for Working with Agents

**Effective Prompting:**
- Be specific and provide context about your codebase and requirements
- Break complex tasks into smaller, manageable subtasks
- Reference specific files, functions, or patterns when relevant
- Include acceptance criteria and expected outcomes

**Code Review and Validation:**
- Always review agent-generated code before merging
- Run comprehensive test suites on agent changes
- Use static analysis tools to catch potential issues
- Verify that changes align with architectural decisions

**Security Considerations:**
- Never expose sensitive credentials or API keys to agents
- Review agent access to external services and APIs
- Use environment variables for configuration
- Implement rate limiting to prevent excessive API calls

**Continuous Learning:**
- Provide feedback on agent suggestions to improve accuracy
- Update project guidelines as patterns emerge
- Share successful prompts and workflows with your team
- Document edge cases and limitations encountered

**Team Collaboration:**
- Establish team conventions for agent usage
- Create shared agent configurations and instruction files
- Conduct code reviews even for agent-generated code
- Share insights and best practices across the team

### Agent Customization and Configuration

**Creating Custom Agents:**

1. **Define Agent Purpose and Scope**
   ```json
   {
     "agents": [
       {
         "name": "database-expert",
         "description": "Specialized in database schema design and query optimization",
         "tools": ["sql", "database-profiler", "migration-generator"],
         "model": "gpt-4",
         "systemPrompt": "You are a database expert specializing in PostgreSQL..."
       }
     ]
   }
   ```

2. **Configure Tool Access**
   - Specify which tools and APIs the agent can access
   - Set rate limits and usage quotas
   - Define error handling and fallback strategies

3. **Establish Guardrails**
   - Define code quality thresholds
   - Set up automated validation rules
   - Implement human-in-the-loop checkpoints for critical operations

**Example Agent Configuration Files:**

**.github/copilot-instructions.md**: Repository-level instructions
**.vscode/agents.json**: Custom agent definitions
**.vscode/settings.json**: VS Code and Copilot settings
**agent.config.yaml**: Advanced agent behavior configuration

**Integration with CI/CD:**
- Automate agent-driven code reviews in pull requests
- Run agent-generated tests in CI pipelines
- Use agents to generate release notes and documentation
- Implement automated security scanning of agent changes

By effectively leveraging AI agents in VS Code, development teams can significantly accelerate feature development, improve code quality, and reduce cognitive load on developers, allowing them to focus on high-level architectural decisions and creative problem-solving.

## Steps to Create an AI Agent

### Prerequisites

Before developing an AI agent, ensure you have the following foundational knowledge and resources:

**Technical Prerequisites:**
- Proficiency in Python or JavaScript programming
- Understanding of REST APIs and HTTP protocols
- Familiarity with Large Language Models (LLMs) and their APIs
- Knowledge of software design patterns and architecture principles
- Experience with version control systems (Git) and containerization (Docker)

**Infrastructure Requirements:**
- Access to LLM APIs (OpenAI GPT, Anthropic Claude, Google Gemini, or open-source alternatives)
- Development environment with package management (pip, npm, conda)
- Database systems for persistent storage (PostgreSQL, MongoDB, or vector databases)
- API rate limiting and error handling capabilities

### Step 1: Task Definition and Scope Analysis

**Objective**: Clearly articulate the agent's purpose, constraints, and success criteria.

**Activities:**
- Define the problem domain and target user base
- Establish measurable performance metrics and evaluation criteria
- Identify required input/output formats and data types
- Document edge cases and failure scenarios
- Create user stories and acceptance criteria

**Deliverables:**
- Task specification document
- Success metrics definition
- Risk assessment and mitigation strategies

### Step 2: Tool Repository Development

**Objective**: Create a comprehensive toolkit of functions and external integrations.

**Tool Categories:**
- **Information Retrieval**: Web scraping, database queries, API integrations
- **Data Processing**: Text analysis, image processing, mathematical computations
- **Communication**: Email sending, messaging platforms, notification systems
- **File Operations**: Document creation, data export, file management
- **External Services**: Cloud services, third-party APIs, specialized platforms

**Implementation Guidelines:**
- Implement standardized tool interfaces with consistent error handling
- Create comprehensive tool documentation and usage examples
- Establish rate limiting and authentication mechanisms
- Implement tool validation and testing procedures
- Design modular architecture for easy tool addition and removal

### Step 3: Framework Selection and Architecture Design

**Objective**: Choose appropriate frameworks and design system architecture.

**Architecture Decisions:**
- Select agent framework based on requirements (see frameworks section below)
- Design conversation flow and state management systems
- Implement memory systems for context retention
- Create error handling and recovery mechanisms
- Establish logging and monitoring infrastructure

**Key Components:**
- **Agent Core**: Main reasoning and decision-making engine
- **Tool Manager**: Interface for tool discovery and execution
- **Memory System**: Context storage and retrieval mechanisms
- **Communication Layer**: Input/output handling and user interaction
- **Monitoring System**: Performance tracking and debugging capabilities

### Step 4: Implementation and Integration

**Objective**: Deploy the complete agent system with comprehensive testing.

**Development Phase:**
- Implement agent logic using chosen framework
- Integrate all tools with proper error handling
- Create comprehensive test suites (unit, integration, end-to-end)
- Implement continuous integration and deployment pipelines
- Establish monitoring and alerting systems

**Testing Strategies:**
- **Unit Testing**: Individual tool and component validation
- **Integration Testing**: Inter-component communication verification
- **Performance Testing**: Load testing and response time analysis
- **User Acceptance Testing**: Real-world scenario validation
- **Security Testing**: Authentication, authorization, and data protection validation

**Deployment Considerations:**
- Containerization for consistent environments
- Horizontal scaling capabilities
- Database migration and backup strategies
- API versioning and backward compatibility
- Documentation and user training materials

## Open-Source Tools and Frameworks for AI Agents (2025)

### Enterprise-Grade Frameworks

#### **LangChain**
*Location: `./LangChain/`*
- **Description**: Comprehensive framework for building LLM-powered applications with extensive tool integration
- **Key Features**: Chain composition, memory management, document loaders, vector store integrations
- **Best For**: Complex multi-step workflows, RAG applications, production deployments
- **Language Support**: Python, JavaScript/TypeScript
- **Notable Integrations**: OpenAI, Anthropic, Pinecone, Chroma, Weaviate

#### **LangGraph**
*Location: `./LangGraph/`*
- **Description**: Graph-based framework for building stateful, multi-actor applications with LLMs
- **Key Features**: Cyclic graph execution, state management, human-in-the-loop workflows
- **Best For**: Complex agent workflows, multi-agent systems, conversational AI
- **Language Support**: Python
- **Notable Features**: Built-in persistence, streaming support, conditional execution

#### **LlamaIndex**
*Location: `./LlamaIndex/`*
- **Description**: Data framework specialized for connecting LLMs with external data sources
- **Key Features**: Advanced RAG techniques, query engines, knowledge graph integration
- **Best For**: Document analysis, knowledge base construction, semantic search
- **Language Support**: Python, TypeScript
- **Data Connectors**: 160+ connectors including databases, APIs, file systems

### Specialized Agent Frameworks

#### **Haystack**
*Location: `./Haystack/`*
- **Description**: End-to-end NLP framework with strong focus on search and question-answering
- **Key Features**: Pipeline architecture, neural search, document preprocessing
- **Best For**: Search applications, QA systems, information extraction
- **Language Support**: Python
- **Production Features**: REST API, Docker support, evaluation tools

#### **Semantic Kernel**
*Location: `./Semantic Kernel/`*
- **Description**: Microsoft's lightweight SDK for integrating AI services
- **Key Features**: Function calling, prompt templating, memory connectors
- **Best For**: Enterprise integration, .NET applications, Microsoft ecosystem
- **Language Support**: C#, Python, Java
- **Enterprise Features**: Azure integration, security frameworks, governance

#### **Agent Development Kit (ADK)**
*Location: `./Agent Development Kit/`*
- **Description**: Google's comprehensive toolkit for building AI agents
- **Key Features**: Multi-modal capabilities, tool integration, deployment automation
- **Best For**: Scalable agent development, Google Cloud integration
- **Language Support**: Python, Go
- **Cloud Integration**: Vertex AI, Google Cloud services

### No-Framework Approach
*Location: `./No Framework/`*
- **Description**: Custom implementation using direct API calls and minimal dependencies
- **Key Features**: Maximum flexibility, minimal overhead, custom architecture
- **Best For**: Educational purposes, specific requirements, performance-critical applications
- **Advantages**: Full control, minimal dependencies, custom optimization
- **Considerations**: Higher development effort, manual implementation of common patterns

### Framework Comparison Matrix

| Framework | Complexity | Learning Curve | Production Ready | Community | Use Case Focus |
|-----------|------------|----------------|------------------|-----------|----------------|
| LangChain | High | Moderate | ✅ | Large | General Purpose |
| LangGraph | High | Steep | ✅ | Growing | Complex Workflows |
| LlamaIndex | Moderate | Moderate | ✅ | Large | Data-Centric |
| Haystack | Moderate | Moderate | ✅ | Medium | Search/QA |
| Semantic Kernel | Low | Easy | ✅ | Medium | Enterprise |
| ADK | High | Steep | ✅ | Small | Google Ecosystem |
| No Framework | Variable | Easy | Depends | N/A | Custom Solutions |

### Selection Criteria of Framework for AI Agents

**Choose LangChain if:** You need comprehensive tooling, extensive integrations, and rapid prototyping capabilities

**Choose LangGraph if:** You're building complex, stateful agents with multiple interaction patterns

**Choose LlamaIndex if:** Your primary focus is document analysis and knowledge retrieval

**Choose Haystack if:** You're building search-centric applications with strong NLP requirements

**Choose Semantic Kernel if:** You're working in enterprise environments with Microsoft technologies

**Choose No Framework if:** You have specific performance requirements or educational goals

## References

### Academic and Research

**Foundation Papers:**
- Russell, S., & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson Education.
- Wooldridge, M. (2020). *An Introduction to MultiAgent Systems* (2nd ed.). John Wiley & Sons.
- Yao, S., et al. (2024). "ReAct: Synergizing Reasoning and Acting in Language Models." *International Conference on Learning Representations*.

**Recent Advances (2024-2025):**
- Wei, J., et al. (2024). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *Nature Machine Intelligence*.
- Park, J. S., et al. (2024). "Generative Agents: Interactive Simulacra of Human Behavior." *ACM Transactions on Computer-Human Interaction*.
- Xi, Z., et al. (2024). "The Rise and Potential of Large Language Model Based Agents: A Survey." *arXiv preprint arXiv:2309.07864*.

### Documentation and Tutorials

**Framework Documentation:**
- **LangChain**: https://python.langchain.com/docs/
- **LangGraph**: https://langraph-doc.readthedocs.io/
- **LlamaIndex**: https://docs.llamaindex.ai/
- **Haystack**: https://docs.haystack.deepset.ai/
- **Semantic Kernel**: https://learn.microsoft.com/en-us/semantic-kernel/
- **Google ADK**: https://google.github.io/adk-docs/

**Industry Resources:**
- **OpenAI API Documentation**: https://platform.openai.com/docs/
- **Anthropic Claude Documentation**: https://docs.anthropic.com/
- **Google AI Documentation**: https://ai.google.dev/
- **Hugging Face Transformers**: https://huggingface.co/docs/transformers/

**Tutorials**
- **Using agents in Visual Studio Code**: https://code.visualstudio.com/docs/copilot/agents/overview
- **Work with agents in VS Code**: https://code.visualstudio.com/docs/copilot/agents/agents-tutorial

### Open Source Repositories

**Framework Repositories:**
- **LangChain**: https://github.com/langchain-ai/langchain
- **LangGraph**: https://github.com/langchain-ai/langgraph
- **LlamaIndex**: https://github.com/run-llama/llama_index
- **Haystack**: https://github.com/deepset-ai/haystack
- **Semantic Kernel**: https://github.com/microsoft/semantic-kernel

**Community Projects:**
- **AutoGen**: https://github.com/microsoft/autogen
- **CrewAI**: https://github.com/joaomdmoura/crewAI
- **OpenDevin**: https://github.com/OpenDevin/OpenDevin
- **SWE-agent**: https://github.com/princeton-nlp/SWE-agent

### Reports and Whitepapers

**Market Analysis:**
- McKinsey Global Institute. (2024). "The Age of AI: Artificial Intelligence and the Future of Work."
- Gartner. (2024). "Hype Cycle for Artificial Intelligence, 2024."
- Stanford HAI. (2024). "Artificial Intelligence Index Report 2024."

**Technical Whitepapers:**
- Google Research. (2024). "PaLM 2 Technical Report."
- OpenAI. (2024). "GPT-4 Technical Report."
- Anthropic. (2024). "Constitutional AI: Harmlessness from AI Feedback."

### Online Learning

**Courses and Tutorials:**
- **CS50's Introduction to AI with Python** (Harvard): https://cs50.harvard.edu/ai/
- **Deep Learning Specialization** (Coursera): https://www.coursera.org/specializations/deep-learning
- **LangChain & Vector Databases in Production** (ActiveLoop): https://learn.activeloop.ai/
- **AI Agents Course** (Hugging Face): https://huggingface.co/learn/agents-course/unit0/introduction

**Video Resources:**
- **Andrej Karpathy's Neural Networks Course**: https://karpathy.ai/
- **DeepLearning.AI Short Courses**: https://www.deeplearning.ai/short-courses/
- **Weights & Biases ML Course**: https://www.wandb.courses/

### Communities

**Research Communities:**
- **Association for Computing Machinery (ACM)**: https://www.acm.org/
- **International Joint Conference on AI (IJCAI)**: https://www.ijcai.org/
- **Neural Information Processing Systems (NeurIPS)**: https://neurips.cc/

**Developer Communities:**
- **AI/ML Reddit**: https://www.reddit.com/r/MachineLearning/
- **Hugging Face Community**: https://huggingface.co/
- **Papers with Code**: https://paperswithcode.com/

**What is an AI Agent?**
- Google Cloud. (2025). "What are AI Agents?" https://cloud.google.com/discover/what-are-ai-agents?hl=en
- Amazon Web Services. (2025). "What are AI Agents?" https://aws.amazon.com/what-is/ai-agents/
