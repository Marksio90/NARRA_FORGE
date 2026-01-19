"""Integration tests with live OpenAI API.

WARNING: These tests make real API calls and will incur costs.
They are marked with @pytest.mark.integration and can be run with:
    pytest -m integration

To run these tests, ensure OPENAI_API_KEY is set in your environment.
"""

import os

import pytest

from core.exceptions import TokenBudgetExceededError
from services.openai_client import OpenAIClient
from services.token_counter import TokenCounter

# Skip all tests in this module if API key is not set
pytestmark = pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_chat_completion_mini_model() -> None:
    """Test live API call with mini model (limited tokens)."""
    client = OpenAIClient()

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello, world!' and nothing else."},
    ]

    result = await client.chat_completion(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=10,  # Limit tokens to minimize cost
        token_budget=1000,
    )

    # Verify response structure
    assert "content" in result
    assert "usage" in result
    assert "cost" in result
    assert "model" in result
    assert "request_id" in result

    # Verify content
    assert len(result["content"]) > 0
    assert "Hello" in result["content"] or "hello" in result["content"]

    # Verify usage
    assert result["usage"]["total_tokens"] > 0
    assert result["usage"]["total_tokens"] < 1000

    # Verify cost is calculated
    assert result["cost"] > 0
    assert result["cost"] < 0.01  # Should be < 1 cent

    print("\nLive API test result:")
    print(f"  Content: {result['content']}")
    print(f"  Tokens: {result['usage']['total_tokens']}")
    print(f"  Cost: ${result['cost']:.6f}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_token_budget_enforcement() -> None:
    """Test that token budget is enforced with live API."""
    client = OpenAIClient()

    messages = [
        {
            "role": "user",
            "content": "Write a detailed essay about artificial intelligence. "
            "Include history, current state, and future prospects.",
        },
    ]

    # Set a very low budget that will likely be exceeded
    with pytest.raises(TokenBudgetExceededError):
        await client.chat_completion(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=100,  # Request 100 tokens
            token_budget=50,  # But only allow 50 total (prompt + completion)
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_token_counter_accuracy() -> None:
    """Test token counter accuracy against live API."""
    client = OpenAIClient()

    messages = [
        {"role": "user", "content": "Count to five."},
    ]

    # Estimate tokens before API call
    estimated_prompt_tokens = TokenCounter.count_message_tokens(messages, model="gpt-4o-mini")

    # Make API call
    result = await client.chat_completion(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=20,
    )

    actual_prompt_tokens = result["usage"]["prompt_tokens"]

    print("\nToken counter accuracy test:")
    print(f"  Estimated prompt tokens: {estimated_prompt_tokens}")
    print(f"  Actual prompt tokens: {actual_prompt_tokens}")
    print(f"  Difference: {abs(estimated_prompt_tokens - actual_prompt_tokens)}")

    # Should be within 20% margin (token counting is approximate)
    margin = 0.2
    lower_bound = actual_prompt_tokens * (1 - margin)
    upper_bound = actual_prompt_tokens * (1 + margin)

    assert lower_bound <= estimated_prompt_tokens <= upper_bound, (
        f"Token estimate {estimated_prompt_tokens} not within {margin * 100}% "
        f"of actual {actual_prompt_tokens}"
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_model_comparison() -> None:
    """Test both mini and high models with same prompt."""
    client = OpenAIClient()

    messages = [
        {"role": "user", "content": "Say 'test' and nothing else."},
    ]

    # Test mini model
    result_mini = await client.chat_completion(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=5,
    )

    # Test high model
    result_high = await client.chat_completion(
        model="gpt-4o",
        messages=messages,
        temperature=0.0,
        max_tokens=5,
    )

    print("\nModel comparison:")
    print("  Mini model:")
    print(f"    Content: {result_mini['content']}")
    print(f"    Tokens: {result_mini['usage']['total_tokens']}")
    print(f"    Cost: ${result_mini['cost']:.6f}")
    print("  High model:")
    print(f"    Content: {result_high['content']}")
    print(f"    Tokens: {result_high['usage']['total_tokens']}")
    print(f"    Cost: ${result_high['cost']:.6f}")

    # High model should be more expensive for same tokens
    assert result_high["cost"] > result_mini["cost"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_cost_calculation() -> None:
    """Test that cost calculation is reasonable."""
    client = OpenAIClient()

    messages = [
        {"role": "user", "content": "Hi"},
    ]

    result = await client.chat_completion(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=5,
    )

    # Calculate cost manually
    manual_cost = TokenCounter.estimate_cost(
        prompt_tokens=result["usage"]["prompt_tokens"],
        completion_tokens=result["usage"]["completion_tokens"],
        model="gpt-4o-mini",
    )

    # Should match (within floating point precision)
    assert abs(result["cost"] - manual_cost) < 0.000001

    print("\nCost calculation verification:")
    print(f"  API cost: ${result['cost']:.8f}")
    print(f"  Manual calculation: ${manual_cost:.8f}")
    print(f"  Match: {abs(result['cost'] - manual_cost) < 0.000001}")
