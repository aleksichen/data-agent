# LLM API Handlers

This module provides a unified interface for interacting with various Large Language Model APIs. It implements the Strategy pattern to allow seamless switching between different LLM providers while maintaining a consistent interface.

## Key Components

- `ApiHandler`: Abstract base class defining the interface for all API handlers
- `ApiStream`: Wrapper for streaming API responses
- `OpenAiHandler`: Implementation for the OpenAI API
- `DeepSeekHandler`: Implementation for the DeepSeek API (including DeepSeek Reasoner)

## Features

- Unified asynchronous streaming interface for all providers
- Support for specialized model features (like DeepSeek's reasoning capabilities)
- Token usage tracking and cost calculation
- Consistent error handling across providers

## Usage

```python
import asyncio
import os
from src.llm.handlers.factory import create_api_handler

async def main():
    # Configure the API handler
    config = {
        "api_provider": "deepseek",  # or "openai"
        "api_key": os.environ.get("DEEPSEEK_API_KEY"),
        "model_name": "deepseek-chat"  # or other model name
    }
    
    # Create the handler
    handler = create_api_handler(config)
    
    # Define a system prompt and messages
    system_prompt = "You are a helpful AI assistant."
    messages = [
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ]
    
    # Create a message stream
    stream = await handler.create_message(system_prompt, messages)
    
    # Process the stream
    async for chunk in stream:
        if "reasoning" in chunk:
            # Handle reasoning output (DeepSeek Reasoner)
            print(f"\n[Reasoning]: {chunk['reasoning']}")
        elif chunk.get("done", False):
            print("\n[Stream completed]")
        elif "delta" in chunk:
            # Print the new content
            print(chunk["delta"], end="", flush=True)
        elif "usage" in chunk:
            # Print usage information
            usage = chunk["usage"]
            print(f"\nUsage: {usage}")
    
    # Get final usage information
    usage = await handler.get_api_stream_usage()
    if usage:
        print(f"\nFinal usage statistics: {usage['usage']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## DeepSeek Specific Features

The DeepSeek implementation includes support for:

- Regular chat models (deepseek-chat, deepseek-coder)
- Reasoning models (deepseek-reasoner) that provide step-by-step reasoning
- Cache token tracking (DeepSeek's KV cache feature)
- Cost calculation based on token usage

## OpenAI Specific Features

The OpenAI implementation supports:

- All OpenAI chat models (gpt-3.5-turbo, gpt-4, gpt-4o, etc.)
- Custom base URL for using compatible APIs
- Organization ID for multi-org accounts

## Extending

To add support for a new LLM provider:

1. Create a new handler class that implements the `ApiHandler` interface
2. Add the new handler to the `create_api_handler` factory function

## Requirements

- `openai`: For OpenAI API integration and DeepSeek API (OpenAI-compatible)
- `httpx`: For asynchronous HTTP requests
