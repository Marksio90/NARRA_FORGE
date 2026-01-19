"""Agent request and response schemas."""

from typing import Any
from uuid import UUID

from pydantic import Field

from models.schemas.base import BaseRequest, BaseResponse, GenreValidator, WordCountValidatorMixin
from services.model_policy import PipelineStage


class InterpretRequest(BaseRequest, GenreValidator):
    """Request schema for Interpreter agent."""

    job_id: UUID = Field(..., description="Job UUID")
    user_prompt: str = Field(..., min_length=10, max_length=5000, description="Raw user request")
    context: dict[str, Any] | None = Field(None, description="Additional context")


class InterpretResponse(BaseResponse):
    """Response schema for Interpreter agent."""

    job_id: UUID
    agent: str = Field(default="interpreter", description="Agent name")
    stage: PipelineStage = Field(default=PipelineStage.STRUCTURE)
    parameters: dict[str, Any] = Field(..., description="Interpreted parameters")
    genre: str | None = None
    length: str | None = None
    themes: list[str] = Field(default_factory=list)


class WorldRequest(BaseRequest, WordCountValidatorMixin):
    """Request schema for ArchitektSwiata (World Architect) agent."""

    job_id: UUID = Field(..., description="Job UUID")
    genre: str = Field(..., description="Genre for world creation")
    themes: list[str] = Field(default_factory=list, description="Themes to incorporate")
    constraints: dict[str, Any] | None = Field(None, description="World constraints")
    summary: str | None = Field(
        None, max_length=2500, description="Optional world summary (max 500 words)"
    )


class WorldResponse(BaseResponse, WordCountValidatorMixin):
    """Response schema for ArchitektSwiata agent."""

    job_id: UUID
    agent: str = Field(default="architekt_swiata")
    stage: PipelineStage = Field(default=PipelineStage.STRUCTURE)
    world_id: UUID = Field(..., description="Created world UUID")
    world_name: str = Field(..., min_length=1, max_length=200)
    summary: str = Field(..., max_length=2500, description="World summary (max 500 words)")
    rules: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)


class CharacterRequest(BaseRequest):
    """Request schema for ArchitektPostaci (Character Architect) agent."""

    job_id: UUID = Field(..., description="Job UUID")
    world_id: UUID = Field(..., description="World UUID")
    character_count: int = Field(..., ge=1, le=50, description="Number of characters to create")
    character_types: list[str] | None = Field(
        None, description="Types (protagonist, antagonist, etc.)"
    )
    constraints: dict[str, Any] | None = Field(None, description="Character constraints")


class CharacterResponse(BaseResponse):
    """Response schema for ArchitektPostaci agent."""

    job_id: UUID
    agent: str = Field(default="architekt_postaci")
    stage: PipelineStage = Field(default=PipelineStage.CHARACTER_PROFILE)
    character_ids: list[UUID] = Field(..., description="Created character UUIDs")
    character_count: int = Field(..., ge=1)


class PlotRequest(BaseRequest, WordCountValidatorMixin):
    """Request schema for KreatorFabuly (Plot Creator) agent."""

    job_id: UUID = Field(..., description="Job UUID")
    world_id: UUID = Field(..., description="World UUID")
    character_ids: list[UUID] = Field(..., min_length=1, description="Character UUIDs")
    structure: str | None = Field(None, description="Plot structure (three-act, hero's journey)")
    summary: str | None = Field(None, max_length=2500, description="Plot seed (max 500 words)")


class PlotResponse(BaseResponse, WordCountValidatorMixin):
    """Response schema for KreatorFabuly agent."""

    job_id: UUID
    agent: str = Field(default="kreator_fabuly")
    stage: PipelineStage = Field(default=PipelineStage.PLAN)
    plot_id: UUID = Field(..., description="Created plot UUID")
    summary: str = Field(..., max_length=2500, description="Plot summary (max 500 words)")
    acts: int = Field(..., ge=1, le=10, description="Number of acts")
    scenes: int = Field(..., ge=1, le=200, description="Number of scenes")


class ProseRequest(BaseRequest):
    """Request schema for GeneratorSegmentow (Prose Generator) agent."""

    job_id: UUID = Field(..., description="Job UUID")
    segment_id: str = Field(..., description="Segment identifier")
    context: dict[str, Any] = Field(..., description="Context for prose generation")
    target_word_count: int = Field(
        default=500, ge=100, le=2000, description="Target word count for segment"
    )
    style_guide: dict[str, Any] | None = Field(None, description="Style guidelines")


class ProseResponse(BaseResponse):
    """Response schema for GeneratorSegmentow agent."""

    job_id: UUID
    agent: str = Field(default="generator_segmentow")
    stage: PipelineStage = Field(default=PipelineStage.PROSE)
    segment_id: str = Field(..., description="Segment identifier")
    prose: str = Field(..., min_length=100, description="Generated prose")
    word_count: int = Field(..., ge=100)
    model_used: str = Field(..., description="Model used for generation")


class QARequest(BaseRequest):
    """Request schema for QA agent."""

    job_id: UUID = Field(..., description="Job UUID")
    artifact_id: UUID = Field(..., description="Artifact UUID to check")
    check_type: str = Field(
        ..., description="Type of check (coherence, style, consistency, timeline)"
    )
    context: dict[str, Any] | None = Field(None, description="Additional context for QA")


class QAResponse(BaseResponse):
    """Response schema for QA agent."""

    job_id: UUID
    agent: str = Field(default="qa")
    stage: PipelineStage = Field(default=PipelineStage.QA)
    artifact_id: UUID
    check_type: str
    passed: bool = Field(..., description="Whether QA check passed")
    logic_score: float = Field(..., ge=0.0, le=1.0)
    psychology_score: float = Field(..., ge=0.0, le=1.0)
    timeline_score: float = Field(..., ge=0.0, le=1.0)
    critical_errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class StyleRequest(BaseRequest):
    """Request schema for Redaktor (Style Polish) agent."""

    job_id: UUID = Field(..., description="Job UUID")
    prose_id: UUID = Field(..., description="Prose artifact UUID to polish")
    target_style: str = Field(..., description="Target writing style")
    language: str = Field(default="pl", description="Target language (default: Polish)")
    commercial_level: str = Field(
        default="standard",
        description="Commercial polish level (light, standard, intensive)",
    )


class StyleResponse(BaseResponse):
    """Response schema for Redaktor agent."""

    job_id: UUID
    agent: str = Field(default="redaktor")
    stage: PipelineStage = Field(default=PipelineStage.STYLE)
    prose_id: UUID
    polished: bool = Field(..., description="Whether polishing succeeded")
    polished_prose_id: UUID | None = Field(None, description="Polished prose artifact UUID")
    changes_count: int = Field(default=0, ge=0)
    style_score: float = Field(..., ge=0.0, le=1.0)
