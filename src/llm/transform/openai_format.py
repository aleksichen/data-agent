"""
Conversion utilities for OpenAI format messages.
"""
from typing import List, Dict, Any, Union
from langchain_core.messages import (
    HumanMessage, 
    AIMessage, 
    SystemMessage, 
    ToolMessage, 
    BaseMessage
)


def convert_to_openai_messages(messages: List[Union[Dict[str, Any], BaseMessage]]) -> List[Dict[str, Any]]:
    """
    Convert various message formats to OpenAI compatible format.
    
    Args:
        messages: List of messages in different formats (dicts, LangChain messages, etc.)
        
    Returns:
        List of messages in OpenAI format
    """
    openai_messages = []
    
    for msg in messages:
        # Handle LangChain message objects
        if isinstance(msg, BaseMessage):
            role = _convert_langchain_role_to_openai(msg)
            content = msg.content
            
            # Create basic message
            openai_msg = {
                "role": role,
                "content": content
            }
            
            # Add name if present (used for tool messages)
            if hasattr(msg, "name") and msg.name and role != "system":
                openai_msg["name"] = msg.name
                
            openai_messages.append(openai_msg)
            continue
            
        # Handle dictionary format
        if isinstance(msg, dict):
            # Extract role and content
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Map common role names to OpenAI expected roles
            if role in ["human", "Human"]:
                role = "user"
            elif role in ["ai", "AI", "assistant", "Assistant"]:
                role = "assistant"
            elif role in ["system", "System"]:
                role = "system"
            elif role in ["tool", "Tool", "function", "Function"]:
                role = "tool"
                
            # Ensure role is one of the allowed OpenAI roles
            if role not in ["system", "user", "assistant", "tool"]:
                role = "user"  # Default to user for unknown roles
            
            # Create OpenAI format message
            formatted_msg = {
                "role": role,
                "content": content
            }
            
            # Add name if present
            if "name" in msg and msg["name"] and role != "system":
                formatted_msg["name"] = msg["name"]
            
            # Handle image content if present
            if isinstance(content, list):
                formatted_content = _process_multimodal_content(content)
                if formatted_content:
                    formatted_msg["content"] = formatted_content
            
            openai_messages.append(formatted_msg)
            continue
            
        # Handle other formats - try to convert to string
        openai_messages.append({
            "role": "user",
            "content": str(msg)
        })
    
    return openai_messages


def _convert_langchain_role_to_openai(msg: BaseMessage) -> str:
    """
    Convert LangChain message type to OpenAI role string.
    
    Args:
        msg: LangChain message object
        
    Returns:
        str: OpenAI compatible role string
    """
    if isinstance(msg, HumanMessage):
        return "user"
    elif isinstance(msg, AIMessage):
        return "assistant"
    elif isinstance(msg, SystemMessage):
        return "system"
    elif isinstance(msg, ToolMessage):
        return "tool"
    
    # For other message types, try to use the type attribute
    if hasattr(msg, "type"):
        msg_type = msg.type
        if msg_type == "human":
            return "user"
        elif msg_type == "ai":
            return "assistant"
        elif msg_type == "system":
            return "system"
        elif msg_type == "tool" or msg_type == "function":
            return "tool"
    
    # Default to user for unknown types
    return "user"


def _process_multimodal_content(content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process multimodal content like text and images.
    
    Args:
        content: List of content parts
        
    Returns:
        Processed content in OpenAI format
    """
    formatted_content = []
    
    for part in content:
        part_type = part.get("type", "")
        
        if part_type == "text":
            formatted_content.append({
                "type": "text",
                "text": part.get("text", "")
            })
        elif part_type == "image":
            # Convert image format
            source = part.get("source", {})
            if isinstance(source, str):
                # Handle URL string
                formatted_content.append({
                    "type": "image_url",
                    "image_url": {"url": source}
                })
            elif isinstance(source, dict):
                # Handle dictionary with media_type and data
                formatted_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{source.get('media_type', '')};base64,{source.get('data', '')}"
                    }
                })
    
    return formatted_content


if __name__ == "__main__":
    """
    Test the conversion functions with various message formats.
    """
    # Example LangChain messages
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    
    langchain_messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Hello, how are you?"),
        AIMessage(content="I'm doing well, thank you for asking!")
    ]
    
    # Convert to OpenAI format
    openai_messages = convert_to_openai_messages(langchain_messages)
    
    print("LangChain to OpenAI conversion:")
    for msg in openai_messages:
        print(f"Role: {msg['role']}, Content: {msg['content']}")
    
    # Example dictionary messages
    dict_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "human", "content": "What's the weather like?"},
        {"role": "ai", "content": "I don't have real-time weather data."}
    ]
    
    # Convert to OpenAI format
    openai_messages = convert_to_openai_messages(dict_messages)
    
    print("\nDictionary to OpenAI conversion:")
    for msg in openai_messages:
        print(f"Role: {msg['role']}, Content: {msg['content']}")
