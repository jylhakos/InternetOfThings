# Prompt Engineering for Large Language Models

## Table of Contents
- [Project Structure](#project-structure)
- [What is a Prompt?](#what-is-a-prompt)
- [Prompt Types](#prompt-types)
  - [1. Chat Style Prompts](#1-chat-style-prompts)
  - [2. Completion Style Prompts](#2-completion-style-prompts)
- [Why Utilize Prompt Engineering?](#why-utilize-prompt-engineering)
- [How to Write Prompts for Open Source LLMs](#how-to-write-prompts-for-open-source-llms)
- [Prompting Techniques](#prompting-techniques)
  - [Zero-Shot Prompting](#zero-shot-prompting)
  - [Few-Shot Prompting](#few-shot-prompting)
  - [Role-Based Prompts](#role-based-prompts)
  - [Chain-of-Thought Prompting](#chain-of-thought-prompting)
- [Principles for Prompting](#principles-for-prompting)
- [Prompts vs. Prompt Templates](#prompts-vs-prompt-templates)
- [Example Prompt Template](#example-prompt-template)
- [Common LLM Tasks](#common-llm-tasks)
  - [Question Answering](#question-answering)
  - [Code Generation](#code-generation)
  - [Reasoning](#reasoning)
- [Fine-Tuning Prompts](#fine-tuning-prompts)
  - [How to Define Prompts for Fine-Tuning?](#how-to-define-prompts-for-fine-tuning)
  - [Defining Fine-Tuning Prompts](#defining-fine-tuning-prompts)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Example](#running-the-example)
- [References](#references)
  - [Official Documentation](#official-documentation)
  - [Tutorials and Guides](#tutorials-and-guides)
  - [Research Papers](#research-papers)
  - [Community Resources](#community-resources)
- [License](#license)
- [Contributing](#contributing)

## Project Structure

```
📁 PROMPTS/
├── 📄 .gitignore              # Git ignore file (excludes venv, cache, binaries)
├── 📄 README.md               # This file - documentation
├── 📄 QUICKSTART.md           # Quick setup guide with troubleshooting
├── 📄 requirements.txt        # Python dependencies
├── 📄 prompt_template_example.py  # Working examples with LangChain & Ollama
└── 📁 venv/                   # Python virtual environment (excluded from Git)
```

## What is a Prompt?

A **prompt** is an instruction to an LLM (Large Language Model). If you have interacted with an LLM like ChatGPT, you have used prompts. A prompt guides the model's behavior without changing its underlying capabilities. By providing instructions, examples, and context, prompts shape how the model responds to inputs.

## Prompt Types

There are two different types of prompt formats:

### 1. Chat Style Prompts
Chat prompts are a list of messages, each with a role (such as `system`, `user`, or `assistant`). This is the prompting style supported by most current model APIs and is the recommended format.

**Example:**
```json
[
  {"role": "system", "content": "You are a helpful assistant."},
  {"role": "user", "content": "What is prompt engineering?"},
  {"role": "assistant", "content": "Prompt engineering is..."}
]
```

### 2. Completion Style Prompts
Completion prompts are a single string. This is an older prompting style maintained primarily for backward compatibility.

**Example:**
```
Complete the following sentence: The capital of France is
```

## Why Utilize Prompt Engineering?

Prompt engineering is crucial because it:

- **Maximizes Model Performance**: Well-crafted prompts help extract the best possible output from an LLM without fine-tuning
- **Ensures Consistency**: Structured prompts produce more predictable and reliable results
- **Saves Resources**: Effective prompting can eliminate the need for expensive model retraining
- **Enhances Control**: Allows precise control over output format, tone, and content
- **Reduces Errors**: Clear instructions minimize misinterpretations and hallucinations

## How to Write Prompts for Open Source LLMs

Writing effective prompts for open-source LLMs (like Llama 3 or Mistral) involves being explicit, providing context, using clear delimiters, and using iterative refinement. Key strategies include:

1. **Assigning a Persona**: Tell the model who it should be (e.g., "You are an expert data scientist")
2. **Defining the Specific Task**: Be clear about what you want the model to do
3. **Formatting Output Constraints**: Specify exactly how you want the output formatted
4. **Chain-of-Thought Prompting**: Use phrases like "think step-by-step" to improve reasoning

## Prompting Techniques

### Zero-Shot Prompting

**What is Zero-Shot Prompting?**

Modern LLMs like Llama are capable of following instructions and producing responses without having previously seen an example of a task. Prompting without examples is called "zero-shot prompting".

**Example:**
```
Translate the following English phrase to French: Hello, world!
```

### Few-Shot Prompting

**What is Few-Shot Prompting?**

A **shot** is an example or demonstration of what type of prompt and response you expect from a large language model. Adding specific examples of your desired output generally results in a more accurate, consistent output when compared with zero-shot prompting. This technique is called "few-shot prompting".

**Example:**
```
Classify the sentiment of the following reviews:

Review: "The product exceeded my expectations!"
Sentiment: Positive

Review: "Terrible quality, broke after one day."
Sentiment: Negative

Review: "The service was okay, nothing special."
Sentiment: Neutral

Review: "Amazing value for money!"
Sentiment: ?
```

### Role-Based Prompts

**What are Role-Based Prompts?**

Creating prompts based on the role or perspective of the person or entity being addressed can be useful for generating more relevant and engaging responses from the model.

**Example:**
```
Act as a senior Python developer with 10 years of experience.
Review the following code and suggest improvements...
```

### Chain-of-Thought Prompting

**What is Chain-of-Thought Prompting?**

Chain-of-thought prompting provides the language model with a series of prompts or questions to help guide its thinking and generate a more coherent and relevant response. This technique significantly improves reasoning capabilities.

**Example:**
```
Solve this problem step-by-step:
If a train travels 120 miles in 2 hours, what is its average speed?

Let's think step-by-step:
1. First, identify the formula: speed = distance / time
2. Then, plug in the values: speed = 120 miles / 2 hours
3. Calculate: speed = 60 miles per hour
```

## Principles for Prompting

Open-source models, while powerful, often require more precise instructions than proprietary counterparts.

### Key Principles:

1. **Be Explicit**: Avoid ambiguity. Instead of "Write a report," try "Write a 300-word report on project risks in markdown format"

2. **Role Prompting**: Actively assign a persona to set context
   ```
   Act as a senior python developer
   ```

3. **Use Delimiters**: Use triple quotes (`"""`), backticks (` ``` `), or tags (`<tag></tag>`) to isolate input data or instructions from context

4. **Structure Your Input**: Follow a structure: **Role → Task → Context → Constraint**

### Prompting Techniques:

- **Chain-of-Thought (CoT)**: Ask the model to "think step-by-step" to improve reasoning
- **Few-Shot Prompting**: Provide 2–5 examples within the prompt to guide the style and format of the output
- **Iterative Refinement**: Test, evaluate the output, and refine the prompt. If the model fails, break the task into smaller steps
- **Negative Constraints**: Explicitly state what to avoid (e.g., "Do not include introductory text")

## Prompts vs. Prompt Templates

While **prompt** and **prompt template** are often used interchangeably, understanding the distinction helps clarify how to manage and evaluate your AI application.

- **Prompts** refer to the messages that are passed into the language model
- **Prompt templates** allow you to create reusable prompts with dynamic placeholders that get filled in at runtime

Instead of hardcoding values, you define variables that get replaced with different inputs each time you run your prompt. This makes prompts flexible, testable, and easier to iterate on.

## Example Prompt Template

Here's a professional prompt template for data analysis:

```
System/Role: You are an expert data analyst.

Task: Summarize the main findings from the text provided below.

Constraints:
- Use bullet points.
- Maximum 5 bullets.
- Focus on financial metrics.

Text: """
[Insert PDF content here]
"""
```

**Using Variables:**
```python
template = """
You are a {role}.
{task}

Input: {input_text}
"""
```

## Common LLM Tasks

### Question Answering
One of the best ways to get the model to respond with specific answers is to improve the format of the prompt. Provide clear context and specify the expected answer format.

**Example:**
```
Context: Python is a high-level programming language created by Guido van Rossum.
Question: Who created Python?
Answer:
```

### Code Generation
Copilot is an example of where LLMs are quite effective in code generation. Clear prompts with examples produce better code.

**Example:**
```
Write a Python function that:
- Takes a list of numbers as input
- Returns the average of those numbers
- Handles empty lists gracefully
```

### Reasoning
One of the most difficult tasks for an LLM is one that requires some form of reasoning. Chain-of-thought prompting significantly improves reasoning performance.

## Fine-Tuning Prompts

### How to Define Prompts for Fine-Tuning?

Defining prompts for fine-tuning LLMs requires structuring data into consistent, task-specific instructions (e.g., "Summarize: [Text]") to teach the model desired behaviors. Effective tuning involves creating high-quality, diverse dataset examples, using consistent input templates, and employing techniques like few-shot prompting to guide output format, tone, and constraints.

### Defining Fine-Tuning Prompts

1. **Instruction Tuning**: Create clear, descriptive directives that tell the model exactly what to do
   ```
   Classify the sentiment of the following review:
   ```

2. **Structure Your Data**: Use a consistent template for all training examples
   ```
   <system prompt> + <input> + <output>
   ```

3. **Incorporate Few-Shot Examples**: Include 1–3 examples of input and desired output within the training data

4. **Define Constraints**: Clearly specify constraints within the prompt
   - "answer in less than 20 words"
   - "use bullet points"
   - "respond in JSON format"

5. **Diverse Data Quality**: Ensure your prompt dataset is diverse, accurate, and high-quality. Noisy or repetitive prompts can cause the model to fail in production.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Ollama (for running local LLMs)

### Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama** (if running models locally):
   - Visit [https://ollama.ai](https://ollama.ai)
   - Pull a model: `ollama pull llama2`

### Running the Example

```bash
python prompt_template_example.py
```

## References

### Official Documentation
- [Anthropic Claude Prompt Engineering Overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
- [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Claude Prompting Tools](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-tools)
- [Google ML Crash Course: Fine-tuning, Distillation, and Prompt Engineering](https://developers.google.com/machine-learning/crash-course/llm/tuning)
- [AWS SageMaker: Fine-tune LLM using Prompt Instructions](https://docs.aws.amazon.com/sagemaker/latest/dg/jumpstart-foundation-models-fine-tuning-instruction-based.html)

### Tutorials and Guides
- [Pinecone: Prompt Engineering and LLMs with LangChain](https://www.pinecone.io/learn/series/langchain/langchain-prompt-templates/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Ollama Documentation](https://github.com/ollama/ollama)

### Research Papers
- "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (Wei et al., 2022)
- "Language Models are Few-Shot Learners" (Brown et al., 2020)

### Community Resources
- [Awesome Prompt Engineering](https://github.com/promptslab/Awesome-Prompt-Engineering)
- [OpenAI Cookbook](https://cookbook.openai.com/)
- [Hugging Face Hub](https://huggingface.co/models)

---
