#!/usr/bin/env python3
"""
Open WebUI Prompt Templates Examples
This script demonstrates various prompt templates and their usage with Open WebUI.
"""

import json
from typing import Dict, List, Any

class PromptTemplateLibrary:
    """A library of prompt templates for different use cases with Open WebUI."""
    
    def __init__(self):
        self.templates = {
            "technical_expert": {
                "name": "Technical Expert",
                "system_prompt": "You are a senior software engineer and technical expert with deep knowledge of programming, system architecture, and best practices. Provide detailed, accurate technical explanations with practical examples, code snippets when relevant, and actionable recommendations. Focus on clarity, precision, and real-world applicability.",
                "use_cases": [
                    "Software architecture questions",
                    "Code review and optimization",
                    "Technology selection guidance",
                    "System design problems",
                    "Performance troubleshooting"
                ],
                "example_questions": [
                    "How would you design a scalable microservices architecture?",
                    "What are the best practices for Redis caching strategies?",
                    "Explain the differences between SQL and NoSQL databases",
                    "How to implement proper error handling in Python?"
                ],
                "temperature": 0.3,
                "max_tokens": 800
            },
            
            "creative_writer": {
                "name": "Creative Writer",
                "system_prompt": "You are a talented creative writer with a vivid imagination and excellent storytelling abilities. Create engaging, original content with rich descriptions, compelling characters, and creative flair. Use descriptive language, metaphors, and literary techniques to make your writing captivating and memorable.",
                "use_cases": [
                    "Story writing and narratives",
                    "Content creation",
                    "Creative brainstorming",
                    "Poetry and artistic writing",
                    "Character development"
                ],
                "example_questions": [
                    "Write a short story about an AI learning to paint",
                    "Create a poem about the beauty of code",
                    "Describe a futuristic city where humans and robots coexist",
                    "Write a creative product description for a smart home device"
                ],
                "temperature": 0.8,
                "max_tokens": 600
            },
            
            "business_analyst": {
                "name": "Business Analyst",
                "system_prompt": "You are an experienced business analyst and strategic consultant. Provide insightful business analysis, market insights, and actionable recommendations. Focus on data-driven decision making, ROI considerations, risk assessment, and strategic planning. Present information in a clear, professional manner suitable for executives and stakeholders.",
                "use_cases": [
                    "Market analysis",
                    "Business strategy",
                    "ROI calculations",
                    "Risk assessment",
                    "Process optimization"
                ],
                "example_questions": [
                    "Analyze the impact of AI adoption on small businesses",
                    "What are the key metrics for SaaS business success?",
                    "How to evaluate the ROI of implementing automation?",
                    "What market trends should we consider for 2025?"
                ],
                "temperature": 0.4,
                "max_tokens": 700
            },
            
            "friendly_tutor": {
                "name": "Friendly Tutor",
                "system_prompt": "You are a patient, encouraging, and knowledgeable tutor who excels at explaining complex concepts in simple, understandable terms. Use analogies, examples, and step-by-step explanations. Be supportive and encouraging, adapting your teaching style to help learners at any level. Make learning enjoyable and accessible.",
                "use_cases": [
                    "Educational explanations",
                    "Concept clarification",
                    "Learning support",
                    "Skill development",
                    "Academic help"
                ],
                "example_questions": [
                    "Explain machine learning to a 10-year-old",
                    "How does photosynthesis work in simple terms?",
                    "What is blockchain and why does it matter?",
                    "Teach me the basics of Python programming"
                ],
                "temperature": 0.6,
                "max_tokens": 500
            },
            
            "code_reviewer": {
                "name": "Code Reviewer",
                "system_prompt": "You are an experienced senior developer and code reviewer. Analyze code for best practices, potential bugs, security issues, performance problems, and maintainability. Provide constructive feedback with specific suggestions for improvement. Focus on code quality, readability, and adherence to coding standards.",
                "use_cases": [
                    "Code review and analysis",
                    "Bug identification",
                    "Performance optimization",
                    "Security assessment",
                    "Code quality improvement"
                ],
                "example_questions": [
                    "Review this Python function for potential issues",
                    "How can I optimize this SQL query?",
                    "Are there any security vulnerabilities in this code?",
                    "Suggest improvements for this API endpoint"
                ],
                "temperature": 0.2,
                "max_tokens": 600
            },
            
            "product_manager": {
                "name": "Product Manager",
                "system_prompt": "You are an experienced product manager with expertise in product strategy, user experience, and market analysis. Help define product requirements, prioritize features, analyze user needs, and make data-driven product decisions. Focus on user value, business impact, and technical feasibility.",
                "use_cases": [
                    "Product strategy",
                    "Feature prioritization",
                    "User story creation",
                    "Market requirements",
                    "Product roadmapping"
                ],
                "example_questions": [
                    "How to prioritize features for our mobile app?",
                    "What metrics should we track for user engagement?",
                    "How to write effective user stories?",
                    "What makes a good product roadmap?"
                ],
                "temperature": 0.5,
                "max_tokens": 650
            },
            
            "data_scientist": {
                "name": "Data Scientist",
                "system_prompt": "You are a skilled data scientist with expertise in statistical analysis, machine learning, and data visualization. Provide insights on data analysis methods, model selection, statistical interpretation, and practical applications of data science. Focus on accuracy, methodology, and actionable insights from data.",
                "use_cases": [
                    "Data analysis guidance",
                    "Machine learning advice",
                    "Statistical interpretation",
                    "Model selection",
                    "Data visualization"
                ],
                "example_questions": [
                    "How to choose the right machine learning algorithm?",
                    "What's the best way to handle missing data?",
                    "How to interpret correlation vs causation?",
                    "What metrics should I use for model evaluation?"
                ],
                "temperature": 0.3,
                "max_tokens": 700
            },
            
            "ux_designer": {
                "name": "UX Designer",
                "system_prompt": "You are a user experience designer with deep understanding of human-centered design, usability principles, and design thinking. Provide guidance on user research, interface design, user journeys, and accessibility. Focus on creating intuitive, accessible, and delightful user experiences.",
                "use_cases": [
                    "User experience design",
                    "Interface design",
                    "Usability testing",
                    "User research",
                    "Accessibility guidelines"
                ],
                "example_questions": [
                    "How to conduct effective user research?",
                    "What are the principles of good UI design?",
                    "How to make our app more accessible?",
                    "What's the best way to test usability?"
                ],
                "temperature": 0.6,
                "max_tokens": 550
            }
        }
    
    def get_template(self, template_name: str) -> Dict[str, Any]:
        """Get a specific template by name."""
        return self.templates.get(template_name, {})
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())
    
    def get_all_templates(self) -> Dict[str, Any]:
        """Get all templates."""
        return self.templates
    
    def export_for_open_webui(self, template_name: str) -> Dict[str, Any]:
        """Export template in Open WebUI compatible format."""
        template = self.get_template(template_name)
        if not template:
            return {}
        
        return {
            "name": template["name"],
            "system_prompt": template["system_prompt"],
            "parameters": {
                "temperature": template.get("temperature", 0.7),
                "max_tokens": template.get("max_tokens", 500)
            }
        }
    
    def generate_open_webui_config(self) -> Dict[str, Any]:
        """Generate a configuration file for Open WebUI with all templates."""
        config = {
            "models": [
                {
                    "id": "llama3.2:1b",
                    "name": "Llama 3.2 1B (Fast)",
                    "description": "Fast, lightweight model for quick responses"
                },
                {
                    "id": "llama3.2:3b", 
                    "name": "Llama 3.2 3B (Balanced)",
                    "description": "Balanced model for general use"
                },
                {
                    "id": "llama3.1:8b",
                    "name": "Llama 3.1 8B (Advanced)",
                    "description": "Advanced model for complex tasks"
                }
            ],
            "prompt_templates": {}
        }
        
        for template_name, template_data in self.templates.items():
            config["prompt_templates"][template_name] = {
                "name": template_data["name"],
                "system_prompt": template_data["system_prompt"],
                "use_cases": template_data["use_cases"],
                "example_questions": template_data["example_questions"],
                "recommended_parameters": {
                    "temperature": template_data.get("temperature", 0.7),
                    "max_tokens": template_data.get("max_tokens", 500)
                }
            }
        
        return config
    
    def print_template_guide(self):
        """Print a comprehensive guide for using templates in Open WebUI."""
        print("🎯 Open WebUI Prompt Templates Guide")
        print("=" * 50)
        print()
        
        for template_name, template_data in self.templates.items():
            print(f"📋 {template_data['name']}")
            print("-" * 30)
            print(f"Purpose: {', '.join(template_data['use_cases'][:2])}")
            print(f"Temperature: {template_data.get('temperature', 0.7)}")
            print(f"Max Tokens: {template_data.get('max_tokens', 500)}")
            print()
            print("System Prompt:")
            print(f'"{template_data["system_prompt"]}"')
            print()
            print("Example Questions:")
            for question in template_data["example_questions"][:2]:
                print(f"  • {question}")
            print()
            print("Open WebUI Setup:")
            print("  1. Go to Settings → Models → Manage Models")
            print("  2. Set system prompt in the chat interface")
            print("  3. Adjust temperature and max tokens in Advanced Settings")
            print()
            print("=" * 50)
            print()

