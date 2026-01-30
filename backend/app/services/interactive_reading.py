"""
Interactive Reading Experience Mode - NarraForge 3.0 Phase 2

System interaktywnego czytania:
- Rozgałęziona narracja z wyborami czytelnika
- Dynamiczne generowanie ścieżek alternatywnych
- Śledzenie decyzji czytelnika
- Personalizacja doświadczenia
- Zakończenia wielowariantowe
- Eksport do formatów interaktywnych

"Twoja historia, Twoje wybory"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
import json
from datetime import datetime
import uuid

from app.services.llm_service import get_llm_service
from app.models.project import GenreType


# =============================================================================
# ENUMS
# =============================================================================

class ChoiceType(Enum):
    """Typy wyborów"""
    BINARY = "binary"  # Tak/Nie
    MULTIPLE = "multiple"  # Wiele opcji
    TIMED = "timed"  # Ograniczony czasowo
    HIDDEN = "hidden"  # Ukryte konsekwencje
    MORAL = "moral"  # Moralny dylemat
    ROMANCE = "romance"  # Wybór romantyczny
    COMBAT = "combat"  # Wybór walki/konfrontacji
    INVESTIGATION = "investigation"  # Wybór śledczy


class ConsequenceType(Enum):
    """Typy konsekwencji"""
    IMMEDIATE = "immediate"  # Natychmiastowa
    DELAYED = "delayed"  # Opóźniona
    CUMULATIVE = "cumulative"  # Kumulatywna
    RELATIONSHIP = "relationship"  # Wpływ na relacje
    STORY_BRANCH = "story_branch"  # Rozgałęzienie fabuły
    ENDING = "ending"  # Wpływ na zakończenie


class NodeType(Enum):
    """Typy węzłów narracyjnych"""
    STORY = "story"  # Normalny tekst narracyjny
    CHOICE = "choice"  # Punkt wyboru
    BRANCH = "branch"  # Rozgałęzienie
    MERGE = "merge"  # Scalenie ścieżek
    ENDING = "ending"  # Zakończenie
    CHECKPOINT = "checkpoint"  # Punkt zapisu


class EndingType(Enum):
    """Typy zakończeń"""
    GOOD = "good"
    BAD = "bad"
    NEUTRAL = "neutral"
    SECRET = "secret"
    TRUE = "true"  # Prawdziwe/kanoniczne zakończenie


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Choice:
    """Pojedynczy wybór"""
    choice_id: str
    text: str  # Tekst opcji wyświetlany graczowi
    subtext: Optional[str]  # Podpowiedź/kontekst
    target_node_id: str  # Dokąd prowadzi
    requirements: Dict[str, Any] = field(default_factory=dict)  # Wymagania do odblokowania
    consequences: List[str] = field(default_factory=list)  # Flagi/zmienne do ustawienia
    hidden: bool = False  # Czy ukryta do odkrycia

    def to_dict(self) -> Dict[str, Any]:
        return {
            "choice_id": self.choice_id,
            "text": self.text,
            "subtext": self.subtext,
            "target_node_id": self.target_node_id,
            "requirements": self.requirements,
            "consequences": self.consequences,
            "hidden": self.hidden
        }


@dataclass
class StoryNode:
    """Węzeł narracyjny"""
    node_id: str
    node_type: NodeType
    content: str  # Treść narracyjna
    choices: List[Choice] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    chapter: int = 1
    scene: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "content": self.content,
            "choices": [c.to_dict() for c in self.choices],
            "metadata": self.metadata,
            "chapter": self.chapter,
            "scene": self.scene
        }


@dataclass
class NarrativeBranch:
    """Gałąź narracyjna"""
    branch_id: str
    name: str
    description: str
    entry_node_id: str
    exit_node_ids: List[str]
    required_flags: List[str]
    exclusive_with: List[str]  # Wzajemnie wykluczające się gałęzie

    def to_dict(self) -> Dict[str, Any]:
        return {
            "branch_id": self.branch_id,
            "name": self.name,
            "description": self.description,
            "entry_node_id": self.entry_node_id,
            "exit_node_ids": self.exit_node_ids,
            "required_flags": self.required_flags,
            "exclusive_with": self.exclusive_with
        }


@dataclass
class GameState:
    """Stan gry/czytania"""
    state_id: str
    current_node_id: str
    visited_nodes: Set[str]
    flags: Dict[str, Any]  # Flagi i zmienne
    relationships: Dict[str, int]  # Relacje z postaciami (-100 do 100)
    inventory: List[str]  # Zebrane przedmioty/informacje
    choices_made: List[Dict[str, str]]  # Historia wyborów
    reading_time: float  # Czas czytania w minutach
    current_ending_path: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "current_node_id": self.current_node_id,
            "visited_nodes": list(self.visited_nodes),
            "flags": self.flags,
            "relationships": self.relationships,
            "inventory": self.inventory,
            "choices_made": self.choices_made,
            "reading_time": self.reading_time,
            "current_ending_path": self.current_ending_path
        }


@dataclass
class Ending:
    """Zakończenie historii"""
    ending_id: str
    ending_type: EndingType
    title: str
    content: str
    required_flags: Dict[str, Any]
    epilogue: Optional[str]
    achievements: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ending_id": self.ending_id,
            "ending_type": self.ending_type.value,
            "title": self.title,
            "content": self.content,
            "required_flags": self.required_flags,
            "epilogue": self.epilogue,
            "achievements": self.achievements
        }


@dataclass
class InteractiveStory:
    """Pełna interaktywna historia"""
    story_id: str
    title: str
    author: str
    genre: GenreType
    description: str
    nodes: Dict[str, StoryNode]
    branches: List[NarrativeBranch]
    endings: List[Ending]
    start_node_id: str
    total_word_count: int
    estimated_playthroughs: int
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "story_id": self.story_id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre.value,
            "description": self.description,
            "nodes_count": len(self.nodes),
            "branches_count": len(self.branches),
            "endings_count": len(self.endings),
            "start_node_id": self.start_node_id,
            "total_word_count": self.total_word_count,
            "estimated_playthroughs": self.estimated_playthroughs,
            "created_at": self.created_at.isoformat()
        }


# =============================================================================
# INTERACTIVE READING ENGINE
# =============================================================================

class InteractiveReadingEngine:
    """
    Silnik interaktywnego czytania.

    Funkcje:
    - Konwersja linearnej narracji na interaktywną
    - Generowanie punktów decyzyjnych
    - Tworzenie alternatywnych ścieżek
    - Zarządzanie stanem gry
    - Generowanie zakończeń
    """

    def __init__(self):
        self.llm_service = get_llm_service()
        self.stories: Dict[str, InteractiveStory] = {}
        self.game_states: Dict[str, GameState] = {}

    def _get_llm(self, tier: str = "mid"):
        """Get appropriate LLM based on tier"""
        return self.llm_service.get_client(tier)

    # =========================================================================
    # STORY CONVERSION
    # =========================================================================

    async def convert_to_interactive(
        self,
        title: str,
        author: str,
        genre: GenreType,
        chapters: List[str],
        choices_per_chapter: int = 3,
        num_endings: int = 3
    ) -> InteractiveStory:
        """
        Konwertuje linearną historię na interaktywną.
        """
        nodes = {}
        all_choices = []

        # Process each chapter
        for chapter_num, chapter_text in enumerate(chapters, 1):
            chapter_nodes = await self._create_chapter_nodes(
                chapter_text,
                chapter_num,
                choices_per_chapter,
                genre
            )

            for node in chapter_nodes:
                nodes[node.node_id] = node
                all_choices.extend(node.choices)

        # Connect nodes
        self._connect_nodes(nodes)

        # Generate branches
        branches = await self._identify_branches(nodes)

        # Generate endings
        endings = await self._generate_endings(
            title,
            genre,
            num_endings,
            list(nodes.values())
        )

        # Add ending nodes
        for ending in endings:
            ending_node = StoryNode(
                node_id=f"ending_{ending.ending_id}",
                node_type=NodeType.ENDING,
                content=ending.content,
                metadata={"ending_type": ending.ending_type.value}
            )
            nodes[ending_node.node_id] = ending_node

        # Calculate stats
        total_words = sum(len(node.content.split()) for node in nodes.values())
        estimated_playthroughs = max(2, len(endings))

        story = InteractiveStory(
            story_id=f"interactive_{title.lower().replace(' ', '_')[:15]}_{datetime.now().strftime('%H%M%S')}",
            title=title,
            author=author,
            genre=genre,
            description=f"Interactive version of {title}",
            nodes=nodes,
            branches=branches,
            endings=endings,
            start_node_id=list(nodes.keys())[0],
            total_word_count=total_words,
            estimated_playthroughs=estimated_playthroughs,
            created_at=datetime.now()
        )

        self.stories[story.story_id] = story
        return story

    async def _create_chapter_nodes(
        self,
        chapter_text: str,
        chapter_num: int,
        num_choices: int,
        genre: GenreType
    ) -> List[StoryNode]:
        """
        Tworzy węzły dla rozdziału z punktami wyboru.
        """
        prompt = f"""Przekształć poniższy tekst rozdziału w interaktywną narrację z {num_choices} punktami wyboru.

