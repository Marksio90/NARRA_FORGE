"""
Tests for memory modules (semantic, evolutionary, structural)

Tests untested methods to increase coverage from ~48% to 70%+
"""
import pytest
import json
from datetime import datetime
from pathlib import Path
import tempfile

from narra_forge.core.config import create_default_config
from narra_forge.core.types import Genre
from narra_forge.memory import MemorySystem


@pytest.fixture
async def memory():
    """Create temporary memory system for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = create_default_config(
            openai_api_key="sk-test-key",
            environment="testing"
        )
        config.db_path = Path(tmpdir) / "test.db"

        mem = MemorySystem(config)
        await mem.initialize()

        yield mem


@pytest.mark.unit
class TestSemanticMemory:
    """Test semantic memory operations"""

    @pytest.mark.asyncio
    async def test_add_node_with_all_parameters(self, memory):
        """Test adding a semantic node with all parameters"""
        node = await memory.semantic.add_node(
            node_type="event",
            content="Hero discovers the ancient artifact",
            world_id="world_123",
            connections=["node_456", "node_789"],
            significance=0.9,
            timestamp_in_story=100,
            metadata={"location": "ancient ruins", "impact": "high"},
        )

        assert node.node_id.startswith("node_")
        assert node.node_type == "event"
        assert node.content == "Hero discovers the ancient artifact"
        assert node.world_id == "world_123"
        assert node.connections == ["node_456", "node_789"]
        assert node.significance == 0.9
        assert node.timestamp_in_story == 100
        assert node.metadata["location"] == "ancient ruins"

    @pytest.mark.asyncio
    async def test_add_node_with_minimal_parameters(self, memory):
        """Test adding node with only required parameters"""
        node = await memory.semantic.add_node(
            node_type="motif",
            content="The price of power",
        )

        assert node.node_id is not None
        assert node.node_type == "motif"
        assert node.content == "The price of power"
        assert node.connections == []
        assert node.significance == 0.5  # Default
        assert node.metadata == {}

    @pytest.mark.asyncio
    async def test_add_event_convenience_method(self, memory):
        """Test add_event convenience method"""
        event = await memory.semantic.add_event(
            content="Battle at the castle gates",
            world_id="world_abc",
            timestamp_in_story=250,
            significance=0.85,
        )

        assert event.node_type == "event"
        assert event.content == "Battle at the castle gates"
        assert event.world_id == "world_abc"
        assert event.timestamp_in_story == 250
        assert event.significance == 0.85

    @pytest.mark.asyncio
    async def test_add_motif_convenience_method(self, memory):
        """Test add_motif convenience method"""
        motif = await memory.semantic.add_motif(
            content="Betrayal and redemption",
            world_id="world_xyz",
            significance=0.7,
        )

        assert motif.node_type == "motif"
        assert motif.content == "Betrayal and redemption"
        assert motif.world_id == "world_xyz"
        assert motif.significance == 0.7

    @pytest.mark.asyncio
    async def test_add_relationship_convenience_method(self, memory):
        """Test add_relationship convenience method"""
        relationship = await memory.semantic.add_relationship(
            content="Master and apprentice",
            world_id="world_def",
            connected_entities=["char_001", "char_002"],
            significance=0.8,
        )

        assert relationship.node_type == "relationship"
        assert relationship.content == "Master and apprentice"
        assert relationship.connections == ["char_001", "char_002"]

    @pytest.mark.asyncio
    async def test_add_conflict_convenience_method(self, memory):
        """Test add_conflict convenience method"""
        conflict = await memory.semantic.add_conflict(
            content="War between kingdoms",
            world_id="world_ghi",
            involved_entities=["faction_a", "faction_b"],
            significance=0.9,
        )

        assert conflict.node_type == "conflict"
        assert conflict.content == "War between kingdoms"
        assert conflict.connections == ["faction_a", "faction_b"]
        assert conflict.significance == 0.9

    @pytest.mark.asyncio
    async def test_get_nodes_by_world(self, memory):
        """Test retrieving nodes by world ID"""
        # Add multiple nodes
        await memory.semantic.add_event(
            content="Event 1",
            world_id="world_test",
            timestamp_in_story=10,
        )
        await memory.semantic.add_motif(
            content="Motif 1",
            world_id="world_test",
        )
        await memory.semantic.add_event(
            content="Event 2",
            world_id="world_test",
            timestamp_in_story=20,
        )

        # Retrieve all nodes for world
        nodes = await memory.semantic.get_nodes_by_world("world_test")

        assert len(nodes) == 3
        assert all(node.world_id == "world_test" for node in nodes)

    @pytest.mark.asyncio
    async def test_get_nodes_by_world_filtered_by_type(self, memory):
        """Test retrieving nodes filtered by type"""
        # Add multiple node types
        await memory.semantic.add_event(
            content="Event 1",
            world_id="world_filter",
            timestamp_in_story=10,
        )
        await memory.semantic.add_motif(
            content="Motif 1",
            world_id="world_filter",
        )
        await memory.semantic.add_event(
            content="Event 2",
            world_id="world_filter",
            timestamp_in_story=20,
        )

        # Get only events
        events = await memory.semantic.get_nodes_by_world("world_filter", node_type="event")

        assert len(events) == 2
        assert all(node.node_type == "event" for node in events)

    @pytest.mark.asyncio
    async def test_connect_nodes(self, memory):
        """Test connect_nodes method (currently TODO)"""
        # Should not raise exception even though it's TODO
        await memory.semantic.connect_nodes("node_a", "node_b")

    @pytest.mark.asyncio
    async def test_get_connected_nodes(self, memory):
        """Test get_connected_nodes method (currently TODO)"""
        # Should return empty list since it's TODO
        connected = await memory.semantic.get_connected_nodes("node_xyz")
        assert connected == []


@pytest.mark.unit
class TestEvolutionaryMemory:
    """Test evolutionary memory operations"""

    @pytest.mark.asyncio
    async def test_record_change_with_all_parameters(self, memory):
        """Test recording a change with all parameters"""
        entry = await memory.evolutionary.record_change(
            entity_id="char_hero_001",
            entity_type="character",
            change_type="belief_shift",
            before_state={"belief": "power_is_everything"},
            after_state={"belief": "compassion_matters"},
            trigger="witnessing_sacrifice",
            significance=0.9,
        )

        assert entry.entry_id.startswith("evol_")
        assert entry.entity_id == "char_hero_001"
        assert entry.entity_type == "character"
        assert entry.change_type == "belief_shift"
        assert entry.before_state["belief"] == "power_is_everything"
        assert entry.after_state["belief"] == "compassion_matters"
        assert entry.trigger == "witnessing_sacrifice"
        assert entry.significance == 0.9
        assert isinstance(entry.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_record_change_with_minimal_parameters(self, memory):
        """Test recording change with minimal parameters"""
        entry = await memory.evolutionary.record_change(
            entity_id="world_001",
            entity_type="world",
            change_type="political_shift",
            before_state={"ruler": "king"},
            after_state={"ruler": "council"},
        )

        assert entry.entity_id == "world_001"
        assert entry.trigger is None  # Default
        assert entry.significance == 0.5  # Default

    @pytest.mark.asyncio
    async def test_get_history(self, memory):
        """Test retrieving evolution history"""
        # Record multiple changes
        await memory.evolutionary.record_change(
            entity_id="char_test",
            entity_type="character",
            change_type="skill_gained",
            before_state={"swordsmanship": 3},
            after_state={"swordsmanship": 5},
        )
        await memory.evolutionary.record_change(
            entity_id="char_test",
            entity_type="character",
            change_type="belief_shift",
            before_state={"honor": "absolute"},
            after_state={"honor": "flexible"},
        )

        # Get history
        history = await memory.evolutionary.get_history("char_test")

        assert len(history) >= 2
        assert all(entry.entity_id == "char_test" for entry in history)
        assert all(isinstance(entry.timestamp, datetime) for entry in history)

    @pytest.mark.asyncio
    async def test_get_history_with_limit(self, memory):
        """Test history retrieval with limit"""
        # Record many changes
        for i in range(10):
            await memory.evolutionary.record_change(
                entity_id="char_limit_test",
                entity_type="character",
                change_type=f"change_{i}",
                before_state={"value": i},
                after_state={"value": i + 1},
            )

        # Get limited history
        history = await memory.evolutionary.get_history("char_limit_test", limit=5)

        assert len(history) <= 5

    @pytest.mark.asyncio
    async def test_record_character_evolution_convenience_method(self, memory):
        """Test record_character_evolution convenience method"""
        entry = await memory.evolutionary.record_character_evolution(
            character_id="char_protagonist",
            change_type="psychological_transformation",
            before={"fear": "abandonment"},
            after={"fear": "loss_of_self"},
            trigger="mentor_death",
            significance=0.85,
        )

        assert entry.entity_type == "character"
        assert entry.entity_id == "char_protagonist"
        assert entry.change_type == "psychological_transformation"
        assert entry.trigger == "mentor_death"
        assert entry.significance == 0.85

    @pytest.mark.asyncio
    async def test_record_world_event_convenience_method(self, memory):
        """Test record_world_event convenience method"""
        entry = await memory.evolutionary.record_world_event(
            world_id="world_epic",
            event_type="cataclysm",
            before={"magic": "abundant"},
            after={"magic": "scarce"},
            trigger="great_ritual",
            significance=0.95,
        )

        assert entry.entity_type == "world"
        assert entry.entity_id == "world_epic"
        assert entry.change_type == "cataclysm"
        assert entry.significance == 0.95

    @pytest.mark.asyncio
    async def test_get_character_arc(self, memory):
        """Test get_character_arc wrapper method"""
        # Record character changes
        await memory.evolutionary.record_character_evolution(
            character_id="char_arc_test",
            change_type="growth",
            before={"maturity": 1},
            after={"maturity": 2},
            trigger="first_trial",
        )
        await memory.evolutionary.record_character_evolution(
            character_id="char_arc_test",
            change_type="growth",
            before={"maturity": 2},
            after={"maturity": 3},
            trigger="second_trial",
        )

        # Get character arc
        arc = await memory.evolutionary.get_character_arc("char_arc_test")

        assert len(arc) >= 2
        assert all(entry.entity_type == "character" for entry in arc)

    @pytest.mark.asyncio
    async def test_get_world_timeline(self, memory):
        """Test get_world_timeline wrapper method"""
        # Record world events
        await memory.evolutionary.record_world_event(
            world_id="world_timeline",
            event_type="founding",
            before={},
            after={"era": "kingdom"},
        )
        await memory.evolutionary.record_world_event(
            world_id="world_timeline",
            event_type="war",
            before={"era": "kingdom"},
            after={"era": "empire"},
        )

        # Get timeline
        timeline = await memory.evolutionary.get_world_timeline("world_timeline")

        assert len(timeline) >= 2
        assert all(entry.entity_type == "world" for entry in timeline)


@pytest.mark.unit
class TestStructuralMemory:
    """Test structural memory operations"""

    @pytest.mark.asyncio
    async def test_create_world_with_all_parameters(self, memory):
        """Test creating a world with all parameters"""
        world = await memory.structural.create_world(
            name="Aethermoor",
            genre="fantasy",
            reality_laws={
                "physics": {"type": "modified_newtonian"},
                "magic": {"exists": True, "cost": "life_essence"},
            },
            boundaries={
                "spatial": {"size": "continent"},
                "temporal": {"flow": "linear", "history_depth": 1000},
            },
            core_conflict="Magic vs Technology",
            existential_theme="The cost of progress",
            anomalies=["void_rifts", "time_loops"],
            description="A world torn between magic and science",
            linked_worlds=["world_adjacent_123"],
        )

        assert world.world_id.startswith("world_")
        assert world.name == "Aethermoor"
        assert world.genre == Genre.FANTASY
        assert world.reality_laws.magic["exists"] is True
        assert world.boundaries.spatial["size"] == "continent"
        assert world.core_conflict == "Magic vs Technology"
        assert world.existential_theme == "The cost of progress"
        assert "void_rifts" in world.anomalies
        assert world.description == "A world torn between magic and science"
        assert "world_adjacent_123" in world.linked_worlds

    @pytest.mark.asyncio
    async def test_create_world_with_minimal_parameters(self, memory):
        """Test creating world with minimal parameters"""
        world = await memory.structural.create_world(
            name="Minimal World",
            genre="scifi",
            reality_laws={"physics": {"type": "standard"}},
            boundaries={"spatial": {}, "temporal": {}},
            core_conflict="Survival",
            existential_theme="Human endurance",
        )

        assert world.name == "Minimal World"
        assert world.genre == Genre.SCIFI
        assert world.anomalies == []  # Default
        assert world.description is None  # Default
        assert world.linked_worlds == []  # Default

    @pytest.mark.asyncio
    async def test_get_world(self, memory):
        """Test retrieving a world by ID"""
        # Create world
        created = await memory.structural.create_world(
            name="Test Retrieval World",
            genre="horror",
            reality_laws={"physics": {"type": "nightmarish"}},
            boundaries={"spatial": {}, "temporal": {}},
            core_conflict="Fear itself",
            existential_theme="Confronting darkness",
        )

        # Retrieve world
        retrieved = await memory.structural.get_world(created.world_id)

        assert retrieved is not None
        assert retrieved.world_id == created.world_id
        assert retrieved.name == "Test Retrieval World"
        assert retrieved.genre == Genre.HORROR

    @pytest.mark.asyncio
    async def test_get_world_nonexistent(self, memory):
        """Test retrieving non-existent world returns None"""
        result = await memory.structural.get_world("nonexistent_world_id")
        assert result is None

    @pytest.mark.asyncio
    async def test_save_world_dict(self, memory):
        """Test saving world from dict"""
        world_dict = {
            "world_id": "test_dict_world",
            "name": "Dict World",
            "genre": Genre.DRAMA.value,
            "reality_laws": {"physics": {"type": "standard"}},
            "boundaries": {"spatial": {}, "temporal": {}},
            "anomalies": [],
            "core_conflict": "Internal struggle",
            "existential_theme": "Identity",
            "description": "A world of introspection",
            "linked_worlds": [],
        }

        await memory.structural.save_world(world_dict)

        # Retrieve and verify
        retrieved = await memory.structural.get_world("test_dict_world")
        assert retrieved is not None
        assert retrieved.name == "Dict World"

    @pytest.mark.asyncio
    async def test_save_character_dict(self, memory):
        """Test saving character from dict"""
        char_dict = {
            "character_id": "char_dict_test",
            "world_id": "world_123",
            "name": "Dict Character",
            "internal_trajectory": {
                "starting_state": {"belief": "test"},
                "potential_arcs": [],
                "triggers": [],
                "resistance_points": [],
            },
            "contradictions": ["brave but fearful"],
            "cognitive_limits": ["blind_to_own_flaws"],
            "evolution_capacity": 0.7,
            "archetype": "reluctant_hero",
            "role": "protagonist",
        }

        await memory.structural.save_character(char_dict)

        # Retrieve and verify
        characters = await memory.structural.get_characters_in_world("world_123")
        assert len(characters) >= 1
        assert any(char.name == "Dict Character" for char in characters)

    @pytest.mark.asyncio
    async def test_get_characters_in_world(self, memory):
        """Test retrieving characters by world"""
        # Create characters in same world
        char1_dict = {
            "character_id": "char_w1_001",
            "world_id": "world_chars_test",
            "name": "Character One",
            "internal_trajectory": {"starting_state": {}, "potential_arcs": [], "triggers": [], "resistance_points": []},
            "contradictions": [],
            "cognitive_limits": [],
            "evolution_capacity": 0.5,
            "archetype": "hero",
            "role": "protagonist",
        }
        char2_dict = {
            "character_id": "char_w1_002",
            "world_id": "world_chars_test",
            "name": "Character Two",
            "internal_trajectory": {"starting_state": {}, "potential_arcs": [], "triggers": [], "resistance_points": []},
            "contradictions": [],
            "cognitive_limits": [],
            "evolution_capacity": 0.6,
            "archetype": "mentor",
            "role": "supporting",
        }

        await memory.structural.save_character(char1_dict)
        await memory.structural.save_character(char2_dict)

        # Retrieve characters
        characters = await memory.structural.get_characters_in_world("world_chars_test")

        assert len(characters) >= 2
        names = [char.name for char in characters]
        assert "Character One" in names
        assert "Character Two" in names

    @pytest.mark.asyncio
    async def test_list_worlds(self, memory):
        """Test listing all worlds"""
        # Create multiple worlds
        for i in range(3):
            await memory.structural.create_world(
                name=f"List World {i}",
                genre="fantasy",
                reality_laws={"physics": {}},
                boundaries={"spatial": {}, "temporal": {}},
                core_conflict=f"Conflict {i}",
                existential_theme=f"Theme {i}",
            )

        # List worlds
        worlds = await memory.structural.list_worlds(limit=10)

        assert len(worlds) >= 3
