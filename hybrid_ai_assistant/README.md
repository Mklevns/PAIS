# Hybrid AI Assistant

A hybrid AI assistant using LangGraph, LangChain, and Ollama/OpenAI for intelligent project automation.

## Overview

This system combines cloud-based AI (OpenAI) for complex reasoning and local AI (Ollama) for faster execution tasks. It uses LangGraph to orchestrate a multi-step workflow with human-in-the-loop checkpoints.

## Architecture

- **Cloud AI**: Used for research, clarification, and planning (GPT-4)
- **Local AI**: Used for code generation and execution (Ollama/Llama2)
- **Human-in-the-Loop**: Interactive option selection before execution

## Directory Structure

```
hybrid_ai_assistant/
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── .env.example               # Template for environment variables
├── config/                    # Configuration files
│   └── config.py              # Central configuration
├── state/                     # State schema and persistence
│   └── state.py               # ProjectState TypedDict and validators
├── nodes/                     # LangGraph nodes
│   ├── clarification.py       # Ambiguity resolution
│   ├── research.py            # Deep research and synthesis
│   ├── option_generator.py    # Generate structured options
│   ├── human_selection.py     # HITL interrupt handler
│   └── execution.py           # Code generation and debugging
├── tools/                     # Custom LangChain tools
│   ├── search.py              # Tavily web search
│   ├── file_ops.py            # Sandboxed file operations
│   └── shell.py               # Docker-wrapped shell execution
├── orchestrator/              # Main graph setup
│   └── graph.py               # LangGraph workflow definition
├── api/                       # Flask API for HITL
│   └── app.py                 # REST endpoints
├── utils/                     # Helper functions
│   ├── routing.py             # Semantic routing logic
│   ├── docker_utils.py        # Docker container management
│   └── repo_map.py            # Repository skeleton generation
├── main.py                    # CLI entry point
└── tests/                     # Unit tests
    ├── test_research.py
    └── test_execution.py
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install Ollama (optional, for local execution):**
   ```bash
   curl https://ollama.ai/install.sh | sh
   ollama pull llama2
   ```

4. **Install Docker (for sandboxed execution):**
   Follow instructions at https://docs.docker.com/get-docker/

## Usage

### CLI Interface

```bash
python main.py "Build a React app with TypeScript"
```

The workflow will:
1. Clarify any ambiguities in your request
2. Research best practices and technologies
3. Generate multiple implementation options
4. Pause for you to select your preferred option
5. Execute the selected plan with code generation

### API Interface

Start the Flask server:
```bash
python api/app.py
```

Then interact via REST API:
```bash
# Start a workflow
curl -X POST http://localhost:5000/start \
  -H "Content-Type: application/json" \
  -d '{"objective": "Build a React app"}'

# Poll for status
curl http://localhost:5000/poll/<run_id>

# Submit selection
curl -X POST http://localhost:5000/select/<run_id> \
  -H "Content-Type: application/json" \
  -d '{"option_id": 0}'
```

## Configuration

Edit `config/config.py` to customize:
- Model names (cloud vs local)
- API endpoints
- Retry budgets
- Timeout values
- Docker settings

## Features

- **Intelligent Routing**: Automatically routes tasks to cloud or local AI based on complexity
- **Sandboxed Execution**: All code runs in isolated Docker containers
- **Checkpointing**: Resume workflows from any point
- **Human-in-the-Loop**: Review and approve plans before execution
- **Comprehensive Logging**: Track all decisions and actions

## Testing

Run tests:
```bash
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_research.py -v
```

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or pull request.
