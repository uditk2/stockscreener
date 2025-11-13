"""
Example usage of the LLM module.

This file demonstrates how to use the LLM module with OpenAI's Responses API.
"""
import os
from typing import Dict, Any

from app.llm_module import OpenAIClient, tool


# Example 1: Simple tool definition
@tool(description="Get the current weather for a location")
def get_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
    """
    Get current weather information.

    Args:
        location: The city name or location
        unit: Temperature unit (celsius or fahrenheit)

    Returns:
        Dictionary with weather information
    """
    # This is a mock implementation
    # In real use, you'd call a weather API
    return {
        "location": location,
        "temperature": 20,
        "unit": unit,
        "conditions": "sunny",
        "humidity": 65
    }


# Example 2: More complex tool with multiple parameters
@tool(description="Calculate stock metrics based on price data")
def calculate_stock_metrics(
    symbol: str,
    current_price: float,
    volume: int,
    prev_close: float
) -> Dict[str, Any]:
    """
    Calculate various stock metrics.

    Args:
        symbol: Stock ticker symbol
        current_price: Current stock price
        volume: Trading volume
        prev_close: Previous closing price

    Returns:
        Dictionary with calculated metrics
    """
    price_change = current_price - prev_close
    price_change_pct = (price_change / prev_close) * 100

    return {
        "symbol": symbol,
        "current_price": current_price,
        "volume": volume,
        "price_change": round(price_change, 2),
        "price_change_percent": round(price_change_pct, 2),
        "status": "up" if price_change > 0 else "down"
    }


# Example 3: Tool for data retrieval
@tool(description="Search for stock information in database")
def search_stocks(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for stocks matching the query.

    Args:
        query: Search query (symbol or company name)
        limit: Maximum number of results

    Returns:
        Dictionary with search results
    """
    # Mock implementation
    return {
        "query": query,
        "results": [
            {"symbol": "AAPL", "name": "Apple Inc.", "price": 150.00},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": 140.00},
        ][:limit]
    }


def example_basic_usage():
    """Example of basic usage without tools."""
    print("\n=== Example 1: Basic Usage ===")

    # Initialize client
    client = OpenAIClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )

    # Set system prompt
    client.set_system_prompt("You are a helpful assistant that provides concise answers.")

    # Generate response
    response = client.generate(
        user_input="What is the capital of France?",
        reasoning=False
    )

    print(f"Response: {response['content']}")
    print(f"Usage: {response['usage']}")


def example_with_tools():
    """Example using tool calling."""
    print("\n=== Example 2: With Tools ===")

    # Initialize client
    client = OpenAIClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )

    # Set system prompt
    client.set_system_prompt(
        "You are a helpful assistant with access to weather information. "
        "Use the get_weather tool when users ask about weather."
    )

    # Register tool
    client.register_tool(get_weather)

    # Generate response - LLM will automatically call the tool
    response = client.generate(
        user_input="What's the weather like in San Francisco?",
        reasoning=False
    )

    print(f"Response: {response['content']}")
    print(f"Tool calls made: {len(response['tool_calls'])}")
    if response['tool_calls']:
        for tc in response['tool_calls']:
            print(f"  - Called: {tc['function']['name']}")


def example_with_multiple_tools():
    """Example with multiple tools."""
    print("\n=== Example 3: Multiple Tools ===")

    client = OpenAIClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )

    client.set_system_prompt(
        "You are a stock market assistant with access to stock data and calculations. "
        "Help users analyze stocks using the available tools."
    )

    # Register multiple tools
    client.register_tools([
        calculate_stock_metrics,
        search_stocks
    ])

    # Generate response
    response = client.generate(
        user_input="Search for Apple stock and calculate its metrics if the current price is $150, "
                  "volume is 50000000, and previous close was $148",
        reasoning=False
    )

    print(f"Response: {response['content']}")
    print(f"Tool calls made: {len(response['tool_calls'])}")


def example_with_reasoning():
    """Example using reasoning mode."""
    print("\n=== Example 4: Reasoning Mode ===")

    client = OpenAIClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="o3-mini"  # Reasoning model
    )

    client.set_system_prompt("You are a mathematical problem solver.")

    # Generate response with reasoning
    response = client.generate(
        user_input="If I invest $1000 at 5% annual interest compounded monthly, "
                  "how much will I have after 10 years?",
        reasoning=True  # Enable reasoning mode
    )

    print(f"Response: {response['content']}")
    if response['reasoning']:
        print(f"Reasoning: {response['reasoning']}")


def example_with_chat_history():
    """Example with conversation history."""
    print("\n=== Example 5: Chat History ===")

    client = OpenAIClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )

    client.set_system_prompt("You are a helpful assistant.")

    # First message
    chat_history = []

    response1 = client.generate(
        user_input="My name is Alice and I like programming.",
        chat_history=chat_history
    )
    print(f"Response 1: {response1['content']}")

    # Add to history
    chat_history.append({"role": "user", "content": "My name is Alice and I like programming."})
    chat_history.append({"role": "assistant", "content": response1['content']})

    # Second message - should remember the name
    response2 = client.generate(
        user_input="What's my name and what do I like?",
        chat_history=chat_history
    )
    print(f"Response 2: {response2['content']}")


def example_with_markdown_prompt():
    """Example loading system prompt from markdown file."""
    print("\n=== Example 6: Markdown System Prompt ===")

    # Create a sample markdown file
    prompt_file = "/tmp/system_prompt.md"
    with open(prompt_file, "w") as f:
        f.write("""# Stock Analysis Assistant

You are an expert stock market analyst with deep knowledge of:
- Technical analysis
- Fundamental analysis
- Market trends
- Risk management

## Your Role
Provide clear, actionable insights to help users make informed investment decisions.

## Guidelines
- Always explain your reasoning
- Consider multiple perspectives
- Highlight potential risks
- Keep explanations concise
""")

    client = OpenAIClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )

    # Load from markdown file
    client.set_system_prompt(prompt_file)

    response = client.generate(
        user_input="What should I consider when analyzing a tech stock?"
    )

    print(f"Response: {response['content']}")


if __name__ == "__main__":
    """
    Run examples.

    Make sure to set OPENAI_API_KEY environment variable before running:
        export OPENAI_API_KEY=your-api-key-here
        python -m app.llm_module.example_usage
    """

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        print("Example: export OPENAI_API_KEY=your-key-here")
        exit(1)

    try:
        # Run examples
        example_basic_usage()
        example_with_tools()
        example_with_multiple_tools()
        example_with_chat_history()
        example_with_markdown_prompt()

        # Uncomment to test reasoning mode (requires reasoning model access)
        # example_with_reasoning()

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
