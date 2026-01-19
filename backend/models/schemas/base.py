"""Base Pydantic v2 schemas and validators."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseRequest(BaseModel):
    """Base request schema with common validation."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=False,
        arbitrary_types_allowed=False,
    )


class BaseResponse(BaseModel):
    """Base response schema with common fields."""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
    )

    id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    limit: int = Field(default=50, ge=1, le=100, description="Number of items per page")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")


class WordCountValidatorMixin:
    """Mixin for word count validation."""

    @field_validator("summary", "description", mode="after", check_fields=False)
    @classmethod
    def validate_word_count(cls, v: str) -> str:
        """Ensure summaries don't exceed 500 words."""
        if v:
            word_count = len(v.split())
            if word_count > 500:
                raise ValueError(f"Summary exceeds 500 words (got {word_count})")
        return v


class UUIDValidator(BaseModel):
    """Mixin for UUID validation."""

    @field_validator("*", mode="before")
    @classmethod
    def validate_uuids(cls, v: Any, info: Any) -> Any:
        """Convert string UUIDs to UUID objects."""
        if isinstance(v, str) and info.field_name and "id" in info.field_name:
            try:
                return UUID(v)
            except ValueError as exc:
                raise ValueError(f"Invalid UUID format: {v}") from exc
        return v


class GenreValidator:
    """Validator for genre fields."""

    ALLOWED_GENRES = [
        "fantasy",
        "sci-fi",
        "thriller",
        "mystery",
        "horror",
        "romance",
        "historical",
        "literary",
        "dystopian",
        "urban_fantasy",
    ]

    @field_validator("genre", mode="after", check_fields=False)
    @classmethod
    def validate_genre(cls, v: str) -> str:
        """Ensure genre is in allowed list."""
        if v not in cls.ALLOWED_GENRES:
            raise ValueError(f"Invalid genre: {v}. Allowed: {', '.join(cls.ALLOWED_GENRES)}")
        return v


class JobTypeValidator:
    """Validator for job type fields."""

    ALLOWED_JOB_TYPES = ["short_story", "novella", "novel", "saga"]

    @field_validator("job_type", "type", mode="after", check_fields=False)
    @classmethod
    def validate_job_type(cls, v: str) -> str:
        """Ensure job type is in allowed list."""
        if v not in cls.ALLOWED_JOB_TYPES:
            raise ValueError(f"Invalid job type: {v}. Allowed: {', '.join(cls.ALLOWED_JOB_TYPES)}")
        return v
