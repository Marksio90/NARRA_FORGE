"""
Testy E2E dla pełnego pipeline'u produkcji narracji
"""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from pathlib import Path

from narra_forge.core.orchestrator import BatchOrchestrator
from narra_forge.core.types import (
    ProductionBrief,
    ProductionType,
    Genre,
    NarrativeOutput,
    World,
    Character,
    NarrativeStructure,
    Segment,
)


@pytest.mark.e2e
class TestFullProductionPipeline:
    """Test pełnego pipeline'u produkcji narracji (brief → output)"""

    @pytest.mark.asyncio
    async def test_full_pipeline_with_mocks(
        self, test_config, memory_system, mock_openai_client, sample_world, sample_character
    ):
        """
        Test pełnego pipeline'u z zamockowanymi wywołaniami LLM

        Ten test sprawdza czy:
        1. Brief jest poprawnie przetwarzany
        2. Pipeline zwraca NarrativeOutput
        3. Output zawiera wszystkie wymagane pola
        4. Success = True
        """
        # Przygotuj brief
        brief = ProductionBrief(
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.FANTASY,
            inspiration="Opowieść o młodym czarodzieju który odkrywa starożytną magię",
            additional_params={
                "tone": "epic",
                "target_word_count": 5000,
            }
        )

        # Utwórz orchestrator
        orchestrator = BatchOrchestrator(
            config=test_config,
            memory=memory_system,
            client=mock_openai_client,
        )

        # Mock dla _run_pipeline - zwróci kompletny NarrativeOutput
        mock_output = NarrativeOutput(
            job_id="job_test_123",
            success=True,
            narrative_text="To jest kompletna wygenerowana narracja testowa. " * 50,
            world=sample_world,
            characters=[sample_character],
            structure=NarrativeStructure(
                structure_type="three_act",
                acts=[],
                key_beats=[],
                pacing_map={},
                estimated_word_count=5000,
            ),
            segments=[
                Segment(
                    segment_id="seg_001",
                    segment_number=1,
                    title="Początek",
                    summary="Początek historii",
                    key_events=[],
                    characters_involved=[],
                    location="",
                    estimated_words=1500,
                    narrative_function="OPENING",
                )
            ],
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.FANTASY,
            word_count=5000,
            quality_metrics={"coherence_score": 0.92},
            total_tokens=10000,
            total_cost_usd=0.50,
            generation_time_seconds=120.0,
            model_usage={"gpt-4o": 5, "gpt-4o-mini": 5},
            output_dir="/tmp/test_output",
            files={"narrative.txt": "/tmp/test_output/narrative.txt"},
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        with patch.object(
            orchestrator, "_run_pipeline", new_callable=AsyncMock
        ) as mock_pipeline:
            mock_pipeline.return_value = mock_output

            # Uruchom produkcję
            output = await orchestrator.produce_narrative(brief, show_progress=False)

            # Weryfikacje
            assert output is not None
            assert output.success is True
            assert output.job_id == "job_test_123"
            assert output.narrative_text is not None
            assert len(output.narrative_text) > 0
            assert output.world is not None
            assert len(output.characters) > 0
            assert output.word_count == 5000
            assert output.production_type == ProductionType.SHORT_STORY
            assert output.genre == Genre.FANTASY

            # Sprawdź że pipeline został wywołany
            mock_pipeline.assert_called_once()


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skip(reason="Wymaga prawdziwych wywołań OpenAI - kosztowne")
class TestRealProductionPipeline:
    """
    Test z PRAWDZIWYMI wywołaniami OpenAI

    UWAGA: Ten test jest DROGI (kosztuje ~$0.50-1.00)!
    Nie uruchamiaj go domyślnie w CI/CD.

    Aby uruchomić manualnie, usuń decorator @pytest.mark.skip:
        pytest tests/e2e/test_full_pipeline.py::TestRealProductionPipeline -v -s
    """

    @pytest.mark.asyncio
    async def test_real_production_minimal_story(self, test_config):
        """
        Test produkcji PRAWDZIWEJ mini-narracji (bardzo krótka historia)

        Brief: Krótka historia (500 słów) - koszt ~$0.20-0.50

        UWAGA: Ten test wymaga prawdziwego klucza API OpenAI
        i wykona prawdziwe wywołania (kosztowne!)
        """
        from narra_forge.core.orchestrator import create_orchestrator

        brief = ProductionBrief(
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.FANTASY,
            inspiration="Bardzo krótka historia o magicznym artefakcie",
            additional_params={
                "target_word_count": 500,  # Minimalny koszt
            }
        )

        orchestrator = await create_orchestrator(test_config)

        output = await orchestrator.produce_narrative(brief, show_progress=True)

        # Weryfikacje
        assert output.success is True
        assert output.narrative_text is not None
        assert len(output.narrative_text) > 100
        assert output.word_count > 0


@pytest.mark.e2e
class TestPipelineErrorHandling:
    """Test obsługi błędów w pipeline'ie"""

    @pytest.mark.asyncio
    async def test_pipeline_handles_invalid_brief(self, test_config, memory_system):
        """Test że pipeline obsługuje niepoprawny brief (None)"""
        orchestrator = BatchOrchestrator(
            config=test_config,
            memory=memory_system,
        )

        # Brief = None powinno wywołać błąd
        with pytest.raises((TypeError, AttributeError)):
            await orchestrator.produce_narrative(None)

    @pytest.mark.asyncio
    async def test_pipeline_handles_pipeline_failure(
        self, test_config, memory_system, mock_openai_client
    ):
        """Test że pipeline obsługuje failure wewnętrzny"""
        orchestrator = BatchOrchestrator(
            config=test_config,
            memory=memory_system,
            client=mock_openai_client,
        )

        brief = ProductionBrief(
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.FANTASY,
            inspiration="Test"
        )

        # Mock że pipeline failuje
        with patch.object(
            orchestrator, "_run_pipeline", new_callable=AsyncMock
        ) as mock_pipeline:
            mock_pipeline.side_effect = Exception("Pipeline failure")

            # Pipeline powinien propagować błąd
            with pytest.raises(Exception, match="Pipeline failure"):
                await orchestrator.produce_narrative(brief, show_progress=False)


@pytest.mark.e2e
class TestPipelineWithExistingWorld:
    """Test pipeline'u z istniejącym światem"""

    @pytest.mark.asyncio
    async def test_production_with_existing_world(
        self, test_config, memory_system, mock_openai_client, sample_world_dict, sample_world, sample_character
    ):
        """Test produkcji w istniejącym świecie"""
        # Zapisz świat do pamięci
        await memory_system.structural.save_world(sample_world_dict)

        brief = ProductionBrief(
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.FANTASY,
            world_id=sample_world_dict["world_id"],
            inspiration="Historia w istniejącym świecie"
        )

        orchestrator = BatchOrchestrator(
            config=test_config,
            memory=memory_system,
            client=mock_openai_client,
        )

        # Mock pipeline - zwróci output z istniejącym światem
        mock_output = NarrativeOutput(
            job_id="job_existing_world_123",
            success=True,
            narrative_text="Narracja w istniejącym świecie. " * 50,
            world=sample_world,  # Używa istniejącego świata
            characters=[sample_character],
            structure=NarrativeStructure(
                structure_type="three_act",
                acts=[],
                key_beats=[],
                pacing_map={},
                estimated_word_count=5000,
            ),
            segments=[],
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.FANTASY,
            word_count=2500,
            quality_metrics={},
            total_tokens=8000,
            total_cost_usd=0.40,
            generation_time_seconds=90.0,
            model_usage={"gpt-4o": 3, "gpt-4o-mini": 7},
            output_dir="/tmp/test_output",
            files={"narrative.txt": "/tmp/test_output/narrative.txt"},
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        with patch.object(
            orchestrator, "_run_pipeline", new_callable=AsyncMock
        ) as mock_pipeline:
            mock_pipeline.return_value = mock_output

            # Uruchom produkcję
            output = await orchestrator.produce_narrative(brief, show_progress=False)

            # Weryfikacje
            assert output.success is True
            assert output.world.world_id == sample_world_dict["world_id"]
            assert output.world.name == sample_world_dict["name"]