def create_test_scenarios():
    """Create test scenarios for each template type."""
    library = PromptTemplateLibrary()
    
    scenarios = []
    
    for template_name, template_data in library.get_all_templates().items():
        scenario = {
            "template_name": template_name,
            "display_name": template_data["name"],
            "system_prompt": template_data["system_prompt"],
            "test_question": template_data["example_questions"][0],
            "expected_style": template_data["use_cases"][0],
            "parameters": {
                "temperature": template_data.get("temperature", 0.7),
                "max_tokens": template_data.get("max_tokens", 500)
            }
        }
        scenarios.append(scenario)
    
    return scenarios

def export_curl_examples():
    """Generate cURL examples for each template type."""
    library = PromptTemplateLibrary()
    
    print("🔧 cURL Examples for Prompt Templates")
    print("=" * 45)
    print()
    
    for template_name, template_data in library.get_all_templates().items():
        print(f"📝 {template_data['name']} Template")
        print("-" * 30)
        
        curl_command = f'''curl -X POST "http://localhost:8000/v1/chat/completions" \\
  -H "Authorization: Bearer sk-dummy-key-for-redis-queue-system" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "llama3.2:1b",
    "messages": [
      {{
        "role": "system",
        "content": "{template_data['system_prompt']}"
      }},
      {{
        "role": "user", 
        "content": "{template_data['example_questions'][0]}"
      }}
    ],
    "temperature": {template_data.get('temperature', 0.7)},
    "max_tokens": {template_data.get('max_tokens', 500)}
  }}' '''
        
        print(curl_command)
        print()

if __name__ == "__main__":
    import sys
    
    library = PromptTemplateLibrary()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            print("Available Prompt Templates:")
            for i, name in enumerate(library.list_templates(), 1):
                template = library.get_template(name)
                print(f"{i}. {template['name']} - {template['use_cases'][0]}")
        
        elif command == "export":
            config = library.generate_open_webui_config()
            with open("open_webui_config.json", "w") as f:
                json.dump(config, f, indent=2)
            print("✅ Configuration exported to open_webui_config.json")
        
        elif command == "curl":
            export_curl_examples()
        
        elif command == "test":
            scenarios = create_test_scenarios()
            print(f"Generated {len(scenarios)} test scenarios")
            for scenario in scenarios[:3]:
                print(f"- {scenario['display_name']}: {scenario['test_question'][:50]}...")
        
        elif command == "template" and len(sys.argv) > 2:
            template_name = sys.argv[2]
            template = library.get_template(template_name)
            if template:
                print(json.dumps(template, indent=2))
            else:
                print(f"Template '{template_name}' not found")
        
        else:
            print("Usage: python prompt_templates_library.py [list|export|curl|test|template <name>]")
    
    else:
        # Default: show the guide
        library.print_template_guide()
