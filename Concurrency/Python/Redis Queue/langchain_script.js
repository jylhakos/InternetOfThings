#!/usr/bin/env node

/**
 * Standalone LangChain.js Script for Ollama Integration
 * This script can be executed directly by the Python worker as a fallback
 * when the HTTP service is not available.
 */

const { Ollama } = require('@langchain/ollama');
const { PromptTemplate } = require('@langchain/core/prompts');
const { LLMChain } = require('langchain/chains');
require('dotenv').config();

// Read input from stdin
function readStdin() {
    return new Promise((resolve) => {
        let data = '';
        process.stdin.setEncoding('utf8');
        
        process.stdin.on('readable', () => {
            let chunk = process.stdin.read();
            if (chunk !== null) {
                data += chunk;
            }
        });
        
        process.stdin.on('end', () => {
            resolve(data.trim());
        });
    });
}

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

async function processRequest(inputData) {
    const startTime = Date.now();
    
    try {
        const {
            question,
            model = 'llama3.2:1b',
            temperature = 0.7,
            max_tokens = 500,
            template_type = 'default'
        } = inputData;

        // Validate input
        if (!question || typeof question !== 'string' || question.trim().length === 0) {
            throw new Error('Question is required and must be a non-empty string');
        }

        // Configure Ollama
        const ollama = new Ollama({
            baseUrl: process.env.OLLAMA_HOST || 'http://localhost:11434',
            model: model,
            temperature: temperature,
            maxTokens: max_tokens,
        });

        // Get the appropriate prompt template
        const promptTemplate = templates[template_type] || templates.default;

        // Create LLM Chain
        const chain = new LLMChain({
            llm: ollama,
            prompt: promptTemplate,
        });

        // Generate response
        const result = await chain.call({
            question: question.trim()
        });

        const processingTime = (Date.now() - startTime) / 1000;

        // Return result as JSON
        const output = {
            response: result.text.trim(),
            model_used: model,
            template_used: template_type,
            processing_time: processingTime,
            success: true,
            timestamp: new Date().toISOString()
        };

        console.log(JSON.stringify(output, null, 2));

    } catch (error) {
        const processingTime = (Date.now() - startTime) / 1000;
        
        const errorOutput = {
            error: error.message || 'An error occurred while processing the request',
            processing_time: processingTime,
            success: false,
            timestamp: new Date().toISOString()
        };

        console.error(JSON.stringify(errorOutput, null, 2));
        process.exit(1);
    }
}

// Main execution
async function main() {
    try {
        // Check if arguments are provided directly
        if (process.argv.length > 2) {
            // Direct argument mode (for testing)
            const question = process.argv.slice(2).join(' ');
            await processRequest({ question });
        } else {
            // Stdin mode (default for worker integration)
            const input = await readStdin();
            const inputData = JSON.parse(input);
            await processRequest(inputData);
        }
    } catch (error) {
        console.error(JSON.stringify({
            error: `Failed to parse input or process request: ${error.message}`,
            success: false,
            timestamp: new Date().toISOString()
        }, null, 2));
        process.exit(1);
    }
}

// Run if this script is executed directly
if (require.main === module) {
    main();
}

module.exports = { processRequest, templates };
