"""Unit tests for agent tasks."""

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


def test_generate_prose_task() -> None:
    """Test prose generation agent task."""
    context = {"plot": "hero's journey", "setting": "dark forest"}
    result = generate_prose_task.apply(
        kwargs={
            "job_id": "job-111",
            "segment_id": "segment-1",
            "context": context,
        }
    ).get()

    assert result["job_id"] == "job-111"
    assert result["agent"] == "generator_segmentow"
    assert result["stage"] == PipelineStage.PROSE.value
    assert result["segment_id"] == "segment-1"
    assert "prose" in result
    assert "word_count" in result
    assert "task_id" in result


def test_qa_check_task() -> None:
    """Test QA agent task."""
    result = qa_check_task.apply(
        kwargs={
            "job_id": "job-222",
            "artifact_id": "artifact-1",
            "check_type": "coherence",
        }
    ).get()

    assert result["job_id"] == "job-222"
    assert result["agent"] == "qa"
    assert result["stage"] == PipelineStage.QA.value
    assert result["artifact_id"] == "artifact-1"
    assert result["check_type"] == "coherence"
    assert "passed" in result
    assert "issues" in result
    assert "task_id" in result


def test_style_polish_task() -> None:
    """Test style polish agent task."""
    result = style_polish_task.apply(
        kwargs={
            "job_id": "job-333",
            "prose_id": "prose-1",
            "target_style": "literary",
        }
    ).get()

    assert result["job_id"] == "job-333"
    assert result["agent"] == "redaktor"
    assert result["stage"] == PipelineStage.STYLE.value
    assert result["prose_id"] == "prose-1"
    assert "polished" in result
    assert "task_id" in result


