"""Unit tests for Style Polish Agent (Redaktor)."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from models.schemas.agent import StyleRequest, StyleResponse
from services.agents.style_polish import StylePolishAgent
from services.model_policy import PipelineStage


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create mock OpenAI client."""
    client = MagicMock()
    client.chat_completion = AsyncMock()
    return client


@pytest.fixture
def style_agent(mock_openai_client: MagicMock) -> StylePolishAgent:
    """Create StylePolishAgent instance with mocked client."""
    return StylePolishAgent(openai_client=mock_openai_client)


@pytest.mark.asyncio
async def test_style_agent_basic_polish(
    style_agent: StylePolishAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test basic prose polishing."""
    job_id = uuid4()
    prose_id = uuid4()

    original_prose = """Kael szedł przez las. Las był ciemny. Czuł strach.
    'Musimy iść' powiedział. Lyra skinęła głową."""

    polished_prose = """Kael przedzierał się przez gąszcz. Ciemność otulała go niczym
    lepki całun, drzewa szeptały po obu stronach ścieżki. Dreszcz przeszedł mu po plecach.

    – Musimy ruszać – szepnął.

    Lyra skinęła głową, zacisnęła palce na rękojeści miecza."""

    # Mock OpenAI response
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "polished_prose": polished_prose,
                "changes_count": 15,
                "style_score": 0.88,
                "changes_summary": "Wzmocniono obrazowanie, poprawiono dialog, usunięto powtórzenia",
                "commercial_notes": "Tekst gotowy do publikacji. Dobra atmosfera.",
            }
        ),
        "cost": 0.042,
        "created_at": datetime.utcnow(),
    }

    # Create request
    request = StyleRequest(
        job_id=job_id,
        prose_id=prose_id,
        target_style="fantasy",
        language="pl",
        commercial_level="standard",
    )

    # Call style agent
    response = await style_agent.polish_prose(request, original_prose)

    # Verify
    assert isinstance(response, StyleResponse)
    assert response.job_id == job_id
    assert response.prose_id == prose_id
    assert response.agent == "redaktor"
    assert response.stage == PipelineStage.STYLE
    assert response.polished is True  # style_score >= 0.7
    assert response.polished_prose_id is not None  # New artifact created
    assert response.changes_count == 15
    assert response.style_score == 0.88

    # Verify OpenAI was called with HIGH MODEL
    mock_openai_client.chat_completion.assert_called_once()
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o"  # HIGH MODEL for style
    assert call_kwargs["temperature"] == 0.8  # Creative for style
    assert call_kwargs["token_budget"] == 2500  # HIGH stage default budget


@pytest.mark.asyncio
async def test_style_agent_intensive_polish(
    style_agent: StylePolishAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test intensive commercial polish."""
    job_id = uuid4()
    prose_id = uuid4()

    original_prose = "Była ciemna noc. Bohater był przestraszony."

    polished_prose = """Noc spowiła miasto ciemnością gęstą jak smoła. W powietrzu
    wisiało napięcie – niewidzialne, ale namacalne. Marcus czuł, jak pot ściera mu się
    po plecach, jak serce wali o żebra niczym więzień o kraty. Wiedział, że to dopiero początek."""

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "polished_prose": polished_prose,
                "changes_count": 42,
                "style_score": 0.95,
                "changes_summary": "Całkowita przebudowa: dodano atmosferę, metafory, napięcie. Wzmocniono page-turner quality.",
                "commercial_notes": "Publikacja premium. Maksymalna atrakcyjność komercyjna.",
            }
        ),
        "cost": 0.038,
        "created_at": datetime.utcnow(),
    }

    request = StyleRequest(
        job_id=job_id,
        prose_id=prose_id,
        target_style="thriller",
        language="pl",
        commercial_level="intensive",
    )

    response = await style_agent.polish_prose(request, original_prose)

    assert response.polished is True
    assert response.style_score == 0.95
    assert response.changes_count == 42


@pytest.mark.asyncio
async def test_style_agent_light_polish(
    style_agent: StylePolishAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test light polish (minimal changes)."""
    job_id = uuid4()
    prose_id = uuid4()

    original_prose = "Kael wrócił do miasta po pięciu latach nieobecności."

    polished_prose = "Kael powrócił do miasta po pięciu latach nieobecności."

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "polished_prose": polished_prose,
                "changes_count": 1,
                "style_score": 0.85,
                "changes_summary": "Zamieniono 'wrócił' na bardziej literackie 'powrócił'.",
                "commercial_notes": "Minimalne ingerencje. Tekst zachował styl autora.",
            }
        ),
        "cost": 0.025,
        "created_at": datetime.utcnow(),
    }

    request = StyleRequest(
        job_id=job_id,
        prose_id=prose_id,
        target_style="literary",
        language="pl",
        commercial_level="light",
    )

    response = await style_agent.polish_prose(request, original_prose)

    assert response.polished is True
    assert response.changes_count == 1
    assert response.style_score == 0.85


@pytest.mark.asyncio
async def test_style_agent_low_score_fails(
    style_agent: StylePolishAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test that low style score marks polishing as failed."""
    job_id = uuid4()
    prose_id = uuid4()

    original_prose = "Tekst z poważnymi problemami stylistycznymi."

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "polished_prose": "Nieudana próba poprawy...",
                "changes_count": 5,
                "style_score": 0.55,  # Below 0.7 threshold
                "changes_summary": "Próba poprawy, ale tekst nadal ma problemy.",
                "commercial_notes": "Wymaga dalszej pracy redakcyjnej.",
            }
        ),
        "cost": 0.030,
        "created_at": datetime.utcnow(),
    }

    request = StyleRequest(
        job_id=job_id,
        prose_id=prose_id,
        target_style="literary",
        language="pl",
        commercial_level="standard",
    )

    response = await style_agent.polish_prose(request, original_prose)

    # Should mark as not polished due to low score
    assert response.polished is False  # style_score < 0.7
    assert response.polished_prose_id is None  # No new artifact created
    assert response.style_score == 0.55


