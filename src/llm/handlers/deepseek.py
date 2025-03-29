"""
DeepSeek API handler implementation.
"""
import json
import os
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator, Union

import httpx
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionChunk

from src.llm.handlers.base import (
    ApiHandler, 
    ApiStream, 
    ApiStreamChunk, 
    ApiStreamUsageChunk,
    MessageParam,
    ModelInfo
)
from src.llm.transform.r1_format import convert_to_r1_format
from src.llm.transform.openai_format import convert_to_openai_messages


# Define DeepSeek model information
DEEPSEEK_MODELS = {
    "deepseek-chat": {
        "name": "deepseek-chat",
        "version": "latest",
        "provider": "deepseek",
        "context_length": 32000,
        "max_tokens": 4096,
        "supports_functions": True,
        "supports_vision": False,
        "supports_json_mode": True,
        "input_price_per_million": 0.5,  # Example pricing
        "output_price_per_million": 1.5  # Example pricing
    },
    "deepseek-coder": {
        "name": "deepseek-coder",
        "version": "latest",
        "provider": "deepseek",
        "context_length": 32000,
        "max_tokens": 4096,
        "supports_functions": True,
        "supports_vision": False,
        "supports_json_mode": True,
        "input_price_per_million": 0.5,  # Example pricing
        "output_price_per_million": 1.5  # Example pricing
    },
    "deepseek-reasoner": {
        "name": "deepseek-reasoner",
        "version": "latest",
        "provider": "deepseek",
        "context_length": 32000,
        "max_tokens": 4096,
        "supports_functions": True,
        "supports_vision": False,
        "supports_json_mode": True,
        "supports_reasoning": True,
        "input_price_per_million": 0.5,  # Example pricing
        "output_price_per_million": 1.5  # Example pricing
    }
}

DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"


def calculate_api_cost(
    model_info: Dict[str, Any], 
    input_tokens: int, 
    output_tokens: int, 
    cache_write_tokens: int = 0, 
    cache_read_tokens: int = 0
) -> float:
    """
    Calculate the cost of API usage based on token counts.
    
    Args:
        model_info: Information about the model used
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        cache_write_tokens: Number of tokens written to cache (DeepSeek specific)
        cache_read_tokens: Number of tokens read from cache (DeepSeek specific)
        
    Returns:
        float: Total cost in USD
    """
    input_cost = (input_tokens / 1_000_000) * model_info.get("input_price_per_million", 0)
    output_cost = (output_tokens / 1_000_000) * model_info.get("output_price_per_million", 0)
    
    # For cached tokens, we might have different pricing
    cache_write_cost = (cache_write_tokens / 1_000_000) * model_info.get("input_price_per_million", 0)
    
    # Usually reading from cache is cheaper or free
    cache_read_cost = (cache_read_tokens / 1_000_000) * model_info.get("cache_price_per_million", 0)
    
    return input_cost + output_cost + cache_write_cost + cache_read_cost


