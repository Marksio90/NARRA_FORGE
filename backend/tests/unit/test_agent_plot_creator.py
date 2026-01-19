"""Unit tests for Plot Creator agent."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from models.schemas.agent import PlotRequest, PlotResponse
from services.agents.plot_creator import PlotCreator
from services.model_policy import PipelineStage


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create mock OpenAI client."""
    client = MagicMock()
    client.chat_completion = AsyncMock()
    return client


@pytest.fixture
def plot_creator(mock_openai_client: MagicMock) -> PlotCreator:
    """Create PlotCreator instance with mocked client."""
    return PlotCreator(openai_client=mock_openai_client)


@pytest.mark.asyncio
async def test_plot_creator_basic(
    plot_creator: PlotCreator,
    mock_openai_client: MagicMock,
) -> None:
    """Test basic plot creation."""
    job_id = uuid4()
    world_id = uuid4()
    char_ids = [uuid4(), uuid4(), uuid4()]

    # Mock OpenAI response with three-act structure
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "structure": "three-act",
                "summary": "A story of redemption as a broken mage saves his apprentice.",
                "acts": [
                    {
                        "number": 1,
                        "name": "Setup",
                        "description": "Establish character and world",
                        "scenes": [1, 2, 3],
                    },
                    {
                        "number": 2,
                        "name": "Confrontation",
                        "description": "Rising tension and challenges",
                        "scenes": [4, 5, 6, 7],
                    },
                    {
                        "number": 3,
                        "name": "Resolution",
                        "description": "Climax and denouement",
                        "scenes": [8, 9, 10],
                    },
                ],
                "scenes": [
                    {"number": 1, "act": 1, "description": "Opening", "purpose": "introduction"},
                    {
                        "number": 2,
                        "act": 1,
                        "description": "Inciting incident",
                        "purpose": "call to action",
                    },
                    {"number": 3, "act": 1, "description": "Accept quest", "purpose": "commitment"},
                    {"number": 4, "act": 2, "description": "First challenge", "purpose": "test"},
                    {"number": 5, "act": 2, "description": "Revelation", "purpose": "midpoint"},
                    {
                        "number": 6,
                        "act": 2,
                        "description": "False victory",
                        "purpose": "escalation",
                    },
                    {"number": 7, "act": 2, "description": "Darkest moment", "purpose": "crisis"},
                    {"number": 8, "act": 3, "description": "Preparation", "purpose": "buildup"},
                    {"number": 9, "act": 3, "description": "Climax", "purpose": "confrontation"},
                    {"number": 10, "act": 3, "description": "Aftermath", "purpose": "resolution"},
                ],
                "conflicts": [
                    "Man vs Self: guilt and redemption",
                    "Man vs Man: hero vs villain",
                    "Man vs Society: magic users hunted",
                ],
            }
        ),
        "cost": 0.025,
        "created_at": datetime.utcnow(),
    }

    # Create request
    request = PlotRequest(
        job_id=job_id,
        world_id=world_id,
        character_ids=char_ids,
    )

    # Call plot creator
    response = await plot_creator.create_plot(request)

    # Verify
    assert isinstance(response, PlotResponse)
    assert response.job_id == job_id
    assert response.agent == "kreator_fabuly"
    assert response.stage == PipelineStage.PLAN
    assert response.acts == 3
    assert response.scenes == 10
    assert "redemption" in response.summary.lower()

    # Verify OpenAI was called
    mock_openai_client.chat_completion.assert_called_once()
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert "3 characters" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_plot_creator_with_structure(
    plot_creator: PlotCreator,
    mock_openai_client: MagicMock,
) -> None:
    """Test plot creation with preferred structure."""
    job_id = uuid4()
    world_id = uuid4()
    char_ids = [uuid4()]

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "structure": "heros-journey",
                "summary": "Hero's journey structure",
                "acts": [
                    {
                        "number": 1,
                        "name": "Departure",
                        "description": "Call to adventure",
                        "scenes": [1, 2],
                    },
                    {"number": 2, "name": "Initiation", "description": "Trials", "scenes": [3, 4]},
                    {"number": 3, "name": "Return", "description": "Back home", "scenes": [5, 6]},
                ],
                "scenes": [
                    {"number": 1, "act": 1, "description": "Ordinary world", "purpose": "intro"},
                    {"number": 2, "act": 1, "description": "Call", "purpose": "call"},
                    {"number": 3, "act": 2, "description": "Tests", "purpose": "test"},
                    {"number": 4, "act": 2, "description": "Ordeal", "purpose": "climax"},
                    {"number": 5, "act": 3, "description": "Return", "purpose": "return"},
                    {"number": 6, "act": 3, "description": "Resolution", "purpose": "end"},
                ],
                "conflicts": ["Man vs Self"],
            }
        ),
        "cost": 0.018,
        "created_at": datetime.utcnow(),
    }

    request = PlotRequest(
        job_id=job_id,
        world_id=world_id,
        character_ids=char_ids,
        structure="heros-journey",
    )

    response = await plot_creator.create_plot(request)

    assert response.acts == 3
    assert response.scenes == 6

    # Verify structure was passed
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert "heros-journey" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_plot_creator_with_summary(
    plot_creator: PlotCreator,
    mock_openai_client: MagicMock,
) -> None:
    """Test plot creation with plot seed summary."""
    job_id = uuid4()
    world_id = uuid4()
    char_ids = [uuid4()]

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "structure": "three-act",
                "summary": "Detective solves mystery",
                "acts": [{"number": 1, "name": "Setup", "description": "Setup", "scenes": [1]}],
                "scenes": [{"number": 1, "act": 1, "description": "Scene 1", "purpose": "intro"}],
                "conflicts": ["Man vs Mystery"],
            }
        ),
        "cost": 0.012,
        "created_at": datetime.utcnow(),
    }

    request = PlotRequest(
        job_id=job_id,
        world_id=world_id,
        character_ids=char_ids,
        summary="A detective must solve a series of locked-room murders",
    )

    response = await plot_creator.create_plot(request)

    assert response.plot_id is not None

    # Verify summary was included
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert "locked-room murders" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_plot_creator_invalid_json(
    plot_creator: PlotCreator,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of invalid JSON response."""
    job_id = uuid4()
    world_id = uuid4()
    char_ids = [uuid4()]

    mock_openai_client.chat_completion.return_value = {
        "content": "Not valid JSON",
        "cost": 0.005,
    }

    request = PlotRequest(
        job_id=job_id,
        world_id=world_id,
        character_ids=char_ids,
    )

    with pytest.raises(ValueError, match="Invalid JSON response"):
        await plot_creator.create_plot(request)


@pytest.mark.asyncio
async def test_plot_creator_missing_required_fields(
    plot_creator: PlotCreator,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of response missing required fields."""
    job_id = uuid4()
    world_id = uuid4()
    char_ids = [uuid4()]

    # Missing 'scenes'
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps({"acts": [], "summary": "Test"}),
        "cost": 0.005,
    }

    request = PlotRequest(
        job_id=job_id,
        world_id=world_id,
        character_ids=char_ids,
    )

    with pytest.raises(ValueError, match="missing fields"):
        await plot_creator.create_plot(request)