ROZDZIAŁ {chapter_num}:
{chapter_text[:4000]}

GATUNEK: {genre.value}

ZASADY:
1. Podziel tekst na segmenty (węzły narracyjne)
2. Między segmentami umieść punkty wyboru
3. Każdy wybór powinien mieć znaczące konsekwencje
4. Opcje wyboru powinny być ciekawe, nie oczywiste
5. Zachowaj główny wątek, ale dodaj warianty

Dla każdego segmentu i wyboru określ:

Odpowiedz w JSON:
{{
    "nodes": [
        {{
            "node_type": "story",
            "content": "Tekst narracyjny...",
            "scene": 1
        }},
        {{
            "node_type": "choice",
            "content": "Tekst przed wyborem...",
            "scene": 2,
            "choices": [
                {{
                    "text": "Opcja A",
                    "subtext": "podpowiedź (opcjonalna)",
                    "consequences": ["flag_a"]
                }},
                {{
                    "text": "Opcja B",
                    "consequences": ["flag_b"]
                }}
            ]
        }}
    ]
}}"""

        response = await self._get_llm("high").chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        nodes = []
        for i, node_data in enumerate(data.get("nodes", [])):
            node_id = f"ch{chapter_num}_node_{i+1}"

            # Parse node type
            try:
                node_type = NodeType(node_data.get("node_type", "story"))
            except ValueError:
                node_type = NodeType.STORY

            # Parse choices if present
            choices = []
            for j, choice_data in enumerate(node_data.get("choices", [])):
                choice = Choice(
                    choice_id=f"{node_id}_choice_{j+1}",
                    text=choice_data.get("text", ""),
                    subtext=choice_data.get("subtext"),
                    target_node_id=f"ch{chapter_num}_node_{i+2}",  # Will be updated later
                    consequences=choice_data.get("consequences", [])
                )
                choices.append(choice)

            node = StoryNode(
                node_id=node_id,
                node_type=node_type,
                content=node_data.get("content", ""),
                choices=choices,
                chapter=chapter_num,
                scene=node_data.get("scene", i + 1)
            )
            nodes.append(node)

        return nodes

    def _connect_nodes(self, nodes: Dict[str, StoryNode]) -> None:
        """
        Łączy węzły w grafie narracyjnym.
        """
        node_list = list(nodes.values())

        for i, node in enumerate(node_list[:-1]):
            next_node = node_list[i + 1]

            if node.choices:
                # Connect choices to next node or create branches
                for choice in node.choices:
                    choice.target_node_id = next_node.node_id
            else:
                # Auto-connect story nodes
                node.choices = [Choice(
                    choice_id=f"{node.node_id}_continue",
                    text="Kontynuuj...",
                    subtext=None,
                    target_node_id=next_node.node_id
                )]

    async def _identify_branches(
        self,
        nodes: Dict[str, StoryNode]
    ) -> List[NarrativeBranch]:
        """
        Identyfikuje gałęzie narracyjne.
        """
        branches = []
        choice_nodes = [n for n in nodes.values() if n.node_type == NodeType.CHOICE]

        for i, choice_node in enumerate(choice_nodes):
            branch = NarrativeBranch(
                branch_id=f"branch_{i+1}",
                name=f"Decision Point {i+1}",
                description=f"Choice at chapter {choice_node.chapter}",
                entry_node_id=choice_node.node_id,
                exit_node_ids=[c.target_node_id for c in choice_node.choices],
                required_flags=[],
                exclusive_with=[]
            )
            branches.append(branch)

        return branches

    async def _generate_endings(
        self,
        title: str,
        genre: GenreType,
        num_endings: int,
        nodes: List[StoryNode]
    ) -> List[Ending]:
        """
        Generuje alternatywne zakończenia.
        """
        prompt = f"""Stwórz {num_endings} różnych zakończeń dla interaktywnej historii.

