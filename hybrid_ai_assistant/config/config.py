import os

class Config:
    CLOUD_LLM = "gpt-4o"  # OpenAI model
    LOCAL_ROUTER_MODEL = "llama3:8b"
    LOCAL_CODER_MODEL = "deepseek-coder:6.7b"
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DOCKER_IMAGE = "python:3.11-slim"
    RETRY_BUDGET = 3
    PROJECT_DIR = os.path.expanduser("~/MyProjects")  # Host mount point

config = Config()
