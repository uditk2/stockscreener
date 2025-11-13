# LLM Module

A flexible and extensible Python module for interacting with Large Language Models (LLMs) with built-in support for tool calling, reasoning modes, and conversation management.

## Features

- **Abstract Client Interface**: Easy to extend with different LLM providers
- **OpenAI Responses API**: Built-in implementation using OpenAI's latest Responses API
- **Automatic Tool Calling**: Decorator-based tool registration with automatic JSON schema extraction
- **Reasoning Mode**: Native support for reasoning models (o3, o3-mini, o4-mini)
- **Tool Calling Loop**: Automatic handling of multi-turn tool calls
- **System Prompts**: Support for loading prompts from text or markdown files
- **Type Safety**: Full type hints and type definitions
- **Conversation History**: Built-in chat history management

## Installation

The module requires the OpenAI Python library:

```bash
pip install openai>=2.0.0
```

Or install from the project requirements:

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from app.llm_module import OpenAIClient

# Initialize client
client = OpenAIClient(api_key="your-api-key", model="gpt-4o")

# Set system prompt
client.set_system_prompt("You are a helpful assistant.")

# Generate response
response = client.generate(user_input="What is Python?")
print(response['content'])
```

### Using Tools

```python
from app.llm_module import OpenAIClient, tool

