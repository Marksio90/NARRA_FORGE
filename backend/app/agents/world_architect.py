"""
WORLD_ARCHITECT agent
Builds detailed fictional worlds with geography, history, systems, and cultures
"""

from typing import Dict, Any
import json
import logging

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class WorldArchitect(BaseAgent):
    """
    World-building specialist
    
    Creates comprehensive World Bibles including:
    - Geography and locations
    - History and timeline
    - Systems (magic/technology/economy)
    - Cultures and societies
    - Rules and physics
    - Glossary of terms
    """
    
    def __init__(self):
        super().__init__("WORLD_ARCHITECT")
    
    def _build_prompt(self, task: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Build world-building prompt based on task and context
        """
        genre = context.get("genre", "sci-fi")
        parameters = context.get("parameters", {})
        
        world_detail_level = parameters.get("world_detail_level", "high")
        target_word_count = parameters.get("target_word_count", 90000)
        
        prompt = f"""Zaprojektuj kompletny, wewnętrznie spójny świat dla książki gatunku {genre}.

PARAMETRY:
- Poziom szczegółowości: {world_detail_level}
- Docelowa długość książki: ~{target_word_count} słów
- Gatunek: {genre}

ZADANIE:
Stwórz World Bible w formacie JSON zawierającą:

1. GEOGRAFIA I LOKACJE:
   - Typ świata (planeta/galaktyka/uniwersum/inne)
   - Główne lokacje (min. 5-10 dla {world_detail_level} detail)
   - Dla każdej lokacji: nazwa, typ, opis, populacja, znaczenie fabularne
   - Relacje przestrzenne między lokacjami

2. HISTORIA:
   - Ery historyczne (min. 3-5)
   - Kluczowe wydarzenia kształtujące obecność
   - Current year/era
   - Konflikty historyczne wpływające na teraźniejszość

3. SYSTEMY:
   {self._get_system_requirements(genre)}

4. KULTURY I SPOŁECZEŃSTWA:
   - Główne grupy kulturowe (min. 2-4)
   - Wartości, obyczaje, tradycje każdej kultury
   - Konflikty i sojusze między kulturami

5. ZASADY I FIZYKA:
   - Jak działa ten świat (fizyka, magia, technologia)
   - Jasne reguły i ograniczenia
   - Co jest możliwe, a co niemożliwe

6. GLOSSARIUSZ:
   - Kluczowe terminy specyficzne dla tego świata (min. 10-20)
   - Definicje i kontekst użycia

KLUCZOWE WYMAGANIA:
✓ SPÓJNOŚĆ - wszystkie elementy muszą ze sobą współgrać
✓ ORYGINALNOŚĆ - unikaj oczywistych tropów bez twista
✓ FUNKCJONALNOŚĆ - każdy element musi służyć narracji
✓ SZCZEGÓŁOWOŚĆ - {world_detail_level} level of detail
✓ WIARYGODNOŚĆ - świat musi mieć wewnętrzną logikę

Zwróć kompleksowe World Bible w formacie JSON."""

        return prompt
    
    def _get_system_requirements(self, genre: str) -> str:
        """Get genre-specific system requirements"""
        requirements = {
            "sci-fi": """
   - System technologiczny (FTL, AI, cyborgizacja, etc.)
   - Poziom rozwoju nauki
   - Wpływ technologii na społeczeństwo
   - System ekonomiczny (post-scarcity/kapitalizm/inne)
   - System polityczny (demokracja/autorytaryzm/federacja/inne)""",
            "fantasy": """
   - System magii (zasady, ograniczenia, koszty)
   - Rasy i ich właściwości
   - Mitologia i religie
   - System feudalny/polityczny
   - Artefakty i miejsca mocy""",
            "thriller": """
   - System prawny i egzekucja prawa
   - Organizacje (policja, przestępcze, wywiad)
   - Technologia dostępna w świecie
   - System społeczny i ekonomiczny""",
            "horror": """
   - Natura zagrożenia (supernatural/psychological)
   - Zasady działania zagrożenia
   - Historia miejsca/przekleństwa
   - Mitologia lokalna""",
        }
        return requirements.get(genre, """
   - System społeczny
   - System ekonomiczny
   - System polityczny
   - Technologia i jej wpływ""")
    
    def _post_process(
        self,
        result: Dict[str, Any],
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Post-process World Bible - parse JSON and validate structure
        """
        if not result["success"]:
            return result
        
        content = result["content"]
        
        # Try to extract JSON
        try:
            # Find JSON in markdown code blocks if present
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content
            
            # Parse JSON
            world_bible = json.loads(json_content)
            
            # Validate required keys
            required_keys = ["geography", "history", "systems", "cultures", "rules", "glossary"]
            missing_keys = [key for key in required_keys if key not in world_bible]
            
            if missing_keys:
                logger.warning(f"World Bible missing keys: {missing_keys}")
            
            result["world_bible"] = world_bible
            result["validated"] = len(missing_keys) == 0
            
            logger.info(f"World Bible parsed successfully ({len(world_bible)} sections)")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse World Bible JSON: {e}")
            result["world_bible"] = {"raw_content": content}
            result["validated"] = False
        
        return result


# Export instance
world_architect = WorldArchitect()
