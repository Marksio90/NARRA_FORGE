"""Unit tests for base Pydantic schemas."""

from datetime import datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from models.schemas.base import (
    BaseRequest,
    BaseResponse,
    ErrorResponse,
    GenreValidator,
    JobTypeValidator,
    PaginationParams,
    WordCountValidatorMixin,
)


def test_base_request_strips_whitespace() -> None:
    """Test that BaseRequest strips whitespace from strings."""

    class TestRequest(BaseRequest):
        name: str

    req = TestRequest(name="  test  ")
    assert req.name == "test"


def test_base_response_with_uuid() -> None:
    """Test BaseResponse with UUID and timestamps."""

    class TestResponse(BaseResponse):
        name: str

    test_id = uuid4()
    now = datetime.utcnow()

    resp = TestResponse(id=test_id, name="test", created_at=now, updated_at=now)

    assert resp.id == test_id
    assert resp.name == "test"
    assert resp.created_at == now
    assert resp.updated_at == now


def test_error_response_structure() -> None:
    """Test ErrorResponse schema."""
    error = ErrorResponse(
        error="ValidationError",
        message="Invalid input",
        details={"field": "name", "reason": "too short"},
    )

    assert error.error == "ValidationError"
    assert error.message == "Invalid input"
    assert error.details == {"field": "name", "reason": "too short"}
    assert isinstance(error.timestamp, datetime)


def test_pagination_params_defaults() -> None:
    """Test PaginationParams default values."""
    params = PaginationParams()

    assert params.limit == 50
    assert params.offset == 0


def test_pagination_params_validation() -> None:
    """Test PaginationParams validation."""
    # Valid
    params = PaginationParams(limit=100, offset=10)
    assert params.limit == 100
    assert params.offset == 10

    # Invalid limit too high
    with pytest.raises(ValidationError, match="less than or equal to 100"):
        PaginationParams(limit=101)

    # Invalid limit too low
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        PaginationParams(limit=0)

    # Invalid offset negative
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        PaginationParams(offset=-1)


def test_word_count_validator_mixin() -> None:
    """Test WordCountValidatorMixin."""

    class TestSchema(BaseRequest, WordCountValidatorMixin):
        summary: str

    # Valid - under 500 words
    schema = TestSchema(summary="This is a short summary with only ten words total.")
    assert schema.summary

    # Invalid - over 500 words
    long_summary = " ".join(["word"] * 501)
    with pytest.raises(ValidationError, match="exceeds 500 words"):
        TestSchema(summary=long_summary)


def test_genre_validator() -> None:
    """Test GenreValidator."""

    class TestSchema(BaseRequest, GenreValidator):
        genre: str

    # Valid genres
    valid_genres = ["fantasy", "sci-fi", "thriller", "mystery", "horror"]
    for genre in valid_genres:
        schema = TestSchema(genre=genre)
        assert schema.genre == genre

    # Invalid genre
    with pytest.raises(ValidationError, match="Invalid genre"):
        TestSchema(genre="invalid_genre")


def test_job_type_validator() -> None:
    """Test JobTypeValidator."""

    class TestSchema(BaseRequest, JobTypeValidator):
        job_type: str

    # Valid job types
    valid_types = ["short_story", "novella", "novel", "saga"]
    for job_type in valid_types:
        schema = TestSchema(job_type=job_type)
        assert schema.job_type == job_type

    # Invalid job type
    with pytest.raises(ValidationError, match="Invalid job type"):
        TestSchema(job_type="invalid_type")


def test_uuid_validator_string_conversion() -> None:
    """Test UUIDValidator converts string UUIDs."""
    # Note: UUIDValidator is a mixin that's not used standalone,
    # but Pydantic v2 handles UUID conversion automatically
    test_uuid = uuid4()
    uuid_str = str(test_uuid)

    class TestSchema(BaseResponse):
        test_id: UUID

    # Pydantic v2 automatically converts valid UUID strings
    schema = TestSchema(
        id=test_uuid,
        test_id=uuid_str,
        created_at=datetime.utcnow(),
    )
    assert schema.test_id == test_uuid


def test_invalid_uuid_string() -> None:
    """Test that invalid UUID strings raise validation error."""

    class TestSchema(BaseResponse):
        test_id: UUID

    with pytest.raises(ValidationError, match="UUID"):
        TestSchema(
            id=uuid4(),
            test_id="not-a-uuid",
            created_at=datetime.utcnow(),
        )


def test_base_request_config() -> None:
    """Test BaseRequest configuration."""

    class TestRequest(BaseRequest):
        value: str

    req = TestRequest(value="test")

    # Config should strip whitespace
    req2 = TestRequest(value="  test  ")
    assert req2.value == "test"

    # Config should validate on assignment
    req.value = "  new value  "
    assert req.value == "new value"
