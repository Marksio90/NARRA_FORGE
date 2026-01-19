"""Unit tests for QA Agent."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from models.schemas.agent import QARequest, QAResponse
from services.agents.qa_agent import QAAgent
from services.model_policy import PipelineStage


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create mock OpenAI client."""
    client = MagicMock()
    client.chat_completion = AsyncMock()
    return client


@pytest.fixture
def qa_agent(mock_openai_client: MagicMock) -> QAAgent:
    """Create QAAgent instance with mocked client."""
    return QAAgent(openai_client=mock_openai_client)


@pytest.mark.asyncio
async def test_qa_agent_basic_pass(
    qa_agent: QAAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test QA check that passes."""
    job_id = uuid4()
    artifact_id = uuid4()

    # Mock OpenAI response - all scores good, no errors
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "logic_score": 0.95,
                "psychology_score": 0.90,
                "timeline_score": 0.92,
                "critical_errors": [],
                "warnings": ["Minor: Time of day not explicitly stated"],
                "explanation": "Prose is coherent and consistent with established world and characters.",
            }
        ),
        "cost": 0.015,
        "created_at": datetime.utcnow(),
    }

    # Create request
    request = QARequest(
        job_id=job_id,
        artifact_id=artifact_id,
        check_type="coherence",
        context={
            "world": {"rules": ["Magic requires crystals"], "geography": ["Nordreach"]},
            "characters": [{"name": "Kael", "traits": ["terse", "protective"]}],
            "prose": "Kael walked through Nordreach, his aether crystal cold in his palm.",
        },
    )

    # Call QA agent
    response = await qa_agent.check_quality(request)

    # Verify
    assert isinstance(response, QAResponse)
    assert response.job_id == job_id
    assert response.artifact_id == artifact_id
    assert response.agent == "qa"
    assert response.stage == PipelineStage.QA
    assert response.check_type == "coherence"
    assert response.passed is True  # All scores >= 0.7, no critical errors
    assert response.logic_score == 0.95
    assert response.psychology_score == 0.90
    assert response.timeline_score == 0.92
    assert len(response.critical_errors) == 0
    assert len(response.warnings) == 1

    # Verify OpenAI was called
    mock_openai_client.chat_completion.assert_called_once()
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs["temperature"] == 0.3  # Analytical for QA
    assert call_kwargs["token_budget"] == 1000  # QA gets lower budget


@pytest.mark.asyncio
async def test_qa_agent_with_critical_errors(
    qa_agent: QAAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test QA check that fails due to critical errors."""
    job_id = uuid4()
    artifact_id = uuid4()

    # Mock OpenAI response - critical errors found
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "logic_score": 0.40,
                "psychology_score": 0.30,
                "timeline_score": 0.85,
                "critical_errors": [
                    "World rule violation: Magic used without aether crystal",
                    "Character contradiction: Kael speaks cheerfully (established as terse)",
                ],
                "warnings": ["Geography: Location not previously established"],
                "explanation": "Significant coherence issues with world rules and character profile.",
            }
        ),
        "cost": 0.018,
        "created_at": datetime.utcnow(),
    }

    request = QARequest(
        job_id=job_id,
        artifact_id=artifact_id,
        check_type="coherence",
        context={
            "world": {"rules": ["Magic requires aether crystals"]},
            "characters": [{"name": "Kael", "traits": ["terse"]}],
            "prose": "'Wonderful day!' Kael shouted, casting a fireball with glee.",
        },
    )

    response = await qa_agent.check_quality(request)

    # Should fail due to critical errors
    assert response.passed is False
    assert len(response.critical_errors) == 2
    assert response.logic_score < 0.7
    assert response.psychology_score < 0.7


@pytest.mark.asyncio
async def test_qa_agent_low_scores_no_errors(
    qa_agent: QAAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test QA check that fails due to low scores but no critical errors."""
    job_id = uuid4()
    artifact_id = uuid4()

    # Mock response - low scores but no critical errors
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "logic_score": 0.65,
                "psychology_score": 0.68,
                "timeline_score": 0.60,
                "critical_errors": [],
                "warnings": [
                    "Multiple minor inconsistencies with character voice",
                    "Timeline references are vague",
                    "Logic flow could be clearer",
                ],
                "explanation": "No critical errors but multiple minor issues affect quality.",
            }
        ),
        "cost": 0.016,
        "created_at": datetime.utcnow(),
    }

    request = QARequest(
        job_id=job_id,
        artifact_id=artifact_id,
        check_type="coherence",
    )

    response = await qa_agent.check_quality(request)

    # Should fail due to low scores even without critical errors
    assert response.passed is False
    assert len(response.critical_errors) == 0
    assert response.logic_score < 0.7
    assert len(response.warnings) == 3


@pytest.mark.asyncio
async def test_qa_agent_perfect_scores(
    qa_agent: QAAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test QA check with perfect scores."""
    job_id = uuid4()
    artifact_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "logic_score": 1.0,
                "psychology_score": 1.0,
                "timeline_score": 1.0,
                "critical_errors": [],
                "warnings": [],
                "explanation": "Perfect coherence, no issues found.",
            }
        ),
        "cost": 0.012,
        "created_at": datetime.utcnow(),
    }

    request = QARequest(
        job_id=job_id,
        artifact_id=artifact_id,
        check_type="coherence",
    )

    response = await qa_agent.check_quality(request)

    assert response.passed is True
    assert response.logic_score == 1.0
    assert response.psychology_score == 1.0
    assert response.timeline_score == 1.0
    assert len(response.critical_errors) == 0
    assert len(response.warnings) == 0


