"""
Tests for CLI (Command Line Interface)

Tests interactive and direct modes, job listing, and helper functions
to increase coverage from 0% to 60%+
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from click.testing import CliRunner

from narra_forge.core.types import Genre, ProductionType, ProductionBrief, NarrativeOutput
from narra_forge.cli import (
    print_banner,
    get_production_type,
    get_genre,
    get_inspiration,
    run_production,
    create_orchestrator,
    list_jobs,
    main,
)


@pytest.mark.unit
class TestCLIHelpers:
    """Test CLI helper functions"""

    def test_print_banner(self):
        """Test banner printing"""
        with patch('narra_forge.cli.console') as mock_console:
            print_banner()

            # Verify console.print was called
            assert mock_console.print.called
            # Check banner contains version
            call_args = str(mock_console.print.call_args)
            assert "NARRA_FORGE" in call_args or "2.0.0" in call_args

    def test_get_production_type_default(self):
        """Test production type selection with default"""
        with patch('narra_forge.cli.console'):
            with patch('narra_forge.cli.Prompt.ask', return_value="1"):
                result = get_production_type()

                assert result == ProductionType.SHORT_STORY

    def test_get_production_type_novel(self):
        """Test production type selection - novel"""
        with patch('narra_forge.cli.console'):
            with patch('narra_forge.cli.Prompt.ask', return_value="3"):
                result = get_production_type()

                assert result == ProductionType.NOVEL

    def test_get_production_type_epic(self):
        """Test production type selection - epic saga"""
        with patch('narra_forge.cli.console'):
            with patch('narra_forge.cli.Prompt.ask', return_value="4"):
                result = get_production_type()

                assert result == ProductionType.EPIC_SAGA

    def test_get_genre_default(self):
        """Test genre selection with default"""
        with patch('narra_forge.cli.console'):
            with patch('narra_forge.cli.Prompt.ask', return_value="1"):
                result = get_genre()

                assert result == Genre.FANTASY

    def test_get_genre_scifi(self):
        """Test genre selection - sci-fi"""
        with patch('narra_forge.cli.console'):
            with patch('narra_forge.cli.Prompt.ask', return_value="2"):
                result = get_genre()

                assert result == Genre.SCIFI

    def test_get_genre_horror(self):
        """Test genre selection - horror"""
        with patch('narra_forge.cli.console'):
            with patch('narra_forge.cli.Prompt.ask', return_value="3"):
                result = get_genre()

                assert result == Genre.HORROR

    def test_get_inspiration_with_text(self):
        """Test getting inspiration with user input"""
        with patch('narra_forge.cli.console'):
            with patch('narra_forge.cli.Prompt.ask', return_value="A hero's journey"):
                result = get_inspiration()

                assert result == "A hero's journey"

    def test_get_inspiration_empty(self):
        """Test getting inspiration with empty input"""
        with patch('narra_forge.cli.console'):
            with patch('narra_forge.cli.Prompt.ask', return_value=""):
                result = get_inspiration()

                assert result is None

    def test_get_inspiration_whitespace_only(self):
        """Test getting inspiration with whitespace only"""
        with patch('narra_forge.cli.console'):
            with patch('narra_forge.cli.Prompt.ask', return_value="   "):
                result = get_inspiration()

                assert result is None


@pytest.mark.unit
class TestCLIProductionFunctions:
    """Test async production functions"""

    @pytest.mark.asyncio
    async def test_run_production_success(self, test_config, sample_world):
        """Test successful production run"""
        # Mock orchestrator
        mock_orchestrator = AsyncMock()
        mock_output = MagicMock(spec=NarrativeOutput)
        mock_output.job_id = "job_test_123"
        mock_output.success = True
        mock_output.narrative_text = "Test narrative"
        mock_output.word_count = 5000
        mock_orchestrator.produce_narrative.return_value = mock_output

        with patch('narra_forge.cli.create_orchestrator', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_orchestrator

            with patch('narra_forge.cli.console'):
                result = await run_production(
                    production_type=ProductionType.SHORT_STORY,
                    genre=Genre.FANTASY,
                    inspiration="Test inspiration",
                    config=test_config,
                )

                assert result == mock_output
                mock_orchestrator.produce_narrative.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_production_handles_error(self, test_config):
        """Test production run error handling"""
        # Mock orchestrator that raises error
        mock_orchestrator = AsyncMock()
        mock_orchestrator.produce_narrative.side_effect = Exception("Production failed")

        with patch('narra_forge.cli.create_orchestrator', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_orchestrator

            with patch('narra_forge.cli.console'):
                with pytest.raises(Exception, match="Production failed"):
                    await run_production(
                        production_type=ProductionType.NOVEL,
                        genre=Genre.SCIFI,
                        inspiration=None,
                        config=test_config,
                    )

    @pytest.mark.asyncio
    async def test_create_orchestrator(self, test_config):
        """Test orchestrator creation"""
        with patch('narra_forge.cli.BatchOrchestrator') as MockOrch:
            mock_orch = AsyncMock()
            MockOrch.return_value = mock_orch

            result = await create_orchestrator(test_config)

            assert result == mock_orch
            mock_orch._ensure_memory_initialized.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_jobs_with_results(self, test_config):
        """Test listing jobs with results"""
        # Mock jobs data
        mock_jobs = [
            {
                "job_id": "job_123",
                "brief": '{"production_type": "short_story", "genre": "fantasy"}',
                "status": "completed",
                "cost_usd": 1.25,
                "created_at": "2024-01-01T10:00:00",
            },
            {
                "job_id": "job_456",
                "brief": '{"production_type": "novel", "genre": "scifi"}',
                "status": "in_progress",
                "cost_usd": 0.50,
                "created_at": "2024-01-02T15:30:00",
            },
        ]

        # Mock MemorySystem
        mock_memory = AsyncMock()
        mock_memory.list_jobs.return_value = mock_jobs

        with patch('narra_forge.memory.MemorySystem') as MockMemory:
            MockMemory.return_value = mock_memory

            with patch('narra_forge.cli.console') as mock_console:
                await list_jobs(test_config, status=None)

                # Verify memory was initialized and jobs listed
                mock_memory.initialize.assert_called_once()
                mock_memory.list_jobs.assert_called_once_with(status=None, limit=20)

                # Verify table was printed
                assert mock_console.print.called

    @pytest.mark.asyncio
    async def test_list_jobs_empty(self, test_config):
        """Test listing jobs with no results"""
        mock_memory = AsyncMock()
        mock_memory.list_jobs.return_value = []

        with patch('narra_forge.memory.MemorySystem') as MockMemory:
            MockMemory.return_value = mock_memory

            with patch('narra_forge.cli.console') as mock_console:
                await list_jobs(test_config, status="completed")

                # Verify empty message was printed
                mock_memory.list_jobs.assert_called_once_with(status="completed", limit=20)
                assert mock_console.print.called

    @pytest.mark.asyncio
    async def test_list_jobs_with_status_filter(self, test_config):
        """Test listing jobs with status filter"""
        mock_memory = AsyncMock()
        mock_memory.list_jobs.return_value = []

        with patch('narra_forge.memory.MemorySystem') as MockMemory:
            MockMemory.return_value = mock_memory

            with patch('narra_forge.cli.console'):
                await list_jobs(test_config, status="failed")

                # Verify status filter was used
                mock_memory.list_jobs.assert_called_once_with(status="failed", limit=20)


@pytest.mark.unit
class TestCLIMainCommand:
    """Test main CLI command with Click"""

    def test_main_list_jobs_mode(self, test_config):
        """Test main command in list-jobs mode"""
        runner = CliRunner()

        with patch('narra_forge.cli.NarraForgeConfig', return_value=test_config):
            with patch('narra_forge.cli.list_jobs', new_callable=AsyncMock) as mock_list:
                with patch('narra_forge.cli.asyncio.run') as mock_run:
                    result = runner.invoke(main, ['--list-jobs'])

                    assert result.exit_code == 0
                    # Verify asyncio.run was called with list_jobs
                    mock_run.assert_called_once()

    def test_main_direct_mode(self, test_config):
        """Test main command in direct mode"""
        runner = CliRunner()

        with patch('narra_forge.cli.NarraForgeConfig', return_value=test_config):
            with patch('narra_forge.cli.print_banner'):
                with patch('narra_forge.cli.run_production', new_callable=AsyncMock) as mock_run_prod:
                    with patch('narra_forge.cli.asyncio.run') as mock_run:
                        result = runner.invoke(main, [
                            '--type', 'novel',
                            '--genre', 'fantasy',
                            '--inspiration', 'Test story'
                        ])

                        assert result.exit_code == 0
                        # Verify asyncio.run was called
                        mock_run.assert_called_once()

    def test_main_interactive_mode_confirmed(self, test_config):
        """Test main command in interactive mode with confirmation"""
        runner = CliRunner()

        with patch('narra_forge.cli.NarraForgeConfig', return_value=test_config):
            with patch('narra_forge.cli.print_banner'):
                with patch('narra_forge.cli.get_production_type', return_value=ProductionType.SHORT_STORY):
                    with patch('narra_forge.cli.get_genre', return_value=Genre.FANTASY):
                        with patch('narra_forge.cli.get_inspiration', return_value="Test"):
                            with patch('narra_forge.cli.Confirm.ask', return_value=True):
                                with patch('narra_forge.cli.run_production', new_callable=AsyncMock):
                                    with patch('narra_forge.cli.asyncio.run') as mock_run:
                                        result = runner.invoke(main, [])

                                        assert result.exit_code == 0
                                        mock_run.assert_called_once()

    def test_main_interactive_mode_cancelled(self, test_config):
        """Test main command in interactive mode with cancellation"""
        runner = CliRunner()

        with patch('narra_forge.cli.NarraForgeConfig', return_value=test_config):
            with patch('narra_forge.cli.print_banner'):
                with patch('narra_forge.cli.get_production_type', return_value=ProductionType.NOVEL):
                    with patch('narra_forge.cli.get_genre', return_value=Genre.HORROR):
                        with patch('narra_forge.cli.get_inspiration', return_value=None):
                            with patch('narra_forge.cli.Confirm.ask', return_value=False):
                                with patch('narra_forge.cli.console'):
                                    result = runner.invoke(main, [])

                                    assert result.exit_code == 0
                                    # Should print "Anulowano" and return

    def test_main_config_error(self):
        """Test main command with config error"""
        runner = CliRunner()

        with patch('narra_forge.cli.NarraForgeConfig', side_effect=Exception("Missing API key")):
            with patch('narra_forge.cli.console'):
                result = runner.invoke(main, [])

                assert result.exit_code == 1

    def test_main_list_jobs_with_status(self, test_config):
        """Test main command list-jobs with status filter"""
        runner = CliRunner()

        with patch('narra_forge.cli.NarraForgeConfig', return_value=test_config):
            with patch('narra_forge.cli.list_jobs', new_callable=AsyncMock) as mock_list:
                with patch('narra_forge.cli.asyncio.run') as mock_run:
                    result = runner.invoke(main, ['--list-jobs', '--status', 'completed'])

                    assert result.exit_code == 0
                    mock_run.assert_called_once()

    def test_main_direct_mode_without_inspiration(self, test_config):
        """Test direct mode without inspiration parameter"""
        runner = CliRunner()

        with patch('narra_forge.cli.NarraForgeConfig', return_value=test_config):
            with patch('narra_forge.cli.print_banner'):
                with patch('narra_forge.cli.run_production', new_callable=AsyncMock):
                    with patch('narra_forge.cli.asyncio.run') as mock_run:
                        result = runner.invoke(main, [
                            '--type', 'short_story',
                            '--genre', 'scifi'
                        ])

                        assert result.exit_code == 0
                        mock_run.assert_called_once()


@pytest.mark.unit
class TestCLIEdgeCases:
    """Test CLI edge cases and error scenarios"""

    def test_production_type_choices_coverage(self):
        """Test all production type choices"""
        choices = ["1", "2", "3", "4"]
        expected = [
            ProductionType.SHORT_STORY,
            ProductionType.NOVELLA,
            ProductionType.NOVEL,
            ProductionType.EPIC_SAGA,
        ]

        with patch('narra_forge.cli.console'):
            for choice, expected_type in zip(choices, expected):
                with patch('narra_forge.cli.Prompt.ask', return_value=choice):
                    result = get_production_type()
                    assert result == expected_type

    def test_genre_choices_coverage(self):
        """Test all genre choices"""
        choices = ["1", "2", "3", "4", "5", "6", "7", "8"]
        expected = [
            Genre.FANTASY,
            Genre.SCIFI,
            Genre.HORROR,
            Genre.THRILLER,
            Genre.MYSTERY,
            Genre.DRAMA,
            Genre.ROMANCE,
            Genre.HYBRID,
        ]

        with patch('narra_forge.cli.console'):
            for choice, expected_genre in zip(choices, expected):
                with patch('narra_forge.cli.Prompt.ask', return_value=choice):
                    result = get_genre()
                    assert result == expected_genre
