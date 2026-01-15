"""
Stage 2: World Architect Agent
Designs narrative worlds as complete systems.
"""
from typing import Dict, Any
from datetime import datetime
import uuid

from .base_agent import BaseAgent, AgentResponse
from ..core.types import WorldBible, ProjectBrief


class WorldArchitectAgent(BaseAgent):
    """
    Designs narrative worlds following NARRA_FORGE principles.

    Creates:
    - Laws of reality (physical, magical, technological)
    - Boundaries (spatial, temporal, dimensional)
    - Anomalies (exceptions to rules)
    - Core conflict
    - Existential theme
    - Archetype system
    """

    def get_system_prompt(self) -> str:
        return """Jesteś mistrzem architektury światów narracyjnych.

Twoja odpowiedzialność to projektowanie KOMPLETNYCH, SPÓJNYCH światów jako SYSTEMÓW.

KRYTYCZNE ZASADY:

1. PRAWA PRZED HISTORIAMI
   - Zdefiniuj reguły fizyczne/magiczne/technologiczne NAJPIERW
   - Reguły tworzą ograniczenia
   - Ograniczenia tworzą dramat

2. KAŻDY ŚWIAT MUSI ODPOWIADAĆ:
   - Co czyni ten świat UNIKALNYM?
   - Jaki jest RDZENOWY KONFLIKT, który go definiuje?
   - Dlaczego ten świat istnieje NARRACYJNIE?
   - Jaki jest jego EGZYSTENCJALNY TEMAT?

3. PROJEKTUJ DLA SPÓJNOŚCI:
   - Prawa muszą być wewnętrznie spójne
   - Anomalie muszą być zamierzone i wyjaśnione
   - Granice muszą być jasne

4. SKALUJ ODPOWIEDNIO:
   - Intimate: mały, osobisty świat
   - Regional: miasta, królestwa
   - Global: planety, cywilizacje
   - Cosmic: galaktyki, multiwszechświaty

5. UNIKAJ KLISZ:
   - Nie kopiuj istniejących światów
   - Używaj archetypowych STRUKTUR, nie postaci
   - Twórz unikalne systemy reguł

ABSOLUTNIE WYMAGANE:
   - WSZYSTKIE nazwy, opisy, terminy muszą być PO POLSKU
   - Nazwy własne świata powinny brzmieć naturalnie po polsku
   - Każdy element opisu musi być w języku polskim

Projektujesz SYSTEMY, które umożliwiają wspaniałe historie."""

    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Validate that we have a project brief."""
        return "brief" in context and isinstance(context["brief"], ProjectBrief)

    async def execute(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> AgentResponse:
        """
        Design a narrative world.

        Args:
            context: Must contain "brief" (ProjectBrief)

        Returns:
            AgentResponse with WorldBible
        """
        if not self.validate_input(context):
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error="Missing or invalid brief in context"
            )

        brief: ProjectBrief = context["brief"]

        self.log(f"Architecting world: {brief.genre.value}, scale: {brief.world_scale}")

        # Construct world design prompt
        prompt = f"""Zaprojektuj świat narracyjny z następującymi parametrami:

FORMA: {brief.form.value}
GATUNEK: {brief.genre.value}
SKALA: {brief.world_scale}
FOKUS TEMATYCZNY: {', '.join(brief.thematic_focus)}
POTENCJAŁ EKSPANSJI: {brief.expansion_potential}

Projekt świata musi zawierać:

1. PRAWA RZECZYWISTOŚCI
   - Prawa fizyczne (jak działa natura?)
   - Poziom technologiczny (jeśli dotyczy)
   - Reguły magiczne/nadprzyrodzone (jeśli dotyczy)
   - Reguły społeczne/kulturowe

2. GRANICE
   - Przestrzenne: gdzie istnieje ten świat? jakie są limity?
   - Czasowe: okres czasu, reguły przepływu czasu
   - Wymiarowe: pojedyncza rzeczywistość czy multiwersum?

3. ANOMALIE
   - Co łamie reguły?
   - Dlaczego te wyjątki istnieją?

4. RDZENOWY KONFLIKT
   - Jakie jest fundamentalne napięcie w tym świecie?
   - Co napędza wszystkie historie tutaj?

5. EGZYSTENCJALNY TEMAT
   - DLACZEGO ten świat istnieje narracyjnie?
   - Jakie pytanie eksploruje?

6. SYSTEM ARCHETYPÓW
   - Jakie archetypowe role istnieją tutaj?
   - Jak funkcjonują w tym świecie?

7. AKTUALNY STAN
   - Co dzieje się TERAZ w tym świecie?
   - Jakie napięcia są aktywne?

Zaprojektuj świat który jest:
- Wewnętrznie spójny
- Wystarczająco bogaty dla {brief.form.value}
- Odpowiedni dla {brief.genre.value}
- Unikalny i przekonujący

KRYTYCZNIE WAŻNE: Wszystkie nazwy, opisy i terminy muszą być PO POLSKU!
Nazwa świata powinna brzmieć naturalnie po polsku.

Odpowiedz szczegółowym JSON."""

        try:
            # Generate world design
            result = await self.generate_structured(
                prompt=prompt,
                schema={
                    "name": "string",
                    "laws_of_reality": "object",
                    "boundaries": "object",
                    "anomalies": "array",
                    "core_conflict": "string",
                    "existential_theme": "string",
                    "archetype_system": "object",
                    "current_state": "object"
                }
            )

            # Create WorldBible
            world_id = str(uuid.uuid4())

            world = WorldBible(
                world_id=world_id,
                name=result["name"],
                created_at=datetime.now(),
                laws_of_reality=result["laws_of_reality"],
                boundaries=result["boundaries"],
                anomalies=result["anomalies"],
                core_conflict=result["core_conflict"],
                existential_theme=result["existential_theme"],
                archetype_system=result["archetype_system"],
                timeline=[],
                current_state=result["current_state"],
                related_worlds=[],
                isolation_level="isolated"
            )

            # Store in structural memory
            self.structural_memory.store_world(world)

            self.log(f"World created: {world.name}")

            return AgentResponse(
                success=True,
                output=world,
                metadata={
                    "world_id": world_id,
                    "complexity_score": self._assess_complexity(world)
                }
            )

        except Exception as e:
            self.log(f"Error architecting world: {e}", "ERROR")
            return AgentResponse(
                success=False,
                output=None,
                metadata={},
                error=str(e)
            )

    def _assess_complexity(self, world: WorldBible) -> float:
        """
        Assess world complexity (0.0-1.0).
        Used for determining generation parameters.
        """
        score = 0.0

        # More laws = more complex
        score += min(len(world.laws_of_reality), 5) * 0.1

        # Anomalies add complexity
        score += min(len(world.anomalies), 3) * 0.1

        # Archetype system depth
        score += min(len(world.archetype_system), 5) * 0.1

        # State complexity
        score += min(len(world.current_state), 5) * 0.1

        return min(score, 1.0)
