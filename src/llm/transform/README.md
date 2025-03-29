# LLM Message Format Transformers

This module provides utility functions for transforming messages between different LLM provider formats.

## Available Transformers

### R1 Format Converter

`convert_to_r1_format` - Converts messages to DeepSeek Reasoner (R1) format and merges consecutive messages with the same role.

DeepSeek Reasoner has specific requirements for optimal performance:
- Does not support successive messages with the same role
- Performs better with 'user' role instead of 'system' role
- Needs special handling for image content

#### Usage

```python
from src.llm.transform.r1_format import convert_to_r1_format

messages = [
    {"role": "user", "content": "Hello"},
    {"role": "user", "content": "I have a question"},
    {"role": "assistant", "content": "I'm listening"},
    {"role": "user", "content": "What is 2+2?"}
]

# Will merge the first two user messages
r1_messages = convert_to_r1_format(messages)
```

### OpenAI Format Converter

`convert_to_openai_messages` - Converts message format to OpenAI compatible format.

Features:
- Handles both text and image content
- Properly converts image data to OpenAI's expected format
- Preserves message structure

#### Usage

```python
from src.llm.transform.openai_format import convert_to_openai_messages

messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "How can I help?"},
    {"role": "user", "content": [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image", "source": {"media_type": "image/jpeg", "data": "base64_data_here"}}
    ]}
]

openai_messages = convert_to_openai_messages(messages)
```

## Integration with API Handlers

These format converters are used by the API handlers to ensure messages are properly formatted for each provider:

- `DeepSeekHandler` uses both converters, selecting the appropriate one based on the model
- For DeepSeek Reasoner models, `convert_to_r1_format` is used to optimize message structure
- For other models, `convert_to_openai_messages` is used to ensure proper format
