"""
Tests for memory system
"""
import pytest
from pathlib import Path
import tempfile

from narra_forge.core.config import create_default_config
from narra_forge.core.types import Genre
from narra_forge.memory import MemorySystem


@pytest.fixture
async def memory_system():
    """Create temporary memory system for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = create_default_config(
            openai_api_key="sk-test-key",
            environment="testing"
        )
        config.db_path = Path(tmpdir) / "test.db"

        memory = MemorySystem(config)
        await memory.initialize()

        yield memory


@pytest.mark.asyncio
async def test_memory_initialization(memory_system):
    """Test memory system initialization"""
    assert memory_system is not None
    assert memory_system.storage is not None
    assert memory_system.structural is not None
    assert memory_system.semantic is not None
    assert memory_system.evolutionary is not None


@pytest.mark.asyncio
async def test_save_and_retrieve_world(memory_system):
    """Test saving and retrieving a world"""
    world_dict = {
        "world_id": "test_world_123",
        "name": "Test World",
        "genre": Genre.FANTASY.value,
        "reality_laws": {"physics": {"type": "standard"}},
        "boundaries": {"spatial": {"size": "small"}},
        "anomalies": [],
        "core_conflict": "Test conflict",
        "existential_theme": "Test theme",
        "description": "Test description",
        "linked_worlds": [],
    }

    # Save
    await memory_system.structural.save_world(world_dict)

    # Retrieve
    retrieved = await memory_system.structural.get_world("test_world_123")

    assert retrieved is not None
    assert retrieved["name"] == "Test World"
    assert retrieved["genre"] == Genre.FANTASY.value


@pytest.mark.asyncio
async def test_save_and_retrieve_character(memory_system):
    """Test saving and retrieving a character"""
    character_dict = {
        "character_id": "char_123",
        "world_id": "world_123",
        "name": "Test Character",
        "internal_trajectory": {
            "starting_state": {"belief": "test"},
            "potential_arcs": [],
            "triggers": [],
            "resistance_points": [],
        },
        "contradictions": ["test"],
        "cognitive_limits": ["test"],
        "evolution_capacity": 0.5,
        "archetype": "hero",
        "role": "protagonist",
    }

    # Save
    await memory_system.structural.save_character(character_dict)

    # Retrieve
    characters = await memory_system.structural.get_characters_by_world("world_123")

    assert len(characters) == 1
    assert characters[0]["name"] == "Test Character"


@pytest.mark.asyncio
async def test_save_and_retrieve_job(memory_system):
    """Test saving and retrieving a production job"""
    job_dict = {
        "job_id": "job_test_123",
        "brief": {"production_type": "short_story", "genre": "fantasy"},
        "status": "completed",
        "current_stage": None,
        "world_id": "world_123",
        "tokens_used": 10000,
        "cost_usd": 1.50,
        "started_at": "2024-01-01T00:00:00",
        "completed_at": "2024-01-01T00:10:00",
        "error": None,
    }

    # Save
    await memory_system.save_job(job_dict)

    # Retrieve
    retrieved = await memory_system.get_job("job_test_123")

    assert retrieved is not None
    assert retrieved["job_id"] == "job_test_123"
    assert retrieved["status"] == "completed"
    assert retrieved["tokens_used"] == 10000


@pytest.mark.asyncio
async def test_list_jobs(memory_system):
    """Test listing jobs with filters"""
    # Create multiple jobs
    for i in range(3):
        job_dict = {
            "job_id": f"job_{i}",
            "brief": {"production_type": "short_story"},
            "status": "completed" if i < 2 else "pending",
            "current_stage": None,
            "world_id": None,
            "tokens_used": 1000 * i,
            "cost_usd": 0.1 * i,
            "started_at": None,
            "completed_at": None,
            "error": None,
        }
        await memory_system.save_job(job_dict)

    # List all
    all_jobs = await memory_system.list_jobs(limit=10)
    assert len(all_jobs) == 3

    # List completed only
    completed_jobs = await memory_system.list_jobs(status="completed", limit=10)
    assert len(completed_jobs) == 2

    # List pending only
    pending_jobs = await memory_system.list_jobs(status="pending", limit=10)
    assert len(pending_jobs) == 1
