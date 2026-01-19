"""ETAP 10: Output Processor Agent - Finalne wyjście"""
import json
from pathlib import Path
from typing import Dict, Any
from narra_forge.agents.base_agent import BaseAgent
from narra_forge.core.types import PipelineStage


class OutputProcessorAgent(BaseAgent):
    """Agent Finalnego Wyjścia"""

    def get_system_prompt(self) -> str:
        return """Jesteś OUTPUT PROCESSOR AGENT - finalizujesz produkcję.

Twoje zadanie:
1. Zapisz tekst do pliku
2. Wygeneruj metadane
3. Przygotuj wersję audiobook (z znacznikami)
4. Przygotuj dane ekspansji (dla sequel/prequel)

Zwróć ścieżki do plików i metadane."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        final_text = self._extract_from_context(context, "final_text")
        brief = self._extract_from_context(context, "brief")
        world = self._extract_from_context(context, "world")

        # Utwórz folder output
        project_id = brief.project_id
        output_dir = self.config.output_path / project_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Zapisz tekst
        text_file = output_dir / "narracja.txt"
        text_file.write_text(final_text, encoding="utf-8")

        # Wersja audiobook (uproszczona - dodaj znaczniki)
        audiobook_text = final_text  # TODO: Dodaj znaczniki [PAUZA], [NARRATOR], etc.
        audiobook_file = output_dir / "narracja_audiobook.txt"
        audiobook_file.write_text(audiobook_text, encoding="utf-8")

        # Metadane
        metadata = {
            "project_id": project_id,
            "title": f"Narracja {project_id}",
            "genre": brief.genre.value,
            "form": brief.form.value,
            "word_count": len(final_text.split()),
            "world_name": world.name,
            "created_at": context.get("started_at"),
        }
        metadata_file = output_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

        # Dane ekspansji
        expansion_data = {
            "world_id": world.world_id,
            "characters": [{"name": c.name, "id": c.character_id} for c in context.get("characters", [])],
            "unresolved_threads": [],  # TODO: Wykryj niewykorzystane wątki
        }
        expansion_file = output_dir / "ekspansja.json"
        expansion_file.write_text(json.dumps(expansion_data, indent=2, ensure_ascii=False), encoding="utf-8")

        self.logger.info(f"Output saved to {output_dir}")

        return {
            "files": {
                "text_file": str(text_file),
                "audiobook_file": str(audiobook_file),
                "metadata_file": str(metadata_file),
                "expansion_file": str(expansion_file),
            },
            "expansion_data": expansion_data,
        }
