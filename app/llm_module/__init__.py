"""
LLM Module - A flexible interface for working with Large Language Models.

This module provides:
- Abstract client interface for LLM providers
- OpenAI Responses API implementation
- Tool decorator for automatic schema extraction
- Type-safe interfaces and utilities

Example usage:
    from app.llm_module import OpenAIClient, tool

    # Define a tool
    @tool(description="Get weather for a location")
    def get_weather(location: str, unit: str = "celsius") -> dict:
        '''Get current weather.

        Args:
            location: City name
            unit: Temperature unit

        Returns:
            Weather data dictionary
        '''
        return {"temp": 20, "conditions": "sunny"}

    # Create client and register tools
    client = OpenAIClient(api_key="your-key", model="gpt-4o")
    client.set_system_prompt("You are a helpful weather assistant.")
    client.register_tool(get_weather)

    # Generate response with automatic tool calling
    response = client.generate(
        user_input="What's the weather in San Francisco?",
        reasoning=False
    )
    print(response['content'])
"""

from app.llm_module.client import LLMClient
from app.llm_module.openai_client import OpenAIClient
from app.llm_module.decorators import tool, get_tool_definition, is_tool
from app.llm_module.types import (
    ChatHistory,
    GenerateConfig,
    GenerateResponse,
    Message,
    MessageRole,
    ToolDefinition,
    ToolFunction,
    ToolCallOutput,
)

__all__ = [
    # Clients
    "LLMClient",
    "OpenAIClient",
    # Decorators
    "tool",
    "get_tool_definition",
    "is_tool",
    # Types
    "ChatHistory",
    "GenerateConfig",
    "GenerateResponse",
    "Message",
    "MessageRole",
    "ToolDefinition",
    "ToolFunction",
    "ToolCallOutput",
]

__version__ = "1.0.0"
