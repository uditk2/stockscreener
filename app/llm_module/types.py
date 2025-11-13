"""
Type definitions for the LLM module.
"""
from typing import Any, Callable, Dict, List, Literal, Optional, TypedDict, Union
from enum import Enum


class MessageRole(str, Enum):
    """Message role types."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class Message(TypedDict, total=False):
    """Chat message type following OpenAI format."""
    role: str
    content: Optional[str]
    name: Optional[str]
    function_call: Optional[Dict[str, Any]]
    tool_calls: Optional[List[Dict[str, Any]]]
    tool_call_id: Optional[str]


class ToolParameter(TypedDict, total=False):
    """Tool parameter definition."""
    type: str
    description: Optional[str]
    enum: Optional[List[Any]]
    items: Optional[Dict[str, Any]]
    properties: Optional[Dict[str, Any]]
    required: Optional[List[str]]


class ToolDefinition(TypedDict):
    """Tool definition for OpenAI API."""
    type: Literal["function"]
    name: str
    description: Optional[str]
    parameters: Dict[str, Any]


class ToolCallOutput(TypedDict):
    """Output from a tool call."""
    type: Literal["function_call_output"]
    call_id: str
    output: str


class GenerateConfig(TypedDict, total=False):
    """Configuration for generate method."""
    temperature: Optional[float]
    max_tokens: Optional[int]
    top_p: Optional[float]
    frequency_penalty: Optional[float]
    presence_penalty: Optional[float]
    stop: Optional[Union[str, List[str]]]


class GenerateResponse(TypedDict):
    """Response from generate method."""
    content: str
    reasoning: Optional[str]
    tool_calls: List[Dict[str, Any]]
    finish_reason: str
    usage: Dict[str, int]
    raw_response: Any


# Type aliases
ToolFunction = Callable[..., Any]
ChatHistory = List[Message]
