"""
AWS Fargate Application for Strands Agent

This module provides a Flask-based web server for deploying a Strands agent
on AWS Fargate.
"""

from flask import Flask, request, jsonify
from strands import Agent
from strands_tools import http_request
import os

app = Flask(__name__)

# Initialize the agent
AGENT_SYSTEM_PROMPT = """You are a helpful AI assistant powered by Strands Agents.
You can help users with various tasks using the tools available to you."""

agent = Agent(
    system_prompt=AGENT_SYSTEM_PROMPT,
    tools=[http_request]
)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for container orchestration."""
    return jsonify({'status': 'healthy'}), 200


@app.route('/agent', methods=['POST'])
def agent_endpoint():
    """
    Agent endpoint to process user queries.
    
    Expects JSON body with 'query' field.
    Returns JSON with agent response.
    """
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        # Get response from the agent
        response = agent(user_query)
        
        return jsonify({
            'response': str(response),
            'query': user_query
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
