"""
Core Orchestrator for NARRA_FORGE.
Manages the complete 10-stage production pipeline.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

from .types import (
    ProjectBrief, WorldBible, Character, NarrativeSegment,
    ProductionContext, PipelineStage
)
from .config import SystemConfig
from .revision import RevisionSystem, RevisionRequest
from ..models.backend import ModelOrchestrator
from ..memory.base import SQLiteMemorySystem
from ..memory.structural import StructuralMemory
from ..memory.semantic import SemanticMemory
from ..memory.evolutionary import EvolutionaryMemory
from ..world.world_manager import WorldManager
from ..agents.base_agent import BaseAgent, AgentResponse


class NarrativeOrchestrator:
    """
    Main orchestrator for narrative production.

    Responsibilities:
    - Manage 10-stage pipeline
    - Coordinate agents
    - Track production state
    - Ensure quality
    - Handle errors and retries
    """

    def __init__(self, config: SystemConfig):
        self.config = config

        # Initialize memory system
        self.memory_system = SQLiteMemorySystem(config.memory_db_path)
        self.structural_memory = StructuralMemory(self.memory_system)
        self.semantic_memory = SemanticMemory(self.memory_system)
        self.evolutionary_memory = EvolutionaryMemory(self.memory_system)

        # Initialize world manager
        self.world_manager = WorldManager(
            self.structural_memory,
            self.semantic_memory,
            self.evolutionary_memory
        )

        # Initialize model orchestrator
        # (In production, this would be fully initialized with backends)
        self.model_orchestrator = None  # Placeholder

        # Initialize revision system
        self.revision_system = RevisionSystem()

        # Agent registry
        self.agents: Dict[PipelineStage, BaseAgent] = {}

        # Production tracking
        self.active_productions: Dict[str, ProductionContext] = {}

    def register_agent(self, stage: PipelineStage, agent: BaseAgent):
        """Register an agent for a pipeline stage."""
        self.agents[stage] = agent
        print(f"Registered agent for stage {stage.name}: {agent.name}")

    async def produce_narrative(
        self,
        user_request: str,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete narrative production from request to final output.

        Args:
            user_request: User's narrative request
            project_id: Optional project ID (generated if not provided)

        Returns:
            Complete production result
        """
        if not project_id:
            import uuid
            project_id = str(uuid.uuid4())

        print(f"\n{'='*60}")
        print(f"NARRA_FORGE PRODUCTION: {project_id}")
        print(f"{'='*60}\n")

        # Initialize production context
        context = {
            "project_id": project_id,
            "user_request": user_request,
            "start_time": datetime.now()
        }

        try:
            # STAGE 1: Brief Interpretation
            print(f"\n[STAGE 1/10] Brief Interpretation")
            brief_result = await self._execute_stage(
                PipelineStage.BRIEF_INTERPRETATION,
                context
            )

            if not brief_result.success:
                raise Exception(f"Stage 1 failed: {brief_result.error}")

            context["brief"] = brief_result.output
            print(f"✓ Form: {brief_result.output.form.value}")
            print(f"✓ Genre: {brief_result.output.genre.value}")

            # STAGE 2: World Architecture
            print(f"\n[STAGE 2/10] World Architecture")
            world_result = await self._execute_stage(
                PipelineStage.WORLD_ARCHITECTURE,
                context
            )

            if not world_result.success:
                raise Exception(f"Stage 2 failed: {world_result.error}")

            context["world"] = world_result.output
            print(f"✓ World created: {world_result.output.name}")

            # STAGE 3: Character Architecture
            print(f"\n[STAGE 3/10] Character Architecture")
            character_result = await self._execute_stage(
                PipelineStage.CHARACTER_ARCHITECTURE,
                context
            )

            if not character_result.success:
                raise Exception(f"Stage 3 failed: {character_result.error}")

            context["characters"] = character_result.output
            print(f"✓ Characters created: {len(character_result.output)}")

            # STAGE 4: Narrative Structure
            print(f"\n[STAGE 4/10] Narrative Structure Design")
            structure_result = await self._execute_stage(
                PipelineStage.NARRATIVE_STRUCTURE,
                context
            )

            if not structure_result.success:
                raise Exception(f"Stage 4 failed: {structure_result.error}")

            context["structure"] = structure_result.output

            # STAGE 5: Segment Planning
            print(f"\n[STAGE 5/10] Segment Planning")
            planning_result = await self._execute_stage(
                PipelineStage.SEGMENT_PLANNING,
                context
            )

            if not planning_result.success:
                raise Exception(f"Stage 5 failed: {planning_result.error}")

            context["segment_plan"] = planning_result.output

            # STAGE 6: Sequential Generation
            print(f"\n[STAGE 6/10] Sequential Generation")
            generation_result = await self._execute_stage(
                PipelineStage.SEQUENTIAL_GENERATION,
                context
            )

            if not generation_result.success:
                raise Exception(f"Stage 6 failed: {generation_result.error}")

            context["segments"] = generation_result.output

            # STAGE 7: Coherence Control
            print(f"\n[STAGE 7/10] Coherence Validation")
            coherence_result = await self._execute_stage(
                PipelineStage.COHERENCE_CONTROL,
                context
            )

            if not coherence_result.success:
                raise Exception(f"Stage 7 failed: {coherence_result.error}")

            context["coherence_report"] = coherence_result.output

            # STAGE 8: Language Stylization
            print(f"\n[STAGE 8/10] Language Stylization")
            style_result = await self._execute_stage(
                PipelineStage.LANGUAGE_STYLIZATION,
                context
            )

            if not style_result.success:
                raise Exception(f"Stage 8 failed: {style_result.error}")

            context["stylized_segments"] = style_result.output

            # STAGE 9: Editorial Review
            print(f"\n[STAGE 9/10] Editorial Review")
            editorial_result = await self._execute_stage(
                PipelineStage.EDITORIAL_REVIEW,
                context
            )

            if not editorial_result.success:
                raise Exception(f"Stage 9 failed: {editorial_result.error}")

            context["edited_segments"] = editorial_result.output

            # STAGE 10: Final Output
            print(f"\n[STAGE 10/10] Final Output Processing")
            output_result = await self._execute_stage(
                PipelineStage.FINAL_OUTPUT,
                context
            )

            if not output_result.success:
                raise Exception(f"Stage 10 failed: {output_result.error}")

            # Complete
            end_time = datetime.now()
            duration = (end_time - context["start_time"]).total_seconds()

            print(f"\n{'='*60}")
            print(f"PRODUCTION COMPLETE")
            print(f"Duration: {duration:.2f}s")
            print(f"{'='*60}\n")

            return {
                "success": True,
                "project_id": project_id,
                "output": output_result.output,
                "duration_seconds": duration,
                "metadata": {
                    "brief": context["brief"],
                    "world": context["world"],
                    "characters": context["characters"],
                    "coherence_report": context.get("coherence_report")
                }
            }

        except Exception as e:
            print(f"\n❌ PRODUCTION FAILED: {e}\n")
            return {
                "success": False,
                "project_id": project_id,
                "error": str(e)
            }

    async def _execute_stage(
        self,
        stage: PipelineStage,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """
        Execute a single pipeline stage.

        Args:
            stage: Pipeline stage to execute
            context: Current production context

        Returns:
            AgentResponse from stage execution
        """
        if stage not in self.agents:
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error=f"No agent registered for stage {stage.name}"
            )

        agent = self.agents[stage]

        # Execute with retries
        max_retries = self.config.max_retries
        retry_count = 0

        while retry_count < max_retries:
            try:
                result = await agent.execute(context)

                if result.success:
                    return result

                # Log failure and retry
                print(f"  Stage failed (attempt {retry_count + 1}): {result.error}")
                retry_count += 1

                if retry_count < max_retries:
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff

            except Exception as e:
                print(f"  Exception in stage (attempt {retry_count + 1}): {e}")
                retry_count += 1

                if retry_count >= max_retries:
                    return AgentResponse(
                        success=False,
                        output=None,
                        metadata={},
                        error=str(e)
                    )

                await asyncio.sleep(2 ** retry_count)

        return AgentResponse(
            success=False,
            output=None,
            metadata={},
            error=f"Failed after {max_retries} attempts"
        )

    def get_production_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a production."""
        if project_id not in self.active_productions:
            return None

        production = self.active_productions[project_id]

        return {
            "project_id": project_id,
            "current_stage": production.current_stage.name,
            "progress": production.current_stage.value / 10.0,
            "created_at": production.created_at.isoformat()
        }

    def list_productions(self) -> List[Dict[str, Any]]:
        """List all active productions."""
        return [
            self.get_production_status(pid)
            for pid in self.active_productions.keys()
        ]

    async def revise_narrative(
        self,
        revision_request: RevisionRequest,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Rewizja i regeneracja narracji od wybranego etapu.

        Args:
            revision_request: Żądanie rewizji z informacjami
            progress_callback: Opcjonalny callback dla postępu

        Returns:
            Wynik rewizji
        """
        project_id = revision_request.project_id
        from_stage = revision_request.from_stage

        print(f"\n{'='*60}")
        print(f"NARRA_FORGE REVISION: {project_id}")
        print(f"Regenerating from stage: {from_stage.name}")
        print(f"{'='*60}\n")

        try:
            # Określ numer wersji
            if revision_request.create_new_version:
                version = self.revision_system.get_latest_version(project_id) + 1
                print(f"Creating new version: v{version}")
            else:
                version = self.revision_system.get_latest_version(project_id)
                print(f"Overwriting version: v{version}")

            # Wczytaj kontekst z etapu przed from_stage
            previous_stage_num = from_stage.value - 1
            if previous_stage_num < 1:
                return {
                    "success": False,
                    "error": "Cannot revise from first stage. Start a new production instead."
                }

            # Znajdź poprzedni etap
            previous_stage = None
            for stage in PipelineStage:
                if stage.value == previous_stage_num:
                    previous_stage = stage
                    break

            if not previous_stage:
                return {
                    "success": False,
                    "error": f"Could not find stage {previous_stage_num}"
                }

            # Wczytaj kontekst
            print(f"Loading context from stage: {previous_stage.name}")
            context = self.revision_system.load_context_snapshot(
                project_id,
                previous_stage,
                version=version if not revision_request.create_new_version else version - 1
            )

            if not context:
                return {
                    "success": False,
                    "error": f"Could not load context for stage {previous_stage.name}"
                }

            # Aplikuj modyfikacje kontekstu jeśli są
            if revision_request.context_modifications:
                print(f"Applying context modifications...")
                context.update(revision_request.context_modifications)

            # Dodaj instrukcje rewizji do kontekstu
            if revision_request.instructions:
                context["revision_instructions"] = revision_request.instructions

            context["start_time"] = datetime.now()
            context["is_revision"] = True
            context["revision_from_stage"] = from_stage.name

            # Wykonaj etapy od from_stage do końca
            all_stages = list(PipelineStage)
            start_index = from_stage.value - 1  # Pipeline stages are 1-indexed

            for stage in all_stages[start_index:]:
                stage_num = stage.value
                print(f"\n[STAGE {stage_num}/10] {stage.name}")

                if progress_callback:
                    await progress_callback(stage.name, {"completed": False})

                result = await self._execute_stage(stage, context)

                if not result.success:
                    print(f"❌ Stage {stage_num} failed: {result.error}")
                    if progress_callback:
                        await progress_callback(stage.name, {"failed": True})

                    return {
                        "success": False,
                        "project_id": project_id,
                        "version": version,
                        "failed_at_stage": stage.name,
                        "error": result.error
                    }

                # Zapisz wynik do kontekstu
                self._update_context_from_stage_result(stage, result, context)

                # Zapisz snapshot
                self.revision_system.save_context_snapshot(
                    project_id,
                    stage,
                    context,
                    version
                )

                if progress_callback:
                    await progress_callback(stage.name, {"completed": True})

                print(f"✓ Stage {stage_num} completed")

            # Zakończ
            end_time = datetime.now()
            duration = (end_time - context["start_time"]).total_seconds()

            print(f"\n{'='*60}")
            print(f"REVISION COMPLETE")
            print(f"Version: v{version}")
            print(f"Duration: {duration:.2f}s")
            print(f"{'='*60}\n")

            return {
                "success": True,
                "project_id": project_id,
                "version": version,
                "from_stage": from_stage.name,
                "duration_seconds": duration,
                "output": context.get("output"),
                "metadata": {
                    "revision_instructions": revision_request.instructions,
                    "context_modifications": revision_request.context_modifications
                }
            }

        except Exception as e:
            print(f"\n❌ REVISION FAILED: {e}\n")
            return {
                "success": False,
                "project_id": project_id,
                "error": str(e)
            }

    def _update_context_from_stage_result(
        self,
        stage: PipelineStage,
        result: AgentResponse,
        context: Dict[str, Any]
    ):
        """
        Zaktualizuj kontekst wynikami z etapu.

        Args:
            stage: Etap pipeline'u
            result: Wynik wykonania etapu
            context: Kontekst do aktualizacji
        """
        # Mapowanie etapów na klucze kontekstu
        stage_context_keys = {
            PipelineStage.BRIEF_INTERPRETATION: "brief",
            PipelineStage.WORLD_ARCHITECTURE: "world",
            PipelineStage.CHARACTER_ARCHITECTURE: "characters",
            PipelineStage.NARRATIVE_STRUCTURE: "structure",
            PipelineStage.SEGMENT_PLANNING: "segment_plan",
            PipelineStage.SEQUENTIAL_GENERATION: "segments",
            PipelineStage.COHERENCE_CONTROL: "coherence_report",
            PipelineStage.LANGUAGE_STYLIZATION: "stylized_segments",
            PipelineStage.EDITORIAL_REVIEW: "edited_segments",
            PipelineStage.FINAL_OUTPUT: "output"
        }

        if stage in stage_context_keys:
            context[stage_context_keys[stage]] = result.output