class DeepSeekHandler(ApiHandler):
    """Handler for the DeepSeek API."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DeepSeek API handler.
        
        Args:
            config: Configuration dictionary with API settings
        """
        self.api_key = config.get("api_key") or config.get("deepSeekApiKey")
        self.model_name = config.get("model_name") or config.get("apiModelId", DEFAULT_DEEPSEEK_MODEL)
        self.base_url = config.get("base_url", "https://api.deepseek.com/v1")
        self._usage = None
        
        # Initialize OpenAI client (DeepSeek uses OpenAI compatible API)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def get_api_stream_usage(self) -> Optional[ApiStreamUsageChunk]:
        """
        Get token usage information for the most recent stream.
        
        Returns:
            ApiStreamUsageChunk if available, None otherwise
        """
        if self._usage:
            # Convert Pydantic model to dictionary for consistency
            try:
                # For newer OpenAI versions where usage is a Pydantic model
                usage_dict = {
                    "prompt_tokens": getattr(self._usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(self._usage, "completion_tokens", 0),
                    "total_tokens": getattr(self._usage, "total_tokens", 0)
                }
                
                # Add DeepSeek-specific fields if they exist
                if hasattr(self._usage, "prompt_cache_hit_tokens"):
                    usage_dict["prompt_cache_hit_tokens"] = getattr(self._usage, "prompt_cache_hit_tokens", 0)
                if hasattr(self._usage, "prompt_cache_miss_tokens"):
                    usage_dict["prompt_cache_miss_tokens"] = getattr(self._usage, "prompt_cache_miss_tokens", 0)
                
                return {"usage": usage_dict}
            except Exception as e:
                # Fallback for dictionary-based usage
                if isinstance(self._usage, dict):
                    return {"usage": self._usage}
                return None
        return None
    
    async def create_message(self, system_prompt: str, messages: List[MessageParam]) -> ApiStream:
        """
        Create a streaming message using the DeepSeek API.
        
        Args:
            system_prompt: The system instructions for the model
            messages: List of previous messages in the conversation
            
        Returns:
            ApiStream: A stream of response chunks
        """
        model_info = self.get_model()
        is_deepseek_reasoner = "deepseek-reasoner" in model_info["id"]
        
        # Format messages for DeepSeek
        if is_deepseek_reasoner:
            # For reasoner models, we use the R1 format converter
            # Include system prompt as the first user message
            all_messages = [{"role": "user", "content": system_prompt}, *messages]
            formatted_messages = convert_to_r1_format(all_messages)
        else:
            # Standard format for non-reasoner models
            # 检查系统提示是否为空
            formatted_messages = convert_to_openai_messages(messages)
            
            # 如果系统提示非空，则添加到消息列表的开头
            if system_prompt and system_prompt.strip():
                # 将系统提示插入到消息列表的开头
                formatted_messages.insert(0, {"role": "system", "content": system_prompt})
        
        # Create the streaming response
        async def stream_generator() -> AsyncGenerator[Dict[str, Any], None]:
            try:
                stream = await self.client.chat.completions.create(
                    model=model_info["id"],
                    max_completion_tokens=model_info["info"].get("max_tokens", 4096),
                    messages=formatted_messages,
                    stream=True,
                    stream_options={"include_usage": True},
                    **({"temperature": 0} if model_info["id"] != "deepseek-reasoner" else {})
                )
                
                async for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    
                    # Handle regular text content
                    if delta and delta.content:
                        yield {
                            "text": delta.content,
                            "delta": delta.content,
                            "done": False
                        }
                    
                    # Handle reasoning content (for reasoner models)
                    if delta and hasattr(delta, "reasoning_content") and delta.reasoning_content:
                        yield {
                            "reasoning": delta.reasoning_content,
                            "done": False
                        }
                    
                    # Handle usage information
                    if hasattr(chunk, "usage") and chunk.usage:
                        self._usage = chunk.usage
                        model_id = model_info["id"]
                        model_details = DEEPSEEK_MODELS.get(model_id, {})
                        
                        # Extract DeepSeek specific usage metrics - safely get attributes from Pydantic model
                        input_tokens = getattr(chunk.usage, "prompt_tokens", 0) or 0
                        output_tokens = getattr(chunk.usage, "completion_tokens", 0) or 0
                        cache_hit_tokens = getattr(chunk.usage, "prompt_cache_hit_tokens", 0) or 0
                        cache_miss_tokens = getattr(chunk.usage, "prompt_cache_miss_tokens", 0) or 0
                        
                        # Calculate cost
                        total_cost = calculate_api_cost(
                            model_details, 
                            input_tokens, 
                            output_tokens,
                            cache_miss_tokens,
                            cache_hit_tokens
                        )
                        
                        yield {
                            "usage": {
                                "input_tokens": input_tokens,
                                "output_tokens": output_tokens,
                                "cache_write_tokens": cache_miss_tokens,
                                "cache_read_tokens": cache_hit_tokens,
                                "total_cost": total_cost
                            },
                            "done": False
                        }
                
                # Final chunk indicates completion
                yield {
                    "text": "",
                    "delta": "",
                    "done": True
                }
                
            except Exception as e:
                # Handle errors
                error_msg = f"DeepSeek API error: {str(e)}"
                yield {
                    "text": error_msg,
                    "delta": error_msg,
                    "done": True
                }
        
        return ApiStream(stream_generator())
    
    def get_model(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dict with 'id' and 'info' keys
        """
        model_id = self.model_name
        
        if model_id in DEEPSEEK_MODELS:
            model_info = DEEPSEEK_MODELS[model_id]
        else:
            # Default to standard model if specified one is not recognized
            model_id = DEFAULT_DEEPSEEK_MODEL
            model_info = DEEPSEEK_MODELS[DEFAULT_DEEPSEEK_MODEL]
        
        return {
            "id": model_id,
            "info": model_info
        }


if __name__ == "__main__":
    """
    Test the DeepSeek handler with different models.
    
    Usage:
    1. Set your DeepSeek API key as an environment variable:
       export DEEPSEEK_API_KEY=your_api_key_here
    
    2. Run this file directly:
       python -m src.llm.handlers.deepseek
    """
    
    async def test_deepseek_handler():
        """Test the DeepSeek handler with different scenarios."""
        # Get API key from environment
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            print("Error: Please set the DEEPSEEK_API_KEY environment variable")
            return
        
        # Test case 1: DeepSeek Chat model
        print("\n=== Testing DeepSeek Chat ===")
        chat_config = {
            "api_key": api_key,
            "model_name": "deepseek-chat"
        }
        
        handler = DeepSeekHandler(chat_config)
        model_info = handler.get_model()
        print(f"Using model: {model_info['id']}")
        
        # Define system prompt and messages
        system_prompt = "You are a helpful AI assistant that provides clear and concise answers."
        messages = [
            {"role": "user", "content": "Explain quantum computing in 3 sentences."}
        ]
        
        # Create a message stream
        stream = await handler.create_message(system_prompt, messages)
        
        # Process the stream
        full_response = ""
        async for chunk in stream:
            if "delta" in chunk:
                print(chunk["delta"], end="", flush=True)
                full_response += chunk["delta"]
            elif "reasoning" in chunk:
                print(f"\n[Reasoning]: {chunk['reasoning']}")
            elif "usage" in chunk:
                usage = chunk["usage"]
                print(f"\n\nUsage: {usage}")
        
        print("\n\n=== Response Complete ===")
        
        # Get final usage
        usage = await handler.get_api_stream_usage()
        if usage:
            print(f"Final usage: {usage['usage']}")
        
        # Test case 2: DeepSeek Reasoner model
        print("\n\n=== Testing DeepSeek Reasoner ===")
        reasoner_config = {
            "api_key": api_key,
            "model_name": "deepseek-reasoner"
        }
        
        handler = DeepSeekHandler(reasoner_config)
        model_info = handler.get_model()
        print(f"Using model: {model_info['id']}")
        
        # Define system prompt and messages for a reasoning task
        system_prompt = "Solve problems step by step with careful reasoning."
        messages = [
            {"role": "user", "content": "If x + y = 10 and x * y = 21, what are the values of x and y?"}
        ]
        
        # Create a message stream
        stream = await handler.create_message(system_prompt, messages)
        
        # Process the stream
        full_response = ""
        async for chunk in stream:
            if "delta" in chunk:
                print(chunk["delta"], end="", flush=True)
                full_response += chunk["delta"]
            elif "reasoning" in chunk:
                print(f"\n[Reasoning]: {chunk['reasoning']}", end="", flush=True)
            elif "usage" in chunk:
                usage = chunk["usage"]
                print(f"\n\nUsage: {usage}")
        
        print("\n\n=== Response Complete ===")
        
        # Get final usage
        usage = await handler.get_api_stream_usage()
        if usage:
            print(f"Final usage: {usage['usage']}")
        
        print("\n\n=== Testing Consecutive Messages ===")
        chat_config = {
            "api_key": api_key,
            "model_name": "deepseek-chat"
        }
        
        handler = DeepSeekHandler(chat_config)
        
        # Define system prompt and consecutive messages with the same role
        system_prompt = "You are a helpful coding assistant."
        messages = [
            {"role": "user", "content": "I'm trying to solve a problem."},
            {"role": "user", "content": "I need to sort a list in Python."},
            {"role": "assistant", "content": "I can help with that."},
            {"role": "assistant", "content": "Python has a built-in sort method."},
            {"role": "user", "content": "Can you show me an example?"}
        ]
        
        # Create a message stream
        stream = await handler.create_message(system_prompt, messages)
        
        # Process the stream
        full_response = ""
        async for chunk in stream:
            if "delta" in chunk:
                print(chunk["delta"], end="", flush=True)
                full_response += chunk["delta"]
            elif "usage" in chunk:
                usage = chunk["usage"]
                print(f"\n\nUsage: {usage}")
        
        print("\n\n=== Response Complete ===")
    
    # Run the test
    asyncio.run(test_deepseek_handler())