TYTUŁ: {title}
GATUNEK: {genre.value}

KONTEKST (fragmenty historii):
{' '.join(n.content[:200] for n in nodes[:5])}

Stwórz zakończenia różnych typów:
- good: Dobre zakończenie
- bad: Złe zakończenie
- neutral: Neutralne/otwarte
- secret: Sekretne (trudne do osiągnięcia)

Dla każdego zakończenia określ:
1. title: Tytuł zakończenia
2. ending_type: good/bad/neutral/secret
3. content: Treść zakończenia (200-400 słów)
4. epilogue: Krótki epilog (opcjonalny)
5. required_flags: Jakie flagi/wybory prowadzą do tego zakończenia
6. achievements: Osiągnięcia za to zakończenie

Odpowiedz w JSON:
{{
    "endings": [
        {{
            "title": "...",
            "ending_type": "good",
            "content": "...",
            "epilogue": "...",
            "required_flags": {{"flag_name": true}},
            "achievements": ["achievement_name"]
        }}
    ]
}}"""

        response = await self._get_llm("high").chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        endings = []
        for i, ending_data in enumerate(data.get("endings", [])):
            try:
                ending_type = EndingType(ending_data.get("ending_type", "neutral"))
            except ValueError:
                ending_type = EndingType.NEUTRAL

            ending = Ending(
                ending_id=f"ending_{i+1}",
                ending_type=ending_type,
                title=ending_data.get("title", f"Ending {i+1}"),
                content=ending_data.get("content", ""),
                required_flags=ending_data.get("required_flags", {}),
                epilogue=ending_data.get("epilogue"),
                achievements=ending_data.get("achievements", [])
            )
            endings.append(ending)

        return endings

    # =========================================================================
    # GAME STATE MANAGEMENT
    # =========================================================================

    def create_game_state(self, story_id: str) -> GameState:
        """
        Tworzy nowy stan gry dla historii.
        """
        story = self.stories.get(story_id)
        if not story:
            raise ValueError(f"Story not found: {story_id}")

        state = GameState(
            state_id=str(uuid.uuid4()),
            current_node_id=story.start_node_id,
            visited_nodes=set(),
            flags={},
            relationships={},
            inventory=[],
            choices_made=[],
            reading_time=0.0,
            current_ending_path=None
        )

        self.game_states[state.state_id] = state
        return state

    def get_current_node(self, state: GameState, story_id: str) -> Optional[StoryNode]:
        """
        Pobiera aktualny węzeł dla stanu gry.
        """
        story = self.stories.get(story_id)
        if not story:
            return None
        return story.nodes.get(state.current_node_id)

    def make_choice(
        self,
        state: GameState,
        story_id: str,
        choice_id: str
    ) -> Tuple[bool, Optional[StoryNode]]:
        """
        Wykonuje wybór i aktualizuje stan gry.
        """
        story = self.stories.get(story_id)
        if not story:
            return False, None

        current_node = story.nodes.get(state.current_node_id)
        if not current_node:
            return False, None

        # Find the choice
        choice = None
        for c in current_node.choices:
            if c.choice_id == choice_id:
                choice = c
                break

        if not choice:
            return False, None

        # Check requirements
        for req_key, req_value in choice.requirements.items():
            if state.flags.get(req_key) != req_value:
                return False, None

        # Apply consequences
        for consequence in choice.consequences:
            if consequence.startswith("!"):
                state.flags[consequence[1:]] = False
            else:
                state.flags[consequence] = True

        # Record choice
        state.choices_made.append({
            "node_id": state.current_node_id,
            "choice_id": choice_id,
            "choice_text": choice.text
        })

        # Move to next node
        state.visited_nodes.add(state.current_node_id)
        state.current_node_id = choice.target_node_id

        next_node = story.nodes.get(choice.target_node_id)
        return True, next_node

    def get_available_choices(
        self,
        state: GameState,
        story_id: str
    ) -> List[Choice]:
        """
        Pobiera dostępne wybory dla aktualnego stanu.
        """
        node = self.get_current_node(state, story_id)
        if not node:
            return []

        available = []
        for choice in node.choices:
            # Check requirements
            meets_requirements = True
            for req_key, req_value in choice.requirements.items():
                if state.flags.get(req_key) != req_value:
                    meets_requirements = False
                    break

            if meets_requirements and not choice.hidden:
                available.append(choice)

        return available

    def check_ending(
        self,
        state: GameState,
        story_id: str
    ) -> Optional[Ending]:
        """
        Sprawdza czy gracz osiągnął zakończenie.
        """
        story = self.stories.get(story_id)
        if not story:
            return None

        current_node = story.nodes.get(state.current_node_id)
        if not current_node or current_node.node_type != NodeType.ENDING:
            return None

        # Find matching ending
        for ending in story.endings:
            matches = True
            for flag_key, flag_value in ending.required_flags.items():
                if state.flags.get(flag_key) != flag_value:
                    matches = False
                    break
            if matches:
                return ending

        # Default ending if no specific match
        return story.endings[0] if story.endings else None

    # =========================================================================
    # DYNAMIC CONTENT GENERATION
    # =========================================================================

    async def generate_dynamic_response(
        self,
        state: GameState,
        story_id: str,
        player_input: str
    ) -> str:
        """
        Generuje dynamiczną odpowiedź na podstawie inputu gracza.
        """
        story = self.stories.get(story_id)
        current_node = self.get_current_node(state, story_id)

        if not story or not current_node:
            return "Historia nie została znaleziona."

        prompt = f"""Jako narrator interaktywnej historii "{story.title}",
