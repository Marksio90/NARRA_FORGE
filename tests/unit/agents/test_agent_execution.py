"""
Tests for Agent execution methods

Focus on testing the execute() methods and agent logic with mocked LLM calls.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from narra_forge.agents import (
    SequentialGeneratorAgent,
    CoherenceValidatorAgent,
    LanguageStylerAgent,
    EditorialReviewerAgent,
)
from narra_forge.core.types import (
    ModelCall,
    Segment,
    World,
    Character,
    Genre,
    InternalTrajectory,
)


@pytest.fixture
def mock_model_call():
    """Create a mock ModelCall result"""
    return ModelCall(
        call_id="call_test_123",
        model_name="gpt-4o",
        prompt_tokens=100,
        completion_tokens=500,
        total_tokens=600,
        cost_usd=0.05,
        latency_seconds=1.5,
        purpose="test",
        timestamp=datetime.now(),
    )


@pytest.fixture
def sample_world():
    """Create a sample World for testing"""
    return World(
        world_id="test_world_123",
        name="Test Fantasy World",
        genre=Genre.FANTASY,
        reality_laws={"magic": {"exists": True}},
        boundaries={"spatial": {"size": "continent"}},
        anomalies=["magic_storms"],
        core_conflict="Light vs Darkness",
        existential_theme="Power corrupts",
        description="A world of magic and mystery",
        linked_worlds=[],
    )


@pytest.fixture
def sample_character():
    """Create a sample Character for testing"""
    return Character(
        character_id="char_001",
        world_id="test_world_123",
        name="Hero",
        internal_trajectory=InternalTrajectory(
            starting_state={"core_belief": "Justice prevails", "fear": "Failure"},
            potential_arcs=["Hero to villain"],
            triggers=["Betrayal"],
            resistance_points=["Loyalty"],
        ),
        contradictions=["Seeks peace but fights wars"],
        cognitive_limits=["Naive about politics"],
        evolution_capacity=0.8,
        archetype="hero",
        role="protagonist",
    )


@pytest.fixture
def sample_segment():
    """Create a sample Segment"""
    return Segment(
        segment_id="seg_001",
        segment_number=1,
        title="The Discovery",
        summary="Hero discovers their destiny",
        key_events=["Discovery", "First challenge"],
        characters_involved=["Hero"],
        location="Ancient temple",
        estimated_words=1000,
        narrative_function="Setup and inciting incident",
    )


@pytest.mark.unit
class TestSequentialGeneratorExecution:
    """Test SequentialGeneratorAgent execution"""

    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        test_config,
        memory_system,
        mock_model_router,
        sample_world,
        sample_character,
        sample_segment,
        mock_model_call,
    ):
        """Test successful segment generation"""
        agent = SequentialGeneratorAgent(test_config, memory_system, mock_model_router)

        # Mock the router's generate method
        generated_text = "The hero stood at the temple entrance. Shadows danced across ancient stones. This was the beginning."
        with patch.object(
            mock_model_router, "generate", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = (generated_text, mock_model_call)

            # Mock memory operations
            with patch.object(
                memory_system.semantic, "add_event", new_callable=AsyncMock
            ):
                context = {
                    "segments": [sample_segment],
                    "world": sample_world,
                    "characters": [sample_character],
                    "structure": {"type": "three_act"},
                }

                result = await agent.execute(context)

        assert result.success is True
        assert "narrative_text" in result.data
        assert "generated_segments" in result.data
        assert result.data["segments_count"] == 1
        assert len(agent.model_calls) == 1

    @pytest.mark.asyncio
    async def test_execute_missing_segments(
        self, test_config, memory_system, mock_model_router, sample_world
    ):
        """Test execution with missing segments"""
        agent = SequentialGeneratorAgent(test_config, memory_system, mock_model_router)

        context = {
            "segments": [],  # Empty!
            "world": sample_world,
        }

        result = await agent.execute(context)

        assert result.success is False
        assert len(agent.errors) > 0
        assert "segments" in agent.errors[0].lower() or "world" in agent.errors[0].lower()

    @pytest.mark.asyncio
    async def test_execute_missing_world(
        self, test_config, memory_system, mock_model_router, sample_segment
    ):
        """Test execution with missing world"""
        agent = SequentialGeneratorAgent(test_config, memory_system, mock_model_router)

        context = {
            "segments": [sample_segment],
            "world": None,  # Missing!
        }

        result = await agent.execute(context)

        assert result.success is False
        assert len(agent.errors) > 0

    @pytest.mark.asyncio
    async def test_execute_multiple_segments(
        self,
        test_config,
        memory_system,
        mock_model_router,
        sample_world,
        sample_character,
        mock_model_call,
    ):
        """Test generation of multiple segments"""
        agent = SequentialGeneratorAgent(test_config, memory_system, mock_model_router)

        segment1 = Segment(
            segment_id="seg_001",
            segment_number=1,
            title="Beginning",
            summary="Beginning",
            key_events=["Event 1"],
            characters_involved=["Hero"],
            location="Temple",
            narrative_function="Setup",
            estimated_words=500,
        )

        segment2 = Segment(
            segment_id="seg_002",
            segment_number=2,
            title="Middle",
            summary="Middle",
            key_events=["Event 2"],
            characters_involved=["Hero"],
            location="Forest",
            narrative_function="Conflict",
            estimated_words=500,
        )

        with patch.object(
            mock_model_router, "generate", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = ("Generated segment text.", mock_model_call)

            with patch.object(
                memory_system.semantic, "add_event", new_callable=AsyncMock
            ):
                context = {
                    "segments": [segment1, segment2],
                    "world": sample_world,
                    "characters": [sample_character],
                }

                result = await agent.execute(context)

        assert result.success is True
        assert result.data["segments_count"] == 2
        assert len(agent.model_calls) == 2
        # Two segments should be joined with double newline
        assert "\n\n" in result.data["narrative_text"]

    @pytest.mark.asyncio
    async def test_execute_generation_error(
        self,
        test_config,
        memory_system,
        mock_model_router,
        sample_world,
        sample_segment,
    ):
        """Test handling of generation errors"""
        agent = SequentialGeneratorAgent(test_config, memory_system, mock_model_router)

        with patch.object(
            mock_model_router, "generate", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.side_effect = Exception("API Error")

            context = {
                "segments": [sample_segment],
                "world": sample_world,
                "characters": [],
            }

            result = await agent.execute(context)

        assert result.success is False
        assert len(agent.errors) > 0
        assert "Failed to generate segment" in agent.errors[0]


@pytest.mark.unit
class TestCoherenceValidatorExecution:
    """Test CoherenceValidatorAgent execution"""

    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        test_config,
        memory_system,
        mock_model_router,
        sample_world,
        mock_model_call,
    ):
        """Test successful coherence validation"""
        agent = CoherenceValidatorAgent(test_config, memory_system, mock_model_router)

        validation_response = {
            "coherence_score": 0.92,
            "logical_consistency": True,
            "psychological_consistency": True,
            "temporal_consistency": True,
            "issues": [],
            "warnings": [],
        }

        with patch.object(
            mock_model_router, "generate_json", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = (validation_response, mock_model_call)

            context = {
                "narrative_text": "The hero's journey began with a simple choice.",
                "world": sample_world,
                "characters": [],
                "structure": {},
            }

            result = await agent.execute(context)

        assert result.success is True
        assert "coherence_score" in result.data
        assert result.data["coherence_score"] >= 0.9

    @pytest.mark.asyncio
    async def test_execute_low_coherence(
        self,
        test_config,
        memory_system,
        mock_model_router,
        sample_world,
        mock_model_call,
    ):
        """Test handling of low coherence score"""
        agent = CoherenceValidatorAgent(test_config, memory_system, mock_model_router)

        validation_response = {
            "coherence_score": 0.65,
            "logical_consistency": False,
            "psychological_consistency": True,
            "temporal_consistency": True,
            "issues": [
                {"description": "Plot hole in chapter 2", "severity": "major"},
                {"description": "Character inconsistency", "severity": "minor"}
            ],
            "warnings": ["Review timeline"],
        }

        with patch.object(
            mock_model_router, "generate_json", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = (validation_response, mock_model_call)

            context = {
                "narrative_text": "Some narrative text.",
                "world": sample_world,
                "characters": [],
                "structure": {},
            }

            result = await agent.execute(context)

        # Low coherence should be reflected in results
        assert "coherence_score" in result.data
        assert result.data["coherence_score"] < 0.9


@pytest.mark.unit
class TestLanguageStylerExecution:
    """Test LanguageStylerAgent execution"""

    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        test_config,
        memory_system,
        mock_model_router,
        mock_model_call,
    ):
        """Test successful language styling"""
        agent = LanguageStylerAgent(test_config, memory_system, mock_model_router)

        original_text = "The hero walked slowly. He was sad."
        styled_text = "The hero trudged forward. Shoulders sagged under invisible weight."

        with patch.object(
            mock_model_router, "generate", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = (styled_text, mock_model_call)

            context = {
                "narrative_text": original_text,
                "additional_params": {"tone": "dark"},
            }

            result = await agent.execute(context)

        assert result.success is True
        assert "stylized_text" in result.data
        assert result.data["stylized_text"] == styled_text

    @pytest.mark.asyncio
    async def test_execute_missing_narrative(
        self, test_config, memory_system, mock_model_router
    ):
        """Test execution with missing narrative text"""
        agent = LanguageStylerAgent(test_config, memory_system, mock_model_router)

        context = {}  # No narrative_text!

        result = await agent.execute(context)

        assert result.success is False
        assert len(agent.errors) > 0


@pytest.mark.unit
class TestEditorialReviewerExecution:
    """Test EditorialReviewerAgent execution"""

    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        test_config,
        memory_system,
        mock_model_router,
        mock_model_call,
    ):
        """Test successful editorial review"""
        agent = EditorialReviewerAgent(test_config, memory_system, mock_model_router)

        review_response = {
            "editorial_score": 0.85,
            "ready_for_publication": True,
            "issues_found": [],
            "strengths": ["Strong prose", "Engaging characters"],
            "weaknesses": [],
            "recommendations": [],
        }

        with patch.object(
            mock_model_router, "generate_json", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = (review_response, mock_model_call)

            # Mock the quality analysis function
            with patch("narra_forge.agents.a09_editorial_reviewer.analyze_text_quality") as mock_quality:
                mock_quality.return_value = {
                    "cliches": [],
                    "repetitions": {
                        "high_risk": [],
                        "moderate": [],
                        "low": [],
                        "warnings": []
                    },
                    "quality_score": 0.9,
                }

                context = {
                    "narrative_text": "Complete narrative text here.",
                }

                result = await agent.execute(context)

        assert result.success is True
        assert "editorial_score" in result.data
        assert result.data["editorial_score"] >= 0.8

    @pytest.mark.asyncio
    async def test_execute_quality_check(
        self,
        test_config,
        memory_system,
        mock_model_router,
        mock_model_call,
    ):
        """Test quality threshold checking"""
        agent = EditorialReviewerAgent(test_config, memory_system, mock_model_router)

        # Low quality review
        review_response = {
            "editorial_score": 0.50,
            "ready_for_publication": False,
            "issues_found": [
                {"description": "Poor prose", "severity": "major"},
                {"description": "Weak characters", "severity": "critical"}
            ],
            "strengths": ["Basic structure"],
            "weaknesses": ["Poor prose", "Weak characters", "No tension"],
            "recommendations": ["Major rewrite needed"],
        }

        with patch.object(
            mock_model_router, "generate_json", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = (review_response, mock_model_call)

            # Mock the quality analysis function
            with patch("narra_forge.agents.a09_editorial_reviewer.analyze_text_quality") as mock_quality:
                mock_quality.return_value = {
                    "cliches": [
                        {"cliche": "serce waliło", "count": 3, "locations": [10, 25, 40]}
                    ],
                    "repetitions": {
                        "high_risk": [{"word": "wiedział", "count": 5}],
                        "moderate": [],
                        "low": [],
                        "warnings": ["High repetition of 'wiedział'"]
                    },
                    "quality_score": 0.4,
                }

                context = {
                    "narrative_text": "Low quality text.",
                }

                result = await agent.execute(context)

        # Should reflect low quality in results
        assert "editorial_score" in result.data
        assert result.data["editorial_score"] < 0.8
        assert result.success is False  # Should fail quality check


@pytest.mark.unit
class TestAgentContextBuilding:
    """Test agent context building methods"""

    @pytest.mark.asyncio
    async def test_sequential_generator_builds_context(
        self,
        test_config,
        memory_system,
        mock_model_router,
        sample_world,
        sample_character,
        sample_segment,
    ):
        """Test that SequentialGenerator builds proper context"""
        agent = SequentialGeneratorAgent(test_config, memory_system, mock_model_router)

        context_str = agent._build_segment_context(
            segment=sample_segment,
            world=sample_world,
            characters=[sample_character],
            previous_segments=[],
        )

        # Context should include world info
        assert sample_world.name in context_str
        assert sample_world.core_conflict in context_str

        # Should include character info if involved
        if sample_character.name in sample_segment.characters_involved:
            assert sample_character.name in context_str

    @pytest.mark.asyncio
    async def test_sequential_generator_includes_previous_segments(
        self,
        test_config,
        memory_system,
        mock_model_router,
        sample_world,
        sample_segment,
        mock_model_call,
    ):
        """Test that previous segments are included in context"""
        from narra_forge.core.types import GeneratedSegment

        agent = SequentialGeneratorAgent(test_config, memory_system, mock_model_router)

        # Create a previous segment
        prev_segment = GeneratedSegment(
            segment=sample_segment,
            text="Previous segment text",
            word_count=100,
            tokens_used=500,
            cost_usd=0.01,
            generation_time_seconds=2.0,
        )

        segment2 = Segment(
            segment_id="seg_002",
            segment_number=2,
            title="Second Segment",
            summary="Second segment",
            key_events=["Event"],
            characters_involved=["Hero"],
            location="Forest",
            narrative_function="Development",
            estimated_words=1000,
        )

        context_str = agent._build_segment_context(
            segment=segment2,
            world=sample_world,
            characters=[],
            previous_segments=[prev_segment],
        )

        # Should mention what happened earlier
        assert "WCZEŚNIEJ" in context_str or sample_segment.summary in context_str
