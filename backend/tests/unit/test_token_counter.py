"""Unit tests for token counter."""

from services.token_counter import TokenCounter


def test_count_tokens_simple_text() -> None:
    """Test counting tokens in simple text."""
    text = "Hello, world!"
    count = TokenCounter.count_tokens(text)
    assert count > 0
    assert count < 10  # Should be around 3-4 tokens


def test_count_tokens_empty_text() -> None:
    """Test counting tokens in empty text."""
    count = TokenCounter.count_tokens("")
    assert count == 0


def test_count_tokens_longer_text() -> None:
    """Test counting tokens in longer text."""
    text = "This is a longer piece of text that should have more tokens. " * 10
    count = TokenCounter.count_tokens(text)
    assert count > 100  # Should be significantly more tokens


def test_count_tokens_different_models() -> None:
    """Test that token counting works with different models."""
    text = "The quick brown fox jumps over the lazy dog."

    count_mini = TokenCounter.count_tokens(text, model="gpt-4o-mini")
    count_high = TokenCounter.count_tokens(text, model="gpt-4o")

    # Same encoding should give same count
    assert count_mini == count_high
    assert count_mini > 0


def test_count_message_tokens_single_message() -> None:
    """Test counting tokens in a single message."""
    messages = [{"role": "user", "content": "Hello!"}]
    count = TokenCounter.count_message_tokens(messages)
    assert count > 0
    # Should include message overhead
    assert count > len("Hello!")


def test_count_message_tokens_multiple_messages() -> None:
    """Test counting tokens in multiple messages."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    count = TokenCounter.count_message_tokens(messages)
    assert count > 0
    # Should be more than single message
    single_count = TokenCounter.count_message_tokens([messages[0]])
    assert count > single_count


def test_count_message_tokens_with_name() -> None:
    """Test counting tokens with name field."""
    messages = [
        {"role": "user", "content": "Hello!", "name": "John"},
    ]
    count_with_name = TokenCounter.count_message_tokens(messages)

    messages_without_name = [
        {"role": "user", "content": "Hello!"},
    ]
    count_without_name = TokenCounter.count_message_tokens(messages_without_name)

    # With name should have slightly more tokens
    assert count_with_name > count_without_name


def test_estimate_cost_mini_model() -> None:
    """Test cost estimation for mini model."""
    cost = TokenCounter.estimate_cost(
        prompt_tokens=1000, completion_tokens=500, model="gpt-4o-mini"
    )
    assert cost > 0
    # Should be relatively cheap
    assert cost < 0.01  # Less than 1 cent for 1500 tokens


def test_estimate_cost_high_model() -> None:
    """Test cost estimation for high model."""
    cost = TokenCounter.estimate_cost(prompt_tokens=1000, completion_tokens=500, model="gpt-4o")
    assert cost > 0
    # Should be more expensive than mini
    mini_cost = TokenCounter.estimate_cost(
        prompt_tokens=1000, completion_tokens=500, model="gpt-4o-mini"
    )
    assert cost > mini_cost


def test_estimate_cost_zero_tokens() -> None:
    """Test cost estimation with zero tokens."""
    cost = TokenCounter.estimate_cost(prompt_tokens=0, completion_tokens=0, model="gpt-4o-mini")
    assert cost == 0.0


def test_estimate_cost_unknown_model() -> None:
    """Test cost estimation with unknown model."""
    cost = TokenCounter.estimate_cost(
        prompt_tokens=1000, completion_tokens=500, model="unknown-model"
    )
    assert cost == 0.0  # Should return 0 for unknown models


def test_check_budget_within_budget() -> None:
    """Test checking budget when text is within budget."""
    text = "Short text"
    fits, count = TokenCounter.check_budget(text, budget=1000)
    assert fits is True
    assert count > 0
    assert count < 1000


def test_check_budget_exceeds_budget() -> None:
    """Test checking budget when text exceeds budget."""
    text = "word " * 1000  # 1000 words
    fits, count = TokenCounter.check_budget(text, budget=100)
    assert fits is False
    assert count > 100


def test_check_budget_with_margin() -> None:
    """Test checking budget with safety margin."""
    text = "word " * 50
    count = TokenCounter.count_tokens(text)

    # With 10% margin, effective budget is budget * 0.9
    # To fit count tokens with 10% margin, need budget = count / 0.9
    required_budget = int(count / 0.9) + 1
    fits, _ = TokenCounter.check_budget(text, budget=required_budget, allow_margin=0.1)
    # Should fit with the margin
    assert fits is True

    # Should not fit with insufficient budget
    insufficient_budget = count - 10
    fits_not, _ = TokenCounter.check_budget(text, budget=insufficient_budget, allow_margin=0.1)
    assert fits_not is False


def test_check_budget_different_models() -> None:
    """Test budget checking with different models."""
    text = "The quick brown fox jumps over the lazy dog."

    fits_mini, count_mini = TokenCounter.check_budget(text, budget=100, model="gpt-4o-mini")
    fits_high, count_high = TokenCounter.check_budget(text, budget=100, model="gpt-4o")

    assert fits_mini == fits_high  # Same encoding
    assert count_mini == count_high


def test_encoding_cache() -> None:
    """Test that encoding is cached for performance."""
    text = "Test text"

    # Call multiple times - should use cached encoding
    count1 = TokenCounter.count_tokens(text, model="gpt-4o-mini")
    count2 = TokenCounter.count_tokens(text, model="gpt-4o-mini")
    count3 = TokenCounter.count_tokens(text, model="gpt-4o-mini")

    # All should return the same result
    assert count1 == count2 == count3
