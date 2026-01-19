"""Unit tests for Character Architect agent."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from models.schemas.agent import CharacterRequest, CharacterResponse
from services.agents.character_architect import CharacterArchitect
from services.model_policy import PipelineStage


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create mock OpenAI client."""
    client = MagicMock()
    client.chat_completion = AsyncMock()
    return client


@pytest.fixture
def character_architect(mock_openai_client: MagicMock) -> CharacterArchitect:
    """Create CharacterArchitect instance with mocked client."""
    return CharacterArchitect(openai_client=mock_openai_client)


@pytest.mark.asyncio
async def test_character_architect_basic(
    character_architect: CharacterArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test basic character creation."""
    job_id = uuid4()
    world_id = uuid4()

    # Mock OpenAI response with 3 characters
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "characters": [
                    {
                        "name": "Kael Thornweave",
                        "role": "protagonist",
                        "trajectory": [
                            {"stage": "beginning", "state": "broken"},
                            {"stage": "end", "state": "redeemed"},
                        ],
                        "relationships": [
                            {"character": "Lyra", "type": "ward", "dynamic": "protects"}
                        ],
                        "constraints": ["Guilt over past"],
                        "motivations": {"core": "redemption"},
                    },
                    {
                        "name": "Lyra",
                        "role": "supporting",
                        "trajectory": [
                            {"stage": "beginning", "state": "naive"},
                            {"stage": "end", "state": "wise"},
                        ],
                        "relationships": [],
                        "constraints": [],
                        "motivations": {"core": "growth"},
                    },
                    {
                        "name": "The Shadowmancer",
                        "role": "antagonist",
                        "trajectory": [
                            {"stage": "beginning", "state": "corrupted"},
                            {"stage": "end", "state": "defeated"},
                        ],
                        "relationships": [],
                        "constraints": [],
                        "motivations": {"core": "power"},
                    },
                ]
            }
        ),
        "cost": 0.020,
        "created_at": datetime.utcnow(),
    }

    # Create request
    request = CharacterRequest(
        job_id=job_id,
        world_id=world_id,
        character_count=3,
    )

    # Call character architect
    response = await character_architect.create_characters(request)

    # Verify
    assert isinstance(response, CharacterResponse)
    assert response.job_id == job_id
    assert response.agent == "architekt_postaci"
    assert response.stage == PipelineStage.CHARACTER_PROFILE
    assert response.character_count == 3
    assert len(response.character_ids) == 3

    # Verify OpenAI was called
    mock_openai_client.chat_completion.assert_called_once()
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert "3 characters" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_character_architect_with_types(
    character_architect: CharacterArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test character creation with specific types."""
    job_id = uuid4()
    world_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "characters": [
                    {
                        "name": "Hero",
                        "role": "protagonist",
                        "trajectory": [],
                        "relationships": [],
                        "constraints": [],
                        "motivations": {},
                    },
                    {
                        "name": "Villain",
                        "role": "antagonist",
                        "trajectory": [],
                        "relationships": [],
                        "constraints": [],
                        "motivations": {},
                    },
                ]
            }
        ),
        "cost": 0.015,
        "created_at": datetime.utcnow(),
    }

    request = CharacterRequest(
        job_id=job_id,
        world_id=world_id,
        character_count=2,
        character_types=["protagonist", "antagonist"],
    )

    response = await character_architect.create_characters(request)

    assert response.character_count == 2

    # Verify types were included
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert "protagonist" in call_kwargs["messages"][1]["content"]
    assert "antagonist" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_character_architect_with_constraints(
    character_architect: CharacterArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test character creation with constraints."""
    job_id = uuid4()
    world_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "characters": [
                    {
                        "name": "Test",
                        "role": "protagonist",
                        "trajectory": [],
                        "relationships": [],
                        "constraints": [],
                        "motivations": {},
                    }
                ]
            }
        ),
        "cost": 0.010,
        "created_at": datetime.utcnow(),
    }

    request = CharacterRequest(
        job_id=job_id,
        world_id=world_id,
        character_count=1,
        constraints={"age_range": "young_adult", "diversity": "high"},
    )

    response = await character_architect.create_characters(request)

    assert response.character_count == 1

    # Verify constraints were passed
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert "young_adult" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_character_architect_invalid_json(
    character_architect: CharacterArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of invalid JSON response."""
    job_id = uuid4()
    world_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": "Not valid JSON",
        "cost": 0.005,
    }

    request = CharacterRequest(
        job_id=job_id,
        world_id=world_id,
        character_count=1,
    )

    with pytest.raises(ValueError, match="Invalid JSON response"):
        await character_architect.create_characters(request)


@pytest.mark.asyncio
async def test_character_architect_missing_characters_list(
    character_architect: CharacterArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of response missing characters list."""
    job_id = uuid4()
    world_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps({"data": "wrong structure"}),
        "cost": 0.005,
    }

    request = CharacterRequest(
        job_id=job_id,
        world_id=world_id,
        character_count=1,
    )

    with pytest.raises(ValueError, match="missing 'characters' list"):
        await character_architect.create_characters(request)


@pytest.mark.asyncio
async def test_character_architect_count_mismatch_warning(
    character_architect: CharacterArchitect,
    mock_openai_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test warning when character count doesn't match requested."""
    job_id = uuid4()
    world_id = uuid4()

    # Return 2 characters when 3 requested
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "characters": [
                    {
                        "name": "Char1",
                        "role": "protagonist",
                        "trajectory": [],
                        "relationships": [],
                        "constraints": [],
                        "motivations": {},
                    },
                    {
                        "name": "Char2",
                        "role": "supporting",
                        "trajectory": [],
                        "relationships": [],
                        "constraints": [],
                        "motivations": {},
                    },
                ]
            }
        ),
        "cost": 0.010,
        "created_at": datetime.utcnow(),
    }

    request = CharacterRequest(
        job_id=job_id,
        world_id=world_id,
        character_count=3,
    )

    response = await character_architect.create_characters(request)

    # Should return 2 characters (what was received)
    assert response.character_count == 2
    assert len(response.character_ids) == 2


@pytest.mark.asyncio
async def test_character_architect_uses_correct_model_policy(
    character_architect: CharacterArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test that CharacterArchitect uses correct ModelPolicy settings."""
    job_id = uuid4()
    world_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "characters": [
                    {
                        "name": "Test",
                        "role": "protagonist",
                        "trajectory": [],
                        "relationships": [],
                        "constraints": [],
                        "motivations": {},
                    }
                ]
            }
        ),
        "cost": 0.005,
        "created_at": datetime.utcnow(),
    }

    request = CharacterRequest(
        job_id=job_id,
        world_id=world_id,
        character_count=1,
    )

    await character_architect.create_characters(request)

    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs["temperature"] == 0.5  # Balanced for CHARACTER_PROFILE
    assert call_kwargs["token_budget"] == 2000  # MINI_STAGES default budget


def test_character_architect_initialization() -> None:
    """Test CharacterArchitect initialization."""
    agent = CharacterArchitect()

    assert agent.client is not None
    assert agent.stage == PipelineStage.CHARACTER_PROFILE
    assert agent.model == "gpt-4o-mini"
