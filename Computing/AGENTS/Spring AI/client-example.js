// Example JavaScript/Node.js Client for Spring AI RAG Demo

const axios = require('axios');

class SpringAIChatClient {
    constructor(baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
        this.chatUrl = `${baseUrl}/api/chat`;
    }

    /**
     * Ask a simple question using default RAG settings
     * @param {string} question - The question to ask
     * @returns {Promise<Object>} Response with answer, sources, etc.
     */
    async askSimple(question) {
        const response = await axios.post(`${this.chatUrl}/ask`, null, {
            params: { question }
        });
        return response.data;
    }

    /**
     * Ask a question with advanced RAG parameters
     * @param {string} question - The question to ask
     * @param {boolean} includeContext - Whether to use RAG
     * @param {number} similarityThreshold - Minimum similarity score (0.0-1.0)
     * @param {number} topK - Number of documents to retrieve
     * @returns {Promise<Object>} Response with answer, sources, response time, etc.
     */
    async askAdvanced(question, {
        includeContext = true,
        similarityThreshold = 0.7,
        topK = 5
    } = {}) {
        const response = await axios.post(this.chatUrl, {
            question,
            includeContext,
            similarityThreshold,
            topK
        }, {
            headers: { 'Content-Type': 'application/json' }
        });
        return response.data;
    }

    /**
     * Check if the service is running
     * @returns {Promise<string>} Health status message
     */
    async healthCheck() {
        const response = await axios.get(`${this.chatUrl}/health`);
        return response.data;
    }
}

// Example usage
async function main() {
    const client = new SpringAIChatClient();

    try {
        // Health check
        console.log('Health Check:');
        const health = await client.healthCheck();
        console.log(health);
        console.log('\n' + '='.repeat(60) + '\n');

        // Example 1: Simple question
        console.log('Example 1: Simple Question');
        const result1 = await client.askSimple('What is Spring AI?');
        console.log('Question: What is Spring AI?');
        console.log('Answer:', result1.answer);
        console.log('Response Time:', result1.responseTimeMs + 'ms');
        console.log('Model:', result1.model);
        console.log('\n' + '='.repeat(60) + '\n');

        // Example 2: Advanced query
        console.log('Example 2: Advanced Query with Parameters');
        const result2 = await client.askAdvanced(
            'How does Retrieval Augmented Generation work?',
            { similarityThreshold: 0.8, topK: 3 }
        );
        console.log('Question: How does Retrieval Augmented Generation work?');
        console.log('Answer:', result2.answer);
        console.log('Sources:', result2.sources);
        console.log('Response Time:', result2.responseTimeMs + 'ms');
        console.log('\n' + '='.repeat(60) + '\n');

        // Example 3: High precision query
        console.log('Example 3: High Precision Query');
        const result3 = await client.askAdvanced(
            'What is the ChatClient API?',
            { similarityThreshold: 0.9, topK: 2 }
        );
        console.log('Question: What is the ChatClient API?');
        console.log('Answer:', result3.answer.substring(0, 200) + '...');
        console.log('Sources:', result3.sources);
        console.log('\n' + '='.repeat(60) + '\n');

        // Example 4: Direct query without RAG
        console.log('Example 4: Direct Query (No RAG)');
        const result4 = await client.askAdvanced(
            'What is 5 + 3?',
            { includeContext: false }
        );
        console.log('Question: What is 5 + 3?');
        console.log('Answer:', result4.answer);
        console.log('\n' + '='.repeat(60) + '\n');

    } catch (error) {
        console.error('Error: Could not connect to Spring AI service');
        console.error('Make sure the application is running on http://localhost:8080');
        console.error('Details:', error.message);
    }
}

// Run if executed directly
if (require.main === module) {
    main();
}

module.exports = SpringAIChatClient;