# Define a tool with the @tool decorator
@tool(description="Get weather for a location")
def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    Get current weather information.

    Args:
        location: City name or location
        unit: Temperature unit (celsius or fahrenheit)

    Returns:
        Weather data dictionary
    """
    # Your implementation here
    return {"temp": 20, "conditions": "sunny"}

# Register and use
client = OpenAIClient(api_key="your-api-key")
client.register_tool(get_weather)

response = client.generate(
    user_input="What's the weather in San Francisco?"
)
# LLM automatically calls get_weather tool and uses result
print(response['content'])
```

### Reasoning Mode

```python
# Use reasoning models for complex problems
client = OpenAIClient(api_key="your-api-key", model="o3-mini")

response = client.generate(
    user_input="Solve this complex math problem...",
    reasoning=True  # Enable reasoning mode
)

print(response['content'])
if response['reasoning']:
    print(f"Reasoning: {response['reasoning']}")
```

### Chat History

```python
chat_history = []

# First turn
response1 = client.generate(
    user_input="My name is Alice",
    chat_history=chat_history
)

# Add to history
chat_history.append({"role": "user", "content": "My name is Alice"})
chat_history.append({"role": "assistant", "content": response1['content']})

# Second turn - LLM remembers context
response2 = client.generate(
    user_input="What's my name?",
    chat_history=chat_history
)
```

## API Reference

### OpenAIClient

Main client implementation using OpenAI's Responses API.

#### Constructor

```python
OpenAIClient(
    api_key: Optional[str] = None,
    model: str = "gpt-4o",
    max_tool_iterations: int = 10
)
```

**Parameters:**
- `api_key`: OpenAI API key (reads from environment if not provided)
- `model`: Model identifier (default: "gpt-4o")
- `max_tool_iterations`: Max tool calling iterations to prevent infinite loops

#### Methods

##### `set_system_prompt(prompt: Union[str, Path])`

Set the system prompt from text or markdown file.

```python
# From string
client.set_system_prompt("You are a helpful assistant.")

# From markdown file
client.set_system_prompt("prompts/system.md")
```

##### `register_tool(func: Callable, tool_def: Optional[ToolDefinition] = None)`

Register a single tool function.

```python
@tool(description="Calculate sum")
def add(a: int, b: int) -> int:
    return a + b

client.register_tool(add)
```

##### `register_tools(tools: List[Callable])`

Register multiple tools at once.

```python
client.register_tools([tool1, tool2, tool3])
```

##### `generate(...) -> GenerateResponse`

Generate a response with automatic tool calling.

```python
response = client.generate(
    user_input: str,                    # Required: User's input
    chat_history: Optional[ChatHistory] = None,  # Previous messages
    reasoning: bool = False,            # Enable reasoning mode
    tools: Optional[List[Callable]] = None,      # Temporary tools
    config: Optional[GenerateConfig] = None      # Generation config
)
```

**Returns:** `GenerateResponse` dictionary with:
- `content`: Final response text
- `reasoning`: Reasoning output (if reasoning mode enabled)
- `tool_calls`: List of tool calls made
- `finish_reason`: Why generation stopped
- `usage`: Token usage statistics
- `raw_response`: Raw API response object

### @tool Decorator

Decorator to mark functions as LLM tools with automatic schema extraction.

```python
@tool(description: Optional[str] = None, name: Optional[str] = None)
def function_name(...):
    pass
```

**Parameters:**
- `description`: Tool description (uses docstring if not provided)
- `name`: Custom tool name (uses function name if not provided)

**Features:**
- Automatically extracts parameter types from type hints
- Parses docstrings for parameter descriptions
- Supports `Optional`, `List`, `Dict`, and basic types
- Handles default parameter values

**Example:**

```python
@tool(description="Calculate statistics")
def calculate_stats(
    numbers: List[float],
    include_median: bool = True
) -> Dict[str, float]:
    """
    Calculate statistical metrics.

    Args:
        numbers: List of numbers to analyze
        include_median: Whether to include median calculation

    Returns:
        Dictionary with calculated statistics
    """
    # Implementation
    pass
```

### Types

The module exports these types for type safety:

- `ChatHistory`: List of message dictionaries
- `Message`: Single message with role and content
- `MessageRole`: Enum for message roles (SYSTEM, USER, ASSISTANT, etc.)
- `ToolDefinition`: Tool schema definition
- `ToolFunction`: Callable tool function
- `GenerateConfig`: Configuration for generation
- `GenerateResponse`: Response from generate method

## Architecture

```
app/llm_module/
├── __init__.py           # Module exports
├── client.py             # Abstract LLMClient interface
├── openai_client.py      # OpenAI Responses API implementation
├── decorators.py         # @tool decorator and schema extraction
├── types.py              # Type definitions
├── example_usage.py      # Usage examples
└── README.md            # This file
```

## Advanced Usage

### Custom Generation Config

```python
from app.llm_module import GenerateConfig

config: GenerateConfig = {
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}

response = client.generate(
    user_input="Write a story...",
    config=config
)
```

### Temporary Tools

Pass tools for a single call without registering:

```python
response = client.generate(
    user_input="Use these tools...",
    tools=[tool1, tool2]  # Only available for this call
)
```

### Tool Management

```python
# Register
client.register_tool(my_tool)

# Unregister
client.unregister_tool("tool_name")

# Clear all
client.clear_tools()

# Check registered tools
print(client.tools)  # Dict of tool name -> function
print(client.tool_definitions)  # List of tool schemas
```

## Error Handling

The module handles errors gracefully:

```python
try:
    response = client.generate(user_input="...")
except Exception as e:
    print(f"Error: {e}")
```

Tool execution errors are caught and returned to the LLM as error messages, allowing it to handle failures gracefully.

## Extending the Module

### Custom LLM Provider

Extend `LLMClient` to add support for other providers:

```python
from app.llm_module import LLMClient, GenerateResponse

class CustomLLMClient(LLMClient):
    def generate(self, user_input, chat_history=None, **kwargs):
        # Your implementation
        pass

    def _execute_tool_call(self, tool_name, arguments):
        # Your implementation
        pass
```

## Best Practices

1. **System Prompts**: Use clear, specific system prompts for better results
2. **Tool Descriptions**: Write detailed tool descriptions and parameter docs
3. **Type Hints**: Always use type hints for automatic schema extraction
4. **Error Handling**: Tools should handle errors and return informative messages
5. **Tool Limits**: Set reasonable `max_tool_iterations` to prevent runaway loops
6. **API Keys**: Use environment variables for API keys, never hardcode

## Examples

See `example_usage.py` for complete working examples:

```bash
export OPENAI_API_KEY=your-key
python -m app.llm_module.example_usage
```

## Troubleshooting

### Import Errors

Make sure you're running from the project root:
```bash
cd /path/to/stockscreener
python -m app.llm_module.example_usage
```

### API Errors

- Verify API key is set correctly
- Check you have access to the requested model
- Ensure OpenAI library is up to date (`openai>=2.0.0`)

### Tool Not Being Called

- Check tool description is clear
- Verify system prompt mentions the tool
- Ensure tool is registered before calling generate

## Contributing

To add new features:

1. Update type definitions in `types.py`
2. Extend abstract interface in `client.py`
3. Implement in `openai_client.py`
4. Add examples to `example_usage.py`
5. Update this README

## License

This module is part of the Stock Screener project.

## Support

For issues or questions, please refer to the main project documentation.
