"""
Universe Memory System for NarraForge 2.0

Remembers everything created in a book universe.
Enables continuations, sequels, prequels, and spin-offs.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import logging

from app.services.ai_service import AIService
from app.models.project import GenreType

logger = logging.getLogger(__name__)


class ContinuationType(str, Enum):
    """Types of story continuations"""
    DIRECT_SEQUEL = "direct_sequel"  # What happens next
    PREQUEL = "prequel"  # What happened before
    SPINOFF = "spinoff"  # Different character's story
    SAME_WORLD_NEW_STORY = "same_world"  # Same world, new characters
    WHAT_IF = "what_if"  # Alternative version


@dataclass
class ContinuationSuggestion:
    """A suggested continuation for a completed book"""
    type: ContinuationType
    title_suggestions: List[str]
    description: str
    starting_point: Optional[str] = None
    focus_character: Optional[str] = None
    time_period: Optional[str] = None
    characters_to_continue: List[str] = field(default_factory=list)
    world_elements_to_reuse: List[str] = field(default_factory=list)
    divergence_point: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "title_suggestions": self.title_suggestions,
            "description": self.description,
            "starting_point": self.starting_point,
            "focus_character": self.focus_character,
            "time_period": self.time_period,
            "characters_to_continue": self.characters_to_continue,
            "world_elements_to_reuse": self.world_elements_to_reuse,
            "divergence_point": self.divergence_point
        }


@dataclass
class UniverseData:
    """Complete universe data for a book/series"""
    project_id: str
    title: str
    genre: GenreType

    # World data
    world_facts: Dict[str, Any] = field(default_factory=dict)
    locations: List[Dict] = field(default_factory=list)
    world_rules: List[str] = field(default_factory=list)
    history: Dict[str, Any] = field(default_factory=dict)

    # Character data
    characters: List[Dict] = field(default_factory=list)
    character_arcs: Dict[str, str] = field(default_factory=dict)
    relationships: Dict[str, List[Dict]] = field(default_factory=dict)

    # Plot data
    events: List[Dict] = field(default_factory=list)
    timeline: List[Dict] = field(default_factory=list)
    unresolved_threads: List[str] = field(default_factory=list)

    # Meta
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "project_id": self.project_id,
            "title": self.title,
            "genre": self.genre.value,
            "world_facts": self.world_facts,
            "locations": self.locations,
            "world_rules": self.world_rules,
            "history": self.history,
            "characters": self.characters,
            "character_arcs": self.character_arcs,
            "relationships": self.relationships,
            "events": self.events,
            "timeline": self.timeline,
            "unresolved_threads": self.unresolved_threads,
            "created_at": self.created_at.isoformat()
        }


class UniverseMemorySystem:
    """
    System for remembering and reusing book universes.
    Enables series, continuations, and expanded universes.
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()
        # In-memory universe store (in production, use database)
        self.universes: Dict[str, UniverseData] = {}
        self.series: Dict[str, List[str]] = {}  # series_id -> list of project_ids

    async def store_universe(
        self,
        project_id: str,
        title: str,
        genre: GenreType,
        world_bible: Dict,
        characters: List[Dict],
        plot_structure: Dict,
        chapters_content: str
    ) -> UniverseData:
        """
        Store complete universe data for a book.

        Args:
            project_id: Project ID
            title: Book title
            genre: Book genre
            world_bible: World bible data
            characters: Character profiles
            plot_structure: Plot structure data
            chapters_content: Combined chapter text

        Returns:
            UniverseData with extracted information
        """
        # Extract universe data using AI
        universe_data = UniverseData(
            project_id=project_id,
            title=title,
            genre=genre
        )

        # Extract world facts
        universe_data.world_facts = await self._extract_world_facts(world_bible)
        universe_data.locations = await self._extract_locations(world_bible, chapters_content)
        universe_data.world_rules = await self._extract_world_rules(world_bible)
        universe_data.history = await self._extract_history(world_bible)

        # Process characters
        universe_data.characters = characters
        universe_data.character_arcs = await self._extract_character_arcs(characters, chapters_content)
        universe_data.relationships = await self._map_relationships(characters)

        # Extract plot data
        universe_data.events = await self._extract_events(plot_structure, chapters_content)
        universe_data.timeline = await self._build_timeline(universe_data.events)
        universe_data.unresolved_threads = await self._find_unresolved_threads(chapters_content, plot_structure)

        # Store
        self.universes[project_id] = universe_data

        logger.info(f"Stored universe for project {project_id}: {title}")
        return universe_data

    async def suggest_continuations(self, project_id: str) -> List[ContinuationSuggestion]:
        """
        Suggest possible continuations for a completed book.

        Returns list of continuation suggestions based on:
        - Unresolved plot threads
        - Characters with development potential
        - World with unexplored areas
        - Times before/after the story
        """
        universe = self.universes.get(project_id)
        if not universe:
            return []

        suggestions = []

        # Type 1: Direct Sequel (if unresolved threads exist)
        if universe.unresolved_threads:
            sequel_titles = await self._generate_sequel_titles(universe)
            suggestions.append(ContinuationSuggestion(
                type=ContinuationType.DIRECT_SEQUEL,
                title_suggestions=sequel_titles,
                description="Bezpośrednia kontynuacja - co dzieje się potem?",
                starting_point=universe.unresolved_threads[0] if universe.unresolved_threads else None,
                characters_to_continue=[c.get("name", "") for c in universe.characters[:5]]
            ))

        # Type 2: Prequel (if rich history exists)
        if universe.history:
            prequel_titles = await self._generate_prequel_titles(universe)
            suggestions.append(ContinuationSuggestion(
                type=ContinuationType.PREQUEL,
                title_suggestions=prequel_titles,
                description="Historia przed historią - jak to się zaczęło?",
                time_period=str(universe.history.get("interesting_past_era", "Przeszłość"))
            ))

        # Type 3: Spin-off (interesting side characters)
        spinoff_chars = await self._find_spinoff_worthy_characters(universe)
        for char in spinoff_chars[:2]:  # Max 2 spin-off suggestions
            spinoff_titles = await self._generate_spinoff_titles(universe, char)
            suggestions.append(ContinuationSuggestion(
                type=ContinuationType.SPINOFF,
                title_suggestions=spinoff_titles,
                description=f"Historia {char} - ich własna przygoda",
                focus_character=char
            ))

        # Type 4: Same World, New Story (if rich world)
        if len(universe.locations) > 5 or len(universe.world_rules) > 3:
            same_world_titles = await self._generate_same_world_titles(universe)
            suggestions.append(ContinuationSuggestion(
                type=ContinuationType.SAME_WORLD_NEW_STORY,
                title_suggestions=same_world_titles,
                description="Ten sam fascynujący świat, zupełnie nowa historia",
                world_elements_to_reuse=universe.world_rules[:5] + [l.get("name", "") for l in universe.locations[:5]]
            ))

        # Type 5: What If (alternative version)
        divergence = await self._find_best_divergence_point(universe)
        if divergence:
            what_if_titles = await self._generate_what_if_titles(universe, divergence)
            suggestions.append(ContinuationSuggestion(
                type=ContinuationType.WHAT_IF,
                title_suggestions=what_if_titles,
                description="Co by było gdyby? Alternatywna wersja wydarzeń",
                divergence_point=divergence
            ))

        return suggestions

    async def create_continuation_context(
        self,
        original_project_id: str,
        continuation_type: ContinuationType,
        new_title: str
    ) -> Dict[str, Any]:
        """
        Create context for a continuation, carrying over relevant universe data.

        Returns context dict with inherited universe information.
        """
        universe = self.universes.get(original_project_id)
        if not universe:
            return {}

        context = {
            "original_project_id": original_project_id,
            "original_title": universe.title,
            "continuation_type": continuation_type.value,
            "new_title": new_title,
            "genre": universe.genre.value
        }

        # Type-specific context
        if continuation_type == ContinuationType.DIRECT_SEQUEL:
            context.update({
                "inherited_world": universe.world_facts,
                "returning_characters": universe.characters,
                "timeline_position": "after",
                "unresolved_threads": universe.unresolved_threads,
                "world_rules": universe.world_rules
            })

        elif continuation_type == ContinuationType.PREQUEL:
            context.update({
                "inherited_world": universe.world_facts,
                "world_rules": universe.world_rules,
                "timeline_position": "before",
                "known_future_events": universe.events[:3],  # What we know happens later
                "characters_ancestors": []  # To be developed
            })

        elif continuation_type == ContinuationType.SPINOFF:
            context.update({
                "inherited_world": universe.world_facts,
                "world_rules": universe.world_rules,
                "main_cast_cameos": [c.get("name", "") for c in universe.characters[:3]],
                "timeline_position": "parallel"
            })

        elif continuation_type == ContinuationType.SAME_WORLD_NEW_STORY:
            context.update({
                "inherited_world": universe.world_facts,
                "world_rules": universe.world_rules,
                "locations": universe.locations,
                "history": universe.history,
                "timeline_position": "any",
                "no_character_overlap": True
            })

        elif continuation_type == ContinuationType.WHAT_IF:
            context.update({
                "base_world": universe.world_facts,
                "base_characters": universe.characters,
                "divergence_point": context.get("divergence_point"),
                "timeline_position": "alternative"
            })

        return context

    # Private extraction methods

    async def _extract_world_facts(self, world_bible: Dict) -> Dict:
        """Extract key world facts from world bible."""
        return {
            "geography": world_bible.get("geography", {}),
            "cultures": world_bible.get("cultures", {}),
            "systems": world_bible.get("systems", {}),  # magic, tech, economy
            "glossary": world_bible.get("glossary", {})
        }

    async def _extract_locations(self, world_bible: Dict, content: str) -> List[Dict]:
        """Extract significant locations."""
        locations = []

        # From world bible
        if "geography" in world_bible:
            geo = world_bible["geography"]
            if isinstance(geo, dict):
                for name, desc in geo.items():
                    locations.append({
                        "name": name,
                        "description": str(desc)[:200],
                        "source": "world_bible"
                    })

        return locations[:20]  # Limit to 20 locations

    async def _extract_world_rules(self, world_bible: Dict) -> List[str]:
        """Extract world rules and laws."""
        rules = []

        systems = world_bible.get("systems", {})
        if isinstance(systems, dict):
            for system_name, system_data in systems.items():
                if isinstance(system_data, dict) and "rules" in system_data:
                    rules.extend(system_data["rules"][:5])
                elif isinstance(system_data, str):
                    rules.append(f"{system_name}: {system_data[:100]}")

        return rules[:15]

    async def _extract_history(self, world_bible: Dict) -> Dict:
        """Extract world history."""
        return {
            "summary": world_bible.get("history", {}).get("summary", ""),
            "key_events": world_bible.get("history", {}).get("events", [])[:10],
            "interesting_past_era": world_bible.get("history", {}).get("interesting_era", "")
        }

    async def _extract_character_arcs(self, characters: List[Dict], content: str) -> Dict[str, str]:
        """Extract character arcs summary."""
        arcs = {}
        for char in characters[:10]:
            name = char.get("name", "")
            arc = char.get("arc", {})
            if isinstance(arc, dict):
                arcs[name] = arc.get("summary", "Łuk rozwoju postaci")
            else:
                arcs[name] = str(arc)[:200]
        return arcs

    async def _map_relationships(self, characters: List[Dict]) -> Dict[str, List[Dict]]:
        """Map relationships between characters."""
        relationships = {}
        for char in characters:
            name = char.get("name", "")
            rels = char.get("relationships", {})
            if isinstance(rels, dict):
                relationships[name] = [
                    {"target": k, "type": v}
                    for k, v in rels.items()
                ]
        return relationships

    async def _extract_events(self, plot_structure: Dict, content: str) -> List[Dict]:
        """Extract key story events."""
        events = []

        plot_points = plot_structure.get("plot_points", {})
        if isinstance(plot_points, dict):
            for point_name, point_data in plot_points.items():
                events.append({
                    "name": point_name,
                    "description": str(point_data)[:200] if point_data else "",
                    "type": "plot_point"
                })

        return events

    async def _build_timeline(self, events: List[Dict]) -> List[Dict]:
        """Build chronological timeline from events."""
        # Simple ordering based on event list order
        return [
            {"order": i, "event": e["name"], "description": e.get("description", "")}
            for i, e in enumerate(events)
        ]

    async def _find_unresolved_threads(self, content: str, plot_structure: Dict) -> List[str]:
        """Find unresolved plot threads."""
        threads = []

        # Check subplots
        subplots = plot_structure.get("subplots", [])
        if isinstance(subplots, list):
            for subplot in subplots[:5]:
                if isinstance(subplot, dict):
                    if not subplot.get("resolved", True):
                        threads.append(subplot.get("name", "Nierozwiązany wątek"))

        # If no explicit unresolved threads, add generic ones
        if not threads:
            threads = [
                "Dalsze losy bohaterów",
                "Konsekwencje wydarzeń",
                "Nowe wyzwania"
            ]

        return threads

    async def _generate_sequel_titles(self, universe: UniverseData) -> List[str]:
        """Generate sequel title suggestions."""
        prompt = f"""
Zaproponuj 3 tytuły kontynuacji (sequela) dla książki "{universe.title}".
Tytuły powinny:
- Nawiązywać do oryginału
- Sugerować kontynuację historii
- Być intrygujące

Odpowiedz TYLKO listą 3 tytułów, po jednym w linii.
"""
        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=1,
                max_tokens=200
            )
            titles = [t.strip().strip('-').strip() for t in response.strip().split('\n') if t.strip()]
            return titles[:3]
        except:
            return [f"{universe.title} II", f"Powrót do {universe.title}", f"Po {universe.title}"]

    async def _generate_prequel_titles(self, universe: UniverseData) -> List[str]:
        """Generate prequel title suggestions."""
        prompt = f"""
Zaproponuj 3 tytuły prequela (historii przed historią) dla książki "{universe.title}".
Tytuły powinny sugerować przeszłość i genezę wydarzeń.

Odpowiedz TYLKO listą 3 tytułów.
"""
        try:
            response = await self.ai_service.generate(prompt=prompt, model_tier=1, max_tokens=200)
            titles = [t.strip().strip('-').strip() for t in response.strip().split('\n') if t.strip()]
            return titles[:3]
        except:
            return [f"Przed {universe.title}", f"Geneza", f"Początki"]

    async def _generate_spinoff_titles(self, universe: UniverseData, character: str) -> List[str]:
        """Generate spin-off title suggestions for a character."""
        return [f"Historia {character}", f"{character}: Osobista droga", f"Świat oczami {character}"]

    async def _generate_same_world_titles(self, universe: UniverseData) -> List[str]:
        """Generate titles for same-world different-story."""
        return ["Inne historie tego świata", "Z drugiej strony", "Nieznani bohaterowie"]

    async def _generate_what_if_titles(self, universe: UniverseData, divergence: str) -> List[str]:
        """Generate what-if title suggestions."""
        return [f"Gdyby... ({divergence})", f"Alternatywa", f"Inna droga"]

    async def _find_spinoff_worthy_characters(self, universe: UniverseData) -> List[str]:
        """Find characters worthy of a spin-off."""
        chars = []
        for char in universe.characters:
            role = char.get("role", "")
            # Supporting characters with potential
            if role in ["supporting", "deuteragonist", "ally", "rival"]:
                chars.append(char.get("name", ""))
        return chars[:3]

    async def _find_best_divergence_point(self, universe: UniverseData) -> Optional[str]:
        """Find the best point for a what-if divergence."""
        events = universe.events
        if events and len(events) > 2:
            # Choose a midpoint event
            mid_event = events[len(events) // 2]
            return mid_event.get("name", "Kluczowy moment")
        return None

    def load_universe(self, project_id: str) -> Optional[UniverseData]:
        """Load universe data for a project."""
        return self.universes.get(project_id)

    def get_series_books(self, series_id: str) -> List[str]:
        """Get all book IDs in a series."""
        return self.series.get(series_id, [])

    def add_to_series(self, series_id: str, project_id: str):
        """Add a book to a series."""
        if series_id not in self.series:
            self.series[series_id] = []
        if project_id not in self.series[series_id]:
            self.series[series_id].append(project_id)


# Singleton instance
_universe_system: Optional[UniverseMemorySystem] = None


def get_universe_system() -> UniverseMemorySystem:
    """Get or create universe memory system instance."""
    global _universe_system
    if _universe_system is None:
        _universe_system = UniverseMemorySystem()
    return _universe_system
