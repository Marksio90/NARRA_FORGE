"""Unit tests for Prose Generator agent."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from models.schemas.agent import ProseRequest, ProseResponse
from services.agents.prose_generator import ProseGenerator
from services.model_policy import PipelineStage


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create mock OpenAI client."""
    client = MagicMock()
    client.chat_completion = AsyncMock()
    return client


@pytest.fixture
def prose_generator(mock_openai_client: MagicMock) -> ProseGenerator:
    """Create ProseGenerator instance with mocked client."""
    return ProseGenerator(openai_client=mock_openai_client)


@pytest.mark.asyncio
async def test_prose_generator_basic(
    prose_generator: ProseGenerator,
    mock_openai_client: MagicMock,
) -> None:
    """Test basic prose generation."""
    job_id = uuid4()

    # Mock OpenAI response with prose
    sample_prose = """The sun dipped below the horizon, painting the sky in shades of amber and crimson. Kael stood at the edge of the cliff, the wind tugging at his cloak. Below, the city sprawled like a constellation fallen to earth.

He'd been gone too long. Five years since he'd last seen these streets, these lights. Five years of running from a past that seemed determined to find him anyway.

The scent of salt and smoke rose from the harbor. He could see the market district, ablaze with lanterns. The old cathedral, its spire reaching toward the stars. The palace, where he'd made his greatest mistake. Where Lyra had been waiting, trusting him to come back. He never had.

Now he had no choice. The letter had found him in the northern wastes, passed from hand to hand until it reached his camp. Three words in Lyra's handwriting: "I need you." No explanation. No plea. Just those three words, and he'd known he had to return, no matter the cost."""

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "prose": sample_prose,
                "word_count": 155,
                "style_notes": "Third person limited, visual imagery",
                "continuity_check": "Kael returning after 5 years away",
            }
        ),
        "cost": 0.035,
        "created_at": datetime.utcnow(),
    }

    # Create request
    request = ProseRequest(
        job_id=job_id,
        segment_id="act1_scene1",
        context={
            "scene_description": "Kael returns to the city",
            "characters_present": ["Kael"],
            "mood": "nostalgic, melancholy",
        },
        target_word_count=500,
    )

    # Call prose generator
    response = await prose_generator.generate_prose(request)

    # Verify
    assert isinstance(response, ProseResponse)
    assert response.job_id == job_id
    assert response.agent == "generator_segmentow"
    assert response.stage == PipelineStage.PROSE
    assert response.segment_id == "act1_scene1"
    assert len(response.prose) > 100
    assert response.word_count > 0
    assert response.model_used == "gpt-4o"  # HIGH MODEL

    # Verify OpenAI was called with correct settings
    mock_openai_client.chat_completion.assert_called_once()
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o"
    assert call_kwargs["temperature"] == 0.8  # Creative temperature
    assert call_kwargs["token_budget"] == 4000  # HIGH budget for prose


@pytest.mark.asyncio
async def test_prose_generator_with_style_guide(
    prose_generator: ProseGenerator,
    mock_openai_client: MagicMock,
) -> None:
    """Test prose generation with style guide."""
    job_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "prose": "Short, punchy sentences. No frills. Just action." * 20,
                "word_count": 120,
                "style_notes": "Noir style - terse and direct",
                "continuity_check": "Detective enters crime scene",
            }
        ),
        "cost": 0.028,
        "created_at": datetime.utcnow(),
    }

    request = ProseRequest(
        job_id=job_id,
        segment_id="investigation_1",
        context={"scene": "crime scene"},
        target_word_count=300,
        style_guide={
            "voice": "first person",
            "tone": "noir",
            "sentence_length": "short",
            "pov": "detective",
        },
    )

    response = await prose_generator.generate_prose(request)

    assert response.segment_id == "investigation_1"
    assert response.prose is not None

    # Verify style guide was included in prompt
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert "Style Guide" in call_kwargs["messages"][1]["content"]
    assert "noir" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_prose_generator_word_count_validation(
    prose_generator: ProseGenerator,
    mock_openai_client: MagicMock,
) -> None:
    """Test word count validation and correction."""
    job_id = uuid4()

    # Generate prose that's actually 150 words but claims 100
    prose = " ".join(["word"] * 150)

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "prose": prose,
                "word_count": 100,  # Incorrect count
                "style_notes": "Test",
                "continuity_check": "Test",
            }
        ),
        "cost": 0.020,
        "created_at": datetime.utcnow(),
    }

    request = ProseRequest(
        job_id=job_id,
        segment_id="test_segment",
        context={"test": "data"},
        target_word_count=150,
    )

    response = await prose_generator.generate_prose(request)

    # Should use actual word count, not reported
    assert response.word_count == 150


@pytest.mark.asyncio
async def test_prose_generator_minimum_length_validation(
    prose_generator: ProseGenerator,
    mock_openai_client: MagicMock,
) -> None:
    """Test minimum prose length validation."""
    job_id = uuid4()

    # Too short prose
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "prose": "Too short.",
                "word_count": 2,
                "style_notes": "Test",
                "continuity_check": "Test",
            }
        ),
        "cost": 0.010,
    }

    request = ProseRequest(
        job_id=job_id,
        segment_id="test_segment",
        context={"test": "data"},
        target_word_count=500,
    )

    # Should raise ValueError for too short prose
    with pytest.raises(ValueError, match="too short"):
        await prose_generator.generate_prose(request)


