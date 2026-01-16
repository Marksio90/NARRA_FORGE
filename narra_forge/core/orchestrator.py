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
from narra_forge.agents import (
    BriefInterpreterAgent,
    CharacterArchitectAgent,
    CoherenceValidatorAgent,
    EditorialReviewerAgent,
    LanguageStylerAgent,
    OutputProcessorAgent,
    SegmentPlannerAgent,
    SequentialGeneratorAgent,
    StructureDesignerAgent,
    WorldArchitectAgent,
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
        Execute a single pipeline stage with REAL agents.
        """
        # Build context for this stage
        context = self._build_stage_context(job, stage)

        # Execute appropriate agent
        if stage == PipelineStage.BRIEF_INTERPRETATION:
            agent = BriefInterpreterAgent(self.config, self.memory, self.router)
            result = await agent.run(context)

            if result.success:
                job._analyzed_brief = result.data.get("analyzed_brief")
            else:
                if result.errors:
                    console.print(f"[yellow]⚠  Agent errors: {result.errors}[/yellow]")

        elif stage == PipelineStage.WORLD_ARCHITECTURE:
            agent = WorldArchitectAgent(self.config, self.memory, self.router)
            result = await agent.run(context)

            if result.success:
                job.world = result.data.get("world")
            else:
                if result.errors:
                    console.print(f"[yellow]⚠  Agent errors: {result.errors}[/yellow]")

        elif stage == PipelineStage.CHARACTER_ARCHITECTURE:
            agent = CharacterArchitectAgent(self.config, self.memory, self.router)
            result = await agent.run(context)

            if result.success:
                job.characters = result.data.get("characters", [])
            else:
                if result.errors:
                    console.print(f"[yellow]⚠  Agent errors: {result.errors}[/yellow]")

        elif stage == PipelineStage.STRUCTURE_DESIGN:
            agent = StructureDesignerAgent(self.config, self.memory, self.router)
            result = await agent.run(context)

            if result.success:
                job.structure = result.data.get("structure")
            else:
                if result.errors:
                    console.print(f"[yellow]⚠  Agent errors: {result.errors}[/yellow]")

        elif stage == PipelineStage.SEGMENT_PLANNING:
            agent = SegmentPlannerAgent(self.config, self.memory, self.router)
            result = await agent.run(context)

            if result.success:
                job.segments = result.data.get("segments", [])
            else:
                if result.errors:
                    console.print(f"[yellow]⚠  Agent errors: {result.errors}[/yellow]")

        elif stage == PipelineStage.SEQUENTIAL_GENERATION:
            agent = SequentialGeneratorAgent(self.config, self.memory, self.router)
            result = await agent.run(context)

            if result.success:
                job._narrative_text = result.data.get("narrative_text")
            else:
                if result.errors:
                    console.print(f"[yellow]⚠  Agent errors: {result.errors}[/yellow]")

        elif stage == PipelineStage.COHERENCE_VALIDATION:
            agent = CoherenceValidatorAgent(self.config, self.memory, self.router)
            result = await agent.run(context)

            # Validation is NON-BLOCKING - log warnings but continue pipeline
            if result.warnings:
                for warning in result.warnings:
                    console.print(f"[yellow]⚠  Quality: {warning}[/yellow]")

            # Store validation results for final report
            job._validation_result = result.data.get("validation")

        elif stage == PipelineStage.LANGUAGE_STYLIZATION:
            agent = LanguageStylerAgent(self.config, self.memory, self.router)
            result = await agent.run(context)

            if result.success:
                job._stylized_text = result.data.get("stylized_text")
            else:
                if result.errors:
                    console.print(f"[yellow]⚠  Agent errors: {result.errors}[/yellow]")

        elif stage == PipelineStage.EDITORIAL_REVIEW:
            agent = EditorialReviewerAgent(self.config, self.memory, self.router)
            result = await agent.run(context)

            if not result.success:
                # Review found critical issues
                self._handle_editorial_issues(result)
                # For now, continue anyway

            job._final_text = result.data.get("final_text")

        elif stage == PipelineStage.OUTPUT_PROCESSING:
            agent = OutputProcessorAgent(self.config, self.memory, self.router)
            result = await agent.run(context)

            if result.success:
                job.output = result.data.get("output")
            else:
                if result.errors:
                    console.print(f"[yellow]⚠  Agent errors: {result.errors}[/yellow]")

        else:
            raise ValueError(f"Unknown stage: {stage}")

        # Aggregate costs from agent
        if hasattr(result, 'model_calls'):
            for call in result.model_calls:
                job.tokens_used += call.total_tokens
                job.cost_usd += call.cost_usd

    def _build_stage_context(self, job: ProductionJob, stage: PipelineStage) -> Dict[str, Any]:
        """Build context dict for stage execution"""
        context = {
            "job_id": job.job_id,
            "brief": job.brief,
            "world": job.world,
            "characters": job.characters,
            "structure": job.structure,
            "segments": job.segments,
        }

        # Add stage-specific data
        if hasattr(job, '_analyzed_brief'):
            context["analyzed_brief"] = job._analyzed_brief

        if hasattr(job, '_narrative_text'):
            context["narrative_text"] = job._narrative_text

        if hasattr(job, '_stylized_text'):
            context["stylized_text"] = job._stylized_text

        if hasattr(job, '_final_text'):
            context["final_text"] = job._final_text

        return context

    def _handle_editorial_issues(self, result):
        """Handle critical editorial issues"""
        # For now, just log
        # In future: could trigger retry or manual review
        pass

    async def _build_output(
        self,
        job: ProductionJob,
        total_time: float,
    ) -> NarrativeOutput:
        """Build final NarrativeOutput from job results"""

        # If output was already built by OutputProcessorAgent, return it
        if job.output:
            return job.output

        # Otherwise, build a minimal output (fallback)
        output_dir = self.config.output_dir / job.job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        narrative_text = getattr(job, '_final_text', None) or getattr(job, '_narrative_text', "")

        narrative_file = output_dir / "narrative.txt"
        narrative_file.write_text(narrative_text or "Production incomplete", encoding="utf-8")

        # Build quality_metrics from validation results
        validation_result = getattr(job, '_validation_result', None)
        quality_metrics = {}
        if validation_result:
            quality_metrics = {
                "coherence_score": validation_result.coherence_score,
                "logical_consistency": validation_result.logical_consistency,
                "psychological_consistency": validation_result.psychological_consistency,
                "temporal_consistency": validation_result.temporal_consistency,
                "passed": validation_result.passed,
                "issues_count": len(validation_result.issues),
            }

        output = NarrativeOutput(
            job_id=job.job_id,
            success=bool(narrative_text),
            narrative_text=narrative_text or "",
            world=job.world,
            characters=job.characters,
            structure=job.structure,
            segments=job.segments,
            production_type=job.brief.production_type,
            genre=job.brief.genre,
            word_count=len(narrative_text.split()) if narrative_text else 0,
            quality_metrics=quality_metrics,
            total_tokens=job.tokens_used,
            total_cost_usd=job.cost_usd,
            generation_time_seconds=total_time,
            model_usage={},
            output_dir=str(output_dir),
            files={"narrative": str(narrative_file)},
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

        # Quality metrics (safe access with defaults)
        if output.quality_metrics:
            console.print(f"\n[cyan]Quality:[/]")
            score = output.quality_metrics.get('coherence_score', 0.0)
            console.print(f"  Coherence: {score:.2f}/1.0")

            logical = output.quality_metrics.get('logical_consistency', False)
            console.print(f"  Logical: {'✓' if logical else '✗'}")

            psych = output.quality_metrics.get('psychological_consistency', False)
            console.print(f"  Psychological: {'✓' if psych else '✗'}")

            temp = output.quality_metrics.get('temporal_consistency', False)
            console.print(f"  Temporal: {'✓' if temp else '✗'}")

            passed = output.quality_metrics.get('passed', False)
            issues = output.quality_metrics.get('issues_count', 0)
            if not passed:
                console.print(f"  [yellow]⚠  Quality below threshold ({issues} issues)[/]")
        else:
            console.print(f"\n[cyan]Quality:[/] [dim]Not validated[/]")

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
