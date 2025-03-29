"""
Conversion utilities for DeepSeek R1 format.

DeepSeek Reasoner requires a specific format for optimal performance.
This module provides the conversion functionality.
"""
from typing import List, Dict, Any, Union, Optional


def convert_to_r1_format(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Converts messages to DeepSeek Reasoner (R1) format and merges consecutive messages with the same role.
    
    DeepSeek Reasoner does not support successive messages with the same role.
    It's recommended to use 'user' role instead of 'system' role for optimal performance.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        List of messages where consecutive messages with the same role are merged
    """
    merged = []
    
    for message in messages:
        message_content = ""
        has_images = False
        
        # Handle content that might be a string or a list of parts
        if isinstance(message.get('content'), list):
            text_parts = []
            image_parts = []
            
            for part in message['content']:
                if part.get('type') == 'text':
                    text_parts.append(part.get('text', ''))
                elif part.get('type') == 'image':
                    has_images = True
                    source = part.get('source', {})
                    image_parts.append({
                        'type': 'image_url',
                        'image_url': {
                            'url': f"data:{source.get('media_type', '')};base64,{source.get('data', '')}"
                        }
                    })
            
            if has_images:
                parts = []
                if text_parts:
                    parts.append({'type': 'text', 'text': '\n'.join(text_parts)})
                parts.extend(image_parts)
                message_content = parts
            else:
                message_content = '\n'.join(text_parts)
        else:
            message_content = message.get('content', '')
        
        # Check if we should merge with the last message
        if merged and merged[-1].get('role') == message.get('role'):
            last_message = merged[-1]
            
            # Merge content based on type
            if isinstance(last_message.get('content'), str) and isinstance(message_content, str):
                last_message['content'] = f"{last_message['content']}\n{message_content}"
            else:
                # Convert string content to text part if needed
                last_content = last_message.get('content', [])
                if isinstance(last_content, str):
                    last_content = [{'type': 'text', 'text': last_content}]
                elif not isinstance(last_content, list):
                    last_content = []
                
                new_content = message_content
                if isinstance(new_content, str):
                    new_content = [{'type': 'text', 'text': new_content}]
                elif not isinstance(new_content, list):
                    new_content = []
                
                # Merge the content lists
                merged_content = [*last_content, *new_content]
                last_message['content'] = merged_content
        else:
            # Add as a new message
            new_message = {
                'role': message.get('role', 'user'),
                'content': message_content
            }
            merged.append(new_message)
    
    return merged
