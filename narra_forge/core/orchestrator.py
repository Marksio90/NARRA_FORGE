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
