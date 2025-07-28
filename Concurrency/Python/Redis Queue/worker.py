"""
Redis Queue Worker for processing LLM requests with LangChain and Ollama.
This worker handles background job processing by interfacing with LangChain.js.
"""

import os
import sys
import time
import json
import subprocess
import requests
import logging
from typing import Dict, Any
from redis import Redis
from rq import Worker, Queue, Connection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis connection
redis_conn = Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0))
)

def test_ollama_connection():
    """Test if Ollama server is running and accessible."""
    try:
        ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        if response.status_code == 200:
            logger.info("Ollama server is accessible")
            return True
    except Exception as e:
        logger.warning(f"Ollama server not accessible: {e}")
    return False

def call_langchain_service(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call the LangChain.js service via HTTP request.
    
    Args:
        job_data: Dictionary containing job parameters
        
    Returns:
        Dictionary with response and processing time
    """
    start_time = time.time()
    
    try:
        langchain_port = os.getenv('LANGCHAIN_SERVICE_PORT', '3000')
        langchain_url = f"http://localhost:{langchain_port}/generate"
        
        payload = {
            "question": job_data["question"],
            "model": job_data.get("model", "llama3.2:1b"),
            "temperature": job_data.get("temperature", 0.7),
            "max_tokens": job_data.get("max_tokens", 500)
        }
        
        logger.info(f"Calling LangChain service at {langchain_url}")
        response = requests.post(
            langchain_url,
            json=payload,
            timeout=300,  # 5-minute timeout
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            processing_time = time.time() - start_time
            
            return {
                "response": result.get("response", "No response received"),
                "processing_time": processing_time,
                "model_used": result.get("model_used"),
                "success": True
            }
        else:
            raise Exception(f"LangChain service returned status {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        logger.warning("LangChain service not available, falling back to direct Node.js execution")
        return call_langchain_script(job_data)
    except Exception as e:
        logger.error(f"Error calling LangChain service: {e}")
        raise

def call_langchain_script(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call the LangChain.js script directly using subprocess.
    
    Args:
        job_data: Dictionary containing job parameters
        
    Returns:
        Dictionary with response and processing time
    """
    start_time = time.time()
    
    try:
        # Prepare the script arguments
        script_path = os.path.join(os.path.dirname(__file__), "langchain_script.js")
        
        # Create input data for the script
        input_data = {
            "question": job_data["question"],
            "model": job_data.get("model", "llama3.2:1b"),
            "temperature": job_data.get("temperature", 0.7),
            "max_tokens": job_data.get("max_tokens", 500)
        }
        
        logger.info(f"Executing LangChain script: {script_path}")
        
        # Execute the Node.js script
        process = subprocess.run(
            ["node", script_path],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=300  # 5-minute timeout
        )
        
        if process.returncode == 0:
            try:
                result = json.loads(process.stdout)
                processing_time = time.time() - start_time
                
                return {
                    "response": result.get("response", "No response received"),
                    "processing_time": processing_time,
                    "model_used": result.get("model_used"),
                    "success": True
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw output
                processing_time = time.time() - start_time
                return {
                    "response": process.stdout.strip(),
                    "processing_time": processing_time,
                    "success": True
                }
        else:
            error_msg = process.stderr or "Unknown error in LangChain script"
            raise Exception(f"LangChain script failed: {error_msg}")
            
    except subprocess.TimeoutExpired:
        raise Exception("LangChain script execution timed out")
    except Exception as e:
        logger.error(f"Error executing LangChain script: {e}")
        raise

def process_ollama_request(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main job function that processes Ollama requests through LangChain.
    This function is called by RQ workers.
    
    Args:
        job_data: Dictionary containing job parameters
        
    Returns:
        Dictionary with the final response
    """
    job_id = job_data.get("job_id", "unknown")
    question = job_data.get("question", "")
    
    logger.info(f"Processing job {job_id} with question: {question[:50]}...")
    
    try:
        # Validate input
        if not question.strip():
            raise ValueError("Question cannot be empty")
        
        # Check if Ollama is accessible
        if not test_ollama_connection():
            logger.warning("Ollama server not accessible, but continuing with LangChain processing")
        
        # Try to call LangChain service first, fallback to direct script execution
        try:
            result = call_langchain_service(job_data)
        except Exception as service_error:
            logger.warning(f"Service call failed, trying direct script execution: {service_error}")
            result = call_langchain_script(job_data)
        
        logger.info(f"Job {job_id} completed successfully in {result.get('processing_time', 0):.2f} seconds")
        return result
        
    except Exception as e:
        error_msg = f"Error processing job {job_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "response": None,
            "error": error_msg,
            "success": False,
            "processing_time": 0
        }

def run_worker():
    """Run the RQ worker."""
    try:
        # Test Redis connection
        redis_conn.ping()
        logger.info("Successfully connected to Redis")
        
        # Create queue
        queue = Queue(connection=redis_conn)
        logger.info(f"Worker listening on queue with {len(queue)} jobs")
        
        # Start worker
        with Connection(redis_conn):
            worker = Worker([queue])
            logger.info("Starting RQ worker...")
            worker.work()
            
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.error(f"Worker error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if this script is being run directly or imported
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode - just test the connections
        logger.info("Running in test mode...")
        test_ollama_connection()
        try:
            redis_conn.ping()
            logger.info("Redis connection successful")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
    else:
        # Normal worker mode
        run_worker()
