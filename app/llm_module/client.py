"""
Abstract client interface for LLM module.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from app.llm_module.types import (
    ChatHistory,
    GenerateConfig,
    GenerateResponse,
    ToolDefinition,
    ToolFunction,
)


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.

    This interface defines the contract that all LLM client implementations must follow.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LLM client.

        Args:
            api_key: API key for authentication
            model: Model identifier to use
        """
        self.api_key = api_key
        self.model = model
        self.system_prompt: Optional[str] = None
        self.tools: Dict[str, ToolFunction] = {}
        self.tool_definitions: List[ToolDefinition] = []

    def set_system_prompt(self, prompt: Union[str, Path]) -> None:
        """
        Set the system prompt from text or a markdown file.

        Args:
            prompt: System prompt as string or path to markdown file
        """
        if isinstance(prompt, Path) or (isinstance(prompt, str) and prompt.endswith('.md')):
            # Read from file
            file_path = Path(prompt) if isinstance(prompt, str) else prompt
            if not file_path.exists():
                raise FileNotFoundError(f"Prompt file not found: {file_path}")
            self.system_prompt = file_path.read_text(encoding='utf-8')
        else:
            # Use as direct text
            self.system_prompt = prompt

    def register_tool(self, func: ToolFunction, tool_def: Optional[ToolDefinition] = None) -> None:
        """
        Register a tool function for LLM to call.

        Args:
            func: The callable function
            tool_def: Optional tool definition (extracted from decorator if not provided)
        """
        from app.llm_module.decorators import get_tool_definition

        # Get tool definition from decorator if not provided
        if tool_def is None:
            tool_def = get_tool_definition(func)
            if tool_def is None:
                raise ValueError(
                    f"Function {func.__name__} is not decorated with @tool. "
                    "Either decorate it or provide tool_def explicitly."
                )

        # Store the function and its definition
        tool_name = tool_def['name']
        self.tools[tool_name] = func
        self.tool_definitions.append(tool_def)

    def register_tools(self, tools: List[ToolFunction]) -> None:
        """
        Register multiple tool functions at once.

        Args:
            tools: List of callable functions decorated with @tool
        """
        for tool in tools:
            self.register_tool(tool)

    def unregister_tool(self, tool_name: str) -> None:
        """
        Unregister a tool by name.

        Args:
            tool_name: Name of the tool to unregister
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.tool_definitions = [
                td for td in self.tool_definitions if td['name'] != tool_name
            ]

    def clear_tools(self) -> None:
        """Clear all registered tools."""
        self.tools.clear()
        self.tool_definitions.clear()

    @abstractmethod
    def generate(
        self,
        user_input: str,
        chat_history: Optional[ChatHistory] = None,
        reasoning: bool = False,
        tools: Optional[List[ToolFunction]] = None,
        config: Optional[GenerateConfig] = None,
    ) -> GenerateResponse:
        """
        Generate a response from the LLM.

        This method handles the complete interaction loop including:
        1. Sending the request with chat history and tools
        2. Processing any tool calls the LLM makes
        3. Sending tool results back to the LLM
        4. Continuing until a final response is received

        Args:
            user_input: The user's input/query
            chat_history: Previous conversation messages in OpenAI format
            reasoning: Whether to enable reasoning mode (for reasoning models like o1)
            tools: Optional list of tool functions to make available for this call
            config: Optional generation configuration (temperature, max_tokens, etc.)

        Returns:
            GenerateResponse containing the final response, tool calls, usage, etc.
        """
        pass

    @abstractmethod
    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool call and return the result.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            String representation of the tool result
        """
        pass

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"{self.__class__.__name__}(model={self.model}, tools={len(self.tools)})"
