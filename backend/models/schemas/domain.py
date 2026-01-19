"""Domain schemas with business logic validation."""

from datetime import datetime
from typing import Any, ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from models.schemas.base import WordCountValidatorMixin


class WorldSchema(BaseModel, WordCountValidatorMixin):
    """World domain schema with validation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    rules: list[str] = Field(default_factory=list, description="World rules (e.g., magic system)")
    geography: dict[str, Any] = Field(default_factory=dict, description="Geographic information")
    history: list[dict[str, Any]] = Field(
        default_factory=list, description="Historical timeline nodes"
    )
    themes: list[str] = Field(default_factory=list)
    version: int = Field(default=1, ge=1)
    checksum: str = Field(..., min_length=64, max_length=64, description="SHA256 checksum")
    created_at: datetime
    updated_at: datetime

    @field_validator("rules")
    @classmethod
    def validate_rules(cls, v: list[str]) -> list[str]:
        """Ensure rules are not empty strings."""
        if v:
            for rule in v:
                if not rule.strip():
                    raise ValueError("World rules cannot be empty strings")
        return v

    @field_validator("themes")
    @classmethod
    def validate_themes(cls, v: list[str]) -> list[str]:
        """Ensure themes are not empty and unique."""
        if v:
            cleaned = [t.strip() for t in v if t.strip()]
            if len(cleaned) != len(set(cleaned)):
                raise ValueError("Themes must be unique")
            return cleaned
        return v


class CharacterSchema(BaseModel):
    """Character domain schema with validation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    world_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    trajectory: list[dict[str, Any]] = Field(
        default_factory=list, description="Character transformation nodes"
    )
    relationships: list[dict[str, Any]] = Field(
        default_factory=list, description="Relationships with other characters"
    )
    constraints: list[str] = Field(default_factory=list, description="Psychological constraints")
    created_at: datetime
    updated_at: datetime

    @field_validator("trajectory")
    @classmethod
    def validate_trajectory(cls, v: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Ensure trajectory nodes have required fields."""
        for node in v:
            if "stage" not in node or "state" not in node:
                raise ValueError("Trajectory nodes must have 'stage' and 'state' fields")
        return v

    @field_validator("relationships")
    @classmethod
    def validate_relationships(cls, v: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Ensure relationships have required fields."""
        for rel in v:
            if "character_id" not in rel or "type" not in rel:
                raise ValueError("Relationships must have 'character_id' and 'type' fields")
        return v


class PlotSchema(BaseModel, WordCountValidatorMixin):
    """Plot domain schema with validation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    structure: str = Field(..., description="Plot structure type")
    acts: list[dict[str, Any]] = Field(..., min_length=1, description="Plot acts")
    scenes: list[dict[str, Any]] = Field(..., min_length=1, description="Plot scenes")
    conflicts: list[str] = Field(default_factory=list, description="Major conflicts")
    summary: str = Field(..., max_length=2500, description="Plot summary (max 500 words)")
    created_at: datetime
    updated_at: datetime

    @field_validator("acts")
    @classmethod
    def validate_acts(cls, v: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Ensure acts have required fields and valid structure."""
        if not v:
            raise ValueError("Plot must have at least one act")
        for i, act in enumerate(v):
            if "number" not in act:
                act["number"] = i + 1
            if "description" not in act or not act["description"]:
                raise ValueError(f"Act {i + 1} must have a description")
        return v

    @field_validator("scenes")
    @classmethod
    def validate_scenes(cls, v: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Ensure scenes have required fields."""
        if not v:
            raise ValueError("Plot must have at least one scene")
        for i, scene in enumerate(v):
            if "number" not in scene:
                scene["number"] = i + 1
            if "act" not in scene:
                raise ValueError(f"Scene {i + 1} must specify which act it belongs to")
        return v


class SegmentSchema(BaseModel):
    """Prose segment schema with validation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    segment_id: str = Field(..., description="Segment identifier (e.g., 'act1_scene3')")
    prose: str = Field(..., min_length=100, description="Prose content")
    word_count: int = Field(..., ge=100, le=5000)
    model_used: str = Field(..., description="AI model used for generation")
    metadata: dict[str, Any] = Field(default_factory=dict)
    version: int = Field(default=1, ge=1)
    created_at: datetime

    @field_validator("word_count", mode="after")
    @classmethod
    def validate_word_count_matches_prose(cls, v: int, info: Any) -> int:
        """Ensure word_count matches actual prose word count."""
        if "prose" in info.data:
            actual_count = len(info.data["prose"].split())
            if abs(actual_count - v) > 10:  # Allow 10 word tolerance
                raise ValueError(f"Word count mismatch: field={v}, actual={actual_count}")
        return v


class ArtifactSchema(BaseModel):
    """Artifact schema with validation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    type: str = Field(
        ...,
        description="Artifact type (world_spec, character_spec, narrative_blueprint, etc.)",
    )
    version: int = Field(default=1, ge=1)
    data: dict[str, Any] = Field(..., description="Artifact data")
    checksum: str = Field(..., min_length=64, max_length=64, description="SHA256 checksum")
    created_at: datetime

    ALLOWED_ARTIFACT_TYPES: ClassVar[list[str]] = [
        "world_spec",
        "character_spec",
        "narrative_blueprint",
        "plot_outline",
        "prose_segment",
        "qa_report",
        "style_guide",
    ]

    @field_validator("type")
    @classmethod
    def validate_artifact_type(cls, v: str) -> str:
        """Ensure artifact type is valid."""
        if v not in cls.ALLOWED_ARTIFACT_TYPES:
            raise ValueError(
                f"Invalid artifact type: {v}. Allowed: {', '.join(cls.ALLOWED_ARTIFACT_TYPES)}"
            )
        return v

    @field_validator("data")
    @classmethod
    def validate_data_not_empty(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Ensure artifact data is not empty."""
        if not v:
            raise ValueError("Artifact data cannot be empty")
        return v


class CostSnapshotSchema(BaseModel):
    """Cost snapshot schema with validation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    stage: str = Field(..., description="Pipeline stage name")
    tokens_used: int = Field(..., ge=0)
    cost_usd: float = Field(..., ge=0.0)
    model: str = Field(..., description="AI model used")
    created_at: datetime

    ALLOWED_MODELS: ClassVar[list[str]] = ["gpt-4o-mini", "gpt-4o"]

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Ensure model is valid."""
        if v not in cls.ALLOWED_MODELS:
            raise ValueError(f"Invalid model: {v}. Allowed: {', '.join(cls.ALLOWED_MODELS)}")
        return v

    @field_validator("cost_usd")
    @classmethod
    def validate_cost_reasonable(cls, v: float) -> float:
        """Ensure cost is reasonable (sanity check)."""
        if v > 100.0:
            raise ValueError(f"Cost seems unreasonably high: ${v:.2f}")
        return v