@pytest.mark.asyncio
async def test_prose_generator_invalid_json(
    prose_generator: ProseGenerator,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of invalid JSON response."""
    job_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": "This is not valid JSON",
        "cost": 0.015,
    }

    request = ProseRequest(
        job_id=job_id,
        segment_id="test_segment",
        context={"test": "data"},
        target_word_count=500,
    )

    with pytest.raises(ValueError, match="Invalid JSON response"):
        await prose_generator.generate_prose(request)


@pytest.mark.asyncio
async def test_prose_generator_missing_prose_field(
    prose_generator: ProseGenerator,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of response missing prose field."""
    job_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps({"word_count": 100, "style_notes": "Test"}),
        "cost": 0.015,
    }

    request = ProseRequest(
        job_id=job_id,
        segment_id="test_segment",
        context={"test": "data"},
        target_word_count=500,
    )

    with pytest.raises(ValueError, match="missing or empty 'prose' field"):
        await prose_generator.generate_prose(request)


@pytest.mark.asyncio
async def test_prose_generator_empty_prose(
    prose_generator: ProseGenerator,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of empty prose field."""
    job_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "prose": "",  # Empty
                "word_count": 0,
            }
        ),
        "cost": 0.010,
    }

    request = ProseRequest(
        job_id=job_id,
        segment_id="test_segment",
        context={"test": "data"},
        target_word_count=500,
    )

    with pytest.raises(ValueError, match="missing or empty 'prose' field"):
        await prose_generator.generate_prose(request)


@pytest.mark.asyncio
async def test_prose_generator_uses_high_model(
    prose_generator: ProseGenerator,
    mock_openai_client: MagicMock,
) -> None:
    """Test that ProseGenerator uses HIGH MODEL (gpt-4o)."""
    job_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "prose": "High quality prose here. " * 50,
                "word_count": 250,
                "style_notes": "Literary quality",
                "continuity_check": "None",
            }
        ),
        "cost": 0.050,  # Higher cost for gpt-4o
        "created_at": datetime.utcnow(),
    }

    request = ProseRequest(
        job_id=job_id,
        segment_id="test_segment",
        context={"test": "data"},
        target_word_count=500,
    )

    response = await prose_generator.generate_prose(request)

    # Verify HIGH MODEL was used
    assert response.model_used == "gpt-4o"

    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o"
    assert call_kwargs["temperature"] == 0.8  # Creative
    assert call_kwargs["token_budget"] == 4000  # High budget


@pytest.mark.asyncio
async def test_prose_generator_long_segment(
    prose_generator: ProseGenerator,
    mock_openai_client: MagicMock,
) -> None:
    """Test prose generation for longer target."""
    job_id = uuid4()

    # Generate 1500 word prose
    long_prose = " ".join(["word"] * 1500)

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "prose": long_prose,
                "word_count": 1500,
                "style_notes": "Extended scene",
                "continuity_check": "Multiple events",
            }
        ),
        "cost": 0.080,
        "created_at": datetime.utcnow(),
    }

    request = ProseRequest(
        job_id=job_id,
        segment_id="long_segment",
        context={"scene": "complex action sequence"},
        target_word_count=1500,
    )

    response = await prose_generator.generate_prose(request)

    assert response.word_count >= 1000
    assert "long_segment" in response.segment_id


@pytest.mark.asyncio
async def test_prose_generator_context_inclusion(
    prose_generator: ProseGenerator,
    mock_openai_client: MagicMock,
) -> None:
    """Test that context is properly included in prompt."""
    job_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "prose": "Context-aware prose that incorporates all the contextual details provided. "
                * 15,
                "word_count": 120,
                "style_notes": "Following context",
                "continuity_check": "None",
            }
        ),
        "cost": 0.025,
        "created_at": datetime.utcnow(),
    }

    complex_context = {
        "previous_segment_summary": "Kael decided to return",
        "characters_present": ["Kael", "Moira"],
        "location": "Tavern in the Lower District",
        "mood": "tense",
        "time_of_day": "evening",
        "plot_points": ["Reveal Lyra is captured", "Kael accepts mission"],
    }

    request = ProseRequest(
        job_id=job_id,
        segment_id="dialogue_scene",
        context=complex_context,
        target_word_count=400,
    )

    _ = await prose_generator.generate_prose(request)

    # Verify context was included in prompt
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    prompt = call_kwargs["messages"][1]["content"]

    assert "Kael" in prompt
    assert "Moira" in prompt
    assert "tense" in prompt or "Context" in prompt


def test_prose_generator_initialization() -> None:
    """Test ProseGenerator initialization."""
    agent = ProseGenerator()

    assert agent.client is not None
    assert agent.stage == PipelineStage.PROSE
    assert agent.model == "gpt-4o"  # HIGH MODEL
    assert agent.temperature == 0.8  # Creative
    assert agent.token_budget == 4000  # High budget


def test_prose_generator_uses_high_stage() -> None:
    """Test that ProseGenerator is configured for HIGH stage."""
    agent = ProseGenerator()

    # Verify it's in HIGH_STAGES, not MINI_STAGES
    from services.model_policy import ModelPolicy

    assert agent.stage in ModelPolicy.HIGH_STAGES
    assert agent.stage not in ModelPolicy.MINI_STAGES
