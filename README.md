# Data Agent

A multi-agent AI system built with LangChain and LangGraph using Test-Driven Development.

## Features

- Multi-agent LangGraph orchestration with specialized agent roles
- Team-based approach with coordinator, planner, supervisor, and specialist agents
- TDD implementation for robust and reliable agent interactions
- FastAPI-based server with streaming support
- Command-line interface for quick testing

## Installation

```bash
# Install dependencies
pip install -e .
```

## Usage

### Running the Server

```bash
python server.py
```

This will start the API server on http://localhost:8000.

### Testing the System

```bash
# Install test dependencies
pip install -e ".[test]"

# Run the test suite
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Or run the main CLI
python main.py "Your query here"
```

### API Endpoints

- `/api/chat/stream` - Original streaming chat endpoint
- `/api/langgraph/chat` - LangGraph-based streaming chat endpoint

## Multi-Agent Workflow

The system uses a team-based LangGraph workflow consisting of the following agents:

1. **Coordinator** - Entry point that communicates with users and determines if planning is needed
2. **Planner** - Generates a comprehensive execution plan
3. **Supervisor** - Central orchestrator that decides which specialist agent to invoke next
4. **Specialist Agents**:
   - **Researcher** - Performs information gathering and analysis
   - **Coder** - Executes Python code for data processing
   - **Browser** - Handles web browsing and data collection
   - **Reporter** - Creates final reports and summaries

The workflow uses a graph-based execution model where the supervisor dynamically routes tasks to the most appropriate specialist agent based on the current needs.

## Project Structure

```
.
├── README.md
├── docs
├── main.py               # CLI interface
├── pyproject.toml
├── pytest.ini           # Pytest configuration
├── scripts
├── server.py             # FastAPI server
├── src
│   ├── __init__.py
│   ├── agents            # Specialist agent implementations
│   │   ├── __init__.py
│   │   ├── browser_agent.py
│   │   ├── coder_agent.py
│   │   └── research_agent.py
│   ├── api               # API endpoints
│   ├── config            # Configuration settings
│   ├── db                # Database connections
│   ├── graph             # LangGraph implementation
│   │   ├── __init__.py
│   │   ├── builder.py    # Graph construction
│   │   ├── nodes.py      # Node functions
│   │   └── types.py      # Type definitions
│   ├── integrations      # External integrations
│   ├── llm               # LLM interface and prompting
│   ├── prompts           # Prompt templates
│   ├── tools             # Tool implementations
│   └── utils             # Utility functions
└── tests                 # TDD test suite
    ├── __init__.py
    ├── conftest.py       # Test fixtures and utilities
    ├── integration       # Integration tests
    └── unit              # Unit tests
```

## Development with TDD

This project follows Test-Driven Development principles:

1. Write failing tests that define expected behavior
2. Implement minimal code to make tests pass
3. Refactor while maintaining passing tests
4. Repeat for new features

See the `tests/README.md` for detailed guidance on the TDD approach used in this project.

## Future Improvements

- Advanced agent capabilities with specialized tools
- Memory systems for long-term context retention
- Automated agent evaluation and performance metrics
- Fine-tuned agent-specific LLM models
- Self-improvement mechanisms for agents to learn from past interactions
