"""Unit tests for domain schemas."""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from models.schemas.domain import (
    ArtifactSchema,
    CharacterSchema,
    CostSnapshotSchema,
    PlotSchema,
    SegmentSchema,
    WorldSchema,
)


def test_world_schema_valid() -> None:
    """Test WorldSchema with valid data."""
    world_id = uuid4()
    now = datetime.utcnow()

    world = WorldSchema(
        id=world_id,
        name="Eldoria",
        rules=["Magic requires sacrifice", "Technology is steam-powered"],
        geography={"continents": 3, "climate": "temperate"},
        history=[{"year": 1000, "event": "The Great War"}],
        themes=["power", "sacrifice"],
        version=1,
        checksum="a" * 64,
        created_at=now,
        updated_at=now,
    )

    assert world.name == "Eldoria"
    assert len(world.rules) == 2
    assert world.themes == ["power", "sacrifice"]


def test_world_schema_rules_validation() -> None:
    """Test WorldSchema rules validation."""
    world_id = uuid4()
    now = datetime.utcnow()

    # Invalid - empty string in rules
    with pytest.raises(ValidationError, match="cannot be empty strings"):
        WorldSchema(
            id=world_id,
            name="Eldoria",
            rules=["Valid rule", ""],
            version=1,
            checksum="a" * 64,
            created_at=now,
            updated_at=now,
        )


def test_world_schema_themes_unique() -> None:
    """Test WorldSchema themes must be unique."""
    world_id = uuid4()
    now = datetime.utcnow()

    # Invalid - duplicate themes
    with pytest.raises(ValidationError, match="must be unique"):
        WorldSchema(
            id=world_id,
            name="Eldoria",
            themes=["power", "magic", "power"],
            version=1,
            checksum="a" * 64,
            created_at=now,
            updated_at=now,
        )


def test_world_schema_checksum_validation() -> None:
    """Test WorldSchema checksum validation."""
    world_id = uuid4()
    now = datetime.utcnow()

    # Invalid - checksum too short
    with pytest.raises(ValidationError, match="at least 64 characters"):
        WorldSchema(
            id=world_id,
            name="Eldoria",
            version=1,
            checksum="short",
            created_at=now,
            updated_at=now,
        )


def test_character_schema_valid() -> None:
    """Test CharacterSchema with valid data."""
    char_id = uuid4()
    world_id = uuid4()
    now = datetime.utcnow()

    character = CharacterSchema(
        id=char_id,
        world_id=world_id,
        name="Aelric",
        trajectory=[
            {"stage": "introduction", "state": "naive"},
            {"stage": "conflict", "state": "tested"},
        ],
        relationships=[
            {"character_id": str(uuid4()), "type": "mentor"},
        ],
        constraints=["Cannot use magic", "Fear of heights"],
        created_at=now,
        updated_at=now,
    )

    assert character.name == "Aelric"
    assert len(character.trajectory) == 2
    assert len(character.relationships) == 1


def test_character_schema_trajectory_validation() -> None:
    """Test CharacterSchema trajectory validation."""
    char_id = uuid4()
    world_id = uuid4()
    now = datetime.utcnow()

    # Invalid - missing required fields in trajectory
    with pytest.raises(ValidationError, match="must have 'stage' and 'state' fields"):
        CharacterSchema(
            id=char_id,
            world_id=world_id,
            name="Aelric",
            trajectory=[{"stage": "introduction"}],  # Missing 'state'
            created_at=now,
            updated_at=now,
        )


def test_character_schema_relationships_validation() -> None:
    """Test CharacterSchema relationships validation."""
    char_id = uuid4()
    world_id = uuid4()
    now = datetime.utcnow()

    # Invalid - missing required fields in relationships
    with pytest.raises(ValidationError, match="must have 'character_id' and 'type' fields"):
        CharacterSchema(
            id=char_id,
            world_id=world_id,
            name="Aelric",
            relationships=[{"character_id": str(uuid4())}],  # Missing 'type'
            created_at=now,
            updated_at=now,
        )


def test_plot_schema_valid() -> None:
    """Test PlotSchema with valid data."""
    plot_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    plot = PlotSchema(
        id=plot_id,
        job_id=job_id,
        structure="three-act",
        acts=[
            {"number": 1, "description": "Setup"},
            {"number": 2, "description": "Confrontation"},
            {"number": 3, "description": "Resolution"},
        ],
        scenes=[
            {"number": 1, "act": 1, "description": "Opening"},
            {"number": 2, "act": 1, "description": "Inciting incident"},
        ],
        conflicts=["Man vs Self", "Man vs Society"],
        summary="A hero's journey through adversity",
        created_at=now,
        updated_at=now,
    )

    assert plot.structure == "three-act"
    assert len(plot.acts) == 3
    assert len(plot.scenes) == 2


def test_plot_schema_acts_validation() -> None:
    """Test PlotSchema acts validation."""
    plot_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    # Invalid - empty acts
    with pytest.raises(ValidationError):  # Pydantic or custom validator
        PlotSchema(
            id=plot_id,
            job_id=job_id,
            structure="three-act",
            acts=[],
            scenes=[{"number": 1, "act": 1, "description": "Test"}],
            summary="Test plot",
            created_at=now,
            updated_at=now,
        )

    # Invalid - act without description
    with pytest.raises(ValidationError, match="Act .* must have a description"):
        PlotSchema(
            id=plot_id,
            job_id=job_id,
            structure="three-act",
            acts=[{"number": 1}],
            scenes=[{"number": 1, "act": 1, "description": "Test"}],
            summary="Test plot",
            created_at=now,
            updated_at=now,
        )


