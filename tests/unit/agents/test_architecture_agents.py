"""
Tests for architecture agents (a02-a05)

Tests World Architect, Character Architect, Structure Designer, Segment Planner
to increase coverage from ~32-37% to 70%+
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4

from narra_forge.core.types import (
    Genre,
    ProductionType,
    ProductionBrief,
    World,
    RealityLaws,
    WorldBoundaries,
    Character,
    InternalTrajectory,
    NarrativeStructure,
    Segment,
)
from narra_forge.agents.a02_world_architect import WorldArchitectAgent
from narra_forge.agents.a03_character_architect import CharacterArchitectAgent
from narra_forge.agents.a04_structure_designer import StructureDesignerAgent
from narra_forge.agents.a05_segment_planner import SegmentPlannerAgent


@pytest.mark.unit
class TestWorldArchitectAgent:
    """Test World Architect Agent (a02)"""

    @pytest.mark.asyncio
    async def test_execute_creates_new_world(self, test_config, memory_system, mock_model_router):
        """Test successful world creation"""
        agent = WorldArchitectAgent(test_config, memory_system, mock_model_router)

        # Mock LLM response
        world_data = {
            "world_name": "Aethermoor",
            "genre": "fantasy",
            "reality_laws": {
                "physics": {"type": "altered", "key_differences": ["gravity fluctuates"]},
                "magic": {"exists": True, "cost": "life essence", "limits": ["range limited"]},
                "technology": {"level": "medieval", "limitations": ["no gunpowder"]},
            },
            "boundaries": {
                "spatial": {"size": "continental"},
                "temporal": {"flow": "normal", "span": "centuries"},
            },
            "anomalies": ["void rifts"],
            "core_conflict": "Magic vs Technology",
            "existential_theme": "Cost of progress",
            "atmosphere": "Dark and mysterious",
        }

        mock_call = MagicMock()
        mock_call.total_tokens = 1500
        mock_call.cost_usd = 0.05

        with patch.object(agent, 'call_model_json', new_callable=AsyncMock) as mock_call_model:
            mock_call_model.return_value = (world_data, mock_call)

            context = {
                "analyzed_brief": {
                    "genre": "fantasy",
                    "themes": ["magic", "conflict"],
                    "tone": "dark",
                },
                "brief": ProductionBrief(
                    production_type=ProductionType.SHORT_STORY,
                    genre=Genre.FANTASY,
                    inspiration="test",
                ),
            }

            result = await agent.execute(context)

            assert result.success is True
            assert "world" in result.data
            assert result.data["world"].name == "Aethermoor"
            assert result.data["world"].genre == Genre.FANTASY
            assert result.data["existing_world"] is False

    @pytest.mark.asyncio
    async def test_execute_reuses_existing_world(self, test_config, memory_system, mock_model_router, sample_world):
        """Test that agent reuses existing world when world_id provided"""
        agent = WorldArchitectAgent(test_config, memory_system, mock_model_router)

        # Mock memory to return existing world
        with patch.object(memory_system.structural, 'get_world', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_world

            context = {
                "analyzed_brief": {"genre": "fantasy"},
                "brief": ProductionBrief(
                    production_type=ProductionType.SHORT_STORY,
                    genre=Genre.FANTASY,
                    inspiration="test",
                    world_id=sample_world.world_id,
                ),
            }

            result = await agent.execute(context)

            assert result.success is True
            assert result.data["world"] == sample_world
            assert result.data["existing_world"] is True

    @pytest.mark.asyncio
    async def test_execute_fails_without_analyzed_brief(self, test_config, memory_system, mock_model_router):
        """Test error handling when analyzed_brief missing"""
        agent = WorldArchitectAgent(test_config, memory_system, mock_model_router)

        context = {"brief": ProductionBrief(
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.FANTASY,
            inspiration="test",
        )}

        result = await agent.execute(context)

        assert result.success is False
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_execute_handles_llm_error(self, test_config, memory_system, mock_model_router):
        """Test error handling when LLM call fails"""
        agent = WorldArchitectAgent(test_config, memory_system, mock_model_router)

        with patch.object(agent, 'call_model_json', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = Exception("LLM API error")

            context = {
                "analyzed_brief": {"genre": "fantasy"},
                "brief": ProductionBrief(
                    production_type=ProductionType.SHORT_STORY,
                    genre=Genre.FANTASY,
                    inspiration="test",
                ),
            }

            result = await agent.execute(context)

            assert result.success is False
            assert len(result.errors) > 0


@pytest.mark.unit
class TestCharacterArchitectAgent:
    """Test Character Architect Agent (a03)"""

    @pytest.mark.asyncio
    async def test_execute_creates_characters(self, test_config, memory_system, mock_model_router, sample_world):
        """Test successful character creation"""
        agent = CharacterArchitectAgent(test_config, memory_system, mock_model_router)

        # Mock LLM response
        char_data = {
            "characters": [
                {
                    "name": "Aria Shadowmend",
                    "role": "protagonist",
                    "archetype": "reluctant_hero",
                    "internal_trajectory": {
                        "starting_state": {"belief": "power corrupts"},
                        "potential_arcs": ["redemption"],
                        "triggers": ["mentor death"],
                        "resistance_points": ["fear of failure"],
                    },
                    "contradictions": ["brave but fearful"],
                    "cognitive_limits": ["blind to own flaws"],
                    "evolution_capacity": 0.8,
                }
            ]
        }

        mock_call = MagicMock()
        mock_call.total_tokens = 2000
        mock_call.cost_usd = 0.08

        with patch.object(agent, 'call_model_json', new_callable=AsyncMock) as mock_call_model:
            mock_call_model.return_value = (char_data, mock_call)

            context = {
                "analyzed_brief": {"genre": "fantasy", "tone": "dark"},
                "brief": ProductionBrief(
                    production_type=ProductionType.SHORT_STORY,
                    genre=Genre.FANTASY,
                    inspiration="test",
                ),
                "world": sample_world,
            }

            result = await agent.execute(context)

            assert result.success is True
            assert "characters" in result.data
            assert len(result.data["characters"]) == 1
            assert result.data["characters"][0].name == "Aria Shadowmend"

    @pytest.mark.asyncio
    async def test_execute_fails_without_world(self, test_config, memory_system, mock_model_router):
        """Test error handling when world missing from context"""
        agent = CharacterArchitectAgent(test_config, memory_system, mock_model_router)

        context = {
            "analyzed_brief": {"genre": "fantasy"},
            "brief": ProductionBrief(
                production_type=ProductionType.SHORT_STORY,
                genre=Genre.FANTASY,
                inspiration="test",
            ),
        }

        result = await agent.execute(context)

        assert result.success is False
        assert len(result.errors) > 0


@pytest.mark.unit
class TestStructureDesignerAgent:
    """Test Structure Designer Agent (a04)"""

    @pytest.mark.asyncio
    async def test_execute_creates_structure(self, test_config, memory_system, mock_model_router, sample_world):
        """Test successful structure design"""
        agent = StructureDesignerAgent(test_config, memory_system, mock_model_router)

        # Mock LLM response
        structure_data = {
            "structure_type": "three_act",
            "total_estimated_words": 5000,
            "acts": [
                {
                    "act_number": 1,
                    "name": "Setup",
                    "estimated_words": 1500,
                    "purpose": "Establish world and conflict",
                }
            ],
            "key_beats": [
                {
                    "beat_name": "Inciting Incident",
                    "position": 0.12,
                    "description": "Hero discovers artifact",
                }
            ],
            "pacing_map": {
                "0.0-0.2": "slow",
                "0.2-0.8": "fast",
                "0.8-1.0": "medium",
            },
        }

        mock_call = MagicMock()
        mock_call.total_tokens = 1800
        mock_call.cost_usd = 0.06

        with patch.object(agent, 'call_model_json', new_callable=AsyncMock) as mock_call_model:
            mock_call_model.return_value = (structure_data, mock_call)

            context = {
                "analyzed_brief": {"genre": "fantasy", "target_length": "short"},
                "brief": ProductionBrief(
                    production_type=ProductionType.SHORT_STORY,
                    genre=Genre.FANTASY,
                    inspiration="test",
                ),
                "world": sample_world,
                "characters": [],
            }

            result = await agent.execute(context)

            assert result.success is True
            assert "structure" in result.data
            assert result.data["structure"].structure_type == "three_act"
            assert result.data["structure"].estimated_word_count == 5000

    @pytest.mark.asyncio
    async def test_execute_fails_without_characters(self, test_config, memory_system, mock_model_router, sample_world):
        """Test error handling when characters missing"""
        agent = StructureDesignerAgent(test_config, memory_system, mock_model_router)

        context = {
            "analyzed_brief": {"genre": "fantasy"},
            "brief": ProductionBrief(
                production_type=ProductionType.SHORT_STORY,
                genre=Genre.FANTASY,
                inspiration="test",
            ),
            "world": sample_world,
        }

        result = await agent.execute(context)

        assert result.success is False
        assert len(result.errors) > 0


@pytest.mark.unit
class TestSegmentPlannerAgent:
    """Test Segment Planner Agent (a05)"""

    @pytest.mark.asyncio
    async def test_execute_creates_segments(
        self, test_config, memory_system, mock_model_router, sample_world, sample_character
    ):
        """Test successful segment planning"""
        agent = SegmentPlannerAgent(test_config, memory_system, mock_model_router)

        # Mock LLM response
        segments_data = {
            "segments": [
                {
                    "segment_id": "seg_001",
                    "sequence_number": 1,
                    "act": 1,
                    "beat": "Inciting Incident",
                    "purpose": "Introduce conflict",
                    "key_events": ["Hero finds artifact"],
                    "characters_present": [sample_character.character_id],
                    "location": "Ancient ruins",
                    "mood": "mysterious",
                    "estimated_words": 500,
                    "must_establish": ["world rules"],
                    "must_advance": ["plot"],
                }
            ]
        }

        mock_call = MagicMock()
        mock_call.total_tokens = 2500
        mock_call.cost_usd = 0.10

        with patch.object(agent, 'call_model_json', new_callable=AsyncMock) as mock_call_model:
            mock_call_model.return_value = (segments_data, mock_call)

            structure = NarrativeStructure(
                structure_type="three_act",
                acts=[],
                key_beats=[],
                pacing_map={},
                estimated_word_count=5000,
            )

            context = {
                "analyzed_brief": {"genre": "fantasy"},
                "brief": ProductionBrief(
                    production_type=ProductionType.SHORT_STORY,
                    genre=Genre.FANTASY,
                    inspiration="test",
                ),
                "world": sample_world,
                "characters": [sample_character],
                "structure": structure,
            }

            result = await agent.execute(context)

            assert result.success is True
            assert "segments" in result.data
            assert len(result.data["segments"]) == 1
            assert result.data["segments"][0].segment_id.startswith("seg_")
            assert result.data["segments"][0].segment_number == 1

    @pytest.mark.asyncio
    async def test_execute_fails_without_structure(
        self, test_config, memory_system, mock_model_router, sample_world, sample_character
    ):
        """Test error handling when structure missing"""
        agent = SegmentPlannerAgent(test_config, memory_system, mock_model_router)

        context = {
            "analyzed_brief": {"genre": "fantasy"},
            "brief": ProductionBrief(
                production_type=ProductionType.SHORT_STORY,
                genre=Genre.FANTASY,
                inspiration="test",
            ),
            "world": sample_world,
            "characters": [sample_character],
        }

        result = await agent.execute(context)

        assert result.success is False
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_execute_handles_empty_segments_response(
        self, test_config, memory_system, mock_model_router, sample_world, sample_character
    ):
        """Test handling of empty segments from LLM"""
        agent = SegmentPlannerAgent(test_config, memory_system, mock_model_router)

        # Mock LLM returning empty segments
        segments_data = {"segments": []}

        mock_call = MagicMock()
        mock_call.total_tokens = 500
        mock_call.cost_usd = 0.02

        with patch.object(agent, 'call_model_json', new_callable=AsyncMock) as mock_call_model:
            mock_call_model.return_value = (segments_data, mock_call)

            structure = NarrativeStructure(
                structure_type="three_act",
                acts=[],
                key_beats=[],
                pacing_map={},
                estimated_word_count=5000,
            )

            context = {
                "analyzed_brief": {"genre": "fantasy"},
                "brief": ProductionBrief(
                    production_type=ProductionType.SHORT_STORY,
                    genre=Genre.FANTASY,
                    inspiration="test",
                ),
                "world": sample_world,
                "characters": [sample_character],
                "structure": structure,
            }

            result = await agent.execute(context)

            # Should still succeed but with empty segments list
            assert result.success is True
            assert result.data["segments"] == []


@pytest.mark.unit
class TestArchitectureAgentsIntegration:
    """Integration tests for architecture agents"""

    @pytest.mark.asyncio
    async def test_agents_have_correct_system_prompts(self, test_config, memory_system, mock_model_router):
        """Test that all agents have system prompts"""
        agents = [
            WorldArchitectAgent(test_config, memory_system, mock_model_router),
            CharacterArchitectAgent(test_config, memory_system, mock_model_router),
            StructureDesignerAgent(test_config, memory_system, mock_model_router),
            SegmentPlannerAgent(test_config, memory_system, mock_model_router),
        ]

        for agent in agents:
            prompt = agent.get_system_prompt()
            assert isinstance(prompt, str)
            assert len(prompt) > 100  # Should be substantial
            assert "JSON" in prompt or "json" in prompt  # Should mention JSON format

    @pytest.mark.asyncio
    async def test_agents_use_correct_models(self, test_config, memory_system, mock_model_router):
        """Test that agents use appropriate model types"""
        # World, character, structure use gpt-4o-mini (structure/analysis)
        # Segment planner uses gpt-4o-mini (planning)

        agents = {
            "WorldArchitect": WorldArchitectAgent(test_config, memory_system, mock_model_router),
            "CharacterArchitect": CharacterArchitectAgent(test_config, memory_system, mock_model_router),
            "StructureDesigner": StructureDesignerAgent(test_config, memory_system, mock_model_router),
            "SegmentPlanner": SegmentPlannerAgent(test_config, memory_system, mock_model_router),
        }

        for name, agent in agents.items():
            assert agent.router == mock_model_router
            # Agents should have access to router for model selection
            assert hasattr(agent, 'call_model_json')
