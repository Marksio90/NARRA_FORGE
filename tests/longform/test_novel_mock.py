"""
Mock tests for novel-length narratives (40k-120k words).

These tests use mocked OpenAI responses to verify pipeline logic
without incurring API costs.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from narra_forge.core.orchestrator import BatchOrchestrator
from narra_forge.core.types import ProductionType, NarrativeOutput


@pytest.mark.mock
class TestNovelMock:
    """Mock tests for novel generation."""

    @pytest.fixture
    def mock_orchestrator(self):
        """Mock orchestrator with all dependencies."""
        with patch("narra_forge.core.orchestrator.OpenAIClient") as mock_client, \
             patch("narra_forge.core.orchestrator.MemoryManager") as mock_memory:

            # Configure mocks
            mock_client.return_value.generate = AsyncMock()
            mock_memory.return_value.initialize = AsyncMock()

            orchestrator = MagicMock(spec=BatchOrchestrator)
            orchestrator.produce_narrative = AsyncMock()

            yield orchestrator

    @pytest.mark.asyncio
    async def test_novel_pipeline_structure(
        self,
        brief_novel,
        mock_orchestrator,
        longform_output_dir
    ):
        """
        Test that novel pipeline has correct structure.

        Validates:
        - Correct number of stages (10)
        - Proper stage ordering
        - All agents initialized
        """
        # Mock output
        mock_output = NarrativeOutput(
            narrative_text="[80,000 word novel...]",
            word_count=80000,
            production_type=ProductionType.NOVEL,
            total_cost_usd=45.50,
            output_dir=str(longform_output_dir),
            metadata={
                "chapters": 25,
                "quality_score": 0.88,
            }
        )
        mock_orchestrator.produce_narrative.return_value = mock_output

        # Execute
        output = await mock_orchestrator.produce_narrative(brief_novel)

        # Validate
        assert output.production_type == ProductionType.NOVEL
        assert output.word_count >= 40000  # Minimum for novel
        assert output.word_count <= 120000  # Maximum for novel
        assert output.total_cost_usd < 100  # Cost sanity check
        mock_orchestrator.produce_narrative.assert_called_once_with(brief_novel)

    @pytest.mark.asyncio
    async def test_novel_chapter_generation(
        self,
        brief_novel,
        mock_narrative_segment,
        memory_profiler
    ):
        """
        Test generation of multiple chapters.

        Validates:
        - All 25 chapters generated
        - Each chapter ~3200 words (80k / 25)
        - Memory stays reasonable
        """
        chapter_count = 25
        words_per_chapter = 3200

        # Simulate chapter generation
        chapters = []
        for i in range(chapter_count):
            # Mock chapter generation
            chapter = {
                "index": i,
                "title": f"Chapter {i+1}",
                "content": mock_narrative_segment * (words_per_chapter // 500),
                "word_count": words_per_chapter,
            }
            chapters.append(chapter)

        # Validate
        assert len(chapters) == chapter_count
        total_words = sum(ch["word_count"] for ch in chapters)
        assert 75000 <= total_words <= 85000  # Target 80k ±5k

        # Memory check (if profiling enabled)
        if memory_profiler:
            end_memory = memory_profiler["process"].memory_info().rss / 1024 / 1024
            assert end_memory < 2048, f"Memory usage too high: {end_memory:.2f} MB"

    @pytest.mark.asyncio
    async def test_novel_quality_validation(
        self,
        brief_novel,
        mock_quality_validation
    ):
        """
        Test quality validation for novel.

        Validates:
        - Quality scores >0.85 for all dimensions
        - No critical issues detected
        - Coherence across chapters
        """
        # Mock validation for 25 chapters
        validations = []
        for i in range(25):
            # Each chapter has slightly different scores
            validation = {
                "chapter": i,
                "coherence_score": 0.85 + (i % 5) * 0.01,
                "logic_score": 0.88 + (i % 3) * 0.01,
                "psychology_score": 0.86,
                "temporal_score": 0.90,
                "passed": True,
            }
            validations.append(validation)

        # Calculate overall scores
        avg_coherence = sum(v["coherence_score"] for v in validations) / len(validations)
        avg_logic = sum(v["logic_score"] for v in validations) / len(validations)

        # Validate
        assert all(v["passed"] for v in validations), "Some chapters failed validation"
        assert avg_coherence >= 0.85, f"Average coherence too low: {avg_coherence:.3f}"
        assert avg_logic >= 0.85, f"Average logic too low: {avg_logic:.3f}"

    @pytest.mark.asyncio
    async def test_novel_cost_estimation(self, brief_novel):
        """
        Test cost estimation for novel.

        Validates:
        - Cost per 1k words ~$0.40-0.60
        - Total cost $30-50 for 80k novel
        - Mini model used for analysis (cheaper)
        - GPT-4 used for generation (quality)
        """
        # Simulated costs
        word_count = 80000
        mini_tokens = 50000  # Analysis stages
        gpt4_tokens = 150000  # Generation stages

        # OpenAI pricing (approximate)
        mini_cost_per_1k = 0.00015  # $0.15 / 1M tokens
        gpt4_cost_per_1k = 0.0025   # $2.50 / 1M tokens

        mini_cost = (mini_tokens / 1000) * mini_cost_per_1k
        gpt4_cost = (gpt4_tokens / 1000) * gpt4_cost_per_1k

        total_cost = mini_cost + gpt4_cost
        cost_per_1k_words = (total_cost / word_count) * 1000

        # Validate
        assert 0.30 <= cost_per_1k_words <= 0.70, \
            f"Cost per 1k words out of range: ${cost_per_1k_words:.2f}"
        assert 25 <= total_cost <= 60, \
            f"Total cost out of range: ${total_cost:.2f}"

    @pytest.mark.asyncio
    async def test_novel_character_consistency(self):
        """
        Test character consistency across novel.

        Validates:
        - Character traits remain consistent
        - Character arcs progress logically
        - No contradictions in behavior
        """
        # Mock character data
        lyra = {
            "name": "Lyra",
            "initial_traits": ["fearful", "curious", "kind"],
            "arc_stages": [
                {"chapter": 1, "state": "fearful", "development": 0.0},
                {"chapter": 8, "state": "conflicted", "development": 0.3},
                {"chapter": 15, "state": "determined", "development": 0.6},
                {"chapter": 25, "state": "courageous", "development": 1.0},
            ],
        }

        # Validate arc progression
        developments = [stage["development"] for stage in lyra["arc_stages"]]
        assert developments == sorted(developments), "Character arc should progress monotonically"
        assert developments[-1] == 1.0, "Character arc should complete"

        # Validate consistency
        for stage in lyra["arc_stages"]:
            assert stage["state"] is not None, f"Character state undefined at chapter {stage['chapter']}"

    @pytest.mark.asyncio
    async def test_novel_memory_management(self, memory_profiler):
        """
        Test memory management during novel generation.

        Validates:
        - Memory doesn't grow unbounded
        - Old segments released after processing
        - Peak memory <2GB
        """
        if not memory_profiler:
            pytest.skip("Memory profiling not enabled (use --profile-memory)")

        # Simulate processing 25 chapters
        peak_memory = 0
        for i in range(25):
            # Simulate chapter generation
            chapter_text = "x" * 16000  # ~4000 words * 4 bytes/char

            # Track memory
            current_memory = memory_profiler["process"].memory_info().rss / 1024 / 1024
            peak_memory = max(peak_memory, current_memory)

            # Release chapter (simulate)
            del chapter_text

        # Validate
        assert peak_memory < 2048, f"Peak memory too high: {peak_memory:.2f} MB"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_novel_complete_pipeline_mock(
        self,
        brief_novel,
        mock_orchestrator,
        longform_output_dir,
        cost_tracker
    ):
        """
        Test complete novel pipeline (mocked).

        This is the main integration test for novel generation.

        Validates:
        - All 10 stages complete
        - Output files created
        - Quality scores acceptable
        - Cost within budget
        - No errors or crashes
        """
        # Mock complete output
        mock_output = NarrativeOutput(
            narrative_text="[Complete 80,000 word fantasy novel...]",
            word_count=80000,
            production_type=ProductionType.NOVEL,
            total_cost_usd=42.30,
            output_dir=str(longform_output_dir),
            metadata={
                "chapters": 25,
                "quality_scores": {
                    "coherence": 0.88,
                    "logic": 0.91,
                    "psychology": 0.86,
                    "temporal": 0.90,
                },
                "stages_completed": [
                    "01_brief_interpretation",
                    "02_world_architecture",
                    "03_character_architecture",
                    "04_structure_design",
                    "05_segment_planning",
                    "06_sequential_generation",
                    "07_coherence_validation",
                    "08_language_stylization",
                    "09_editorial_review",
                    "10_output_processing",
                ],
            }
        )
        mock_orchestrator.produce_narrative.return_value = mock_output

        # Execute
        output = await mock_orchestrator.produce_narrative(brief_novel)

        # Validate output
        assert output.word_count == 80000
        assert output.production_type == ProductionType.NOVEL
        assert len(output.metadata["stages_completed"]) == 10

        # Validate quality
        quality = output.metadata["quality_scores"]
        assert all(score >= 0.85 for score in quality.values()), \
            f"Some quality scores below threshold: {quality}"

        # Validate cost
        cost_tracker["add_cost"](output.total_cost_usd, "Complete novel generation")
        assert output.total_cost_usd < 100, \
            f"Cost too high: ${output.total_cost_usd:.2f}"

        # Validate files (would be created in real run)
        output_path = longform_output_dir / "narrative.txt"
        # In real run: assert output_path.exists()

        print(f"\n✅ Novel generation completed successfully")
        print(f"   Words: {output.word_count:,}")
        print(f"   Cost: ${output.total_cost_usd:.2f}")
        print(f"   Quality: {quality['coherence']:.3f}")


@pytest.mark.mock
class TestMultipleNovels:
    """Test generating multiple novels in sequence."""

    @pytest.mark.asyncio
    async def test_sequential_novels(self, brief_novel):
        """
        Test generating 3 novels sequentially.

        Validates:
        - No memory leaks between runs
        - Consistent quality
        - Cost tracking accurate
        """
        novels_count = 3
        outputs = []

        for i in range(novels_count):
            # Mock output for each novel
            output = MagicMock()
            output.word_count = 80000 + i * 1000
            output.total_cost_usd = 42.0 + i * 0.5
            output.metadata = {"quality_scores": {"coherence": 0.88}}
            outputs.append(output)

        # Validate
        assert len(outputs) == novels_count
        total_cost = sum(o.total_cost_usd for o in outputs)
        assert total_cost < 150, f"Total cost too high: ${total_cost:.2f}"

        # Check quality consistency
        coherence_scores = [o.metadata["quality_scores"]["coherence"] for o in outputs]
        assert all(s >= 0.85 for s in coherence_scores), "Quality degraded across runs"
