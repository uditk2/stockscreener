"""
Decorators for LLM module, including tool decorator for automatic schema extraction.
"""
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, get_type_hints, get_origin, get_args
from functools import wraps

from app.llm_module.types import ToolDefinition

logger = logging.getLogger(__name__)


def _python_type_to_json_schema(py_type: Any) -> Dict[str, Any]:
    """
    Convert Python type hints to JSON schema types.

    Args:
        py_type: Python type annotation

    Returns:
        JSON schema type definition
    """
    # Get origin for generic types
    origin = get_origin(py_type)

    # Handle Optional[T] (Union[T, None])
    if origin is type(Optional):
        args = get_args(py_type)
        if len(args) == 2 and type(None) in args:
            inner_type = args[0] if args[1] is type(None) else args[1]
            return _python_type_to_json_schema(inner_type)

    # Handle List[T]
    if origin is list or origin is List:
        args = get_args(py_type)
        item_type = args[0] if args else Any
        return {
            "type": "array",
            "items": _python_type_to_json_schema(item_type)
        }

    # Handle Dict[K, V]
    if origin is dict or origin is Dict:
        return {"type": "object"}

    # Basic type mappings
    type_map = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        list: {"type": "array"},
        dict: {"type": "object"},
        Any: {"type": "string"},  # Default to string for Any
    }

    # Handle the type itself (not origin)
    if py_type in type_map:
        return type_map[py_type]

    # Check if it's a string representation
    if isinstance(py_type, str):
        if py_type == "str":
            return {"type": "string"}
        elif py_type == "int":
            return {"type": "integer"}
        elif py_type == "float":
            return {"type": "number"}
        elif py_type == "bool":
            return {"type": "boolean"}

    # Default to string for unknown types
    logger.warning(f"Unknown type {py_type}, defaulting to string")
    return {"type": "string"}


def tool(description: Optional[str] = None, name: Optional[str] = None):
    """
    Decorator to mark a function as an LLM tool and automatically extract its JSON schema.

    The decorator extracts:
    - Function name (or uses provided name)
    - Function description (from docstring or provided description)
    - Parameter types and descriptions (from type hints and docstring)

    Example:
        @tool(description="Get the current weather for a location")
        def get_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
            '''
            Get weather information.

            Args:
                location: The city name or coordinates
                unit: Temperature unit (celsius or fahrenheit)

            Returns:
                Weather information dictionary
            '''
            # Implementation
            return {"temperature": 20, "conditions": "sunny"}

    Args:
        description: Optional description of what the tool does
        name: Optional custom name for the tool (defaults to function name)

    Returns:
        Decorated function with tool metadata
    """
    def decorator(func: Callable) -> Callable:
        # Get function name
        tool_name = name or func.__name__

        # Get description from parameter or docstring
        tool_description = description
        if not tool_description and func.__doc__:
            # Extract first line of docstring as description
            doc_lines = func.__doc__.strip().split('\n')
            tool_description = doc_lines[0].strip()

        # Get function signature
        sig = inspect.signature(func)

        # Get type hints
        try:
            type_hints = get_type_hints(func)
        except Exception as e:
            logger.warning(f"Failed to get type hints for {tool_name}: {e}")
            type_hints = {}

        # Parse docstring for parameter descriptions
        param_descriptions = {}
        if func.__doc__:
            doc = func.__doc__
            # Simple parser for "Args:" section
            if "Args:" in doc:
                args_section = doc.split("Args:")[1]
                if "Returns:" in args_section:
                    args_section = args_section.split("Returns:")[0]

                for line in args_section.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        parts = line.split(':', 1)
                        param_name = parts[0].strip()
                        param_desc = parts[1].strip() if len(parts) > 1 else ""
                        param_descriptions[param_name] = param_desc

        # Build parameters schema
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            # Skip self and cls parameters
            if param_name in ('self', 'cls'):
                continue

            # Get type from type hints or annotation
            param_type = type_hints.get(param_name, param.annotation)
            if param_type == inspect.Parameter.empty:
                param_type = Any

            # Convert to JSON schema
            param_schema = _python_type_to_json_schema(param_type)

            # Add description if available
            if param_name in param_descriptions:
                param_schema["description"] = param_descriptions[param_name]

            properties[param_name] = param_schema

            # Check if required (no default value)
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        # Build tool definition
        tool_definition: ToolDefinition = {
            "type": "function",
            "name": tool_name,
            "description": tool_description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

        # Attach metadata to function
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._tool_definition = tool_definition
        wrapper._tool_function = func
        wrapper._is_tool = True

        return wrapper

    return decorator


def get_tool_definition(func: Callable) -> Optional[ToolDefinition]:
    """
    Extract tool definition from a decorated function.

    Args:
        func: Function to extract definition from

    Returns:
        Tool definition or None if not a tool
    """
    if hasattr(func, '_tool_definition'):
        return func._tool_definition
    return None


def is_tool(func: Callable) -> bool:
    """
    Check if a function is decorated as a tool.

    Args:
        func: Function to check

    Returns:
        True if function is a tool
    """
    return hasattr(func, '_is_tool') and func._is_tool
