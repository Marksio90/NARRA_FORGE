"""
Pytest configuration and shared fixtures for all tests
"""
import asyncio
import pytest
import tempfile
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from narra_forge.core.config import NarraForgeConfig, create_default_config
from narra_forge.core.types import (
    Genre,
    ProductionType,
    ProductionBrief,
    World,
    Character,
    RealityLaws,
    WorldBoundaries,
    InternalTrajectory,
)
from narra_forge.memory import MemorySystem


# Configure pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config() -> NarraForgeConfig:
    """Create test configuration with dummy API key"""
    return create_default_config(
        openai_api_key="sk-test-key-12345678901234567890",
        environment="testing",
        max_cost_per_job=10.0,
        min_coherence_score=0.85,
    )


@pytest.fixture
async def temp_db_path():
    """Create temporary database path for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield db_path


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
async def memory_system(test_config, temp_db_path) -> AsyncGenerator[MemorySystem, None]:
    """Create temporary memory system for testing"""
    test_config.db_path = temp_db_path
    memory = MemorySystem(test_config)
    await memory.initialize()
    yield memory
    # Cleanup is automatic with tempfile


@pytest.fixture
def sample_production_brief() -> ProductionBrief:
    """Create sample production brief for testing"""
    return ProductionBrief(
        production_type=ProductionType.SHORT_STORY,
        genre=Genre.FANTASY,
        inspiration="A young alchemist discovers her master's dark secret about the price of immortality",
        additional_params={"tone": "dark", "target_word_count": 7000},
    )


@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client for testing without API calls"""
    from narra_forge.models.openai_client import OpenAIClient

    mock = AsyncMock(spec=OpenAIClient)

    # Mock chat_completion method (returns tuple: content, metadata)
    async def mock_chat_completion(*args, **kwargs):
        return (
            "Test generated content",
            {
                "model": "gpt-4o-mini",
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "total_tokens": 300,
                "cost_usd": 0.01
            }
        )

    mock.chat_completion = mock_chat_completion

    return mock


@pytest.fixture
def mock_model_router(test_config, mock_openai_client):
    """Create ModelRouter with mocked OpenAI client"""
    from narra_forge.models.model_router import ModelRouter

    router = ModelRouter(config=test_config, client=mock_openai_client)
    return router


@pytest.fixture
def sample_world_dict():
    """Sample world data for testing"""
    return {
        "world_id": "test_world_123",
        "name": "Eldoria",
        "genre": Genre.FANTASY.value,
        "reality_laws": {
            "physics": {"type": "standard"},
            "magic": {"exists": True, "cost": "life_essence"}
        },
        "boundaries": {
            "spatial": {"size": "small_continent"},
            "temporal": {"flow": "linear", "history_depth": 500}
        },
        "anomalies": ["unstable_magic_zones"],
        "core_conflict": "The price of immortality threatens the natural order",
        "existential_theme": "All power requires sacrifice",
        "description": "A world where alchemy is the dominant force",
        "linked_worlds": [],
    }


@pytest.fixture
def sample_world():
    """Sample World object for testing"""
    return World(
        world_id="test_world_123",
        name="Eldoria",
        genre=Genre.FANTASY,
        reality_laws=RealityLaws(
            physics={"type": "standard"},
            magic={"exists": True, "cost": "life_essence"},
        ),
        boundaries=WorldBoundaries(
            spatial={"size": "small_continent"},
            temporal={"flow": "linear", "history_depth": 500},
        ),
        anomalies=["unstable_magic_zones"],
        core_conflict="The price of immortality threatens the natural order",
        existential_theme="All power requires sacrifice",
        description="A world where alchemy is the dominant force",
    )


@pytest.fixture
def sample_character_dict():
    """Sample character data for testing"""
    return {
        "character_id": "char_lyra_001",
        "world_id": "test_world_123",
        "name": "Lyra Silvermoon",
        "internal_trajectory": {
            "starting_state": {
                "belief": "Alchemy can solve any problem",
                "fear": "Being powerless",
                "desire": "Master all alchemical arts"
            },
            "potential_arcs": [
                "Realizes power has a terrible cost",
                "Must choose between knowledge and innocence"
            ],
            "triggers": ["Discovery of master's secret"],
            "resistance_points": ["Loyalty to master", "Fear of truth"],
        },
        "contradictions": [
            "Seeks power but fears its consequences",
            "Values life but pursues death-defying alchemy"
        ],
        "cognitive_limits": ["Naive about human nature", "Overconfident in abilities"],
        "evolution_capacity": 0.8,
        "archetype": "innocent_to_experienced",
        "role": "protagonist",
    }


@pytest.fixture
def sample_character():
    """Sample Character object for testing"""
    return Character(
        character_id="char_lyra_001",
        world_id="test_world_123",
        name="Lyra Silvermoon",
        internal_trajectory=InternalTrajectory(
            starting_state={
                "belief": "Alchemy can solve any problem",
                "fear": "Being powerless",
                "desire": "Master all alchemical arts",
            },
            potential_arcs=[
                {"arc": "Realizes power has a terrible cost"},
                {"arc": "Must choose between knowledge and innocence"},
            ],
            triggers=["Discovery of master's secret"],
            resistance_points=["Loyalty to master", "Fear of truth"],
        ),
        contradictions=[
            "Seeks power but fears its consequences",
            "Values life but pursues death-defying alchemy",
        ],
        cognitive_limits=["Naive about human nature", "Overconfident in abilities"],
        evolution_capacity=0.8,
        archetype="innocent_to_experienced",
        role="protagonist",
    )


@pytest.fixture
def sample_narrative_structure():
    """Sample narrative structure for testing"""
    return {
        "structure_type": "three_act",
        "acts": [
            {
                "act_number": 1,
                "name": "Setup",
                "purpose": "Introduce world and character",
                "key_events": ["Discovery", "First confrontation"],
                "target_word_count": 2000,
            },
            {
                "act_number": 2,
                "name": "Confrontation",
                "purpose": "Character faces the truth",
                "key_events": ["Investigation", "Revelation", "Choice"],
                "target_word_count": 3500,
            },
            {
                "act_number": 3,
                "name": "Resolution",
                "purpose": "Character transformed by truth",
                "key_events": ["Final confrontation", "New understanding"],
                "target_word_count": 1500,
            },
        ],
        "pacing": "fast",
        "tension_curve": "rising",
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (may call APIs)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (full pipeline, slow)"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and benchmarking tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take >5 seconds"
    )
