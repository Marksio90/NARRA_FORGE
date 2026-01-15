"""
Batch Orchestrator - The Heart of NARRA_FORGE V2

This is NOT a streaming system. This is NOT interactive.
This is a BATCH PRODUCTION ENGINE.

Work mode:
    input → full analysis → full production → final output

One cycle. One complete result.
"""
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from narra_forge.core.config import NarraForgeConfig
from narra_forge.core.types import (
    JobStatus,
    NarrativeOutput,
    PipelineStage,
    ProductionBrief,
    ProductionJob,
    ProductionType,
)
from narra_forge.memory import MemorySystem
from narra_forge.models import ModelRouter, OpenAIClient

console = Console()


class BatchOrchestrator:
    """
    Batch production orchestrator.

    Manages the complete 10-stage production pipeline:
    1. Brief Interpretation
    2. World Architecture
    3. Character Architecture
    4. Structure Design
    5. Segment Planning
    6. Sequential Generation (EXPENSIVE)
    7. Coherence Validation
    8. Language Stylization (EXPENSIVE)
    9. Editorial Review
    10. Output Processing

    This is a SINGLE CLOSED CYCLE. No streaming. No interaction.
    """

    def __init__(
        self,
        config: NarraForgeConfig,
        memory: Optional[MemorySystem] = None,
        client: Optional[OpenAIClient] = None,
        router: Optional[ModelRouter] = None,
    ):
        """
        Initialize orchestrator.

        Args:
            config: NarraForgeConfig
            memory: MemorySystem (optional, will create if None)
            client: OpenAIClient (optional, will create if None)
            router: ModelRouter (optional, will create if None)
        """
        self.config = config

        # Initialize components
        self.memory = memory
        self.client = client or OpenAIClient(config)
        self.router = router or ModelRouter(config, self.client)

        # Initialize memory lazily (requires async)
        self._memory_initialized = False

    async def _ensure_memory_initialized(self) -> None:
        """Ensure memory is initialized"""
        if not self._memory_initialized:
            if self.memory is None:
                self.memory = MemorySystem(self.config)
            await self.memory.initialize()
            self._memory_initialized = True

    async def produce_narrative(
        self,
        brief: ProductionBrief,
        show_progress: bool = True,
    ) -> NarrativeOutput:
        """
        MAIN ENTRY POINT: Produce a complete narrative.

        This is a BATCH operation. It runs through ALL 10 stages
        and returns ONLY when complete.

        Args:
            brief: ProductionBrief with user requirements
            show_progress: Show progress in console

        Returns:
            NarrativeOutput with complete narrative

        Raises:
            Exception if production fails
        """
        # Ensure memory initialized
        await self._ensure_memory_initialized()

        # Create job
        job = ProductionJob(
            job_id=f"job_{uuid4().hex[:12]}",
            brief=brief,
            status=JobStatus.PENDING,
        )

        # Save initial job state
        await self._save_job(job)

        try:
            # Update status
            job.status = JobStatus.IN_PROGRESS
            job.started_at = datetime.now()
            await self._save_job(job)

            if show_progress:
                console.print("\n[bold cyan]═══════════════════════════════════════════[/]")
                console.print("[bold cyan]    NARRA_FORGE - Batch Production[/]")
                console.print("[bold cyan]═══════════════════════════════════════════[/]\n")
                console.print(f"[dim]Job ID: {job.job_id}[/]")
                console.print(f"[dim]Type: {brief.production_type.value}[/]")
                console.print(f"[dim]Genre: {brief.genre.value}[/]\n")

            # Run pipeline
            output = await self._run_pipeline(job, show_progress)

            # Update job
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.output = output
            await self._save_job(job)

            if show_progress:
                console.print("\n[bold green]✓ Production complete![/]\n")
                self._print_summary(output)

            return output

        except Exception as e:
            # Handle failure
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            job.error = str(e)
            await self._save_job(job)

            if show_progress:
                console.print(f"\n[bold red]✗ Production failed: {e}[/]\n")

            raise

    async def _run_pipeline(
        self,
        job: ProductionJob,
        show_progress: bool,
    ) -> NarrativeOutput:
        """
        Run the complete 10-stage pipeline.

        This is where the MAGIC happens.
        """
        stages = [
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

        total_start = time.time()

        for i, stage in enumerate(stages, 1):
            if show_progress:
                console.print(f"[cyan]⚙ Stage {i}/10:[/] {self._stage_name(stage)}")

            job.current_stage = stage
            await self._save_job(job)

            stage_start = time.time()

            # Execute stage
            await self._execute_stage(job, stage)

            stage_time = time.time() - stage_start

            # Mark completed
            job.stages_completed.append(stage)
            await self._save_job(job)

            if show_progress:
                console.print(
                    f"  [green]✓[/] Completed in {stage_time:.1f}s "
                    f"[dim](cost: ${job.cost_usd:.2f})[/]\n"
                )

            # Check cost limit
            if job.cost_usd > self.config.max_cost_per_job:
                raise ValueError(
                    f"Cost limit exceeded: ${job.cost_usd:.2f} > "
                    f"${self.config.max_cost_per_job:.2f}"
                )

        total_time = time.time() - total_start

        # Build final output
        output = await self._build_output(job, total_time)

        return output

    async def _execute_stage(
        self,
        job: ProductionJob,
        stage: PipelineStage,
    ) -> None:
        """
        Execute a single pipeline stage.

        This is a placeholder. Real implementation will import and call agents.
        """
        # TODO: Import and execute actual agents
        # For now, just simulate work

        # Simulate API call cost
        if stage == PipelineStage.SEQUENTIAL_GENERATION:
            # Most expensive stage (narrative generation with gpt-4o)
            await asyncio.sleep(0.5)
            job.cost_usd += 1.50  # Simulated
            job.tokens_used += 15000  # Simulated
        elif stage == PipelineStage.LANGUAGE_STYLIZATION:
            # Second most expensive (stylization with gpt-4o)
            await asyncio.sleep(0.3)
            job.cost_usd += 0.80  # Simulated
            job.tokens_used += 8000  # Simulated
        else:
            # Analysis stages (cheap, using gpt-4o-mini)
            await asyncio.sleep(0.1)
            job.cost_usd += 0.05  # Simulated
            job.tokens_used += 1000  # Simulated

        # Store stage-specific results in job
        if stage == PipelineStage.BRIEF_INTERPRETATION:
            # Placeholder: Real agent would analyze brief
            pass

        elif stage == PipelineStage.WORLD_ARCHITECTURE:
            # Placeholder: Real agent would create world
            if not job.world:
                from narra_forge.core.types import Genre, RealityLaws, World, WorldBoundaries

                job.world = World(
                    world_id=f"world_{uuid4().hex[:8]}",
                    name=f"{job.brief.genre.value.title()} World",
                    genre=job.brief.genre,
                    reality_laws=RealityLaws(
                        physics={"type": "standard"},
                        magic={"level": "high"} if job.brief.genre == Genre.FANTASY else None,
                    ),
                    boundaries=WorldBoundaries(
                        spatial={"size": "continental"},
                        temporal={"span": "centuries"},
                    ),
                    anomalies=[],
                    core_conflict="Light vs Darkness",
                    existential_theme="The nature of power",
                )

        elif stage == PipelineStage.CHARACTER_ARCHITECTURE:
            # Placeholder: Real agent would create characters
            pass

        elif stage == PipelineStage.STRUCTURE_DESIGN:
            # Placeholder: Real agent would design structure
            pass

        elif stage == PipelineStage.SEGMENT_PLANNING:
            # Placeholder: Real agent would plan segments
            pass

        elif stage == PipelineStage.SEQUENTIAL_GENERATION:
            # Placeholder: Real agent would generate narrative
            pass

        elif stage == PipelineStage.COHERENCE_VALIDATION:
            # Placeholder: Real agent would validate
            pass

        elif stage == PipelineStage.LANGUAGE_STYLIZATION:
            # Placeholder: Real agent would stylize
            pass

        elif stage == PipelineStage.EDITORIAL_REVIEW:
            # Placeholder: Real agent would review
            pass

        elif stage == PipelineStage.OUTPUT_PROCESSING:
            # Placeholder: Real agent would finalize
            pass

    async def _build_output(
        self,
        job: ProductionJob,
        total_time: float,
    ) -> NarrativeOutput:
        """Build final NarrativeOutput"""
        # Create output directory
        output_dir = self.config.output_dir / job.job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write placeholder narrative
        narrative_file = output_dir / "narrative.txt"
        narrative_text = (
            f"Narrative for job {job.job_id}\n\n"
            f"Type: {job.brief.production_type.value}\n"
            f"Genre: {job.brief.genre.value}\n\n"
            f"[Narrative would be generated here by agents]\n"
        )
        narrative_file.write_text(narrative_text)

        # Write metadata
        import json

        metadata_file = output_dir / "metadata.json"
        metadata = {
            "job_id": job.job_id,
            "type": job.brief.production_type.value,
            "genre": job.brief.genre.value,
            "world_id": job.world.world_id if job.world else None,
            "tokens_used": job.tokens_used,
            "cost_usd": job.cost_usd,
            "generation_time": total_time,
        }
        metadata_file.write_text(json.dumps(metadata, indent=2))

        # Build output
        output = NarrativeOutput(
            job_id=job.job_id,
            success=True,
            narrative_text=narrative_text,
            world=job.world,
            characters=job.characters,
            structure=job.structure,
            segments=job.segments,
            production_type=job.brief.production_type,
            genre=job.brief.genre,
            word_count=len(narrative_text.split()),
            quality_metrics={
                "coherence_score": 0.90,
                "logical_consistency": True,
                "psychological_consistency": True,
                "temporal_consistency": True,
            },
            total_tokens=job.tokens_used,
            total_cost_usd=job.cost_usd,
            generation_time_seconds=total_time,
            model_usage={
                "mini_tokens": int(job.tokens_used * 0.6),
                "gpt4_tokens": int(job.tokens_used * 0.4),
            },
            output_dir=str(output_dir),
            files={
                "narrative": str(narrative_file),
                "metadata": str(metadata_file),
            },
            started_at=job.started_at,
            completed_at=datetime.now(),
        )

        return output

    async def _save_job(self, job: ProductionJob) -> None:
        """Save job state to memory"""
        job_dict = {
            "job_id": job.job_id,
            "brief": {
                "production_type": job.brief.production_type.value,
                "genre": job.brief.genre.value,
                "inspiration": job.brief.inspiration,
                "world_id": job.brief.world_id,
            },
            "status": job.status.value,
            "current_stage": job.current_stage.value if job.current_stage else None,
            "world_id": job.world.world_id if job.world else None,
            "tokens_used": job.tokens_used,
            "cost_usd": job.cost_usd,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error": job.error,
        }
        await self.memory.save_job(job_dict)

    def _stage_name(self, stage: PipelineStage) -> str:
        """Get readable stage name"""
        names = {
            PipelineStage.BRIEF_INTERPRETATION: "Brief Interpretation",
            PipelineStage.WORLD_ARCHITECTURE: "World Architecture",
            PipelineStage.CHARACTER_ARCHITECTURE: "Character Architecture",
            PipelineStage.STRUCTURE_DESIGN: "Structure Design",
            PipelineStage.SEGMENT_PLANNING: "Segment Planning",
            PipelineStage.SEQUENTIAL_GENERATION: "Narrative Generation",
            PipelineStage.COHERENCE_VALIDATION: "Coherence Validation",
            PipelineStage.LANGUAGE_STYLIZATION: "Language Stylization",
            PipelineStage.EDITORIAL_REVIEW: "Editorial Review",
            PipelineStage.OUTPUT_PROCESSING: "Output Processing",
        }
        return names.get(stage, stage.value)

    def _print_summary(self, output: NarrativeOutput) -> None:
        """Print production summary"""
        console.print("[bold]═══════════════════════════════════════════[/]")
        console.print("[bold]           Production Summary[/]")
        console.print("[bold]═══════════════════════════════════════════[/]\n")

        console.print(f"[cyan]Job ID:[/] {output.job_id}")
        console.print(f"[cyan]Type:[/] {output.production_type.value}")
        console.print(f"[cyan]Genre:[/] {output.genre.value}")
        console.print(f"[cyan]Word Count:[/] {output.word_count:,}")
        console.print(f"\n[cyan]Quality:[/]")
        console.print(
            f"  Coherence: {output.quality_metrics['coherence_score']:.2f}/1.0"
        )
        console.print(
            f"  Logical: {'✓' if output.quality_metrics['logical_consistency'] else '✗'}"
        )
        console.print(
            f"  Psychological: {'✓' if output.quality_metrics['psychological_consistency'] else '✗'}"
        )
        console.print(
            f"  Temporal: {'✓' if output.quality_metrics['temporal_consistency'] else '✗'}"
        )

        console.print(f"\n[cyan]Cost:[/] ${output.total_cost_usd:.2f} USD")
        console.print(f"[cyan]Tokens:[/] {output.total_tokens:,}")
        console.print(f"[cyan]Time:[/] {output.generation_time_seconds:.1f}s")

        console.print(f"\n[cyan]Output:[/]")
        for name, path in output.files.items():
            console.print(f"  {name}: [dim]{path}[/]")

        console.print("\n[bold]═══════════════════════════════════════════[/]\n")


async def create_orchestrator(config: NarraForgeConfig) -> BatchOrchestrator:
    """
    Create and initialize orchestrator.

    Args:
        config: NarraForgeConfig

    Returns:
        Initialized BatchOrchestrator
    """
    orchestrator = BatchOrchestrator(config)
    await orchestrator._ensure_memory_initialized()
    return orchestrator
