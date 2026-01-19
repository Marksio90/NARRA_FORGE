"""Agent tasks for literary production."""

import logging
from typing import Any

from services.model_policy import PipelineStage
from services.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.agent.interpret_request", bind=True)
def interpret_request_task(
    self: Any,
    job_id: str,
    user_prompt: str,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Agent: Interpreter - Parse user request into structured parameters.

    Args:
        job_id: UUID of the job
        user_prompt: Raw user request

    Returns:
        Dictionary with interpreted parameters
    """
    logger.info(
        "Agent: Interpreter starting",
        extra={
            "job_id": job_id,
            "stage": PipelineStage.STRUCTURE.value,
            "task_id": self.request.id,
        },
    )

    # Placeholder - will be implemented in KROK 8
    return {
        "job_id": job_id,
        "agent": "interpreter",
        "stage": PipelineStage.STRUCTURE.value,
        "parameters": {
            "genre": "fantasy",
            "length": "short_story",
            "themes": ["adventure", "magic"],
        },
        "task_id": self.request.id,
    }


@celery_app.task(name="tasks.agent.create_world", bind=True)
def create_world_task(
    self: Any,
    job_id: str,
    world_parameters: dict[str, Any],  # noqa: ARG001
) -> dict[str, Any]:
    """
    Agent: ArchitektSwiata - Create world structure.

    Args:
        job_id: UUID of the job
        world_parameters: World creation parameters

    Returns:
        Dictionary with world structure
    """
    logger.info(
        "Agent: ArchitektSwiata starting",
        extra={
            "job_id": job_id,
            "stage": PipelineStage.STRUCTURE.value,
            "task_id": self.request.id,
        },
    )

    # Placeholder - will be implemented in KROK 8
    return {
        "job_id": job_id,
        "agent": "architekt_swiata",
        "stage": PipelineStage.STRUCTURE.value,
        "world_id": "placeholder-world-id",
        "world_summary": "Fantasy world with magic system",
        "task_id": self.request.id,
    }


@celery_app.task(name="tasks.agent.create_characters", bind=True)
def create_characters_task(
    self: Any,
    job_id: str,
    world_id: str,  # noqa: ARG001
    character_count: int,
) -> dict[str, Any]:
    """
    Agent: ArchitektPostaci - Create character profiles.

    Args:
        job_id: UUID of the job
        world_id: UUID of the world
        character_count: Number of characters to create

    Returns:
        Dictionary with character profiles
    """
    logger.info(
        "Agent: ArchitektPostaci starting",
        extra={
            "job_id": job_id,
            "stage": PipelineStage.CHARACTER_PROFILE.value,
            "character_count": character_count,
            "task_id": self.request.id,
        },
    )

    # Placeholder - will be implemented in KROK 8
    return {
        "job_id": job_id,
        "agent": "architekt_postaci",
        "stage": PipelineStage.CHARACTER_PROFILE.value,
        "character_ids": [f"char-{i}" for i in range(character_count)],
        "task_id": self.request.id,
    }


@celery_app.task(name="tasks.agent.create_plot", bind=True)
def create_plot_task(
    self: Any,
    job_id: str,
    world_id: str,  # noqa: ARG001
    character_ids: list[str],  # noqa: ARG001
) -> dict[str, Any]:
    """
    Agent: KreatorFabuly - Create plot structure.

    Args:
        job_id: UUID of the job
        world_id: UUID of the world
        character_ids: List of character UUIDs

    Returns:
        Dictionary with plot structure
    """
    logger.info(
        "Agent: KreatorFabuly starting",
        extra={
            "job_id": job_id,
            "stage": PipelineStage.PLAN.value,
            "task_id": self.request.id,
        },
    )

    # Placeholder - will be implemented in KROK 8
    return {
        "job_id": job_id,
        "agent": "kreator_fabuly",
        "stage": PipelineStage.PLAN.value,
        "plot_summary": "Three-act structure with hero's journey",
        "task_id": self.request.id,
    }


@celery_app.task(name="tasks.agent.generate_prose", bind=True)
def generate_prose_task(
    self: Any,
    job_id: str,
    segment_id: str,
    context: dict[str, Any],
    target_word_count: int = 500,
    style_guide: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Agent: GeneratorSegmentow - Generate prose for a segment.

    Args:
        job_id: UUID of the job
        segment_id: Segment identifier
        context: Context for prose generation
        target_word_count: Target word count for prose
        style_guide: Optional style guide parameters

    Returns:
        Dictionary with generated prose
    """
    logger.info(
        "Agent: GeneratorSegmentow starting",
        extra={
            "job_id": job_id,
            "segment_id": segment_id,
            "stage": PipelineStage.PROSE.value,
            "task_id": self.request.id,
        },
    )

    # Import here to avoid circular dependencies
    from uuid import UUID

    from models.schemas.agent import ProseRequest
    from services.agents.prose_generator import ProseGenerator

    # Create request
    request = ProseRequest(
        job_id=UUID(job_id) if isinstance(job_id, str) else job_id,
        segment_id=segment_id,
        context=context,
        target_word_count=target_word_count,
        style_guide=style_guide,
    )

    # Generate prose
    agent = ProseGenerator()
    import asyncio

    response = asyncio.run(agent.generate_prose(request))

    logger.info(
        "Agent: GeneratorSegmentow completed",
        extra={
            "job_id": job_id,
            "segment_id": segment_id,
            "word_count": response.word_count,
            "model": response.model_used,
            "task_id": self.request.id,
        },
    )

    return {
        "job_id": str(response.job_id),
        "agent": response.agent,
        "stage": response.stage.value,
        "segment_id": response.segment_id,
        "prose": response.prose,
        "word_count": response.word_count,
        "model_used": response.model_used,
        "task_id": self.request.id,
    }


@celery_app.task(name="tasks.agent.qa_check", bind=True)
def qa_check_task(
    self: Any,
    job_id: str,
    artifact_id: str,
    check_type: str,
) -> dict[str, Any]:
    """
    Agent: QA - Perform quality assurance check.

    Args:
        job_id: UUID of the job
        artifact_id: UUID of artifact to check
        check_type: Type of check (coherence, style, consistency)

    Returns:
        Dictionary with QA results
    """
    logger.info(
        "Agent: QA starting",
        extra={
            "job_id": job_id,
            "artifact_id": artifact_id,
            "check_type": check_type,
            "stage": PipelineStage.QA.value,
            "task_id": self.request.id,
        },
    )

    # Placeholder - will be implemented in KROK 10
    return {
        "job_id": job_id,
        "agent": "qa",
        "stage": PipelineStage.QA.value,
        "artifact_id": artifact_id,
        "check_type": check_type,
        "passed": True,
        "issues": [],
        "task_id": self.request.id,
    }


@celery_app.task(name="tasks.agent.style_polish", bind=True)
def style_polish_task(
    self: Any,
    job_id: str,
    prose_id: str,
    target_style: str,
) -> dict[str, Any]:
    """
    Agent: Redaktor - Polish prose style.

    Args:
        job_id: UUID of the job
        prose_id: UUID of prose to polish
        target_style: Target writing style

    Returns:
        Dictionary with polished prose
    """
    logger.info(
        "Agent: Redaktor starting",
        extra={
            "job_id": job_id,
            "prose_id": prose_id,
            "target_style": target_style,
            "stage": PipelineStage.STYLE.value,
            "task_id": self.request.id,
        },
    )

    # Placeholder - will be implemented in KROK 11
    return {
        "job_id": job_id,
        "agent": "redaktor",
        "stage": PipelineStage.STYLE.value,
        "prose_id": prose_id,
        "polished": True,
        "task_id": self.request.id,
    }