@pytest.mark.asyncio
async def test_style_agent_different_genres(
    style_agent: StylePolishAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test style agent with different target styles."""
    job_id = uuid4()
    prose_id = uuid4()

    original_prose = "Przykładowa proza do stylizacji."

    for target_style in ["fantasy", "sci-fi", "thriller", "literary", "horror"]:
        mock_openai_client.chat_completion.return_value = {
            "content": json.dumps(
                {
                    "polished_prose": f"Proza w stylu {target_style}...",
                    "changes_count": 10,
                    "style_score": 0.85,
                    "changes_summary": f"Dostosowano do stylu {target_style}",
                    "commercial_notes": "OK",
                }
            ),
            "cost": 0.028,
            "created_at": datetime.utcnow(),
        }

        request = StyleRequest(
            job_id=job_id,
            prose_id=prose_id,
            target_style=target_style,
            language="pl",
            commercial_level="standard",
        )

        response = await style_agent.polish_prose(request, original_prose)
        assert response.polished is True


@pytest.mark.asyncio
async def test_style_agent_invalid_json(
    style_agent: StylePolishAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of invalid JSON response."""
    job_id = uuid4()
    prose_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": "Not valid JSON at all",
        "cost": 0.020,
    }

    request = StyleRequest(
        job_id=job_id,
        prose_id=prose_id,
        target_style="fantasy",
        language="pl",
        commercial_level="standard",
    )

    with pytest.raises(ValueError, match="Invalid JSON response"):
        await style_agent.polish_prose(request, "Some prose")


@pytest.mark.asyncio
async def test_style_agent_missing_polished_prose(
    style_agent: StylePolishAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of response missing polished_prose field."""
    job_id = uuid4()
    prose_id = uuid4()

    # Missing polished_prose
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "changes_count": 10,
                "style_score": 0.8,
                "changes_summary": "Some changes",
            }
        ),
        "cost": 0.020,
    }

    request = StyleRequest(
        job_id=job_id,
        prose_id=prose_id,
        target_style="fantasy",
        language="pl",
        commercial_level="standard",
    )

    with pytest.raises(ValueError, match="missing or empty 'polished_prose'"):
        await style_agent.polish_prose(request, "Some prose")


@pytest.mark.asyncio
async def test_style_agent_score_clamping(
    style_agent: StylePolishAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test that out-of-range scores are clamped to [0.0, 1.0]."""
    job_id = uuid4()
    prose_id = uuid4()

    # Score > 1.0 (invalid)
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "polished_prose": "Polished text here",
                "changes_count": 5,
                "style_score": 1.5,  # Invalid, should be clamped to 1.0
                "changes_summary": "Changes",
                "commercial_notes": "Notes",
            }
        ),
        "cost": 0.025,
        "created_at": datetime.utcnow(),
    }

    request = StyleRequest(
        job_id=job_id,
        prose_id=prose_id,
        target_style="fantasy",
        language="pl",
        commercial_level="standard",
    )

    response = await style_agent.polish_prose(request, "Original prose")

    # Score should be clamped to 1.0
    assert response.style_score == 1.0
    assert response.polished is True


@pytest.mark.asyncio
async def test_style_agent_length_warning(
    style_agent: StylePolishAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test that significant length changes trigger warning log."""
    job_id = uuid4()
    prose_id = uuid4()

    original_prose = "Short text with ten words here for testing purposes today."

    # Polished prose is 3x longer (>50% difference)
    polished_prose = " ".join(["word"] * 30)

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "polished_prose": polished_prose,
                "changes_count": 20,
                "style_score": 0.75,
                "changes_summary": "Significantly expanded text",
                "commercial_notes": "Maybe too much expansion",
            }
        ),
        "cost": 0.035,
        "created_at": datetime.utcnow(),
    }

    request = StyleRequest(
        job_id=job_id,
        prose_id=prose_id,
        target_style="fantasy",
        language="pl",
        commercial_level="intensive",
    )

    # Should complete but log warning
    response = await style_agent.polish_prose(request, original_prose)
    assert response.polished is True


def test_style_agent_initialization() -> None:
    """Test StylePolishAgent initialization."""
    agent = StylePolishAgent()

    assert agent.client is not None
    assert agent.stage == PipelineStage.STYLE
    assert agent.model == "gpt-4o"  # HIGH MODEL for style
    assert agent.temperature == 0.8  # Creative (0.8 for PROSE/STYLE/DIALOG)
    assert agent.token_budget == 2500  # HIGH stage default


def test_style_agent_uses_high_stage() -> None:
    """Test that StylePolishAgent is configured for HIGH stage."""
    agent = StylePolishAgent()

    from services.model_policy import ModelPolicy

    assert agent.stage in ModelPolicy.HIGH_STAGES
    assert agent.stage not in ModelPolicy.MINI_STAGES
