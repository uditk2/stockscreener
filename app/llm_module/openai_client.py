"""
OpenAI implementation of LLM client using the Responses API.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI

from app.llm_module.client import LLMClient
from app.llm_module.types import (
    ChatHistory,
    GenerateConfig,
    GenerateResponse,
    Message,
    ToolFunction,
)

logger = logging.getLogger(__name__)


class OpenAIClient(LLMClient):
    """
    OpenAI implementation using the Responses API.

    This client uses OpenAI's latest Responses API which provides:
    - Stateful conversation management
    - Native tool calling support
    - Reasoning model integration
    - Automatic orchestration of tool calls
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        max_tool_iterations: int = 10
    ):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key (uses environment variable if not provided)
            model: Model to use (default: gpt-4o)
            max_tool_iterations: Maximum number of tool call iterations to prevent infinite loops
        """
        super().__init__(api_key=api_key, model=model)
        self.client = OpenAI(api_key=api_key)
        self.max_tool_iterations = max_tool_iterations

    def generate(
        self,
        user_input: str,
        chat_history: Optional[ChatHistory] = None,
        reasoning: bool = False,
        tools: Optional[List[ToolFunction]] = None,
        config: Optional[GenerateConfig] = None,
    ) -> GenerateResponse:
        """
        Generate a response using OpenAI Responses API with automatic tool calling loop.

        Args:
            user_input: The user's input/query
            chat_history: Previous conversation messages
            reasoning: Enable reasoning mode (uses reasoning models like o3-mini)
            tools: Optional tools for this specific call
            config: Generation configuration

        Returns:
            GenerateResponse with content, tool calls, and metadata
        """
        # Register temporary tools if provided
        temp_tools = []
        if tools:
            temp_tools = [t for t in tools if t.__name__ not in self.tools]
            for tool in temp_tools:
                self.register_tool(tool)

        try:
            # Build input messages
            input_messages = self._build_input_messages(user_input, chat_history)

            # Select model based on reasoning flag
            model = self._select_model(reasoning)

            # Build request parameters
            request_params = self._build_request_params(input_messages, model, config)

            # Execute the tool calling loop
            response = self._execute_tool_loop(request_params)

            return response

        finally:
            # Cleanup temporary tools
            for tool in temp_tools:
                self.unregister_tool(tool.__name__)

    def _build_input_messages(
        self,
        user_input: str,
        chat_history: Optional[ChatHistory] = None
    ) -> List[Message]:
        """
        Build input messages for the Responses API.

        Args:
            user_input: User's input
            chat_history: Previous messages

        Returns:
            List of formatted messages
        """
        messages: List[Message] = []

        # Add system prompt if set
        if self.system_prompt:
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })

        # Add chat history
        if chat_history:
            messages.extend(chat_history)

        # Add current user input
        messages.append({
            "role": "user",
            "content": user_input
        })

        return messages

    def _select_model(self, reasoning: bool) -> str:
        """
        Select appropriate model based on reasoning flag.

        Args:
            reasoning: Whether reasoning is enabled

        Returns:
            Model identifier
        """
        if reasoning:
            # Use reasoning model (o3-mini is more cost-effective than o3)
            if self.model.startswith('o'):
                return self.model
            return "o3-mini"
        return self.model

    def _build_request_params(
        self,
        input_messages: List[Message],
        model: str,
        config: Optional[GenerateConfig] = None
    ) -> Dict[str, Any]:
        """
        Build request parameters for Responses API.

        Args:
            input_messages: Input messages
            model: Model to use
            config: Optional configuration

        Returns:
            Request parameters dictionary
        """
        params: Dict[str, Any] = {
            "model": model,
            "input": input_messages,
        }

        # Add tools if registered
        if self.tool_definitions:
            params["tools"] = self.tool_definitions

        # Add optional config parameters
        if config:
            if config.get("temperature") is not None:
                params["temperature"] = config["temperature"]
            if config.get("max_tokens") is not None:
                params["max_tokens"] = config["max_tokens"]
            if config.get("top_p") is not None:
                params["top_p"] = config["top_p"]
            if config.get("frequency_penalty") is not None:
                params["frequency_penalty"] = config["frequency_penalty"]
            if config.get("presence_penalty") is not None:
                params["presence_penalty"] = config["presence_penalty"]
            if config.get("stop") is not None:
                params["stop"] = config["stop"]

        return params

    def _execute_tool_loop(self, request_params: Dict[str, Any]) -> GenerateResponse:
        """
        Execute the tool calling loop until final response.

        This method handles:
        1. Making the API call
        2. Checking for tool calls in the response
        3. Executing tools and collecting results
        4. Sending results back to the API
        5. Repeating until no more tool calls

        Args:
            request_params: Request parameters

        Returns:
            Final GenerateResponse
        """
        iteration = 0
        all_tool_calls = []
        reasoning_output = None

        while iteration < self.max_tool_iterations:
            iteration += 1
            logger.debug(f"Tool loop iteration {iteration}/{self.max_tool_iterations}")

            # Make API call
            response = self.client.responses.create(**request_params)

            # Extract response data
            output_text = getattr(response, 'output_text', '')
            finish_reason = getattr(response, 'finish_reason', 'stop')
            usage = getattr(response, 'usage', {})

            # Check for reasoning output (for reasoning models)
            if hasattr(response, 'reasoning'):
                reasoning_output = response.reasoning

            # Check for tool calls in output
            tool_calls_in_response = []
            if hasattr(response, 'output'):
                for output_item in response.output:
                    if hasattr(output_item, 'type') and output_item.type == 'function_call':
                        tool_call = {
                            'id': output_item.call_id,
                            'type': 'function',
                            'function': {
                                'name': output_item.name,
                                'arguments': output_item.arguments
                            }
                        }
                        tool_calls_in_response.append(tool_call)
                        all_tool_calls.append(tool_call)

            # If no tool calls, we're done
            if not tool_calls_in_response:
                return GenerateResponse(
                    content=output_text,
                    reasoning=reasoning_output,
                    tool_calls=all_tool_calls,
                    finish_reason=finish_reason,
                    usage=self._format_usage(usage),
                    raw_response=response
                )

            # Execute tool calls and prepare results
            tool_outputs = []
            for tool_call in tool_calls_in_response:
                try:
                    tool_name = tool_call['function']['name']
                    arguments = tool_call['function']['arguments']

                    # Parse arguments if string
                    if isinstance(arguments, str):
                        arguments = json.loads(arguments)

                    # Execute tool
                    result = self._execute_tool_call(tool_name, arguments)

                    tool_outputs.append({
                        "type": "function_call_output",
                        "call_id": tool_call['id'],
                        "output": result
                    })

                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}")
                    tool_outputs.append({
                        "type": "function_call_output",
                        "call_id": tool_call['id'],
                        "output": json.dumps({"error": str(e)})
                    })

            # Update input with tool outputs for next iteration
            # The Responses API expects us to provide the tool outputs in the next call
            if isinstance(request_params['input'], list):
                request_params['input'] = request_params['input'] + tool_outputs
            else:
                request_params['input'] = tool_outputs

        # Max iterations reached
        logger.warning(f"Max tool iterations ({self.max_tool_iterations}) reached")
        return GenerateResponse(
            content=output_text if output_text else "Max tool iterations reached",
            reasoning=reasoning_output,
            tool_calls=all_tool_calls,
            finish_reason="max_iterations",
            usage=self._format_usage(usage) if 'usage' in locals() else {},
            raw_response=response if 'response' in locals() else None
        )

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool call and return the result as JSON string.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            JSON string of the result
        """
        if tool_name not in self.tools:
            error_msg = f"Tool '{tool_name}' not found in registered tools"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})

        try:
            tool_func = self.tools[tool_name]
            result = tool_func(**arguments)

            # Convert result to JSON string
            if isinstance(result, str):
                # If already a string, try to parse as JSON, otherwise wrap it
                try:
                    json.loads(result)
                    return result
                except json.JSONDecodeError:
                    return json.dumps({"result": result})
            else:
                return json.dumps(result)

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return json.dumps({"error": str(e)})

    def _format_usage(self, usage: Any) -> Dict[str, int]:
        """
        Format usage statistics.

        Args:
            usage: Usage object from API

        Returns:
            Dictionary with usage stats
        """
        if isinstance(usage, dict):
            return usage

        return {
            "prompt_tokens": getattr(usage, 'prompt_tokens', 0),
            "completion_tokens": getattr(usage, 'completion_tokens', 0),
            "total_tokens": getattr(usage, 'total_tokens', 0)
        }