odpowiedz na akcję gracza w kontekście aktualnej sceny.

AKTUALNA SCENA:
{current_node.content[:500]}

FLAGI GRACZA: {state.flags}
RELACJE: {state.relationships}

AKCJA GRACZA: {player_input}

Wygeneruj krótką (2-3 zdania) odpowiedź narratora, która:
1. Reaguje na akcję gracza
2. Jest spójna z gatunkiem ({story.genre.value})
3. Może wpływać na fabułę

Odpowiedź:"""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    # =========================================================================
    # MANAGEMENT
    # =========================================================================

    def get_story(self, story_id: str) -> Optional[InteractiveStory]:
        """Pobiera historię"""
        return self.stories.get(story_id)

    def get_state(self, state_id: str) -> Optional[GameState]:
        """Pobiera stan gry"""
        return self.game_states.get(state_id)

    def list_stories(self) -> List[str]:
        """Lista historii"""
        return list(self.stories.keys())

    def get_story_stats(self, story_id: str) -> Dict[str, Any]:
        """Statystyki historii"""
        story = self.stories.get(story_id)
        if not story:
            return {}

        choice_nodes = len([n for n in story.nodes.values() if n.node_type == NodeType.CHOICE])
        total_choices = sum(len(n.choices) for n in story.nodes.values())

        return {
            "total_nodes": len(story.nodes),
            "choice_points": choice_nodes,
            "total_choices": total_choices,
            "endings": len(story.endings),
            "branches": len(story.branches),
            "word_count": story.total_word_count,
            "estimated_playtime_minutes": story.total_word_count // 200
        }


# =============================================================================
# SINGLETON
# =============================================================================

_interactive_engine: Optional[InteractiveReadingEngine] = None

def get_interactive_reading_engine() -> InteractiveReadingEngine:
    """Get singleton instance of interactive reading engine"""
    global _interactive_engine
    if _interactive_engine is None:
        _interactive_engine = InteractiveReadingEngine()
    return _interactive_engine
