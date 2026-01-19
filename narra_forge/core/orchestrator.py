"""
NarrativeOrchestrator - Główny silnik generowania narracji

Koordynuje wszystkie 10 etapów pipeline'u i zarządza agentami.
"""

import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from narra_forge.core.config import SystemConfig, get_adaptive_config
from narra_forge.core.types import (
    PipelineStage,
    GenerationResult,
    ProjectBrief,
    WorldBible,
    Character,
    NarrativeStructure,
    NarrativeSegment,
    CoherenceReport,
    NarrativeForm,
    Genre,
)


class NarrativeOrchestrator:
    """
    Główny Orchestrator Produkcji Narracji

    Zarządza pełnym pipeline'm 10-etapowym:
    1. Interpretacja zlecenia
    2. Architektura świata
    3. Architektura postaci
    4. Struktura narracyjna
    5. Planowanie segmentów
    6. Generacja sekwencyjna
    7. Walidacja koherencji
    8. Stylizacja językowa
    9. Redakcja wydawnicza
    10. Finalne wyjście

    UNIWERSALNY: Adaptuje się automatycznie do:
    - Wszystkich długości (flash fiction → saga)
    - Wszystkich gatunków (fantasy → literary)
    - Wszystkich tonów (dark → light)
    """

    def __init__(self, config: SystemConfig):
        """
        Args:
            config: Konfiguracja systemu
        """
        self.config = config
        self.logger = logging.getLogger("NarrativeOrchestrator")

        # Kontekst bieżącego projektu
        self.context: Dict[str, Any] = {}
        self.current_stage: Optional[PipelineStage] = None

        # Agenty (lazy loading)
        self._agents: Dict[PipelineStage, Any] = {}

        self.logger.info("NarrativeOrchestrator initialized")

    def _get_agent(self, stage: PipelineStage):
        """
        Pobierz agenta dla danego etapu (lazy loading)

        Args:
            stage: Etap pipeline

        Returns:
            Agent dla tego etapu
        """
        if stage not in self._agents:
            # Import dynamiczny (unikamy circular imports)
            from narra_forge.agents.brief_interpreter import BriefInterpreterAgent
            from narra_forge.agents.world_architect import WorldArchitectAgent
            from narra_forge.agents.character_architect import CharacterArchitectAgent
            from narra_forge.agents.structure_designer import StructureDesignerAgent
            from narra_forge.agents.segment_planner import SegmentPlannerAgent
            from narra_forge.agents.sequential_generator import SequentialGeneratorAgent
            from narra_forge.agents.coherence_validator import CoherenceValidatorAgent
            from narra_forge.agents.language_stylizer import LanguageStylerAgent
            from narra_forge.agents.editorial_reviewer import EditorialReviewerAgent
            from narra_forge.agents.output_processor import OutputProcessorAgent

            agent_classes = {
                PipelineStage.BRIEF_INTERPRETATION: BriefInterpreterAgent,
                PipelineStage.WORLD_ARCHITECTURE: WorldArchitectAgent,
                PipelineStage.CHARACTER_ARCHITECTURE: CharacterArchitectAgent,
                PipelineStage.NARRATIVE_STRUCTURE: StructureDesignerAgent,
                PipelineStage.SEGMENT_PLANNING: SegmentPlannerAgent,
                PipelineStage.SEQUENTIAL_GENERATION: SequentialGeneratorAgent,
                PipelineStage.COHERENCE_VALIDATION: CoherenceValidatorAgent,
                PipelineStage.LANGUAGE_STYLIZATION: LanguageStylerAgent,
                PipelineStage.EDITORIAL_REVIEW: EditorialReviewerAgent,
                PipelineStage.FINAL_OUTPUT: OutputProcessorAgent,
            }

            agent_class = agent_classes.get(stage)
            if not agent_class:
                raise ValueError(f"No agent class for stage: {stage}")

            self._agents[stage] = agent_class(self.config, stage)
            self.logger.info(f"Loaded agent for stage: {stage.name}")

        return self._agents[stage]

    async def produce_narrative(
        self,
        user_request: str,
        world_id: Optional[str] = None,
        characters: Optional[List[Character]] = None,
        resume_from: Optional[PipelineStage] = None,
    ) -> GenerationResult:
        """
        GŁÓWNA FUNKCJA: Wyprodukuj narrację na podstawie requestu użytkownika

        Args:
            user_request: Request użytkownika (dowolny język naturalny)
            world_id: ID istniejącego świata (jeśli kontynuacja)
            characters: Istniejące postacie (jeśli kontynuacja)
            resume_from: Wznów od określonego etapu (dla rewizji)

        Returns:
            GenerationResult z pełną narracją i metadanymi

        Example:
            >>> result = await orchestrator.produce_narrative(
            ...     "Napisz mroczne opowiadanie fantasy o alchemiku"
            ... )
            >>> print(result.full_text)
        """
        start_time = time.time()

        try:
            # Inicjalizuj kontekst
            self.context = {
                "user_request": user_request,
                "world_id": world_id,
                "existing_characters": characters or [],
                "started_at": datetime.now().isoformat(),
            }

            # Określ od którego etapu zaczynamy
            start_stage = resume_from or PipelineStage.BRIEF_INTERPRETATION

            # ===== ETAP 1: INTERPRETACJA ZLECENIA =====
            if start_stage.value <= PipelineStage.BRIEF_INTERPRETATION.value:
                self.logger.info("📋 STAGE 1: Brief Interpretation")
                self.current_stage = PipelineStage.BRIEF_INTERPRETATION

                brief_result = await self._execute_stage(
                    PipelineStage.BRIEF_INTERPRETATION,
                    retries=self.config.max_retries
                )

                self.context["brief"] = brief_result["brief"]

                # Adaptuj config do wykrytej formy i gatunku
                brief: ProjectBrief = self.context["brief"]
                self.config = get_adaptive_config(
                    form=brief.form,
                    genre=brief.genre,
                    base_config=self.config
                )
                self.logger.info(
                    f"Config adapted for {brief.form.value} / {brief.genre.value}"
                )

            # ===== ETAP 2: ARCHITEKTURA ŚWIATA =====
            if start_stage.value <= PipelineStage.WORLD_ARCHITECTURE.value:
                self.logger.info("🌍 STAGE 2: World Architecture")
                self.current_stage = PipelineStage.WORLD_ARCHITECTURE

                world_result = await self._execute_stage(
                    PipelineStage.WORLD_ARCHITECTURE,
                    retries=self.config.max_retries
                )

                self.context["world"] = world_result["world"]

            # ===== ETAP 3: ARCHITEKTURA POSTACI =====
            if start_stage.value <= PipelineStage.CHARACTER_ARCHITECTURE.value:
                self.logger.info("👤 STAGE 3: Character Architecture")
                self.current_stage = PipelineStage.CHARACTER_ARCHITECTURE

                char_result = await self._execute_stage(
                    PipelineStage.CHARACTER_ARCHITECTURE,
                    retries=self.config.max_retries
                )

                self.context["characters"] = char_result["characters"]

            # ===== ETAP 4: STRUKTURA NARRACYJNA =====
            if start_stage.value <= PipelineStage.NARRATIVE_STRUCTURE.value:
                self.logger.info("📐 STAGE 4: Narrative Structure")
                self.current_stage = PipelineStage.NARRATIVE_STRUCTURE

                structure_result = await self._execute_stage(
                    PipelineStage.NARRATIVE_STRUCTURE,
                    retries=self.config.max_retries
                )

                self.context["structure"] = structure_result["structure"]

            # ===== ETAP 5: PLANOWANIE SEGMENTÓW =====
            if start_stage.value <= PipelineStage.SEGMENT_PLANNING.value:
                self.logger.info("📚 STAGE 5: Segment Planning")
                self.current_stage = PipelineStage.SEGMENT_PLANNING

                segment_plan_result = await self._execute_stage(
                    PipelineStage.SEGMENT_PLANNING,
                    retries=self.config.max_retries
                )

                self.context["segment_plan"] = segment_plan_result["segments"]

            # ===== ETAP 6: GENERACJA SEKWENCYJNA =====
            if start_stage.value <= PipelineStage.SEQUENTIAL_GENERATION.value:
                self.logger.info("✍️ STAGE 6: Sequential Generation")
                self.current_stage = PipelineStage.SEQUENTIAL_GENERATION

                generation_result = await self._execute_stage(
                    PipelineStage.SEQUENTIAL_GENERATION,
                    retries=self.config.max_retries
                )

                self.context["generated_segments"] = generation_result["segments"]
                self.context["full_text"] = generation_result.get("full_text", "")

            # ===== ETAP 7: WALIDACJA KOHERENCJI =====
            if start_stage.value <= PipelineStage.COHERENCE_VALIDATION.value:
                self.logger.info("✅ STAGE 7: Coherence Validation")
                self.current_stage = PipelineStage.COHERENCE_VALIDATION

                validation_result = await self._execute_stage(
                    PipelineStage.COHERENCE_VALIDATION,
                    retries=self.config.max_retries
                )

                self.context["coherence_report"] = validation_result["report"]

                # Sprawdź czy przeszła walidację
                report: CoherenceReport = validation_result["report"]
                if not report.passed:
                    self.logger.warning(
                        f"Coherence validation failed: {report.overall_score:.2f}"
                    )
                    if self.config.enable_strict_validation:
                        raise ValueError(
                            f"Story failed coherence check: {report.overall_score:.2f} "
                            f"< {self.config.min_coherence_score}"
                        )

            # ===== ETAP 8: STYLIZACJA JĘZYKOWA =====
            if start_stage.value <= PipelineStage.LANGUAGE_STYLIZATION.value:
                self.logger.info("💎 STAGE 8: Language Stylization")
                self.current_stage = PipelineStage.LANGUAGE_STYLIZATION

                style_result = await self._execute_stage(
                    PipelineStage.LANGUAGE_STYLIZATION,
                    retries=self.config.max_retries
                )

                self.context["stylized_text"] = style_result["text"]

            # ===== ETAP 9: REDAKCJA WYDAWNICZA =====
            if start_stage.value <= PipelineStage.EDITORIAL_REVIEW.value:
                self.logger.info("🔍 STAGE 9: Editorial Review")
                self.current_stage = PipelineStage.EDITORIAL_REVIEW

                editorial_result = await self._execute_stage(
                    PipelineStage.EDITORIAL_REVIEW,
                    retries=self.config.max_retries
                )

                self.context["final_text"] = editorial_result["text"]

            # ===== ETAP 10: FINALNE WYJŚCIE =====
            self.logger.info("📦 STAGE 10: Final Output")
            self.current_stage = PipelineStage.FINAL_OUTPUT

            output_result = await self._execute_stage(
                PipelineStage.FINAL_OUTPUT,
                retries=self.config.max_retries
            )

            # Oblicz czas
            generation_time = time.time() - start_time

            # Utwórz GenerationResult
            result = GenerationResult(
                success=True,
                project_id=self.context["brief"].project_id,
                brief=self.context["brief"],
                world=self.context["world"],
                characters=self.context["characters"],
                structure=self.context["structure"],
                segments=self.context.get("generated_segments", []),
                full_text=self.context.get("final_text", ""),
                total_word_count=len(self.context.get("final_text", "").split()),
                total_chapters=len(self.context.get("generated_segments", [])),
                generation_time_seconds=generation_time,
                coherence_report=self.context.get("coherence_report"),
                quality_score=self.context.get("coherence_report").overall_score
                if self.context.get("coherence_report")
                else 0.0,
                output_files=output_result.get("files", {}),
                expansion_data=output_result.get("expansion_data", {}),
            )

            self.logger.info(
                f"✅ Production complete! {result.total_word_count} words in "
                f"{generation_time:.1f}s"
            )

            return result

        except Exception as e:
            self.logger.error(f"Production failed at stage {self.current_stage}: {e}")

            # Zwróć wynik z błędem
            return GenerationResult(
                success=False,
                project_id=self.context.get("brief", type("", (), {"project_id": "unknown"})).project_id,
                brief=self.context.get("brief"),
                world=self.context.get("world"),
                characters=self.context.get("characters", []),
                structure=self.context.get("structure"),
                segments=[],
                full_text="",
                total_word_count=0,
                total_chapters=0,
                generation_time_seconds=time.time() - start_time,
                coherence_report=None,
                quality_score=0.0,
                output_files={},
                expansion_data={},
                errors=[str(e)],
            )

    async def _execute_stage(
        self,
        stage: PipelineStage,
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Wykonaj pojedynczy etap pipeline z retry logic

        Args:
            stage: Etap do wykonania
            retries: Liczba prób

        Returns:
            Wynik etapu

        Raises:
            Exception: Jeśli wszystkie próby zawiodły
        """
        agent = self._get_agent(stage)

        for attempt in range(retries):
            try:
                result = await agent.execute(self.context)

                # Waliduj output
                if not agent.validate_output(result):
                    raise ValueError(f"Agent {agent.__class__.__name__} returned invalid output")

                return result

            except Exception as e:
                self.logger.warning(
                    f"Stage {stage.name} failed (attempt {attempt + 1}/{retries}): {e}"
                )

                if attempt == retries - 1:
                    # Ostatnia próba - rzuć wyjątek
                    raise

                # Poczekaj przed retry
                await self._async_sleep(self.config.retry_delay_seconds * (attempt + 1))

        raise RuntimeError(f"Stage {stage.name} failed after {retries} attempts")

    async def _async_sleep(self, seconds: float):
        """Async sleep"""
        import asyncio
        await asyncio.sleep(seconds)
