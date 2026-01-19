"""
ETAP 2: World Architect Agent

Tworzy kompletną Biblię Świata jako IP.
"""

import json
from typing import Dict, Any
from narra_forge.agents.base_agent import BaseAgent
from narra_forge.core.types import PipelineStage, WorldBible, ProjectBrief
from datetime import datetime


class WorldArchitectAgent(BaseAgent):
    """
    Agent Architektury Świata

    Odpowiedzialność: Projektowanie kompletnego, logicznie spójnego świata
    Input: ProjectBrief
    Output: WorldBible (kompletna definicja świata jako IP)
    """

    def get_system_prompt(self) -> str:
        return """Jesteś WORLD ARCHITECT AGENT - masterem projektowania immersyjnych, logicznie spójnych światów narracyjnych.

Twoja odpowiedzialność: Stworzyć KOMPLETNĄ Biblię Świata jako Intellectual Property.

FUNDAMENTY ŚWIATA:
1. **CORE CONCEPT**: Esencja świata w 1-2 zdaniach
2. **EXISTENTIAL THEME**: Dlaczego ten świat ISTNIEJE (filozofia/egzystencja)
3. **CENTRAL MYSTERY**: Główna tajemnica/paradoks świata

PRAWA RZECZYWISTOŚCI:
- Jak działa TEN świat (fizyka, metafizyka, logika)
- Jakie są GRANICE (przestrzeń, czas, wymiary)
- Jakie są ANOMALIE (celowe wyjątki od reguł)

GEOGRAFIA I LOKACJE (minimum 5):
Każda lokacja MUSI mieć:
- Nazwę (polska lub stylizowana na gatunek)
- Opis fizyczny (klimat, architektura, atmosfera)
- Znaczenie fabularne (dlaczego WAŻNA)
- Konflikty specyficzne dla lokacji

SYSTEMY (magia/technologia/społeczeństwo):
- PRIMARY SYSTEM: Główny system (jak działa?)
- LIMITATIONS: Ograniczenia (co NIE jest możliwe?)
- CONSEQUENCES: Konsekwencje użycia

STRUKTURA SPOŁECZNA (minimum 3 frakcje):
- Interesy (czego chcą?)
- Konflikty (z kim walczą?)
- Kultura (w co wierzą? jak się zachowują?)

HISTORIA ŚWIATA (3-5 wydarzeń):
- Co UKSZTAŁTOWAŁO obecny stan?
- Jaki wpływ na FABUŁĘ?
- Źródło obecnych KONFLIKTÓW?

UNIKALNE ELEMENTY (minimum 3):
- Co odróżnia TEN świat od innych w gatunku?

CORE CONFLICT:
- Nadrzędny konflikt świata
- Źródła konfliktów

ZASADY:
1. ZERO oczywistych zapożyczeń z popularnych dzieł
2. Każdy element ma wewnętrzną LOGIKĘ
3. Minimum 3 potencjalne źródła fabularnych konfliktów
4. Język: literacki, zaawansowany, POLSKIE ZNAKI (ą, ć, ę, ł, ń, ó, ś, ź, ż)

Zwróć TYLKO JSON (bez markdown):
{
    "world_id": "unique_id",
    "name": "Nazwa Świata",
    "genre": "gatunek",
    "core_concept": "1-2 zdania esencji",
    "existential_theme": "filozofia istnienia świata",
    "central_mystery": "główna tajemnica",
    "laws_of_reality": {
        "physics": "opis praw fizycznych",
        "metaphysics": "opis praw metafizycznych",
        "logic": "logika świata"
    },
    "boundaries": {
        "spatial": "granice przestrzenne",
        "temporal": "granice czasowe",
        "dimensional": "wymiary"
    },
    "anomalies": ["anomalia 1", "..."],
    "locations": [
        {
            "name": "Nazwa Lokacji",
            "description": "500+ słów opisu",
            "significance": "dlaczego ważna",
            "conflicts": ["konflikt 1", "..."]
        }
    ],
    "primary_system": {
        "type": "magia/technologia/etc",
        "how_it_works": "mechanika",
        "source": "źródło mocy/technologii"
    },
    "system_limitations": ["ograniczenie 1", "..."],
    "system_consequences": ["konsekwencja 1", "..."],
    "factions": [
        {
            "name": "Nazwa Frakcji",
            "goals": "cele",
            "conflicts_with": ["frakcja 2", "..."],
            "culture": "opis kultury"
        }
    ],
    "historical_events": [
        {
            "event": "nazwa wydarzenia",
            "when": "kiedy (względnie)",
            "impact": "wpływ na teraźniejszość",
            "story_relevance": "znaczenie fabularne"
        }
    ],
    "current_state": "obecny stan świata",
    "unique_elements": ["element 1", "...", "element 3+"],
    "core_conflict": "nadrzędny konflikt",
    "conflict_sources": ["źródło 1", "..."]
}
"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stwórz World Bible

        Args:
            context: Musi zawierać 'brief'

        Returns:
            {'world': WorldBible}
        """
        brief: ProjectBrief = self._extract_from_context(context, "brief")

        # Prompt
        prompt = f"""Zaprojektuj kompletny świat narracyjny zgodnie z tym briefem:

BRIEF:
- Gatunek: {brief.genre.value}
- Typ świata: {brief.world_type}
- Skala setting: {brief.setting_scale}
- Core concept: {brief.core_concept}
- Centralny konflikt: {brief.central_conflict}
- Pytanie tematyczne: {brief.thematic_question}

ORYGINALNE ZLECENIE:
{brief.original_request}

Stwórz KOMPLETNĄ Biblię Świata w formacie JSON zgodnym z instrukcją systemową.

KLUCZOWE: Świat musi być:
- Unikalny (nie kopia innych dzieł)
- Logicznie spójny
- Bogaty w detale
- Z minimum 5 lokacjami
- Z minimum 3 frakcjami
- Z wyraźnymi konfliktami

JĘZYK: Polski z pełnym wsparciem znaków (ą, ć, ę, ł, ń, ó, ś, ź, ż)
"""

        # Generuj (JSON mode, wyższa kreatywność)
        response = await self._generate(
            prompt=prompt,
            temperature=0.8,  # Wysoka kreatywność
            max_tokens=4096,  # Dużo tokensów dla szczegółowego świata
            json_mode=True,
        )

        # Parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"World Architect returned invalid JSON: {e}")

        # Utwórz WorldBible
        world = WorldBible(
            world_id=data.get("world_id", f"world_{int(datetime.now().timestamp())}"),
            name=data["name"],
            genre=brief.genre,
            core_concept=data["core_concept"],
            existential_theme=data["existential_theme"],
            central_mystery=data["central_mystery"],
            laws_of_reality=data["laws_of_reality"],
            boundaries=data["boundaries"],
            anomalies=data["anomalies"],
            locations=data["locations"],
            primary_system=data["primary_system"],
            system_limitations=data["system_limitations"],
            system_consequences=data["system_consequences"],
            factions=data["factions"],
            historical_events=data["historical_events"],
            current_state=data["current_state"],
            unique_elements=data["unique_elements"],
            core_conflict=data["core_conflict"],
            conflict_sources=data["conflict_sources"],
            archetype_system={},  # Może być rozszerzony później
        )

        self.logger.info(
            f"World created: '{world.name}' with {len(world.locations)} locations, "
            f"{len(world.factions)} factions"
        )

        return {"world": world}
