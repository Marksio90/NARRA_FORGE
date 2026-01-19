"""Unit tests for Interpreter agent."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from models.schemas.agent import InterpretRequest, InterpretResponse
from services.agents.interpreter import Interpreter
from services.model_policy import PipelineStage


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create mock OpenAI client."""
    client = MagicMock()
    client.chat_completion = AsyncMock()
    return client


@pytest.fixture
def interpreter(mock_openai_client: MagicMock) -> Interpreter:
    """Create Interpreter instance with mocked client."""
    return Interpreter(openai_client=mock_openai_client)


@pytest.mark.asyncio
async def test_interpreter_basic(interpreter: Interpreter, mock_openai_client: MagicMock) -> None:
    """Test basic interpretation of user request."""
    job_id = uuid4()

    # Mock OpenAI response
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "genre": "fantasy",
                "length": "novel",
                "themes": ["redemption", "power"],
                "setting": "medieval fantasy",
                "tone": "epic",
                "target_audience": "adult",
                "constraints": {},
            }
        ),
        "cost": 0.005,
        "created_at": datetime.utcnow(),
    }

    # Create request
    request = InterpretRequest(
        job_id=job_id,
        user_prompt="I want an epic fantasy story about redemption",
    )

    # Call interpreter
    response = await interpreter.interpret(request)

    # Verify
    assert isinstance(response, InterpretResponse)
    assert response.job_id == job_id
    assert response.agent == "interpreter"
    assert response.stage == PipelineStage.STRUCTURE
    assert response.genre == "fantasy"
    assert response.length == "novel"
    assert "redemption" in response.themes
    assert "power" in response.themes

    # Verify OpenAI was called
    mock_openai_client.chat_completion.assert_called_once()
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert len(call_kwargs["messages"]) == 2  # system + user


@pytest.mark.asyncio
async def test_interpreter_with_context(
    interpreter: Interpreter, mock_openai_client: MagicMock
) -> None:
    """Test interpretation with additional context."""
    job_id = uuid4()

    # Mock OpenAI response
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "genre": "sci-fi",
                "length": "novella",
                "themes": ["AI consciousness"],
                "setting": "near future",
                "tone": "philosophical",
                "target_audience": "literary fiction readers",
                "constraints": {"max_characters": 5},
            }
        ),
        "cost": 0.004,
        "created_at": datetime.utcnow(),
    }

    # Create request with context
    request = InterpretRequest(
        job_id=job_id,
        user_prompt="A story about AI",
        context={"series": "standalone", "max_length": "40000"},
    )

    # Call interpreter
    response = await interpreter.interpret(request)

    # Verify
    assert response.genre == "sci-fi"
    assert response.length == "novella"
    assert "constraints" in response.parameters
    assert response.parameters["constraints"]["max_characters"] == 5

    # Verify context was included in messages
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert len(call_kwargs["messages"]) == 3  # system + user + context


@pytest.mark.asyncio
async def test_interpreter_invalid_json(
    interpreter: Interpreter, mock_openai_client: MagicMock
) -> None:
    """Test handling of invalid JSON response."""
    job_id = uuid4()

    # Mock invalid JSON response
    mock_openai_client.chat_completion.return_value = {
        "content": "This is not valid JSON { broken",
        "cost": 0.003,
    }

    request = InterpretRequest(
        job_id=job_id,
        user_prompt="Test prompt",
    )

    # Should raise ValueError
    with pytest.raises(ValueError, match="Invalid JSON response"):
        await interpreter.interpret(request)


@pytest.mark.asyncio
async def test_interpreter_missing_required_fields(
    interpreter: Interpreter,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of response missing required fields."""
    job_id = uuid4()

    # Mock response missing 'length'
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps({"genre": "fantasy", "themes": ["adventure"]}),
        "cost": 0.003,
    }

    request = InterpretRequest(
        job_id=job_id,
        user_prompt="Test prompt",
    )

    # Should raise ValueError
    with pytest.raises(ValueError, match="missing required fields"):
        await interpreter.interpret(request)


@pytest.mark.asyncio
async def test_interpreter_uses_correct_model_policy(
    interpreter: Interpreter,
    mock_openai_client: MagicMock,
) -> None:
    """Test that Interpreter uses correct ModelPolicy settings."""
    job_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "genre": "thriller",
                "length": "short_story",
                "themes": ["mystery"],
                "setting": "modern",
                "tone": "suspenseful",
                "target_audience": "adult",
                "constraints": {},
            }
        ),
        "cost": 0.002,
    }

    request = InterpretRequest(
        job_id=job_id,
        user_prompt="Test prompt",
    )

    await interpreter.interpret(request)

    # Verify model policy was applied
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs["temperature"] == 0.3  # Analytical temperature for STRUCTURE
    assert call_kwargs["token_budget"] == 2000  # Budget for STRUCTURE


@pytest.mark.asyncio
async def test_interpreter_handles_non_list_themes(
    interpreter: Interpreter,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of themes as non-list value."""
    job_id = uuid4()

    # Mock response with themes as string instead of list
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "genre": "horror",
                "length": "short_story",
                "themes": "fear and isolation",  # String instead of list
                "setting": "abandoned house",
                "tone": "dark",
                "target_audience": "horror fans",
                "constraints": {},
            }
        ),
        "cost": 0.003,
        "created_at": datetime.utcnow(),
    }

    request = InterpretRequest(
        job_id=job_id,
        user_prompt="Test prompt",
    )

    response = await interpreter.interpret(request)

    # Should convert to list
    assert isinstance(response.themes, list)
    assert len(response.themes) > 0


def test_interpreter_initialization_with_client(mock_openai_client: MagicMock) -> None:
    """Test Interpreter initialization with provided client."""
    agent = Interpreter(openai_client=mock_openai_client)

    assert agent.client == mock_openai_client
    assert agent.stage == PipelineStage.STRUCTURE
    assert agent.model == "gpt-4o-mini"


def test_interpreter_initialization_without_client() -> None:
    """Test Interpreter initialization creates new client."""
    agent = Interpreter()

    assert agent.client is not None
    assert agent.stage == PipelineStage.STRUCTURE
    assert agent.model == "gpt-4o-mini"
