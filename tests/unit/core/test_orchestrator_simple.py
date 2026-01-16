"""
Simple orchestrator tests that focus on testable methods
"""
import pytest
from narra_forge.core.orchestrator import BatchOrchestrator, create_orchestrator
from narra_forge.core.types import PipelineStage


@pytest.mark.unit
class TestOrchestratorFactory:
    """Test orchestrator creation"""

    @pytest.mark.asyncio
    async def test_create_orchestrator(self, test_config, temp_db_path):
        """Test factory function"""
        test_config.db_path = temp_db_path
        orchestrator = await create_orchestrator(test_config)

        assert orchestrator is not None
        assert orchestrator.config == test_config


@pytest.mark.unit
class TestOrchestratorStageNames:
    """Test stage name methods"""

    def test_stage_name_formatting(self, test_config):
        """Test stage name formatting"""
        orchestrator = BatchOrchestrator(config=test_config)

        name = orchestrator._stage_name(PipelineStage.BRIEF_INTERPRETATION)

        assert isinstance(name, str)
        assert len(name) > 0

    def test_all_stage_names(self, test_config):
        """Test all stage names can be formatted"""
        orchestrator = BatchOrchestrator(config=test_config)

        stages = list(PipelineStage)

        for stage in stages:
            name = orchestrator._stage_name(stage)
            assert isinstance(name, str)
            assert len(name) > 0


@pytest.mark.unit
class TestOrchestratorBuildContext:
    """Test context building"""

    def test_build_stage_context_includes_brief(self, test_config, sample_production_brief):
        """Test context includes brief"""
        from narra_forge.core.types import ProductionJob, JobStatus
        from datetime import datetime

        orchestrator = BatchOrchestrator(config=test_config)

        job = ProductionJob(
            job_id="job_123",
            brief=sample_production_brief,
            status=JobStatus.IN_PROGRESS,
            created_at=datetime.now(),
        )

        context = orchestrator._build_stage_context(job, PipelineStage.BRIEF_INTERPRETATION)

        assert "brief" in context
        assert "job_id" in context
        assert context["job_id"] == "job_123"
