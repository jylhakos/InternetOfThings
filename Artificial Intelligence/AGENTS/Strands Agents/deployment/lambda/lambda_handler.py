"""
AWS Lambda Handler for Strands Agent

This module provides a Lambda function handler for deploying a Strands agent
behind an AWS Lambda function.
"""

import json
import os
from strands import Agent
from strands_tools import http_request

# Initialize the agent (reused across invocations)
AGENT_SYSTEM_PROMPT = """You are a helpful AI assistant powered by Strands Agents.
You can help users with various tasks using the tools available to you."""

agent = Agent(
    system_prompt=AGENT_SYSTEM_PROMPT,
    tools=[http_request]
)


def lambda_handler(event, context):
    """
    AWS Lambda handler function for Strands Agent.
    
    Args:
        event: Lambda event object containing the request
        context: Lambda context object
        
    Returns:
        dict: Response with statusCode and body
    """
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        user_query = body.get('query', '')
        
        if not user_query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing query parameter'
                })
            }
        
        # Get response from the agent
        response = agent(user_query)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': str(response),
                'query': user_query
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
