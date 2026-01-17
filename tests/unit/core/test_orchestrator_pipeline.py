"""
Tests for BatchOrchestrator pipeline execution

Tests the actual _run_pipeline, _execute_stage, _build_output methods
that were previously untested (coverage: 36.68% → 70%+)
"""
import pytest
import time
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch, call
from pathlib import Path

from narra_forge.core.orchestrator import BatchOrchestrator
from narra_forge.core.types import (
    ProductionBrief,
    ProductionType,
    Genre,
    ProductionJob,
    JobStatus,
    PipelineStage,
    NarrativeOutput,
    NarrativeStructure,
    CoherenceValidation,
    AgentResult,
)


@pytest.mark.unit
class TestOrchestratorRunPipeline:
    """Test _run_pipeline method"""

    @pytest.mark.asyncio
    async def test_run_pipeline_executes_all_10_stages(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test that _run_pipeline executes all 10 stages"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_test_123",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        # Mock _execute_stage to avoid real agent calls
        with patch.object(orchestrator, '_execute_stage', new_callable=AsyncMock) as mock_execute:
            with patch.object(orchestrator, '_save_job', new_callable=AsyncMock):
                with patch.object(orchestrator, '_build_output', new_callable=AsyncMock) as mock_build:
                    mock_build.return_value = MagicMock()

                    output = await orchestrator._run_pipeline(job, show_progress=False)

                    # Verify all 10 stages were executed
                    assert mock_execute.call_count == 10

                    # Verify stages are in correct order
                    expected_stages = [
                        PipelineStage.BRIEF_INTERPRETATION,
                        PipelineStage.WORLD_ARCHITECTURE,
                        PipelineStage.CHARACTER_ARCHITECTURE,
                        PipelineStage.STRUCTURE_DESIGN,
                        PipelineStage.SEGMENT_PLANNING,
                        PipelineStage.SEQUENTIAL_GENERATION,
                        PipelineStage.COHERENCE_VALIDATION,
                        PipelineStage.LANGUAGE_STYLIZATION,
                        PipelineStage.EDITORIAL_REVIEW,
                        PipelineStage.OUTPUT_PROCESSING,
                    ]

                    for i, expected_stage in enumerate(expected_stages):
                        assert mock_execute.call_args_list[i][0][1] == expected_stage

    @pytest.mark.asyncio
    async def test_run_pipeline_updates_job_stages_completed(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test that completed stages are tracked in job"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_test_456",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        with patch.object(orchestrator, '_execute_stage', new_callable=AsyncMock):
            with patch.object(orchestrator, '_save_job', new_callable=AsyncMock):
                with patch.object(orchestrator, '_build_output', new_callable=AsyncMock) as mock_build:
                    mock_build.return_value = MagicMock()

                    await orchestrator._run_pipeline(job, show_progress=False)

                    # All 10 stages should be marked completed
                    assert len(job.stages_completed) == 10

    @pytest.mark.asyncio
    async def test_run_pipeline_checks_cost_limit(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test that pipeline enforces cost limit"""
        test_config.max_cost_per_job = 1.0  # Set low limit
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_test_789",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        # Mock execute_stage to increase cost above limit
        async def mock_execute_expensive(job, stage):
            job.cost_usd += 0.5  # Each stage costs $0.50

        with patch.object(orchestrator, '_execute_stage', side_effect=mock_execute_expensive):
            with patch.object(orchestrator, '_save_job', new_callable=AsyncMock):
                with pytest.raises(ValueError, match="Cost limit exceeded"):
                    await orchestrator._run_pipeline(job, show_progress=False)

    @pytest.mark.asyncio
    async def test_run_pipeline_with_progress_display(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test pipeline with progress display enabled"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_progress_123",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        with patch.object(orchestrator, '_execute_stage', new_callable=AsyncMock):
            with patch.object(orchestrator, '_save_job', new_callable=AsyncMock):
                with patch.object(orchestrator, '_build_output', new_callable=AsyncMock) as mock_build:
                    mock_build.return_value = MagicMock()

                    with patch('narra_forge.core.orchestrator.console') as mock_console:
                        await orchestrator._run_pipeline(job, show_progress=True)

                        # Verify progress was displayed
                        assert mock_console.print.call_count > 10  # At least one per stage


@pytest.mark.unit
class TestOrchestratorExecuteStage:
    """Test _execute_stage method for each stage type"""

    @pytest.mark.asyncio
    async def test_execute_stage_brief_interpretation(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test executing BRIEF_INTERPRETATION stage"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_brief_123",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        # Mock the agent
        with patch('narra_forge.core.orchestrator.BriefInterpreterAgent') as MockAgent:
            mock_agent = AsyncMock()
            mock_agent.run.return_value = AgentResult(
                agent_name="BriefInterpreterAgent",
                stage=PipelineStage.BRIEF_INTERPRETATION,
                success=True,
                data={"analyzed_brief": {"theme": "adventure"}},
                model_calls=[],
            )
            MockAgent.return_value = mock_agent

            await orchestrator._execute_stage(job, PipelineStage.BRIEF_INTERPRETATION)

            # Verify analyzed_brief was set
            assert hasattr(job, '_analyzed_brief')
            assert job._analyzed_brief == {"theme": "adventure"}

    @pytest.mark.asyncio
    async def test_execute_stage_world_architecture(
        self, test_config, memory_system, sample_production_brief, sample_world
    ):
        """Test executing WORLD_ARCHITECTURE stage"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_world_123",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        with patch('narra_forge.core.orchestrator.WorldArchitectAgent') as MockAgent:
            mock_agent = AsyncMock()
            mock_agent.run.return_value = AgentResult(
                agent_name="WorldArchitectAgent",
                stage=PipelineStage.WORLD_ARCHITECTURE,
                success=True,
                data={"world": sample_world},
                model_calls=[],
            )
            MockAgent.return_value = mock_agent

            await orchestrator._execute_stage(job, PipelineStage.WORLD_ARCHITECTURE)

            assert job.world == sample_world

    @pytest.mark.asyncio
    async def test_execute_stage_character_architecture(
        self, test_config, memory_system, sample_production_brief, sample_character
    ):
        """Test executing CHARACTER_ARCHITECTURE stage"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_char_123",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        with patch('narra_forge.core.orchestrator.CharacterArchitectAgent') as MockAgent:
            mock_agent = AsyncMock()
            mock_agent.run.return_value = AgentResult(
                agent_name="CharacterArchitectAgent",
                stage=PipelineStage.CHARACTER_ARCHITECTURE,
                success=True,
                data={"characters": [sample_character]},
                model_calls=[],
            )
            MockAgent.return_value = mock_agent

            await orchestrator._execute_stage(job, PipelineStage.CHARACTER_ARCHITECTURE)

            assert len(job.characters) == 1
            assert job.characters[0] == sample_character

    @pytest.mark.asyncio
    async def test_execute_stage_structure_design(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test executing STRUCTURE_DESIGN stage"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_struct_123",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        structure = NarrativeStructure(
            structure_type="three_act",
            acts=[],
            key_beats=[],
            pacing_map={},
            estimated_word_count=5000,
        )

        with patch('narra_forge.core.orchestrator.StructureDesignerAgent') as MockAgent:
            mock_agent = AsyncMock()
            mock_agent.run.return_value = AgentResult(
                agent_name="StructureDesignerAgent",
                stage=PipelineStage.STRUCTURE_DESIGN,
                success=True,
                data={"structure": structure},
                model_calls=[],
            )
            MockAgent.return_value = mock_agent

            await orchestrator._execute_stage(job, PipelineStage.STRUCTURE_DESIGN)

            assert job.structure == structure

    @pytest.mark.asyncio
    async def test_execute_stage_sequential_generation(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test executing SEQUENTIAL_GENERATION stage"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_gen_123",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        with patch('narra_forge.core.orchestrator.SequentialGeneratorAgent') as MockAgent:
            mock_agent = AsyncMock()
            mock_agent.run.return_value = AgentResult(
                agent_name="SequentialGeneratorAgent",
                stage=PipelineStage.SEQUENTIAL_GENERATION,
                success=True,
                data={"narrative_text": "This is the generated narrative text."},
                model_calls=[],
            )
            MockAgent.return_value = mock_agent

            await orchestrator._execute_stage(job, PipelineStage.SEQUENTIAL_GENERATION)

            assert hasattr(job, '_narrative_text')
            assert job._narrative_text == "This is the generated narrative text."

    @pytest.mark.asyncio
    async def test_execute_stage_coherence_validation(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test executing COHERENCE_VALIDATION stage (non-blocking)"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_val_123",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        validation = CoherenceValidation(
            passed=True,
            coherence_score=0.92,
            logical_consistency=True,
            psychological_consistency=True,
            temporal_consistency=True,
            issues=[],
            warnings=[],
        )

        with patch('narra_forge.core.orchestrator.CoherenceValidatorAgent') as MockAgent:
            mock_agent = AsyncMock()
            mock_agent.run.return_value = AgentResult(
                agent_name="CoherenceValidatorAgent",
                stage=PipelineStage.COHERENCE_VALIDATION,
                success=True,
                data={"validation": validation},
                warnings=["Minor issue detected"],
                model_calls=[],
            )
            MockAgent.return_value = mock_agent

            with patch('narra_forge.core.orchestrator.console'):
                await orchestrator._execute_stage(job, PipelineStage.COHERENCE_VALIDATION)

            assert hasattr(job, '_validation_result')
            assert job._validation_result == validation

    @pytest.mark.asyncio
    async def test_execute_stage_tracks_costs(
        self, test_config, memory_system, sample_production_brief
    ):
        """Test that _execute_stage tracks token usage and costs"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_cost_123",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        # Create mock model call with costs
        mock_model_call = MagicMock()
        mock_model_call.total_tokens = 1000
        mock_model_call.cost_usd = 0.05

        with patch('narra_forge.core.orchestrator.BriefInterpreterAgent') as MockAgent:
            mock_agent = AsyncMock()
            result = AgentResult(
                agent_name="BriefInterpreterAgent",
                stage=PipelineStage.BRIEF_INTERPRETATION,
                success=True,
                data={"analyzed_brief": {}},
                model_calls=[mock_model_call],
            )
            result.model_calls = [mock_model_call]  # Ensure attribute exists
            mock_agent.run.return_value = result
            MockAgent.return_value = mock_agent

            initial_tokens = job.tokens_used
            initial_cost = job.cost_usd

            await orchestrator._execute_stage(job, PipelineStage.BRIEF_INTERPRETATION)

            # Verify costs were aggregated
            assert job.tokens_used == initial_tokens + 1000
            assert job.cost_usd == initial_cost + 0.05


@pytest.mark.unit
class TestOrchestratorBuildOutput:
    """Test _build_output method"""

    @pytest.mark.asyncio
    async def test_build_output_uses_existing_output(
        self, test_config, memory_system, sample_production_brief, sample_world
    ):
        """Test that _build_output uses job.output if already set"""
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_output_123",
            brief=sample_production_brief,
            status=JobStatus.COMPLETED,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        existing_output = NarrativeOutput(
            job_id=job.job_id,
            success=True,
            narrative_text="Existing narrative",
            world=sample_world,
            characters=[],
            structure=None,
            segments=[],
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.FANTASY,
            word_count=1000,
            quality_metrics={},
            total_tokens=5000,
            total_cost_usd=0.25,
            generation_time_seconds=0.0,  # Will be updated
            model_usage={},
            output_dir="/tmp/test",
            files={},
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        job.output = existing_output

        result = await orchestrator._build_output(job, total_time=120.5)

        # Should return the existing output with updated time
        assert result == existing_output
        assert result.generation_time_seconds == 120.5

    @pytest.mark.asyncio
    async def test_build_output_fallback_creates_minimal_output(
        self, test_config, memory_system, sample_production_brief, sample_world, tmp_path
    ):
        """Test _build_output creates minimal output when job.output is None"""
        test_config.output_dir = tmp_path
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_fallback_123",
            brief=sample_production_brief,
            status=JobStatus.COMPLETED,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        job.world = sample_world
        job._final_text = "This is the final narrative text."
        job.tokens_used = 8000
        job.cost_usd = 0.40

        result = await orchestrator._build_output(job, total_time=150.0)

        # Verify minimal output was created
        assert result.job_id == "job_fallback_123"
        assert result.success is True
        assert result.narrative_text == "This is the final narrative text."
        assert result.world == sample_world
        assert result.total_tokens == 8000
        assert result.total_cost_usd == 0.40
        assert result.generation_time_seconds == 150.0

        # Verify file was written
        output_dir = tmp_path / "job_fallback_123"
        narrative_file = output_dir / "narrative.txt"
        assert narrative_file.exists()
        assert narrative_file.read_text(encoding="utf-8") == "This is the final narrative text."

    @pytest.mark.asyncio
    async def test_build_output_fallback_with_validation_metrics(
        self, test_config, memory_system, sample_production_brief, tmp_path
    ):
        """Test _build_output includes quality metrics from validation"""
        test_config.output_dir = tmp_path
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_metrics_123",
            brief=sample_production_brief,
            status=JobStatus.COMPLETED,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        validation = CoherenceValidation(
            passed=True,
            coherence_score=0.95,
            logical_consistency=True,
            psychological_consistency=True,
            temporal_consistency=False,
            issues=["Minor timeline issue"],
            warnings=[],
        )

        job._validation_result = validation
        job._narrative_text = "Test narrative"

        result = await orchestrator._build_output(job, total_time=100.0)

        # Verify quality metrics were included
        assert result.quality_metrics["coherence_score"] == 0.95
        assert result.quality_metrics["logical_consistency"] is True
        assert result.quality_metrics["temporal_consistency"] is False
        assert result.quality_metrics["issues_count"] == 1

    @pytest.mark.asyncio
    async def test_build_output_fallback_without_narrative(
        self, test_config, memory_system, sample_production_brief, tmp_path
    ):
        """Test _build_output handles missing narrative text"""
        test_config.output_dir = tmp_path
        orchestrator = BatchOrchestrator(config=test_config, memory=memory_system)

        job = ProductionJob(
            job_id="job_empty_123",
            brief=sample_production_brief,
            status=JobStatus.FAILED,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        # No narrative text set

        result = await orchestrator._build_output(job, total_time=50.0)

        # Should create output with empty/incomplete narrative
        assert result.success is False
        assert result.narrative_text == ""
        assert result.word_count == 0

        # Verify fallback file was written
        output_dir = tmp_path / "job_empty_123"
        narrative_file = output_dir / "narrative.txt"
        assert narrative_file.exists()
        assert "Production incomplete" in narrative_file.read_text(encoding="utf-8")


@pytest.mark.unit
class TestOrchestratorPrintSummary:
    """Test _print_summary method"""

    def test_print_summary_with_quality_metrics(
        self, test_config, sample_world
    ):
        """Test _print_summary displays quality metrics"""
        orchestrator = BatchOrchestrator(config=test_config)

        output = NarrativeOutput(
            job_id="job_summary_123",
            success=True,
            narrative_text="Test narrative",
            world=sample_world,
            characters=[],
            structure=None,
            segments=[],
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.FANTASY,
            word_count=5000,
            quality_metrics={
                "coherence_score": 0.92,
                "logical_consistency": True,
                "psychological_consistency": True,
                "temporal_consistency": True,
                "passed": True,
                "issues_count": 0,
            },
            total_tokens=10000,
            total_cost_usd=0.50,
            generation_time_seconds=120.5,
            model_usage={},
            output_dir="/tmp/test",
            files={"narrative": "/tmp/test/narrative.txt"},
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        with patch('narra_forge.core.orchestrator.console') as mock_console:
            orchestrator._print_summary(output)

            # Verify console.print was called
            assert mock_console.print.called
            # Verify quality metrics were included in calls
            calls_text = ' '.join([str(call) for call in mock_console.print.call_args_list])
            assert "0.92" in calls_text  # coherence score

    def test_print_summary_without_quality_metrics(
        self, test_config, sample_world
    ):
        """Test _print_summary handles missing quality metrics"""
        orchestrator = BatchOrchestrator(config=test_config)

        output = NarrativeOutput(
            job_id="job_summary_456",
            success=True,
            narrative_text="Test narrative",
            world=sample_world,
            characters=[],
            structure=None,
            segments=[],
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.SCIFI,
            word_count=3000,
            quality_metrics=None,  # No quality metrics
            total_tokens=6000,
            total_cost_usd=0.30,
            generation_time_seconds=80.0,
            model_usage={},
            output_dir="/tmp/test",
            files={},
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        with patch('narra_forge.core.orchestrator.console') as mock_console:
            # Should not raise exception
            orchestrator._print_summary(output)

            assert mock_console.print.called

    def test_print_summary_with_failed_validation(
        self, test_config, sample_world
    ):
        """Test _print_summary shows warning for failed validation"""
        orchestrator = BatchOrchestrator(config=test_config)

        output = NarrativeOutput(
            job_id="job_summary_789",
            success=True,
            narrative_text="Test narrative",
            world=sample_world,
            characters=[],
            structure=None,
            segments=[],
            production_type=ProductionType.SHORT_STORY,
            genre=Genre.HORROR,
            word_count=4000,
            quality_metrics={
                "coherence_score": 0.65,
                "logical_consistency": False,
                "psychological_consistency": True,
                "temporal_consistency": True,
                "passed": False,  # Failed validation
                "issues_count": 5,
            },
            total_tokens=8000,
            total_cost_usd=0.40,
            generation_time_seconds=100.0,
            model_usage={},
            output_dir="/tmp/test",
            files={},
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        with patch('narra_forge.core.orchestrator.console') as mock_console:
            orchestrator._print_summary(output)

            # Verify warning was displayed
            calls_text = ' '.join([str(call) for call in mock_console.print.call_args_list])
            assert "Quality below threshold" in calls_text or "issues" in calls_text


@pytest.mark.unit
class TestOrchestratorBuildStageContext:
    """Test _build_stage_context with all conditional branches"""

    def test_build_stage_context_includes_analyzed_brief(
        self, test_config, sample_production_brief
    ):
        """Test context includes analyzed_brief when available"""
        orchestrator = BatchOrchestrator(config=test_config)

        job = ProductionJob(
            job_id="job_ctx_123",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        job._analyzed_brief = {"theme": "adventure", "tone": "epic"}

        context = orchestrator._build_stage_context(job, PipelineStage.WORLD_ARCHITECTURE)

        assert "analyzed_brief" in context
        assert context["analyzed_brief"]["theme"] == "adventure"

    def test_build_stage_context_includes_narrative_text(
        self, test_config, sample_production_brief
    ):
        """Test context includes narrative_text when available"""
        orchestrator = BatchOrchestrator(config=test_config)

        job = ProductionJob(
            job_id="job_ctx_456",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        job._narrative_text = "This is the narrative text."

        context = orchestrator._build_stage_context(job, PipelineStage.COHERENCE_VALIDATION)

        assert "narrative_text" in context
        assert context["narrative_text"] == "This is the narrative text."

    def test_build_stage_context_includes_stylized_text(
        self, test_config, sample_production_brief
    ):
        """Test context includes stylized_text when available"""
        orchestrator = BatchOrchestrator(config=test_config)

        job = ProductionJob(
            job_id="job_ctx_789",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        job._stylized_text = "This is the stylized text."

        context = orchestrator._build_stage_context(job, PipelineStage.EDITORIAL_REVIEW)

        assert "stylized_text" in context
        assert context["stylized_text"] == "This is the stylized text."

    def test_build_stage_context_includes_final_text(
        self, test_config, sample_production_brief
    ):
        """Test context includes final_text when available"""
        orchestrator = BatchOrchestrator(config=test_config)

        job = ProductionJob(
            job_id="job_ctx_final",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        job._final_text = "This is the final text."

        context = orchestrator._build_stage_context(job, PipelineStage.OUTPUT_PROCESSING)

        assert "final_text" in context
        assert context["final_text"] == "This is the final text."

    def test_build_stage_context_includes_quality_metrics_from_validation(
        self, test_config, sample_production_brief
    ):
        """Test context includes quality_metrics from validation results"""
        orchestrator = BatchOrchestrator(config=test_config)

        job = ProductionJob(
            job_id="job_ctx_quality",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        validation = CoherenceValidation(
            passed=True,
            coherence_score=0.88,
            logical_consistency=True,
            psychological_consistency=True,
            temporal_consistency=False,
            issues=["Issue 1", "Issue 2"],
            warnings=[],
        )

        job._validation_result = validation

        context = orchestrator._build_stage_context(job, PipelineStage.OUTPUT_PROCESSING)

        assert "quality_metrics" in context
        assert context["quality_metrics"]["coherence_score"] == 0.88
        assert context["quality_metrics"]["passed"] is True
        assert context["quality_metrics"]["issues_count"] == 2

    def test_build_stage_context_includes_cost_and_tokens(
        self, test_config, sample_production_brief
    ):
        """Test context always includes cost and token tracking"""
        orchestrator = BatchOrchestrator(config=test_config)

        job = ProductionJob(
            job_id="job_ctx_cost",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        job.tokens_used = 12000
        job.cost_usd = 0.60

        context = orchestrator._build_stage_context(job, PipelineStage.OUTPUT_PROCESSING)

        assert context["total_cost"] == 0.60
        assert context["total_tokens"] == 12000
        assert "started_at" in context
