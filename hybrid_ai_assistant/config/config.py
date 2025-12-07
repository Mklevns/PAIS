"""
Central configuration for the Hybrid AI Assistant.
Manages model names, API endpoints, retry budgets, and other settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration class"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    
    # Ollama Configuration
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # Model Configuration
    CLOUD_MODEL = os.getenv("CLOUD_MODEL", "gpt-4")
    LOCAL_MODEL = os.getenv("LOCAL_MODEL", "llama2")
    
    # Docker Configuration
    DOCKER_HOST = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
    DOCKER_IMAGE = "python:3.11-slim"
    DOCKER_TIMEOUT = 300  # seconds
    
    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    # LangGraph Configuration
    CHECKPOINT_DIR = ".checkpoints"
    
    # Flask Configuration
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # Execution Configuration
    MAX_EXECUTION_STEPS = 10
    CODE_TIMEOUT = 60  # seconds
    
    # Research Configuration
    MAX_SEARCH_RESULTS = 5
    RESEARCH_DEPTH = 3  # Number of research iterations
    
    # Routing Configuration
    ROUTING_THRESHOLD = 0.7  # Semantic similarity threshold for routing

# Singleton instance
config = Config()
