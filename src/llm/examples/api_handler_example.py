"""
Example usage of the API handlers.
"""
import asyncio
import os
from typing import Dict, List, Any

from src.llm.handlers.factory import create_api_handler
from src.llm.handlers.base import MessageParam


async def process_stream(handler_name: str, config: Dict[str, Any], system_prompt: str, messages: List[MessageParam]):
    """Process a stream from an API handler."""
    print(f"\n=== Testing {handler_name} handler ===")
    
    # Create the handler
    handler = create_api_handler(config)
    
    # Get model information
    model_info = handler.get_model()
    print(f"Using model: {model_info['id']}")
    print(f"Model capabilities: {model_info['info']}")
    
    # Create a message stream
    stream = await handler.create_message(system_prompt, messages)
    
    # Process the stream
    response_text = ""
    async for chunk in stream:
        if "reasoning" in chunk:
            # Handle reasoning output from DeepSeek Reasoner
            print(f"\n[Reasoning]: {chunk['reasoning']}")
        elif chunk.get("done", False):
            print("\n[Stream completed]")
        elif "delta" in chunk:
            # Print just the delta (new content)
            print(chunk["delta"], end="", flush=True)
            response_text += chunk["delta"]
        elif "usage" in chunk:
            # Print usage information if available
            usage = chunk["usage"]
            print(f"\n\n[Usage]:")
            print(f"  Input tokens: {usage.get('input_tokens', 0)}")
            print(f"  Output tokens: {usage.get('output_tokens', 0)}")
            if "cache_read_tokens" in usage:
                print(f"  Cache read tokens: {usage.get('cache_read_tokens', 0)}")
            if "cache_write_tokens" in usage:
                print(f"  Cache write tokens: {usage.get('cache_write_tokens', 0)}")
            if "total_cost" in usage:
                print(f"  Total cost: ${usage.get('total_cost', 0):.6f}")
    
    # Get usage information if available
    usage = await handler.get_api_stream_usage()
    if usage:
        print(f"\nFinal usage statistics: {usage['usage']}")
    
    return response_text


async def run_examples():
    """Run examples using different API handlers."""
    # System prompt and messages for testing
    system_prompt = "You are a helpful AI assistant."
    messages = [
        {"role": "user", "content": "Explain the concept of polymorphism in object-oriented programming with a short example."}
    ]
    
    # Reasoning prompt for DeepSeek Reasoner
    reasoning_messages = [
        {"role": "user", "content": "If x + y = 10 and x * y = 16, what are the values of x and y?"}
    ]
    
    # Get API keys from environment variables (safer approach)
    openai_api_key = os.environ.get("OPENAI_API_KEY", "your-openai-api-key")
    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "your-deepseek-api-key")
    
    # Example OpenAI configuration
    openai_config = {
        "api_provider": "openai",
        "api_key": openai_api_key,
        "model_name": "gpt-4o"
    }
    
    # Example DeepSeek configuration
    deepseek_config = {
        "api_provider": "deepseek",
        "api_key": deepseek_api_key,
        "model_name": "deepseek-chat"
    }
    
    # Example DeepSeek Reasoner configuration
    deepseek_reasoner_config = {
        "api_provider": "deepseek",
        "api_key": deepseek_api_key,
        "model_name": "deepseek-reasoner"
    }
    
    # Run the examples (uncomment to test)
    # Note: You need to set the appropriate API keys in environment variables
    
    # await process_stream("OpenAI", openai_config, system_prompt, messages)
    # await process_stream("DeepSeek Chat", deepseek_config, system_prompt, messages)
    # await process_stream("DeepSeek Reasoner", deepseek_reasoner_config, system_prompt, reasoning_messages)


if __name__ == "__main__":
    asyncio.run(run_examples())
