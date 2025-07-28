/**
 * LangChain.js Service for Ollama Integration
 * This service provides an HTTP API for LLM interactions using LangChain and Ollama
 */

const express = require('express');
const cors = require('cors');
const { Ollama } = require('@langchain/ollama');
const { PromptTemplate } = require('@langchain/core/prompts');
const { LLMChain } = require('langchain/chains');
require('dotenv').config();

// Initialize Express app
const app = express();
const PORT = process.env.LANGCHAIN_SERVICE_PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Configure Ollama
const ollama = new Ollama({
    baseUrl: process.env.OLLAMA_HOST || 'http://localhost:11434',
    model: process.env.DEFAULT_MODEL || 'llama3.2:1b',
    temperature: 0.7,
});

// Define prompt templates
const templates = {
    default: PromptTemplate.fromTemplate(
        "You are a helpful assistant. Answer the following question accurately and concisely:\n\nQuestion: {question}\n\nAnswer:"
    ),
    
    chat: PromptTemplate.fromTemplate(
        "You are a helpful AI assistant in a chat conversation. Provide a friendly and informative response to the user's message.\n\nUser: {question}\n\nAssistant:"
    ),
    
    technical: PromptTemplate.fromTemplate(
        "You are a technical expert. Provide a detailed and accurate technical response to the following question:\n\nQuestion: {question}\n\nTechnical Response:"
    ),
    
    creative: PromptTemplate.fromTemplate(
        "You are a creative assistant. Provide an imaginative and engaging response to the following prompt:\n\nPrompt: {question}\n\nCreative Response:"
    )
};

// Helper function to get appropriate template
function getTemplate(type = 'default') {
    return templates[type] || templates.default;
}

// Health check endpoint
app.get('/health', async (req, res) => {
    try {
        // Test Ollama connection
        const testResponse = await ollama.invoke("Test connection");
        res.json({
            status: 'healthy',
            service: 'LangChain.js Service',
            ollama_connection: 'connected',
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            status: 'unhealthy',
            service: 'LangChain.js Service',
            ollama_connection: 'disconnected',
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// Main generation endpoint
app.post('/generate', async (req, res) => {
    const startTime = Date.now();
    
    try {
        const {
            question,
            model = 'llama3.2:1b',
            temperature = 0.7,
            max_tokens = 500,
            template_type = 'default'
        } = req.body;

        // Validate input
        if (!question || typeof question !== 'string' || question.trim().length === 0) {
            return res.status(400).json({
                error: 'Question is required and must be a non-empty string',
                success: false
            });
        }

        console.log(`Processing request: ${question.substring(0, 50)}...`);

        // Configure Ollama for this request
        const ollamaInstance = new Ollama({
            baseUrl: process.env.OLLAMA_HOST || 'http://localhost:11434',
            model: model,
            temperature: temperature,
            maxTokens: max_tokens,
        });

        // Get the appropriate prompt template
        const promptTemplate = getTemplate(template_type);

        // Create LLM Chain
        const chain = new LLMChain({
            llm: ollamaInstance,
            prompt: promptTemplate,
        });

        // Generate response
        const result = await chain.call({
            question: question.trim()
        });

        const processingTime = (Date.now() - startTime) / 1000;

        console.log(`Request completed in ${processingTime.toFixed(2)} seconds`);

        res.json({
            response: result.text.trim(),
            model_used: model,
            template_used: template_type,
            processing_time_seconds: processingTime,
            success: true,
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        const processingTime = (Date.now() - startTime) / 1000;
        
        console.error('Error processing request:', error);
        
        res.status(500).json({
            error: error.message || 'An error occurred while processing the request',
            processing_time_seconds: processingTime,
            success: false,
            timestamp: new Date().toISOString()
        });
    }
});

// Batch processing endpoint
app.post('/generate_batch', async (req, res) => {
    const startTime = Date.now();
    
    try {
        const {
            questions,
            model = 'llama3.2:1b',
            temperature = 0.7,
            max_tokens = 500,
            template_type = 'default'
        } = req.body;

        if (!Array.isArray(questions) || questions.length === 0) {
            return res.status(400).json({
                error: 'Questions must be a non-empty array',
                success: false
            });
        }

        console.log(`Processing batch of ${questions.length} questions`);

        const ollamaInstance = new Ollama({
            baseUrl: process.env.OLLAMA_HOST || 'http://localhost:11434',
            model: model,
            temperature: temperature,
            maxTokens: max_tokens,
        });

        const promptTemplate = getTemplate(template_type);
        const chain = new LLMChain({
            llm: ollamaInstance,
            prompt: promptTemplate,
        });

        // Process all questions
        const results = await Promise.all(
            questions.map(async (question, index) => {
                try {
                    const result = await chain.call({ question: question.trim() });
                    return {
                        index,
                        question,
                        response: result.text.trim(),
                        success: true
                    };
                } catch (error) {
                    return {
                        index,
                        question,
                        error: error.message,
                        success: false
                    };
                }
            })
        );

        const processingTime = (Date.now() - startTime) / 1000;

        res.json({
            results,
            model_used: model,
            template_used: template_type,
            processing_time_seconds: processingTime,
            success: true,
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        const processingTime = (Date.now() - startTime) / 1000;
        
        console.error('Error processing batch request:', error);
        
        res.status(500).json({
            error: error.message || 'An error occurred while processing the batch request',
            processing_time_seconds: processingTime,
            success: false,
            timestamp: new Date().toISOString()
        });
    }
});

// Get available models endpoint
app.get('/models', async (req, res) => {
    try {
        // This would typically call Ollama's API to list available models
        // For now, return a default list
        res.json({
            models: [
                'llama3.2:1b',
                'llama3.2:3b',
                'llama3.1:8b',
                'codellama:7b',
                'mistral:7b'
            ],
            default_model: process.env.DEFAULT_MODEL || 'llama3.2:1b'
        });
    } catch (error) {
        res.status(500).json({
            error: 'Failed to retrieve models',
            success: false
        });
    }
});

// Get available templates endpoint
app.get('/templates', (req, res) => {
    res.json({
        templates: Object.keys(templates),
        default_template: 'default'
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`LangChain.js Service running on port ${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
    console.log(`Generation endpoint: http://localhost:${PORT}/generate`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\nShutting down LangChain.js Service...');
    process.exit(0);
});

module.exports = app;
