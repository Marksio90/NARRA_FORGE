"""Unit tests for agent schemas."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from models.schemas.agent import (
    CharacterRequest,
    InterpretRequest,
    InterpretResponse,
    PlotRequest,
    PlotResponse,
    ProseRequest,
    ProseResponse,
    QARequest,
    QAResponse,
    StyleRequest,
    StyleResponse,
    WorldRequest,
    WorldResponse,
)
from services.model_policy import PipelineStage


def test_interpret_request_valid() -> None:
    """Test InterpretRequest with valid data."""
    job_id = uuid4()

    req = InterpretRequest(
        job_id=job_id,
        user_prompt="Create a fantasy story with magic and dragons",
    )

    assert req.job_id == job_id
    assert "fantasy" in req.user_prompt
    assert req.context is None


def test_interpret_request_with_context() -> None:
    """Test InterpretRequest with context."""
    job_id = uuid4()

    req = InterpretRequest(
        job_id=job_id,
        user_prompt="Create a fantasy story",
        context={"previous_work": "trilogy"},
    )

    assert req.context == {"previous_work": "trilogy"}


def test_interpret_request_validation() -> None:
    """Test InterpretRequest validation."""
    job_id = uuid4()

    # Prompt too short
    with pytest.raises(ValidationError, match="at least 10 characters"):
        InterpretRequest(job_id=job_id, user_prompt="short")

    # Prompt too long
    with pytest.raises(ValidationError, match="at most 5000 characters"):
        InterpretRequest(job_id=job_id, user_prompt="x" * 5001)


def test_world_request_valid() -> None:
    """Test WorldRequest with valid data."""
    job_id = uuid4()

    req = WorldRequest(
        job_id=job_id,
        genre="fantasy",
        themes=["magic", "dragons"],
    )

    assert req.job_id == job_id
    assert req.genre == "fantasy"
    assert req.themes == ["magic", "dragons"]


def test_world_request_summary_word_count() -> None:
    """Test WorldRequest summary word count validation."""
    job_id = uuid4()

    # Valid summary
    req = WorldRequest(
        job_id=job_id,
        genre="fantasy",
        summary="A world with magic and dragons",
    )
    assert req.summary

    # Invalid - over 500 words
    long_summary = " ".join(["word"] * 501)
    with pytest.raises(ValidationError):  # Pydantic max_length or word count validator
        WorldRequest(job_id=job_id, genre="fantasy", summary=long_summary)


def test_character_request_valid() -> None:
    """Test CharacterRequest with valid data."""
    job_id = uuid4()
    world_id = uuid4()

    req = CharacterRequest(
        job_id=job_id,
        world_id=world_id,
        character_count=3,
    )

    assert req.job_id == job_id
    assert req.world_id == world_id
    assert req.character_count == 3


def test_character_request_validation() -> None:
    """Test CharacterRequest validation."""
    job_id = uuid4()
    world_id = uuid4()

    # Invalid - count too low
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        CharacterRequest(job_id=job_id, world_id=world_id, character_count=0)

    # Invalid - count too high
    with pytest.raises(ValidationError, match="less than or equal to 50"):
        CharacterRequest(job_id=job_id, world_id=world_id, character_count=51)


def test_plot_request_valid() -> None:
    """Test PlotRequest with valid data."""
    job_id = uuid4()
    world_id = uuid4()
    char_ids = [uuid4(), uuid4()]

    req = PlotRequest(
        job_id=job_id,
        world_id=world_id,
        character_ids=char_ids,
        structure="three-act",
    )

    assert req.job_id == job_id
    assert req.world_id == world_id
    assert len(req.character_ids) == 2
    assert req.structure == "three-act"


def test_plot_request_requires_characters() -> None:
    """Test PlotRequest requires at least one character."""
    job_id = uuid4()
    world_id = uuid4()

    with pytest.raises(ValidationError, match="at least 1 item"):
        PlotRequest(job_id=job_id, world_id=world_id, character_ids=[])


def test_prose_request_valid() -> None:
    """Test ProseRequest with valid data."""
    job_id = uuid4()

    req = ProseRequest(
        job_id=job_id,
        segment_id="act1_scene3",
        context={"previous": "summary"},
        target_word_count=1000,
    )

    assert req.segment_id == "act1_scene3"
    assert req.target_word_count == 1000


def test_prose_request_word_count_validation() -> None:
    """Test ProseRequest word count validation."""
    job_id = uuid4()

    # Invalid - too low
    with pytest.raises(ValidationError, match="greater than or equal to 100"):
        ProseRequest(
            job_id=job_id,
            segment_id="test",
            context={},
            target_word_count=50,
        )

    # Invalid - too high
    with pytest.raises(ValidationError, match="less than or equal to 2000"):
        ProseRequest(
            job_id=job_id,
            segment_id="test",
            context={},
            target_word_count=2500,
        )


def test_qa_request_valid() -> None:
    """Test QARequest with valid data."""
    job_id = uuid4()
    artifact_id = uuid4()

    req = QARequest(
        job_id=job_id,
        artifact_id=artifact_id,
        check_type="coherence",
    )

    assert req.check_type == "coherence"


def test_qa_response_score_validation() -> None:
    """Test QAResponse score validation."""
    from datetime import datetime

    job_id = uuid4()
    artifact_id = uuid4()

    # Valid scores
    resp = QAResponse(
        id=uuid4(),
        job_id=job_id,
        artifact_id=artifact_id,
        check_type="coherence",
        passed=True,
        logic_score=0.95,
        psychology_score=0.88,
        timeline_score=0.92,
        created_at=datetime.utcnow(),
    )

    assert 0.0 <= resp.logic_score <= 1.0

    # Invalid scores
    with pytest.raises(ValidationError, match="less than or equal to 1"):
        QAResponse(
            id=uuid4(),
            job_id=job_id,
            artifact_id=artifact_id,
            check_type="coherence",
            passed=True,
            logic_score=1.5,
            psychology_score=0.88,
            timeline_score=0.92,
            created_at=datetime.utcnow(),
        )


def test_style_request_valid() -> None:
    """Test StyleRequest with valid data."""
    job_id = uuid4()
    prose_id = uuid4()

    req = StyleRequest(
        job_id=job_id,
        prose_id=prose_id,
        target_style="literary",
    )

    assert req.language == "pl"  # Default
    assert req.commercial_level == "standard"  # Default


def test_style_response_valid() -> None:
    """Test StyleResponse with valid data."""
    from datetime import datetime

    job_id = uuid4()
    prose_id = uuid4()
    polished_id = uuid4()

    resp = StyleResponse(
        id=uuid4(),
        job_id=job_id,
        prose_id=prose_id,
        polished=True,
        polished_prose_id=polished_id,
        changes_count=15,
        style_score=0.89,
        created_at=datetime.utcnow(),
    )

    assert resp.polished is True
    assert resp.changes_count == 15
    assert 0.0 <= resp.style_score <= 1.0


def test_interpret_response_defaults() -> None:
    """Test InterpretResponse default values."""
    from datetime import datetime

    job_id = uuid4()

    resp = InterpretResponse(
        id=uuid4(),
        job_id=job_id,
        parameters={"genre": "fantasy"},
        created_at=datetime.utcnow(),
    )

    assert resp.agent == "interpreter"
    assert resp.stage == PipelineStage.STRUCTURE


def test_world_response_requires_summary() -> None:
    """Test WorldResponse requires summary."""
    from datetime import datetime

    job_id = uuid4()
    world_id = uuid4()

    # Valid with summary
    resp = WorldResponse(
        id=uuid4(),
        job_id=job_id,
        world_id=world_id,
        world_name="Eldoria",
        summary="A fantasy world with magic",
        created_at=datetime.utcnow(),
    )

    assert resp.summary

    # Summary word count validation applies
    long_summary = " ".join(["word"] * 501)
    with pytest.raises(ValidationError):  # Pydantic max_length or word count validator
        WorldResponse(
            id=uuid4(),
            job_id=job_id,
            world_id=world_id,
            world_name="Eldoria",
            summary=long_summary,
            created_at=datetime.utcnow(),
        )


def test_plot_response_validation() -> None:
    """Test PlotResponse validation."""
    from datetime import datetime

    job_id = uuid4()
    plot_id = uuid4()

    # Valid
    resp = PlotResponse(
        id=uuid4(),
        job_id=job_id,
        plot_id=plot_id,
        summary="Three-act structure with hero's journey",
        acts=3,
        scenes=12,
        created_at=datetime.utcnow(),
    )

    assert resp.acts >= 1
    assert resp.scenes >= 1

    # Invalid - too many acts
    with pytest.raises(ValidationError, match="less than or equal to 10"):
        PlotResponse(
            id=uuid4(),
            job_id=job_id,
            plot_id=plot_id,
            summary="Epic story",
            acts=11,
            scenes=12,
            created_at=datetime.utcnow(),
        )


def test_prose_response_requires_prose() -> None:
    """Test ProseResponse requires prose content."""
    from datetime import datetime

    job_id = uuid4()

    # Valid
    resp = ProseResponse(
        id=uuid4(),
        job_id=job_id,
        segment_id="act1_scene1",
        prose="The sun rose over the mountains, casting golden light across the valley. " * 10,
        word_count=500,
        model_used="gpt-4o",
        created_at=datetime.utcnow(),
    )

    assert len(resp.prose) >= 100

    # Invalid - prose too short
    with pytest.raises(ValidationError, match="at least 100 characters"):
        ProseResponse(
            id=uuid4(),
            job_id=job_id,
            segment_id="act1_scene1",
            prose="Too short",
            word_count=500,
            model_used="gpt-4o",
            created_at=datetime.utcnow(),
        )