@pytest.mark.asyncio
async def test_qa_agent_with_full_context(
    qa_agent: QAAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test QA check with complete context."""
    job_id = uuid4()
    artifact_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "logic_score": 0.88,
                "psychology_score": 0.92,
                "timeline_score": 0.90,
                "critical_errors": [],
                "warnings": [],
                "explanation": "All context checked, prose is consistent.",
            }
        ),
        "cost": 0.020,
        "created_at": datetime.utcnow(),
    }

    request = QARequest(
        job_id=job_id,
        artifact_id=artifact_id,
        check_type="full",
        context={
            "world": {
                "name": "Aethermoor",
                "rules": ["Magic requires crystals", "Crystals drain life"],
                "geography": ["Nordreach - port city"],
            },
            "characters": [
                {
                    "name": "Kael",
                    "role": "protagonist",
                    "traits": ["terse", "protective", "guilt-ridden"],
                    "arc": "redemption",
                }
            ],
            "plot": {"act": 1, "scene": 3, "purpose": "Accept quest"},
            "previous_segment": "Kael received a letter from Lyra asking for help.",
            "prose": "Kael clutched the aether crystal. The cold bite reminded him of the cost. 'I'm coming,' he muttered.",
        },
    )

    response = await qa_agent.check_quality(request)

    assert response.passed is True

    # Verify context was included in prompt
    call_kwargs = mock_openai_client.chat_completion.call_args.kwargs
    prompt = call_kwargs["messages"][1]["content"]

    assert "World Context" in prompt
    assert "Character Context" in prompt
    assert "Plot Context" in prompt
    assert "Previous Segment" in prompt
    assert "Current Prose" in prompt


@pytest.mark.asyncio
async def test_qa_agent_invalid_json(
    qa_agent: QAAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of invalid JSON response."""
    job_id = uuid4()
    artifact_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": "Not valid JSON",
        "cost": 0.010,
    }

    request = QARequest(
        job_id=job_id,
        artifact_id=artifact_id,
        check_type="coherence",
    )

    with pytest.raises(ValueError, match="Invalid JSON response"):
        await qa_agent.check_quality(request)


@pytest.mark.asyncio
async def test_qa_agent_missing_required_fields(
    qa_agent: QAAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of response missing required fields."""
    job_id = uuid4()
    artifact_id = uuid4()

    # Missing psychology_score
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {"logic_score": 0.8, "timeline_score": 0.9, "critical_errors": []}
        ),
        "cost": 0.010,
    }

    request = QARequest(
        job_id=job_id,
        artifact_id=artifact_id,
        check_type="coherence",
    )

    with pytest.raises(ValueError, match="missing fields"):
        await qa_agent.check_quality(request)


@pytest.mark.asyncio
async def test_qa_agent_score_out_of_range(
    qa_agent: QAAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test handling of scores outside valid range."""
    job_id = uuid4()
    artifact_id = uuid4()

    # Score > 1.0
    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "logic_score": 1.5,  # Invalid
                "psychology_score": 0.9,
                "timeline_score": 0.8,
                "critical_errors": [],
            }
        ),
        "cost": 0.010,
    }

    request = QARequest(
        job_id=job_id,
        artifact_id=artifact_id,
        check_type="coherence",
    )

    with pytest.raises(ValueError, match="out of range"):
        await qa_agent.check_quality(request)


@pytest.mark.asyncio
async def test_qa_agent_different_check_types(
    qa_agent: QAAgent,
    mock_openai_client: MagicMock,
) -> None:
    """Test QA agent with different check types."""
    job_id = uuid4()
    artifact_id = uuid4()

    mock_openai_client.chat_completion.return_value = {
        "content": json.dumps(
            {
                "logic_score": 0.85,
                "psychology_score": 0.88,
                "timeline_score": 0.90,
                "critical_errors": [],
                "warnings": [],
                "explanation": "Timeline check passed.",
            }
        ),
        "cost": 0.012,
        "created_at": datetime.utcnow(),
    }

    for check_type in ["coherence", "style", "consistency", "timeline"]:
        request = QARequest(
            job_id=job_id,
            artifact_id=artifact_id,
            check_type=check_type,
        )

        response = await qa_agent.check_quality(request)
        assert response.check_type == check_type


def test_qa_agent_initialization() -> None:
    """Test QAAgent initialization."""
    agent = QAAgent()

    assert agent.client is not None
    assert agent.stage == PipelineStage.QA
    assert agent.model == "gpt-4o-mini"  # MINI model for QA
    assert agent.temperature == 0.3  # Analytical
    assert agent.token_budget == 1000  # QA gets lower budget (brief checks)


def test_qa_agent_uses_mini_stage() -> None:
    """Test that QAAgent is configured for MINI stage."""
    agent = QAAgent()

    from services.model_policy import ModelPolicy

    assert agent.stage in ModelPolicy.MINI_STAGES
    assert agent.stage not in ModelPolicy.HIGH_STAGES
