"""Unit tests for World Architect agent."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from models.schemas.agent import WorldRequest, WorldResponse
from services.agents.world_architect import WorldArchitect
from services.model_policy import PipelineStage


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create mock OpenAI client."""
    client = MagicMock()
    client.chat_completion = AsyncMock()
    return client


@pytest.fixture
def world_architect(mock_openai_client: MagicMock) -> WorldArchitect:
    """Create WorldArchitect instance with mocked client."""
    return WorldArchitect(openai_client=mock_openai_client)


@pytest.mark.asyncio
async def test_world_architect_basic(
    world_architect: WorldArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test basic world creation."""
    job_id = uuid4()

    # Mock OpenAI response
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "world_name": "Aethermoor",
                "summary": "A post-apocalyptic fantasy world where magic is fading.",
                "rules": [
                    "Magic requires aether crystals",
                    "Crystals are finite and irreplaceable",
                    "Technology beyond Renaissance fails near magic",
                ],
                "geography": {
                    "continents": ["Nordreach", "Shattered Isles"],
                    "climate": "temperate",
                },
                "history": [
                    {"year": 0, "event": "The Sundering"},
                    {"year": 500, "event": "Present day"},
                ],
                "themes": ["scarcity", "rebuilding"],
            }
        ),
        "cost": 0.015,
        "created_at": datetime.utcnow(),
    }

    # Create request
    request = WorldRequest(
        job_id=job_id,
        genre="fantasy",
        themes=["magic", "post-apocalypse"],
    )

    # Call world architect
    response = await world_architect.create_world(request)

    # Verify
    assert isinstance(response, WorldResponse)
    assert response.job_id == job_id
    assert response.agent == "architekt_swiata"
    assert response.stage == PipelineStage.STRUCTURE
    assert response.world_name == "Aethermoor"
    assert len(response.rules) == 3
    assert "scarcity" in response.themes

    # Verify OpenAI was called
    mock_openai_client.chat_completion.assert_called_once()
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert "fantasy" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_world_architect_with_constraints(
    world_architect: WorldArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test world creation with constraints."""
    job_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "world_name": "Neo-Tokyo 2157",
                "summary": "Cyberpunk megacity with advanced AI.",
                "rules": [
                    "AI cannot harm humans",
                    "Megacorps control everything",
                    "Privacy is extinct",
                ],
                "geography": {"continents": ["Unified Asia"], "climate": "urban heat island"},
                "history": [
                    {"year": 2100, "event": "AI Singularity"},
                    {"year": 2157, "event": "Present day"},
                ],
                "themes": ["surveillance", "transhumanism"],
            }
        ),
        "cost": 0.012,
        "created_at": datetime.utcnow(),
    }

    request = WorldRequest(
        job_id=job_id,
        genre="sci-fi",
        themes=["AI", "dystopia"],
        constraints={"setting": "cyberpunk", "tone": "noir"},
    )

    response = await world_architect.create_world(request)

    # Verify constraints were passed
    assert response.world_name == "Neo-Tokyo 2157"
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert "cyberpunk" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_world_architect_with_summary(
    world_architect: WorldArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test world creation with user summary guidance."""
    job_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "world_name": "The Shattered Empire",
                "summary": "A world recovering from magical war.",
                "rules": ["Magic is forbidden", "Empire is fragmented"],
                "geography": {"continents": ["Old Empire"]},
                "history": [{"year": 0, "event": "The War"}],
                "themes": ["recovery"],
            }
        ),
        "cost": 0.010,
        "created_at": datetime.utcnow(),
    }

    request = WorldRequest(
        job_id=job_id,
        genre="fantasy",
        themes=["war", "recovery"],
        summary="A world where magic was used in a devastating war",
    )

    _ = await world_architect.create_world(request)

    # Verify summary was included
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert "devastating war" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_world_architect_invalid_json(
    world_architect: WorldArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of invalid JSON response."""
    job_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": "Not valid JSON",
        "cost": 0.005,
    }

    request = WorldRequest(
        job_id=job_id,
        genre="fantasy",
        themes=["adventure"],
    )

    with pytest.raises(ValueError, match="Invalid JSON response"):
        await world_architect.create_world(request)


@pytest.mark.asyncio
async def test_world_architect_missing_required_fields(
    world_architect: WorldArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of response missing required fields."""
    job_id = uuid4()

    # Missing 'rules'
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps({"world_name": "Test World", "summary": "A test world"}),
        "cost": 0.005,
    }

    request = WorldRequest(
        job_id=job_id,
        genre="fantasy",
        themes=["test"],
    )

    with pytest.raises(ValueError, match="missing fields"):
        await world_architect.create_world(request)


@pytest.mark.asyncio
async def test_world_architect_uses_correct_model_policy(
    world_architect: WorldArchitect,
    mock_openai_client: MagicMock,
) -> None:
    """Test that WorldArchitect uses correct ModelPolicy settings."""
    job_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {"world_name": "Test", "summary": "Test", "rules": ["Test rule"], "themes": ["test"]}
        ),
        "cost": 0.005,
        "created_at": datetime.utcnow(),
    }

    request = WorldRequest(
        job_id=job_id,
        genre="fantasy",
        themes=["test"],
    )

    await world_architect.create_world(request)

    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs["temperature"] == 0.3  # Analytical for STRUCTURE
    assert call_kwargs["token_budget"] == 2000


def test_world_architect_create_world_schema(world_architect: WorldArchitect) -> None:
    """Test creating WorldSchema from response."""
    world_id = uuid4()
    job_id = uuid4()

    response = WorldResponse(
        id=world_id,
        job_id=job_id,
        world_id=world_id,
        world_name="Test World",
        summary="A test world",
        rules=["Rule 1"],
        themes=["theme1"],
        created_at=datetime.utcnow(),
    )

    world_data = {
        "world_name": "Test World",
        "summary": "A test world",
        "rules": ["Rule 1"],
        "geography": {"continents": ["Test"]},
        "history": [{"year": 0, "event": "Start"}],
        "themes": ["theme1"],
    }

    schema = world_architect.create_world_schema(response, world_data)

    assert schema.id == world_id
    assert schema.name == "Test World"
    assert len(schema.rules) == 1
    assert schema.checksum is not None
    assert len(schema.checksum) == 64  # SHA256 hex


def test_world_architect_initialization() -> None:
    """Test WorldArchitect initialization."""
    agent = WorldArchitect()

    assert agent.client is not None
    assert agent.stage == PipelineStage.STRUCTURE
    assert agent.model == "gpt-4o-mini"
    assert agent.temperature == 0.3
    assert agent.token_budget == 2000
