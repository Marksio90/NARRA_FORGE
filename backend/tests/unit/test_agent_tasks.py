"""Unit tests for agent tasks."""

import json
from datetime import datetime
from typing import Any

import pytest

from services.agent_tasks import (
    create_characters_task,
    create_plot_task,
    create_world_task,
    generate_prose_task,
    interpret_request_task,
    qa_check_task,
    style_polish_task,
)
from services.model_policy import PipelineStage


@pytest.fixture
def mock_openai_response() -> dict[str, Any]:
    """Mock OpenAI API response."""
    return {
        "content": json.dumps(
            {
                "prose": "The hero embarked on a journey through the dark forest. " * 10,
                "word_count": 110,
                "style_notes": "Epic adventure tone",
                "continuity_check": "Hero entering forest",
            }
        ),
        "cost": 0.025,
        "created_at": datetime.utcnow(),
    }


def test_interpret_request_task() -> None:
    """Test interpreter agent task."""
    result = interpret_request_task.apply(
        kwargs={
            "job_id": "job-123",
            "user_prompt": "Write a fantasy short story",
        }
    ).get()

    assert result["job_id"] == "job-123"
    assert result["agent"] == "interpreter"
    assert result["stage"] == PipelineStage.STRUCTURE.value
    assert "parameters" in result
    assert "task_id" in result


def test_create_world_task() -> None:
    """Test world creation agent task."""
    world_params = {"magic_system": True, "technology_level": "medieval"}
    result = create_world_task.apply(
        kwargs={
            "job_id": "job-456",
            "world_parameters": world_params,
        }
    ).get()

    assert result["job_id"] == "job-456"
    assert result["agent"] == "architekt_swiata"
    assert result["stage"] == PipelineStage.STRUCTURE.value
    assert "world_id" in result
    assert "world_summary" in result
    assert "task_id" in result


def test_create_characters_task() -> None:
    """Test character creation agent task."""
    result = create_characters_task.apply(
        kwargs={
            "job_id": "job-789",
            "world_id": "world-123",
            "character_count": 3,
        }
    ).get()

    assert result["job_id"] == "job-789"
    assert result["agent"] == "architekt_postaci"
    assert result["stage"] == PipelineStage.CHARACTER_PROFILE.value
    assert len(result["character_ids"]) == 3
    assert "task_id" in result


def test_create_plot_task() -> None:
    """Test plot creation agent task."""
    result = create_plot_task.apply(
        kwargs={
            "job_id": "job-999",
            "world_id": "world-456",
            "character_ids": ["char-1", "char-2"],
        }
    ).get()

    assert result["job_id"] == "job-999"
    assert result["agent"] == "kreator_fabuly"
    assert result["stage"] == PipelineStage.PLAN.value
    assert "plot_summary" in result
    assert "task_id" in result


def test_generate_prose_task(mock_openai_response: dict[str, Any]) -> None:
    """Test prose generation agent task."""
    from unittest.mock import AsyncMock, patch
    from uuid import uuid4

    job_id = str(uuid4())
    context = {"plot": "hero's journey", "setting": "dark forest"}

    # Mock the OpenAI client
    with patch("services.agents.prose_generator.OpenAIClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.chat_completion = AsyncMock(return_value=mock_openai_response)

        result = generate_prose_task.apply(
            kwargs={
                "job_id": job_id,
                "segment_id": "segment-1",
                "context": context,
            }
        ).get()

    assert result["job_id"] == job_id
    assert result["agent"] == "generator_segmentow"
    assert result["stage"] == PipelineStage.PROSE.value
    assert result["segment_id"] == "segment-1"
    assert "prose" in result
    assert "word_count" in result
    assert result["model_used"] == "gpt-4o"
    assert "task_id" in result


def test_qa_check_task(mock_openai_response: dict[str, Any]) -> None:
    """Test QA agent task."""
    from unittest.mock import AsyncMock, patch
    from uuid import uuid4

    job_id = str(uuid4())
    artifact_id = str(uuid4())

    # Mock the OpenAI client
    qa_response = {
        "content": json.dumps(
            {
                "logic_score": 0.90,
                "psychology_score": 0.85,
                "timeline_score": 0.92,
                "critical_errors": [],
                "warnings": ["Minor timeline ambiguity"],
                "explanation": "Prose is coherent.",
            }
        ),
        "cost": 0.015,
        "created_at": datetime.utcnow(),
    }

    with patch("services.agents.qa_agent.OpenAIClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.chat_completion = AsyncMock(return_value=qa_response)

        result = qa_check_task.apply(
            kwargs={
                "job_id": job_id,
                "artifact_id": artifact_id,
                "check_type": "coherence",
            }
        ).get()

    assert result["job_id"] == job_id
    assert result["agent"] == "qa"
    assert result["stage"] == PipelineStage.QA.value
    assert result["artifact_id"] == artifact_id
    assert result["check_type"] == "coherence"
    assert result["passed"] is True
    assert result["logic_score"] == 0.90
    assert result["psychology_score"] == 0.85
    assert result["timeline_score"] == 0.92
    assert len(result["critical_errors"]) == 0
    assert len(result["warnings"]) == 1
    assert "task_id" in result


def test_style_polish_task(mock_openai_response: dict[str, Any]) -> None:
    """Test style polish agent task."""
    from unittest.mock import AsyncMock, patch
    from uuid import uuid4

    job_id = str(uuid4())
    prose_id = str(uuid4())
    original_prose = "Kael szedł przez las. Czuł strach."

    # Mock the OpenAI client
    style_response = {
        "content": json.dumps(
            {
                "polished_prose": "Kael przedzierał się przez gąszcz, dreszcz lęku przebiegał mu po plecach.",
                "changes_count": 5,
                "style_score": 0.88,
                "changes_summary": "Wzmocniono obrazowanie, usunięto powtórzenia",
                "commercial_notes": "Tekst gotowy do publikacji.",
            }
        ),
        "cost": 0.035,
        "created_at": datetime.utcnow(),
    }

    with patch("services.agents.style_polish.OpenAIClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.chat_completion = AsyncMock(return_value=style_response)

        result = style_polish_task.apply(
            kwargs={
                "job_id": job_id,
                "prose_id": prose_id,
                "target_style": "fantasy",
                "original_prose": original_prose,
                "language": "pl",
                "commercial_level": "standard",
            }
        ).get()

    assert result["job_id"] == job_id
    assert result["agent"] == "redaktor"
    assert result["stage"] == PipelineStage.STYLE.value
    assert result["prose_id"] == prose_id
    assert result["polished"] is True
    assert result["polished_prose_id"] is not None
    assert result["changes_count"] == 5
    assert result["style_score"] == 0.88
    assert "task_id" in result
