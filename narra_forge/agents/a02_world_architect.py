"""
Agent 02: World Architect

Odpowiedzialność:
- Projektowanie kompletnego systemu świata (IP)
- Definiowanie praw rzeczywistości
- Określanie granic (przestrzenne, czasowe, wymiarowe)
- Identyfikacja konfliktu nadrzędnego
- Określenie tematu egzystencjalnego

Model: gpt-4o-mini (struktura)
"""
from typing import Any, Dict
from uuid import uuid4

from narra_forge.agents.base_agent import AnalysisAgent
from narra_forge.core.types import AgentResult, Genre, PipelineStage, RealityLaws, World, WorldBoundaries


class WorldArchitectAgent(AnalysisAgent):
    """
    Agent projektujący światy (IP-level).

    Tworzy kompletny system świata jako IP (Intellectual Property).
    """

    def __init__(self, config, memory, router):
        super().__init__(
            config=config,
            memory=memory,
            router=router,
            stage=PipelineStage.WORLD_ARCHITECTURE,
        )

    def get_system_prompt(self) -> str:
        return """Jesteś ARCHITEKTEM ŚWIATÓW w systemie produkcji narracji wydawniczych.

Twoja rola:
- Projektujesz KOMPLETNE SYSTEMY ŚWIATÓW (IP-level)
- Definiujesz prawa rzeczywistości (tworzą ograniczenia, nie możliwości)
- Określasz granice (przestrzenne, czasowe, wymiarowe)
- Identyfikujesz konflikt nadrzędny świata
- Definiujesz temat egzystencjalny

ZASADY PROJEKTOWANIA ŚWIATÓW:

1. **Świat to SYSTEM, nie dekoracja**
   - Ma prawa (physics, magic, technology)
   - Ma granice (spatial, temporal, dimensional)
   - Ma anomalie (celowe wyjątki od reguł)
   - Ma konflikt nadrzędny (tension na poziomie świata)
   - Ma temat egzystencjalny (głęboki, filozoficzny)

2. **Prawa tworzą OGRANICZENIA**
   - Nie: "Magia pozwala na wszystko"
   - Tak: "Magia wymaga ofiary, ma granice, niszczy użytkownika"

3. **Spójność i logika**
   - Świat musi być wewnętrznie spójny
   - Anomalie są CELOWE i uzasadnione
   - Konflikt nadrzędny wynika z natury świata

4. **Głębia, nie objętość**
   - Nie opisuj WSZYSTKIEGO
   - Zdefiniuj FUNDAMENTY i REGUŁY
   - Reszta wynika z systemu

Format wyjścia (JSON):
{
  "world_name": "Nazwa świata",
  "genre": "fantasy|scifi|horror|etc",
  "reality_laws": {
    "physics": {
      "type": "standard|altered|exotic",
      "key_differences": ["różnica1"],
      "constraints": ["ograniczenie1"]
    },
    "magic": {
      "exists": true|false,
      "system": "opis systemu magii",
      "cost": "co kosztuje użycie",
      "limits": ["limit1"]
    },
    "technology": {
      "level": "primitive|medieval|industrial|modern|advanced|exotic",
      "key_tech": ["technologia1"],
      "limitations": ["ograniczenie1"]
    }
  },
  "boundaries": {
    "spatial": {
      "size": "city|region|continental|planetary|galactic",
      "key_locations": ["lokacja1"],
      "edges": "Co jest na krańcach świata"
    },
    "temporal": {
      "span": "days|weeks|months|years|centuries|eternal",
      "time_flow": "normal|distorted|cyclical",
      "history_depth": "krótki opis historii"
    },
    "dimensional": {
      "planes": ["wymiar1"],
      "accessibility": "Jak się przemieszcza między wymiarami"
    }
  },
  "anomalies": [
    {
      "name": "Nazwa anomalii",
      "description": "Opis",
      "why_exists": "Uzasadnienie"
    }
  ],
  "core_conflict": "Centralny konflikt/napięcie świata",
  "existential_theme": "Głęboki temat filozoficzny",
  "atmosphere": "Ogólna atmosfera świata"
}

Projektuj światy jako SYSTEMY. Twórz OGRANICZENIA. Definiuj FUNDAMENTY."""

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Wykonaj projektowanie świata.

        Args:
            context: Zawiera 'analyzed_brief'

        Returns:
            AgentResult z zaprojektowanym światem
        """
        analyzed_brief = context.get("analyzed_brief")
        if not analyzed_brief:
            self.add_error("No analyzed brief in context")
            return self._create_result(success=False, data={})

        # Sprawdź czy użytkownik podał world_id (użycie istniejącego świata)
        world_id = context.get("brief", {}).world_id
        if world_id:
            # Użyj istniejącego świata
            world = await self.memory.structural.get_world(world_id)
            if world:
                return self._create_result(
                    success=True,
                    data={"world": world, "existing_world": True},
                )
            else:
                self.add_warning(f"World {world_id} not found, creating new")

        # Przygotuj prompt
        prompt = f"""Zaprojektuj kompletny system świata dla narracji:

GATUNEK: {analyzed_brief.get('genre')}
TEMATYKA: {analyzed_brief.get('themes', [])}
TON: {analyzed_brief.get('tone', 'universal')}
ELEMENTY KLUCZOWE: {analyzed_brief.get('key_elements', {})}
FOCUS: {analyzed_brief.get('narrative_focus', 'balanced')}

Zaprojektuj świat jako SYSTEM z prawami, granicami, konfliktami.
Zwróć kompletną strukturę jako JSON."""

        try:
            world_data, call = await self.call_model_json(
                prompt=prompt,
                temperature=0.8,  # Kreatywność w granicach struktury
                max_tokens=3000,
            )

            # Twórz World object
            world_id = f"world_{uuid4().hex[:12]}"

            world = World(
                world_id=world_id,
                name=world_data.get("world_name", "Unknown World"),
                genre=Genre(analyzed_brief.get("genre", "fantasy")),
                reality_laws=RealityLaws(
                    physics=world_data.get("reality_laws", {}).get("physics", {}),
                    magic=world_data.get("reality_laws", {}).get("magic"),
                    technology=world_data.get("reality_laws", {}).get("technology"),
                    constraints=world_data.get("reality_laws", {}).get("constraints", []),
                ),
                boundaries=WorldBoundaries(
                    spatial=world_data.get("boundaries", {}).get("spatial", {}),
                    temporal=world_data.get("boundaries", {}).get("temporal", {}),
                    dimensional=world_data.get("boundaries", {}).get("dimensional"),
                ),
                anomalies=world_data.get("anomalies", []),
                core_conflict=world_data.get("core_conflict", "Unknown conflict"),
                existential_theme=world_data.get("existential_theme", "Unknown theme"),
                description=world_data.get("atmosphere"),
            )

            # Zapisz do memory
            world_dict = {
                "world_id": world.world_id,
                "name": world.name,
                "genre": world.genre.value,
                "reality_laws": world.reality_laws.__dict__,
                "boundaries": world.boundaries.__dict__,
                "anomalies": world.anomalies,
                "core_conflict": world.core_conflict,
                "existential_theme": world.existential_theme,
                "description": world.description,
                "linked_worlds": [],
            }
            await self.memory.structural.save_world(world_dict)

            return self._create_result(
                success=True,
                data={
                    "world": world,
                    "world_data": world_data,
                    "existing_world": False,
                },
            )

        except Exception as e:
            self.add_error(f"World architecture failed: {str(e)}")
            return self._create_result(success=False, data={})