def test_plot_schema_scenes_validation() -> None:
    """Test PlotSchema scenes validation."""
    plot_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    # Invalid - empty scenes
    with pytest.raises(ValidationError):  # Pydantic or custom validator
        PlotSchema(
            id=plot_id,
            job_id=job_id,
            structure="three-act",
            acts=[{"number": 1, "description": "Act 1"}],
            scenes=[],
            summary="Test plot",
            created_at=now,
            updated_at=now,
        )

    # Invalid - scene without act
    with pytest.raises(ValidationError, match="Scene .* must specify which act"):
        PlotSchema(
            id=plot_id,
            job_id=job_id,
            structure="three-act",
            acts=[{"number": 1, "description": "Act 1"}],
            scenes=[{"number": 1}],
            summary="Test plot",
            created_at=now,
            updated_at=now,
        )


def test_segment_schema_valid() -> None:
    """Test SegmentSchema with valid data."""
    segment_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    prose_text = " ".join(["word"] * 150)  # 150 words

    segment = SegmentSchema(
        id=segment_id,
        job_id=job_id,
        segment_id="act1_scene1",
        prose=prose_text,
        word_count=150,
        model_used="gpt-4o",
        version=1,
        created_at=now,
    )

    assert segment.segment_id == "act1_scene1"
    assert segment.word_count == 150
    assert segment.model_used == "gpt-4o"


def test_segment_schema_word_count_validation() -> None:
    """Test SegmentSchema word count validation."""
    segment_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    prose_text = " ".join(["word"] * 150)  # 150 words

    # Invalid - word count mismatch
    with pytest.raises(ValidationError, match="Word count mismatch"):
        SegmentSchema(
            id=segment_id,
            job_id=job_id,
            segment_id="act1_scene1",
            prose=prose_text,
            word_count=500,  # Incorrect count
            model_used="gpt-4o",
            version=1,
            created_at=now,
        )


def test_segment_schema_prose_length_validation() -> None:
    """Test SegmentSchema prose length validation."""
    segment_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    # Invalid - prose too short
    with pytest.raises(ValidationError, match="at least 100 characters"):
        SegmentSchema(
            id=segment_id,
            job_id=job_id,
            segment_id="act1_scene1",
            prose="Too short",
            word_count=2,
            model_used="gpt-4o",
            version=1,
            created_at=now,
        )


def test_artifact_schema_valid() -> None:
    """Test ArtifactSchema with valid data."""
    artifact_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    artifact = ArtifactSchema(
        id=artifact_id,
        job_id=job_id,
        type="world_spec",
        version=1,
        data={"name": "Eldoria", "rules": ["Magic exists"]},
        checksum="a" * 64,
        created_at=now,
    )

    assert artifact.type == "world_spec"
    assert artifact.data == {"name": "Eldoria", "rules": ["Magic exists"]}


def test_artifact_schema_type_validation() -> None:
    """Test ArtifactSchema type validation."""
    artifact_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    # Invalid - invalid artifact type
    with pytest.raises(ValidationError, match="Invalid artifact type"):
        ArtifactSchema(
            id=artifact_id,
            job_id=job_id,
            type="invalid_type",
            version=1,
            data={"test": "data"},
            checksum="a" * 64,
            created_at=now,
        )


def test_artifact_schema_data_not_empty() -> None:
    """Test ArtifactSchema data cannot be empty."""
    artifact_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    # Invalid - empty data
    with pytest.raises(ValidationError, match="cannot be empty"):
        ArtifactSchema(
            id=artifact_id,
            job_id=job_id,
            type="world_spec",
            version=1,
            data={},
            checksum="a" * 64,
            created_at=now,
        )


def test_cost_snapshot_schema_valid() -> None:
    """Test CostSnapshotSchema with valid data."""
    snapshot_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    snapshot = CostSnapshotSchema(
        id=snapshot_id,
        job_id=job_id,
        stage="world_architect",
        tokens_used=1500,
        cost_usd=0.15,
        model="gpt-4o-mini",
        created_at=now,
    )

    assert snapshot.stage == "world_architect"
    assert snapshot.tokens_used == 1500
    assert snapshot.cost_usd == 0.15


def test_cost_snapshot_schema_model_validation() -> None:
    """Test CostSnapshotSchema model validation."""
    snapshot_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    # Invalid - invalid model
    with pytest.raises(ValidationError, match="Invalid model"):
        CostSnapshotSchema(
            id=snapshot_id,
            job_id=job_id,
            stage="world_architect",
            tokens_used=1500,
            cost_usd=0.15,
            model="gpt-3.5-turbo",
            created_at=now,
        )


def test_cost_snapshot_schema_cost_validation() -> None:
    """Test CostSnapshotSchema cost validation."""
    snapshot_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    # Invalid - unreasonably high cost
    with pytest.raises(ValidationError, match="unreasonably high"):
        CostSnapshotSchema(
            id=snapshot_id,
            job_id=job_id,
            stage="world_architect",
            tokens_used=1500,
            cost_usd=150.0,
            model="gpt-4o",
            created_at=now,
        )


def test_cost_snapshot_schema_negative_values() -> None:
    """Test CostSnapshotSchema rejects negative values."""
    snapshot_id = uuid4()
    job_id = uuid4()
    now = datetime.utcnow()

    # Invalid - negative tokens
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        CostSnapshotSchema(
            id=snapshot_id,
            job_id=job_id,
            stage="world_architect",
            tokens_used=-100,
            cost_usd=0.15,
            model="gpt-4o-mini",
            created_at=now,
        )

    # Invalid - negative cost
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        CostSnapshotSchema(
            id=snapshot_id,
            job_id=job_id,
            stage="world_architect",
            tokens_used=1500,
            cost_usd=-0.15,
            model="gpt-4o-mini",
            created_at=now,
        )
