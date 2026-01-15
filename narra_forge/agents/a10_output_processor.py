"""
Agent 10: Output Processor

Odpowiedzialność:
- Finalizacja outputu
- Tworzenie plików (txt, JSON, audiobook format)
- Generowanie metadata
- Przygotowanie do publikacji

Model: Głównie local processing, opcjonalnie gpt-4o-mini dla audiobook markers
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from narra_forge.agents.base_agent import AnalysisAgent
from narra_forge.core.types import AgentResult, NarrativeOutput, PipelineStage


class OutputProcessorAgent(AnalysisAgent):
    """
    Agent finalizujący output i tworzący wszystkie pliki.

    Głównie local processing (bez AI).
    """

    def __init__(self, config, memory, router):
        super().__init__(
            config=config,
            memory=memory,
            router=router,
            stage=PipelineStage.OUTPUT_PROCESSING,
        )

    def get_system_prompt(self) -> str:
        return """Jesteś PROCESOREM WYJŚCIA w systemie produkcji narracji wydawniczych.

Twoja rola:
- Tworzysz znaczniki dla audiobooka (narrator, character voices)
- Przygotowujesz metadata
- NIE zmieniasz treści narracji

Format znaczników audiobooka:
[NARRATOR] - narrator opowiada
[CHARACTER:Name] - postać mówi
[PAUSE:short/medium/long] - pauza
[TONE:emotion] - ton głosu
[EMPHASIS] - nacisk

Przykład:
[NARRATOR] Spojrzał w niebo.
[CHARACTER:Anna] Musisz odejść. [TONE:sad]
[PAUSE:medium]
[NARRATOR] Wiedział, że ma rację."""

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Wykonaj finalizację outputu.

        Args:
            context: Zawiera wszystkie poprzednie wyniki

        Returns:
            AgentResult z NarrativeOutput
        """
        # Pobierz dane z kontekstu
        job_id = context.get("job_id", "unknown")
        brief = context.get("brief")
        world = context.get("world")
        characters = context.get("characters", [])
        structure = context.get("structure")
        segments = context.get("segments", [])

        final_text = (
            context.get("final_text")
            or context.get("stylized_text")
            or context.get("narrative_text")
        )

        if not final_text:
            self.add_error("No final text in context")
            return self._create_result(success=False, data={})

        # Utwórz output directory
        output_dir = self.config.output_dir / job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Zapisz główną narrację
        narrative_file = output_dir / "narrative.txt"
        narrative_file.write_text(final_text, encoding="utf-8")

        # 2. Stwórz wersję audiobook (z znacznikami)
        audiobook_text = await self._create_audiobook_version(final_text, characters)
        audiobook_file = output_dir / "narrative_audiobook.txt"
        audiobook_file.write_text(audiobook_text, encoding="utf-8")

        # 3. Metadata
        metadata = self._create_metadata(
            job_id=job_id,
            brief=brief,
            world=world,
            characters=characters,
            structure=structure,
            final_text=final_text,
            context=context,
        )
        metadata_file = output_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

        # 4. World export (dla potential expansion)
        world_export = self._export_world(world, characters)
        world_file = output_dir / "world_export.json"
        world_file.write_text(json.dumps(world_export, ensure_ascii=False, indent=2), encoding="utf-8")

        # 5. Stwórz NarrativeOutput
        word_count = len(final_text.split())

        # Agreguj koszty (jeśli są w kontekście)
        total_cost = context.get("total_cost", 0.0)
        total_tokens = context.get("total_tokens", 0)

        narrative_output = NarrativeOutput(
            job_id=job_id,
            success=True,
            narrative_text=final_text,
            audiobook_text=audiobook_text,
            world=world,
            characters=characters,
            structure=structure,
            segments=segments,
            production_type=brief.production_type if brief else None,
            genre=brief.genre if brief else None,
            word_count=word_count,
            quality_metrics=context.get("quality_metrics", {}),
            total_tokens=total_tokens,
            total_cost_usd=total_cost,
            generation_time_seconds=context.get("generation_time", 0.0),
            model_usage=context.get("model_usage", {}),
            output_dir=str(output_dir),
            files={
                "narrative": str(narrative_file),
                "audiobook": str(audiobook_file),
                "metadata": str(metadata_file),
                "world_export": str(world_file),
            },
            started_at=context.get("started_at", datetime.now()),
            completed_at=datetime.now(),
        )

        return self._create_result(
            success=True,
            data={
                "output": narrative_output,
                "files_created": list(narrative_output.files.keys()),
            },
        )

    async def _create_audiobook_version(self, text: str, characters: list) -> str:
        """Stwórz wersję z znacznikami dla audiobooka"""

        # Dla prostoty - dodaj podstawowe znaczniki
        # W pełnej wersji - użyj AI do inteligentnego dodania znaczników

        lines = text.split("\n")
        audiobook_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                audiobook_lines.append("")
                continue

            # Wykryj dialogi (proste - sprawdź czy jest " lub —)
            if '"' in line or "—" in line or "–" in line:
                # Może być dialog - zostawiamy bez zmiany
                audiobook_lines.append(line)
            else:
                # Narracja - dodaj znacznik
                audiobook_lines.append(f"[NARRATOR] {line}")

        return "\n".join(audiobook_lines)

    def _create_metadata(
        self,
        job_id: str,
        brief,
        world,
        characters,
        structure,
        final_text: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Stwórz metadata JSON"""

        return {
            "job_id": job_id,
            "generated_at": datetime.now().isoformat(),
            "production_info": {
                "type": brief.production_type.value if brief else "unknown",
                "genre": brief.genre.value if brief else "unknown",
                "inspiration": brief.inspiration if brief else None,
            },
            "world_info": {
                "world_id": world.world_id if world else None,
                "name": world.name if world else "Unknown",
                "core_conflict": world.core_conflict if world else None,
                "theme": world.existential_theme if world else None,
            },
            "characters": [
                {
                    "name": c.name,
                    "role": c.role,
                    "archetype": c.archetype,
                }
                for c in characters[:10]
            ] if characters else [],
            "structure": {
                "type": structure.structure_type if structure else "unknown",
                "acts": len(structure.acts) if structure else 0,
                "estimated_words": structure.estimated_word_count if structure else 0,
            } if structure else {},
            "output": {
                "word_count": len(final_text.split()),
                "character_count": len(final_text),
                "paragraph_count": len([p for p in final_text.split("\n\n") if p.strip()]),
            },
            "quality": context.get("quality_metrics", {}),
            "cost": {
                "total_usd": context.get("total_cost", 0.0),
                "total_tokens": context.get("total_tokens", 0),
            },
        }

    def _export_world(self, world, characters) -> Dict[str, Any]:
        """Export świata dla potential expansion"""

        if not world:
            return {}

        return {
            "world_id": world.world_id,
            "name": world.name,
            "genre": world.genre.value,
            "reality_laws": world.reality_laws.__dict__,
            "boundaries": world.boundaries.__dict__,
            "anomalies": world.anomalies,
            "core_conflict": world.core_conflict,
            "existential_theme": world.existential_theme,
            "description": world.description,
            "characters": [
                {
                    "character_id": c.character_id,
                    "name": c.name,
                    "role": c.role,
                    "evolution_capacity": c.evolution_capacity,
                }
                for c in characters
            ] if characters else [],
            "expansion_notes": "This world can be expanded in future productions",
        }
