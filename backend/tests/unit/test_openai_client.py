"""Unit tests for OpenAI client with mocked responses."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import openai
import pytest

from core.exceptions import TokenBudgetExceededError
from services.openai_client import OpenAIClient


@pytest.fixture
def openai_client() -> OpenAIClient:
    """Create OpenAI client instance."""
    return OpenAIClient()


@pytest.fixture
def mock_openai_response() -> MagicMock:
    """Create mock OpenAI response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = "This is a test response."

    # Mock usage
    response.usage = MagicMock()
    response.usage.prompt_tokens = 10
    response.usage.completion_tokens = 5
    response.usage.total_tokens = 15

    return response


@pytest.fixture
def mock_http_response() -> MagicMock:
    """Create mock httpx response for OpenAI exceptions."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 429
    response.headers = {"x-request-id": "test-request-id"}
    response.request = MagicMock(spec=httpx.Request)
    response.request.method = "POST"
    response.request.url = "https://api.openai.com/v1/chat/completions"
    return response


@pytest.fixture
def mock_http_request() -> MagicMock:
    """Create mock httpx request for OpenAI exceptions."""
    request = MagicMock(spec=httpx.Request)
    request.method = "POST"
    request.url = "https://api.openai.com/v1/chat/completions"
    return request


@pytest.mark.asyncio
async def test_chat_completion_success(
    openai_client: OpenAIClient, mock_openai_response: MagicMock, mocker: MagicMock
) -> None:
    """Test successful chat completion."""
    # Mock the client.chat.completions.create method
    mock_create = AsyncMock(return_value=mock_openai_response)
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)

    messages = [{"role": "user", "content": "Hello!"}]
    result = await openai_client.chat_completion(
        model="gpt-4o-mini", messages=messages, temperature=0.7
    )

    # Verify result structure
    assert "content" in result
    assert "usage" in result
    assert "cost" in result
    assert "model" in result
    assert "request_id" in result

    # Verify values
    assert result["content"] == "This is a test response."
    assert result["model"] == "gpt-4o-mini"
    assert result["usage"]["total_tokens"] == 15
    assert result["cost"] > 0

    # Verify API was called
    mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_chat_completion_with_token_budget(
    openai_client: OpenAIClient, mock_openai_response: MagicMock, mocker: MagicMock
) -> None:
    """Test chat completion with token budget."""
    mock_create = AsyncMock(return_value=mock_openai_response)
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)

    messages = [{"role": "user", "content": "Hello!"}]
    result = await openai_client.chat_completion(
        model="gpt-4o-mini", messages=messages, token_budget=100
    )

    # Should succeed as usage (15) < budget (100)
    assert result["usage"]["total_tokens"] == 15


@pytest.mark.asyncio
async def test_chat_completion_exceeds_token_budget(
    openai_client: OpenAIClient, mock_openai_response: MagicMock, mocker: MagicMock
) -> None:
    """Test chat completion that exceeds token budget."""
    mock_create = AsyncMock(return_value=mock_openai_response)
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)

    messages = [{"role": "user", "content": "Hello!"}]

    # Budget is 10, but usage is 15 - should raise
    with pytest.raises(TokenBudgetExceededError, match="exceeds budget"):
        await openai_client.chat_completion(model="gpt-4o-mini", messages=messages, token_budget=10)


@pytest.mark.asyncio
async def test_chat_completion_timeout_mini_model(
    openai_client: OpenAIClient, mock_openai_response: MagicMock, mocker: MagicMock
) -> None:
    """Test that mini model uses shorter timeout."""
    mock_create = AsyncMock(return_value=mock_openai_response)
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)

    messages = [{"role": "user", "content": "Hello!"}]
    await openai_client.chat_completion(model="gpt-4o-mini", messages=messages)

    # Verify timeout was set correctly
    call_kwargs = mock_create.call_args.kwargs
    assert call_kwargs["timeout"] == OpenAIClient.TIMEOUT_MINI


@pytest.mark.asyncio
async def test_chat_completion_timeout_high_model(
    openai_client: OpenAIClient, mock_openai_response: MagicMock, mocker: MagicMock
) -> None:
    """Test that high model uses longer timeout."""
    mock_create = AsyncMock(return_value=mock_openai_response)
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)

    messages = [{"role": "user", "content": "Hello!"}]
    await openai_client.chat_completion(model="gpt-4o", messages=messages)

    # Verify timeout was set correctly
    call_kwargs = mock_create.call_args.kwargs
    assert call_kwargs["timeout"] == OpenAIClient.TIMEOUT_HIGH


@pytest.mark.asyncio
async def test_chat_completion_retry_on_rate_limit(
    openai_client: OpenAIClient,
    mock_openai_response: MagicMock,
    mock_http_response: MagicMock,
    mocker: MagicMock,
) -> None:
    """Test retry logic on rate limit error."""
    # First call raises RateLimitError, second succeeds
    mock_create = AsyncMock(
        side_effect=[
            openai.RateLimitError("Rate limit exceeded", response=mock_http_response, body=None),
            mock_openai_response,
        ]
    )
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)
    mocker.patch("time.sleep")  # Mock sleep to avoid delays in tests

    messages = [{"role": "user", "content": "Hello!"}]
    result = await openai_client.chat_completion(model="gpt-4o-mini", messages=messages)

    # Should succeed after retry
    assert result["content"] == "This is a test response."
    assert mock_create.call_count == 2


@pytest.mark.asyncio
async def test_chat_completion_retry_on_timeout(
    openai_client: OpenAIClient,
    mock_openai_response: MagicMock,
    mock_http_request: MagicMock,
    mocker: MagicMock,
) -> None:
    """Test retry logic on timeout error."""
    mock_create = AsyncMock(
        side_effect=[
            openai.APITimeoutError(request=mock_http_request),
            mock_openai_response,
        ]
    )
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)
    mocker.patch("time.sleep")

    messages = [{"role": "user", "content": "Hello!"}]
    result = await openai_client.chat_completion(model="gpt-4o-mini", messages=messages)

    assert result["content"] == "This is a test response."
    assert mock_create.call_count == 2


@pytest.mark.asyncio
async def test_chat_completion_retry_on_connection_error(
    openai_client: OpenAIClient,
    mock_openai_response: MagicMock,
    mock_http_request: MagicMock,
    mocker: MagicMock,
) -> None:
    """Test retry logic on connection error."""
    mock_create = AsyncMock(
        side_effect=[
            openai.APIConnectionError(request=mock_http_request),
            mock_openai_response,
        ]
    )
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)
    mocker.patch("time.sleep")

    messages = [{"role": "user", "content": "Hello!"}]
    result = await openai_client.chat_completion(model="gpt-4o-mini", messages=messages)

    assert result["content"] == "This is a test response."
    assert mock_create.call_count == 2


@pytest.mark.asyncio
async def test_chat_completion_max_retries_exceeded(
    openai_client: OpenAIClient, mock_http_response: MagicMock, mocker: MagicMock
) -> None:
    """Test that max retries are respected."""
    # Always raise RateLimitError
    mock_create = AsyncMock(
        side_effect=openai.RateLimitError(
            "Rate limit exceeded", response=mock_http_response, body=None
        )
    )
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)
    mocker.patch("time.sleep")

    messages = [{"role": "user", "content": "Hello!"}]

    with pytest.raises(openai.RateLimitError):
        await openai_client.chat_completion(model="gpt-4o-mini", messages=messages)

    # Should have tried MAX_RETRIES times
    assert mock_create.call_count == OpenAIClient.MAX_RETRIES


@pytest.mark.asyncio
async def test_chat_completion_non_retryable_error(
    openai_client: OpenAIClient, mock_http_response: MagicMock, mocker: MagicMock
) -> None:
    """Test that non-retryable errors are not retried."""
    # Raise a non-retryable error
    mock_create = AsyncMock(
        side_effect=openai.AuthenticationError(
            "Invalid API key", response=mock_http_response, body=None
        )
    )
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)

    messages = [{"role": "user", "content": "Hello!"}]

    with pytest.raises(openai.AuthenticationError):
        await openai_client.chat_completion(model="gpt-4o-mini", messages=messages)

    # Should have tried only once (no retry for auth errors)
    assert mock_create.call_count == 1


@pytest.mark.asyncio
async def test_calculate_cost_mini_model(openai_client: OpenAIClient) -> None:
    """Test cost calculation for mini model."""
    cost = openai_client._calculate_cost(model="gpt-4o-mini", input_tokens=1000, output_tokens=500)
    assert cost > 0
    assert cost < 0.01  # Should be less than 1 cent


@pytest.mark.asyncio
async def test_calculate_cost_high_model(openai_client: OpenAIClient) -> None:
    """Test cost calculation for high model."""
    cost = openai_client._calculate_cost(model="gpt-4o", input_tokens=1000, output_tokens=500)

    mini_cost = openai_client._calculate_cost(
        model="gpt-4o-mini", input_tokens=1000, output_tokens=500
    )

    # High model should be more expensive
    assert cost > mini_cost


@pytest.mark.asyncio
async def test_get_timeout(openai_client: OpenAIClient) -> None:
    """Test timeout selection based on model."""
    assert openai_client._get_timeout("gpt-4o-mini") == OpenAIClient.TIMEOUT_MINI
    assert openai_client._get_timeout("gpt-4o") == OpenAIClient.TIMEOUT_HIGH


@pytest.mark.asyncio
async def test_chat_completion_with_max_tokens(
    openai_client: OpenAIClient, mock_openai_response: MagicMock, mocker: MagicMock
) -> None:
    """Test chat completion with max_tokens parameter."""
    mock_create = AsyncMock(return_value=mock_openai_response)
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)

    messages = [{"role": "user", "content": "Hello!"}]
    await openai_client.chat_completion(model="gpt-4o-mini", messages=messages, max_tokens=100)

    # Verify max_tokens was passed
    call_kwargs = mock_create.call_args.kwargs
    assert call_kwargs["max_tokens"] == 100


@pytest.mark.asyncio
async def test_chat_completion_no_usage_data(
    openai_client: OpenAIClient, mocker: MagicMock
) -> None:
    """Test handling response without usage data."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = "Test response"
    response.usage = None  # No usage data

    mock_create = AsyncMock(return_value=response)
    mocker.patch.object(openai_client.client.chat.completions, "create", mock_create)

    messages = [{"role": "user", "content": "Hello!"}]
    result = await openai_client.chat_completion(model="gpt-4o-mini", messages=messages)

    # Should handle gracefully with 0 tokens
    assert result["usage"]["total_tokens"] == 0
    assert result["cost"] == 0.0
