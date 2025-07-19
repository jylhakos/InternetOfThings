// JavaScript/Node.js Example Client for AI Agent
// This demonstrates how to interact with the Python-based AI Agent API

const https = require('http'); // Use 'https' for HTTPS endpoints

// Configuration
const BASE_URL = 'http://localhost:8000';

/**
 * Send a chat completion request to the AI Agent
 * @param {string} message - The user message
 * @param {number} temperature - Sampling temperature (0.0 to 1.0)
 * @returns {Promise<string>} - The agent's response
 */
async function chatWithAgent(message, temperature = 0.7) {
    const payload = JSON.stringify({
        messages: [{ role: 'user', content: message }],
        temperature: temperature
    });

    const options = {
        hostname: 'localhost',
        port: 8000,
        path: '/v1/chat/completions',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(payload)
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                try {
                    const response = JSON.parse(data);
                    if (response.choices && response.choices[0]) {
                        resolve(response.choices[0].message.content);
                    } else {
                        reject(new Error('Invalid response format'));
                    }
                } catch (error) {
                    reject(error);
                }
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        req.write(payload);
        req.end();
    });
}

/**
 * Check agent health
 * @returns {Promise<Object>} - Health status object
 */
async function checkHealth() {
    const options = {
        hostname: 'localhost',
        port: 8000,
        path: '/health',
        method: 'GET'
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (error) {
                    reject(error);
                }
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        req.end();
    });
}

/**
 * Example usage and testing
 */
async function runExamples() {
    console.log('🚀 AI Agent JavaScript Client Examples');
    console.log('=====================================');

    try {
        // Health check
        console.log('\n🏥 Health Check...');
        const health = await checkHealth();
        console.log(`Status: ${health.status}`);
        console.log(`LLM: ${health.services.llm}`);
        console.log(`Weather API: ${health.services.weather_api}`);

        // Example conversations
        const examples = [
            'Hello, how are you?',
            'What is the temperature in London?',
            'Tell me about Python programming',
            'Good morning!',
            'What\'s the weather like in Tokyo?'
        ];

        console.log('\n💬 Chat Examples...');
        for (const message of examples) {
            console.log(`\nUser: ${message}`);
            try {
                const response = await chatWithAgent(message);
                console.log(`Agent: ${response.substring(0, 100)}${response.length > 100 ? '...' : ''}`);
            } catch (error) {
                console.log(`Error: ${error.message}`);
            }
        }

    } catch (error) {
        console.error('❌ Error:', error.message);
        console.log('\nMake sure the AI Agent server is running:');
        console.log('  python src/index.py');
    }
}

// Export functions for use as a module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        chatWithAgent,
        checkHealth,
        runExamples
    };
}

// Run examples if this file is executed directly
if (require.main === module) {
    runExamples();
}

// Browser-compatible version (if needed)
if (typeof window !== 'undefined') {
    window.AIAgentClient = {
        chatWithAgent: async (message, temperature = 0.7) => {
            const response = await fetch('/v1/chat/completions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: [{ role: 'user', content: message }],
                    temperature: temperature
                })
            });
            
            const data = await response.json();
            return data.choices[0].message.content;
        },
        
        checkHealth: async () => {
            const response = await fetch('/health');
            return await response.json();
        }
    };
}