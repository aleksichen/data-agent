"""
Base API handler classes and interfaces for LLM providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, AsyncGenerator, Protocol, Tuple, TypedDict


class MessageParam(TypedDict, total=False):
    """Message format for chat completions."""
    role: str
    content: str


class ModelInfo(TypedDict, total=False):
    """Model information structure."""
    name: str
    version: str
    provider: str
    context_length: int
    supports_functions: bool
    supports_vision: bool
    supports_json_mode: bool


class UsageInfo(TypedDict, total=False):
    """Usage information for tracking token consumption."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ApiStreamChunk(TypedDict, total=False):
    """Chunk of streamed API response."""
    text: str
    delta: str
    done: bool


class ApiStreamUsageChunk(TypedDict, total=False):
    """Usage information for API stream."""
    usage: UsageInfo


class ApiStream:
    """Stream of API responses that can be iterated over."""
    
    def __init__(self, stream_generator: AsyncGenerator[ApiStreamChunk, None]):
        self.stream_generator = stream_generator
        
    async def __aiter__(self):
        async for chunk in self.stream_generator:
            yield chunk


class ApiHandler(ABC):
    """Abstract base class for API handlers."""
    
    @abstractmethod
    async def create_message(self, system_prompt: str, messages: List[MessageParam]) -> ApiStream:
        """
        Create a streaming message with the given system prompt and message history.
        
        Args:
            system_prompt: The system instructions for the model
            messages: List of previous messages in the conversation
            
        Returns:
            ApiStream: A stream of response chunks
        """
        pass
    
    @abstractmethod
    def get_model(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dict with 'id' and 'info' keys
        """
        pass
    
    @abstractmethod
    async def get_api_stream_usage(self) -> Optional[ApiStreamUsageChunk]:
        """
        Get token usage information for the most recent stream.
        
        Returns:
            Optional[ApiStreamUsageChunk]: Usage information if available
        """
        pass


class ApiConfiguration(TypedDict, total=False):
    """Configuration for API handlers."""
    api_provider: str
    api_key: str
    model_name: str
    base_url: Optional[str]
    organization_id: Optional[str]


def build_api_handler(configuration: ApiConfiguration) -> ApiHandler:
    """
    Factory function to build the appropriate API handler based on configuration.
    
    Args:
        configuration: Configuration for the API handler
        
    Returns:
        ApiHandler: An instance of the appropriate ApiHandler implementation
    """
    api_provider = configuration.get("api_provider", "openai")
    
    # Import handlers dynamically to avoid circular imports
    if api_provider == "openai":
        from src.llm.handlers.openai import OpenAiHandler
        return OpenAiHandler(configuration)
    elif api_provider == "deepseek":
        from src.llm.handlers.deepseek import DeepSeekHandler
        return DeepSeekHandler(configuration)
    else:
        # Default to OpenAI if provider not recognized
        from src.llm.handlers.openai import OpenAiHandler
        return OpenAiHandler(configuration)