@pytest.mark.asyncio
async def test_plot_creator_uses_correct_model_policy(
    plot_creator: PlotCreator,
    mock_openai_client: MagicMock,
) -> None:
    """Test that PlotCreator uses correct ModelPolicy settings."""
    job_id = uuid4()
    world_id = uuid4()
    char_ids = [uuid4()]

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "structure": "three-act",
                "summary": "Test plot",
                "acts": [{"number": 1, "name": "Act 1", "description": "Test", "scenes": [1]}],
                "scenes": [{"number": 1, "act": 1, "description": "Scene 1", "purpose": "test"}],
                "conflicts": ["Test conflict"],
            }
        ),
        "cost": 0.010,
        "created_at": datetime.utcnow(),
    }

    request = PlotRequest(
        job_id=job_id,
        world_id=world_id,
        character_ids=char_ids,
    )

    await plot_creator.create_plot(request)

    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs["temperature"] == 0.3  # Analytical for PLAN
    assert call_kwargs["token_budget"] == 2000  # MINI_STAGES default budget


@pytest.mark.asyncio
async def test_plot_creator_multiple_characters(
    plot_creator: PlotCreator,
    mock_openai_client: MagicMock,
) -> None:
    """Test plot creation with many characters."""
    job_id = uuid4()
    world_id = uuid4()
    char_ids = [uuid4() for _ in range(10)]  # 10 characters

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "structure": "ensemble",
                "summary": "Ensemble cast story",
                "acts": [{"number": 1, "name": "Act 1", "description": "Setup", "scenes": [1, 2]}],
                "scenes": [
                    {"number": 1, "act": 1, "description": "Scene 1", "purpose": "intro"},
                    {"number": 2, "act": 1, "description": "Scene 2", "purpose": "develop"},
                ],
                "conflicts": ["Multiple conflicts"],
            }
        ),
        "cost": 0.030,
        "created_at": datetime.utcnow(),
    }

    request = PlotRequest(
        job_id=job_id,
        world_id=world_id,
        character_ids=char_ids,
    )

    response = await plot_creator.create_plot(request)

    assert response.acts == 1
    assert response.scenes == 2

    # Verify character count was mentioned
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert "10 characters" in call_kwargs["messages"][1]["content"]


def test_plot_creator_initialization() -> None:
    """Test PlotCreator initialization."""
    agent = PlotCreator()

    assert agent.client is not None
    assert agent.stage == PipelineStage.PLAN
    assert agent.model == "gpt-4o-mini"
