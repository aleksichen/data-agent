"""
OpenAI API handler implementation.
"""
import json
from typing import Dict, List, Optional, Any, AsyncGenerator

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


class OpenAiHandler(ApiHandler):
    """Handler for the OpenAI API."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the OpenAI API handler.
        
        Args:
            config: Configuration dictionary with API settings
        """
        self.api_key = config.get("api_key")
        self.model_name = config.get("model_name", "gpt-4o")
        self.base_url = config.get("base_url")
        self.organization_id = config.get("organization_id")
        
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        if self.organization_id:
            client_kwargs["organization"] = self.organization_id
            
        self.client = AsyncOpenAI(**client_kwargs)
        self._usage = None
        
    async def create_message(self, system_prompt: str, messages: List[MessageParam]) -> ApiStream:
        """
        Create a streaming message using the OpenAI API.
        
        Args:
            system_prompt: The system instructions for the model
            messages: List of previous messages in the conversation
            
        Returns:
            ApiStream: A stream of response chunks
        """
        # Format messages for OpenAI
        formatted_messages = []
        
        # Add system message if provided
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Create the streaming response
        async def stream_generator() -> AsyncGenerator[ApiStreamChunk, None]:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                stream=True
            )
            
            full_text = ""
            async for chunk in response:
                delta = self._get_delta_text(chunk)
                if delta:
                    full_text += delta
                    yield {
                        "text": full_text,
                        "delta": delta,
                        "done": False
                    }
            
            # Final chunk indicates completion
            yield {
                "text": full_text,
                "delta": "",
                "done": True
            }
        
        return ApiStream(stream_generator())
    
    def _get_delta_text(self, chunk: ChatCompletionChunk) -> str:
        """Extract delta text from an OpenAI response chunk."""
        if not chunk.choices:
            return ""
        
        choice = chunk.choices[0]
        if not choice.delta or not choice.delta.content:
            return ""
            
        return choice.delta.content
    
    def get_model(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dict with 'id' and 'info' keys
        """
        # Define model capabilities based on model name
        supports_functions = "gpt-4" in self.model_name or "gpt-3.5-turbo" in self.model_name
        supports_vision = "gpt-4" in self.model_name and ("vision" in self.model_name or "o" in self.model_name)
        supports_json = True  # Most OpenAI models support JSON mode
        
        model_info: ModelInfo = {
            "name": self.model_name,
            "version": "latest",
            "provider": "openai",
            "context_length": 128000 if "gpt-4o" in self.model_name else 16000,
            "supports_functions": supports_functions,
            "supports_vision": supports_vision,
            "supports_json_mode": supports_json
        }
        
        return {
            "id": self.model_name,
            "info": model_info
        }
    
    async def get_api_stream_usage(self) -> Optional[ApiStreamUsageChunk]:
        """
        Get token usage information.
        
        Note: OpenAI streaming API doesn't provide token counts in stream mode,
        so this returns None. For production, implement a token counter.
        
        Returns:
            None for streaming API calls
        """
        # OpenAI doesn't provide usage stats in streaming mode
        # In a real implementation, you might use a tokenizer to count tokens
        return None
