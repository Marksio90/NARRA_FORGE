"""
Tests for core data types
"""
from datetime import datetime

from narra_forge.core.types import (
    Character,
    Genre,
    InternalTrajectory,
    NarrativeStructure,
    ProductionBrief,
    ProductionType,
    RealityLaws,
    Segment,
    World,
    WorldBoundaries,
)


def test_production_brief_creation():
    """Test ProductionBrief creation"""
    brief = ProductionBrief(
        production_type=ProductionType.SHORT_STORY,
        genre=Genre.FANTASY,
        inspiration="Test inspiration"
    )

    assert brief.production_type == ProductionType.SHORT_STORY
    assert brief.genre == Genre.FANTASY
    assert brief.inspiration == "Test inspiration"
    assert brief.brief_id.startswith("brief_")
    assert isinstance(brief.created_at, datetime)


def test_world_creation():
    """Test World creation"""
    world = World(
        world_id="test_world_123",
        name="Test World",
        genre=Genre.FANTASY,
        reality_laws=RealityLaws(
            physics={"type": "standard"},
            magic={"level": "high"},
        ),
        boundaries=WorldBoundaries(
            spatial={"size": "continental"},
            temporal={"span": "centuries"},
        ),
        anomalies=[],
        core_conflict="Light vs Darkness",
        existential_theme="Nature of power"
    )

    assert world.world_id == "test_world_123"
    assert world.name == "Test World"
    assert world.genre == Genre.FANTASY
    assert world.reality_laws.magic["level"] == "high"


def test_character_creation():
    """Test Character creation"""
    character = Character(
        character_id="char_123",
        world_id="world_123",
        name="Test Character",
        internal_trajectory=InternalTrajectory(
            starting_state={"belief": "test"},
            potential_arcs=[],
            triggers=[],
            resistance_points=[],
        ),
        contradictions=["contradiction1"],
        cognitive_limits=["limit1"],
        evolution_capacity=0.7,
    )

    assert character.character_id == "char_123"
    assert character.name == "Test Character"
    assert character.evolution_capacity == 0.7
    assert len(character.contradictions) == 1


def test_segment_creation():
    """Test Segment creation"""
    segment = Segment(
        segment_id="seg_123",
        segment_number=1,
        title="Chapter 1",
        summary="Test summary",
        key_events=["event1", "event2"],
        characters_involved=["char1"],
        location="test_location",
        estimated_words=1500,
        narrative_function="setup"
    )

    assert segment.segment_id == "seg_123"
    assert segment.segment_number == 1
    assert segment.estimated_words == 1500
    assert len(segment.key_events) == 2


def test_narrative_structure():
    """Test NarrativeStructure"""
    structure = NarrativeStructure(
        structure_type="three_act",
        acts=[{"act": 1}, {"act": 2}, {"act": 3}],
        key_beats=[{"beat": "inciting_incident"}],
        pacing_map={"act1": "slow", "act2": "fast"},
        estimated_word_count=10000
    )

    assert structure.structure_type == "three_act"
    assert len(structure.acts) == 3
    assert structure.estimated_word_count == 10000


def test_production_type_enum():
    """Test ProductionType enum"""
    assert ProductionType.SHORT_STORY.value == "short_story"
    assert ProductionType.NOVEL.value == "novel"
    assert ProductionType.EPIC_SAGA.value == "epic_saga"


def test_genre_enum():
    """Test Genre enum"""
    assert Genre.FANTASY.value == "fantasy"
    assert Genre.SCIFI.value == "scifi"
    assert Genre.HORROR.value == "horror"
