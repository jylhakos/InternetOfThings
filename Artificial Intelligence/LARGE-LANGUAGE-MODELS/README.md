# Artificial Intelligence (AI)

## Example: LLM application deployed on AWS

To utilize AWS for AI, you can leverage services like Amazon SageMaker for model development and deployment, Amazon Bedrock for accessing and customizing foundation models.

Client (React) → API Gateway → Lambda/ECS → Vector DB (OpenSearch/Pinecone) → LLM (Ollama/vLLM)

1. Setting up the AWS

Amazon S3

Store your documents in an S3 bucket. 

S3 bucket provides scalable and durable storage for your knowledge base. 

Amazon SageMaker

Consider using SageMaker for deploying your LLM server and potentially other components like the embedding model.

Vector database

Choose a vector database like Pinecone, Milvus, or a managed service like Amazon OpenSearch Service or Amazon Aurora PostgreSQL with pgvector for storing document embeddings.

API Gateway

Set up API Gateway to handle incoming requests from your client application and route them to your backend service. 

Lambda Functions

Use Lambda functions to handle specific tasks like document processing, embedding generation, and RAG logic.

IAM Roles and Policies:

Ensure proper access control for your services using IAM roles and policies.

2. Deploying the LLM Server (e.g., Ollama)

Instance Type

Choose an appropriate EC2 instance type for your chosen LLM (e.g., GPU instances for larger models).

Ollama Setup

Install and configure Ollama on the EC2 instance, and download your desired open-source LLM (e.g., Llama 2, Mistral).

API endpoint

Expose an API endpoint from your Ollama server to receive requests and send responses.

3. Document processing and Embedding generation

Chunking

Break down your documents into smaller chunks to optimize embedding generation and search.

Embeddings model

Use an embedding model (e.g., SentenceTransformers, BGE embeddings) to convert text chunks into vector representations.

Vector storage

Store the generated embeddings in your chosen vector database, along with metadata about the original document chunks.

4. Building the RAG workflow

User Input 

The client sends a question to your API endpoint.

Vector Search

Your application queries the vector database to find the most relevant document chunks based on semantic similarity with the user's question.

Contextualization

Retrieve the content of the relevant document chunks.

Prompt Engineering

Construct a prompt that includes the user's question and the retrieved context.

LLM Inference

Send the prompt to your Ollama server (or your deployed LLM) to generate a response.

Response

Return the LLM's response to the client. 

References

Amazon SageMaker

https://aws.amazon.com/sagemaker/

