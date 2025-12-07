# Hybrid AI Assistant

A hybrid AI assistant using LangGraph, LangChain, and Ollama/OpenAI for intelligent project automation.

## Overview

This system combines cloud-based AI (OpenAI) for complex reasoning and local AI (Ollama) for faster execution tasks. It uses LangGraph to orchestrate a multi-step workflow with human-in-the-loop checkpoints.

## Setup

1. Install dependencies:
   ```bash
   cd hybrid_ai_assistant
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (OPENAI_API_KEY, TAVILY_API_KEY, etc.)
   ```

3. Run the assistant:
   ```bash
   python main.py "Your query here"
   # Example: python main.py "Build a REST API with Python Flask"
   ```

## Documentation

For detailed documentation, architecture, and usage examples, see [hybrid_ai_assistant/README.md](hybrid_ai_assistant/README.md).

## Directory Structure

```
hybrid_ai_assistant/
├── README.md                  # Detailed documentation
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variable template
├── main.py                   # CLI entry point
├── config/                   # Configuration
├── state/                    # State schema
├── nodes/                    # LangGraph workflow nodes
├── tools/                    # Custom tools (search, file ops, shell)
├── orchestrator/             # Graph definition
├── api/                      # Flask REST API
├── utils/                    # Helper utilities
└── tests/                    # Unit tests
```

## Quick Start

1. **Install dependencies**: `pip install -r hybrid_ai_assistant/requirements.txt`
2. **Set up environment**: Copy `.env.example` to `.env` and add your API keys
3. **Run a task**: `cd hybrid_ai_assistant && python main.py "Your project idea"`

The assistant will research your request, generate implementation options, and execute your selected plan.

## Features

- **Hybrid AI**: Cloud AI for planning, local AI for execution
- **Research Phase**: Web search and synthesis using Tavily
- **Option Generation**: Multiple implementation approaches
- **Human-in-the-Loop**: Review and approve plans before execution
- **Sandboxed Execution**: Safe code execution in Docker containers
- **Checkpointing**: Resume workflows from interruption points

## License

MIT License
