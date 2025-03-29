"""
Factory for creating API handlers.
"""
from typing import Dict, Any

from src.llm.handlers.base import ApiHandler
from src.llm.handlers.openai import OpenAiHandler
from src.llm.handlers.deepseek import DeepSeekHandler
from src.llm.handlers.mock import MockLLMHandler


def create_api_handler(config: Dict[str, Any]) -> ApiHandler:
    """
    Create the appropriate API handler based on configuration.
    
    Args:
        config: Configuration dictionary with API settings
        
    Returns:
        ApiHandler: An instance of the appropriate ApiHandler implementation
    """
    api_provider = config.get("api_provider", "openai")
    
    if api_provider == "openai":
        return OpenAiHandler(config)
    elif api_provider == "deepseek":
        return DeepSeekHandler(config)
    elif api_provider == "mock":
        return MockLLMHandler(config)
    else:
        # Default to OpenAI if provider not recognized
        return OpenAiHandler(config)
