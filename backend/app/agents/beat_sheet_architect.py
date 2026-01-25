"""
Beat Sheet Architect - Chain of Thought Planning for Narrative Generation

Implementacja metodologii "Łańcucha Myślowego" (Chain of Thought) do planowania narracji.
Zamiast bezpośredniej generacji prozy, model NAJPIERW tworzy plan (Beat Sheet),
a dopiero potem realizuje go w formie tekstu.

Rozwiązuje problemy:
1. Pętla narracyjna - wymusza postęp przez zdefiniowane punkty zwrotne
2. Gubienie wątku - jasna struktura sceny przed pisaniem
3. Niespójność - każdy beat ma przypisane postacie i cele

Architektura:
- Beat Sheet = lista 5 punktów zwrotnych dla każdej sceny
- Każdy beat wymusza zmianę stanu (lokalizacja/wiedza/relacja/decyzja)
- Walidacja Beat Sheet przed generacją prozy
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

from app.services.ai_service import get_ai_service, ModelTier

logger = logging.getLogger(__name__)


class BeatType(Enum):
    """Typy punktów zwrotnych w scenie"""
    OPENING_HOOK = "opening_hook"          # Mocne otwarcie przyciągające uwagę
    CONFLICT_INTRO = "conflict_intro"       # Wprowadzenie/eskalacja konfliktu
    COMPLICATION = "complication"           # Komplikacja/przeszkoda
    TURNING_POINT = "turning_point"         # Punkt zwrotny - zmiana kierunku
    CLIMAX = "climax"                       # Kulminacja sceny
    CLIFFHANGER = "cliffhanger"             # Hak na następną scenę
    # Additional types AI might return
    INCITING_INCIDENT = "inciting_incident" # Zdarzenie inicjujące
    RISING_ACTION = "rising_action"         # Wzrost napięcia
    FALLING_ACTION = "falling_action"       # Spadek napięcia
    RESOLUTION = "resolution"               # Rozwiązanie
    SETUP = "setup"                         # Wprowadzenie/setup
    REVELATION = "revelation"               # Odkrycie/rewelacja
    CONFRONTATION = "confrontation"         # Konfrontacja
    DECISION = "decision"                   # Decyzja
    CONSEQUENCE = "consequence"             # Konsekwencja


# Mapping of common AI responses to valid BeatTypes
BEAT_TYPE_ALIASES = {
    "opening": BeatType.OPENING_HOOK,
    "hook": BeatType.OPENING_HOOK,
    "intro": BeatType.CONFLICT_INTRO,
    "conflict": BeatType.CONFLICT_INTRO,
    "obstacle": BeatType.COMPLICATION,
    "twist": BeatType.TURNING_POINT,
    "midpoint": BeatType.TURNING_POINT,
    "peak": BeatType.CLIMAX,
    "crisis": BeatType.CLIMAX,
    "ending": BeatType.CLIFFHANGER,
    "suspense": BeatType.CLIFFHANGER,
}


def parse_beat_type(value: str) -> BeatType:
    """
    Safely parse beat_type from AI response, handling unknown values.
    """
    if not value:
        return BeatType.COMPLICATION

    value_lower = value.lower().strip()

    # Try direct enum match first
    try:
        return BeatType(value_lower)
    except ValueError:
        pass

    # Try aliases
    if value_lower in BEAT_TYPE_ALIASES:
        return BEAT_TYPE_ALIASES[value_lower]

    # Try partial match
    for beat_type in BeatType:
        if value_lower in beat_type.value or beat_type.value in value_lower:
            return beat_type

    # Default fallback based on position hints in the name
    if "open" in value_lower or "start" in value_lower or "begin" in value_lower:
        return BeatType.OPENING_HOOK
    if "conflict" in value_lower or "problem" in value_lower:
        return BeatType.CONFLICT_INTRO
    if "turn" in value_lower or "change" in value_lower or "shift" in value_lower:
        return BeatType.TURNING_POINT
    if "climax" in value_lower or "peak" in value_lower or "high" in value_lower:
        return BeatType.CLIMAX
    if "end" in value_lower or "cliff" in value_lower or "hook" in value_lower:
        return BeatType.CLIFFHANGER

    # Ultimate fallback
    return BeatType.COMPLICATION


@dataclass
class Beat:
    """Pojedynczy punkt zwrotny w scenie"""
    beat_number: int
    beat_type: BeatType
    description: str
    characters_involved: List[str]
    goal: str
    conflict: str
    change_type: str  # "location", "knowledge", "relationship", "decision", "stakes"
    change_description: str
    emotional_tone: str


@dataclass
class BeatSheet:
    """Pełny plan sceny z punktami zwrotnymi"""
    scene_number: int
    chapter_number: int
    total_beats: int
    beats: List[Beat]
    pov_character: str
    setting: str
    scene_goal: str
    scene_stakes: str
    forbidden_elements: List[str]
    required_progress: str  # Co MUSI się zmienić do końca sceny


@dataclass
class BeatSheetValidation:
    """Wynik walidacji Beat Sheet"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    progress_verified: bool


class BeatSheetArchitect:
    """
    Architekt Beat Sheet - planuje strukturę sceny przed pisaniem.

    Implementuje metodologię Chain of Thought:
    1. Analizuje kontekst i cel sceny
    2. Generuje Beat Sheet z 5 punktami zwrotnymi
    3. Waliduje postęp fabularny
    4. Przekazuje plan do generatora prozy
    """

    def __init__(self):
        self.ai_service = get_ai_service()
        self.name = "Beat Sheet Architect"

    async def create_beat_sheet(
        self,
        scene_number: int,
        total_scenes: int,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        pov_character: Dict[str, Any],
        active_characters: List[Dict[str, Any]],
        previous_scene_summary: str,
        current_location: str,
        scene_goal: str,
        forbidden_tropes: List[str],
        tier: ModelTier = ModelTier.TIER_2
    ) -> BeatSheet:
        """
        Tworzy Beat Sheet dla sceny metodą Chain of Thought.

        Args:
            scene_number: Numer sceny w rozdziale (1-5)
            total_scenes: Łączna liczba scen w rozdziale
            chapter_number: Numer rozdziału
            chapter_outline: Zarys rozdziału z celami
            pov_character: Postać POV (słownik z profilem)
            active_characters: Lista postaci obecnych w scenie
            previous_scene_summary: Streszczenie poprzedniej sceny
            current_location: Aktualna lokalizacja
            scene_goal: Cel fabularny sceny
            forbidden_tropes: Lista zakazanych tropów/klisz

        Returns:
            BeatSheet z 5 punktami zwrotnymi
        """
        logger.info(f"🎬 {self.name}: Planning scene {scene_number}/{total_scenes} (Chapter {chapter_number})")

        # Określ typ sceny na podstawie pozycji
        scene_type = self._determine_scene_type(scene_number, total_scenes)

        # Przygotuj listę postaci
        char_names = [c.get('name', 'Unknown') for c in active_characters]
        pov_name = pov_character.get('name', 'protagonist')

        # Prompt do generacji Beat Sheet
        prompt = self._build_beat_sheet_prompt(
            scene_number=scene_number,
            total_scenes=total_scenes,
            chapter_number=chapter_number,
            scene_type=scene_type,
            pov_name=pov_name,
            pov_wound=pov_character.get('wound', pov_character.get('ghost_wound', {}).get('wound', '')),
            char_names=char_names,
            previous_scene_summary=previous_scene_summary,
            current_location=current_location,
            scene_goal=scene_goal,
            chapter_goal=chapter_outline.get('goal', ''),
            forbidden_tropes=forbidden_tropes
        )

        system_prompt = self._build_architect_system_prompt()

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                tier=tier,
                temperature=0.7,
                max_tokens=2000,
                json_mode=True,
                prefer_anthropic=False,
                metadata={
                    "agent": self.name,
                    "task": "beat_sheet_creation",
                    "chapter": chapter_number,
                    "scene": scene_number
                }
            )

            # Parsuj odpowiedź JSON
            beat_sheet_data = json.loads(response.content)
            beat_sheet = self._parse_beat_sheet(
                data=beat_sheet_data,
                scene_number=scene_number,
                chapter_number=chapter_number,
                pov_name=pov_name,
                current_location=current_location,
                scene_goal=scene_goal,
                forbidden_tropes=forbidden_tropes
            )

            # Waliduj Beat Sheet
            validation = self._validate_beat_sheet(beat_sheet)
            if not validation.is_valid:
                logger.warning(f"⚠️ Beat Sheet validation failed: {validation.errors}")
                # Możemy tu dodać retry lub repair, ale dla prostoty kontynuujemy

            logger.info(f"✅ Beat Sheet created: {len(beat_sheet.beats)} beats, progress: {beat_sheet.required_progress}")
            return beat_sheet

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Beat Sheet JSON: {e}")
            # Fallback: stwórz podstawowy Beat Sheet
            return self._create_fallback_beat_sheet(
                scene_number, chapter_number, scene_type, pov_name,
                char_names, current_location, scene_goal, forbidden_tropes
            )

        except Exception as e:
            logger.error(f"❌ Beat Sheet creation failed: {e}", exc_info=True)
            raise RuntimeError(f"Beat Sheet creation failed for scene {scene_number}: {e}")

    def _determine_scene_type(self, scene_number: int, total_scenes: int) -> str:
        """Określa typ sceny na podstawie jej pozycji w rozdziale"""
        if scene_number == 1:
            return "OTWARCIE"
        elif scene_number == total_scenes:
            return "FINAŁ"
        elif scene_number == (total_scenes + 1) // 2:
            return "PUNKT_ZWROTNY"
        elif scene_number < total_scenes // 2:
            return "BUDOWANIE"
        else:
            return "ESKALACJA"

    def _build_architect_system_prompt(self) -> str:
        """System prompt dla architekta Beat Sheet"""
        return """Jesteś genialnym architektem narracji, specjalizującym się w bestsellerach.
Twoim zadaniem jest PLANOWANIE struktury sceny PRZED jej napisaniem.

## TWOJA ROLA
Nie piszesz prozy - projektujesz SZKIELET sceny.
Każda scena to 5 punktów zwrotnych (beats), które WYMUSZAJĄ postęp fabularny.

## ZASADY ABSOLUTNE

1. **POSTĘP JEST OBOWIĄZKOWY**
   - Scena MUSI kończyć się w INNYM stanie niż zaczęła
   - Minimum jedna zmiana: lokalizacja / wiedza / relacja / decyzja / stawka

2. **ŻADNYCH PĘTLI**
   - Bohater NIE może wrócić do punktu wyjścia
   - Każdy beat popycha akcję NAPRZÓD
   - Zakaz: "bohater się waha", "rozważa opcje", "zastanawia się"

3. **KONKRETNOŚĆ**
   - Każdy beat = konkretne DZIAŁANIE lub ZDARZENIE
   - Nie: "bohater czuje napięcie"
   - Tak: "bohater zauważa krew na klamce"

4. **SPÓJNOŚĆ POSTACI**
   - Tylko wymienione postacie mogą działać
   - Każda postać wchodząca do sceny musi z niej wyjść (lub zostać)

## FORMAT ODPOWIEDZI

Odpowiedz TYLKO w formacie JSON:
{
    "beats": [
        {
            "beat_number": 1,
            "beat_type": "opening_hook",
            "description": "Konkretny opis co się dzieje",
            "characters_involved": ["Imię1", "Imię2"],
            "goal": "Co ten beat osiąga fabularnie",
            "conflict": "Jaki konflikt/napięcie",
            "change_type": "location|knowledge|relationship|decision|stakes",
            "change_description": "Co się zmienia",
            "emotional_tone": "napięcie|strach|nadzieja|gniew|etc"
        }
    ],
    "scene_stakes": "Co jest stawką w tej scenie",
    "required_progress": "Co MUSI się zmienić do końca sceny"
}"""

    def _build_beat_sheet_prompt(
        self,
        scene_number: int,
        total_scenes: int,
        chapter_number: int,
        scene_type: str,
        pov_name: str,
        pov_wound: str,
        char_names: List[str],
        previous_scene_summary: str,
        current_location: str,
        scene_goal: str,
        chapter_goal: str,
        forbidden_tropes: List[str]
    ) -> str:
        """Buduje prompt do generacji Beat Sheet"""

        forbidden_str = "\n".join(f"- {trope}" for trope in forbidden_tropes) if forbidden_tropes else "- brak"

        return f"""# ZADANIE: Stwórz Beat Sheet dla Sceny {scene_number}/{total_scenes}

## KONTEKST
- **Rozdział**: {chapter_number}
- **Typ sceny**: {scene_type}
- **Cel rozdziału**: {chapter_goal}
- **Cel sceny**: {scene_goal}

## POV
- **Postać**: {pov_name}
- **Rana wewnętrzna**: {pov_wound}

## POSTACIE W SCENIE (TYLKO TE!)
{', '.join(char_names)}

## LOKALIZACJA
{current_location}

## POPRZEDNIA SCENA
{previous_scene_summary if previous_scene_summary else "Brak - to pierwsza scena rozdziału"}

## ZAKAZANE ELEMENTY (NIGDY ICH NIE UŻYWAJ!)
{forbidden_str}
- Tajemniczy nieznajomy wyłaniający się z cienia
- Wewnętrzny monolog o wahaniu/ucieczce
- Powrót do punktu wyjścia
- Wprowadzanie NOWYCH postaci spoza listy

## WYMAGANIA DLA TYPU SCENY: {scene_type}

{"OTWARCIE: Mocny hook (akcja/dialog), wprowadzenie konfliktu, zaskoczenie" if scene_type == "OTWARCIE" else ""}
{"BUDOWANIE: Pogłębianie konfliktu, rozwój relacji, podnoszenie stawki" if scene_type == "BUDOWANIE" else ""}
{"PUNKT_ZWROTNY: Rewelacja, zmiana kierunku, moment 'wszystko się zmienia'" if scene_type == "PUNKT_ZWROTNY" else ""}
{"ESKALACJA: Intensyfikacja konfliktu, decyzje pod presją, konsekwencje" if scene_type == "ESKALACJA" else ""}
{"FINAŁ: Kulminacja rozdziału, cliffhanger, poważna zmiana stanu" if scene_type == "FINAŁ" else ""}

## ZADANIE

Stwórz 5 KONKRETNYCH beatów dla tej sceny.
Każdy beat to działanie lub zdarzenie - nie stan emocjonalny.
Scena MUSI zakończyć się ZMIANĄ (lokalizacja/wiedza/relacja/decyzja/stawka).

Odpowiedz w formacie JSON zgodnym z systemem."""

    def _parse_beat_sheet(
        self,
        data: Dict[str, Any],
        scene_number: int,
        chapter_number: int,
        pov_name: str,
        current_location: str,
        scene_goal: str,
        forbidden_tropes: List[str]
    ) -> BeatSheet:
        """Parsuje odpowiedź JSON do obiektu BeatSheet"""

        beats = []
        for beat_data in data.get('beats', []):
            beat = Beat(
                beat_number=beat_data.get('beat_number', len(beats) + 1),
                beat_type=parse_beat_type(beat_data.get('beat_type', 'complication')),
                description=beat_data.get('description', ''),
                characters_involved=beat_data.get('characters_involved', [pov_name]),
                goal=beat_data.get('goal', ''),
                conflict=beat_data.get('conflict', ''),
                change_type=beat_data.get('change_type', 'knowledge'),
                change_description=beat_data.get('change_description', ''),
                emotional_tone=beat_data.get('emotional_tone', 'napięcie')
            )
            beats.append(beat)

        return BeatSheet(
            scene_number=scene_number,
            chapter_number=chapter_number,
            total_beats=len(beats),
            beats=beats,
            pov_character=pov_name,
            setting=current_location,
            scene_goal=scene_goal,
            scene_stakes=data.get('scene_stakes', ''),
            forbidden_elements=forbidden_tropes,
            required_progress=data.get('required_progress', 'Zmiana wiedzy lub lokalizacji')
        )

    def _validate_beat_sheet(self, beat_sheet: BeatSheet) -> BeatSheetValidation:
        """Waliduje Beat Sheet pod kątem kompletności i postępu"""

        errors = []
        warnings = []
        progress_verified = False

        # Sprawdź liczbę beatów
        if len(beat_sheet.beats) < 3:
            errors.append("Beat Sheet ma mniej niż 3 beaty - za mało struktury")
        if len(beat_sheet.beats) > 7:
            warnings.append("Beat Sheet ma więcej niż 7 beatów - może być zbyt skomplikowany")

        # Sprawdź czy jest postęp
        change_types = [b.change_type for b in beat_sheet.beats]
        if not change_types:
            errors.append("Żaden beat nie definiuje zmiany - scena bez postępu")
        else:
            progress_verified = True

        # Sprawdź czy ostatni beat ma istotną zmianę
        if beat_sheet.beats:
            last_beat = beat_sheet.beats[-1]
            if last_beat.change_type not in ['location', 'decision', 'stakes']:
                warnings.append("Ostatni beat nie kończy się silną zmianą (lokalizacja/decyzja/stawka)")

        # Sprawdź spójność postaci
        all_characters = set()
        for beat in beat_sheet.beats:
            all_characters.update(beat.characters_involved)

        if len(all_characters) > 6:
            warnings.append(f"Zbyt wiele postaci ({len(all_characters)}) - może być chaotycznie")

        is_valid = len(errors) == 0

        return BeatSheetValidation(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            progress_verified=progress_verified
        )

    def _create_fallback_beat_sheet(
        self,
        scene_number: int,
        chapter_number: int,
        scene_type: str,
        pov_name: str,
        char_names: List[str],
        current_location: str,
        scene_goal: str,
        forbidden_tropes: List[str]
    ) -> BeatSheet:
        """Tworzy podstawowy Beat Sheet gdy AI zawiedzie"""

        logger.warning(f"⚠️ Using fallback Beat Sheet for scene {scene_number}")

        # Podstawowa struktura 5 beatów
        beats = [
            Beat(
                beat_number=1,
                beat_type=BeatType.OPENING_HOOK,
                description="Mocne otwarcie - działanie lub dialog wprowadzający napięcie",
                characters_involved=[pov_name],
                goal="Przyciągnąć uwagę, wprowadzić konflikt",
                conflict="Zewnętrzna przeszkoda lub wewnętrzny dylemat",
                change_type="stakes",
                change_description="Stawka zostaje ujawniona",
                emotional_tone="napięcie"
            ),
            Beat(
                beat_number=2,
                beat_type=BeatType.CONFLICT_INTRO,
                description="Eskalacja konfliktu - przeszkoda lub komplikacja",
                characters_involved=char_names[:2] if len(char_names) >= 2 else [pov_name],
                goal="Podnieść napięcie",
                conflict="Konflikt interpersonalny lub zewnętrzny",
                change_type="knowledge",
                change_description="Nowa informacja zmienia perspektywę",
                emotional_tone="frustracja"
            ),
            Beat(
                beat_number=3,
                beat_type=BeatType.TURNING_POINT,
                description="Punkt zwrotny - niespodziewane odkrycie lub decyzja",
                characters_involved=[pov_name],
                goal="Zmienić kierunek akcji",
                conflict="Wewnętrzny konflikt prowadzi do wyboru",
                change_type="decision",
                change_description="Bohater podejmuje decyzję",
                emotional_tone="determinacja"
            ),
            Beat(
                beat_number=4,
                beat_type=BeatType.CLIMAX,
                description="Kulminacja - konsekwencje decyzji, działanie",
                characters_involved=char_names[:3] if len(char_names) >= 3 else [pov_name],
                goal="Rozstrzygnąć napięcie sceny",
                conflict="Konfrontacja lub odkrycie",
                change_type="relationship",
                change_description="Relacja między postaciami się zmienia",
                emotional_tone="intensywność"
            ),
            Beat(
                beat_number=5,
                beat_type=BeatType.CLIFFHANGER,
                description="Hak na następną scenę - nowe zagrożenie lub pytanie",
                characters_involved=[pov_name],
                goal="Zmusić czytelnika do czytania dalej",
                conflict="Nowa przeszkoda lub tajemnica",
                change_type="location",
                change_description="Bohater musi się przemieścić lub działać",
                emotional_tone="niepewność"
            )
        ]

        return BeatSheet(
            scene_number=scene_number,
            chapter_number=chapter_number,
            total_beats=5,
            beats=beats,
            pov_character=pov_name,
            setting=current_location,
            scene_goal=scene_goal,
            scene_stakes="Stawka wynikająca z celu sceny",
            forbidden_elements=forbidden_tropes,
            required_progress="Zmiana lokalizacji lub decyzja"
        )

    def format_beat_sheet_for_writer(self, beat_sheet: BeatSheet) -> str:
        """
        Formatuje Beat Sheet do przekazania agentowi piszącemu.
        Jasna, zwięzła instrukcja co ma się wydarzyć.
        """
        lines = [
            f"## BEAT SHEET - Scena {beat_sheet.scene_number}",
            f"POV: {beat_sheet.pov_character}",
            f"Lokalizacja: {beat_sheet.setting}",
            f"Cel: {beat_sheet.scene_goal}",
            f"Stawka: {beat_sheet.scene_stakes}",
            "",
            "### STRUKTURA (5 punktów zwrotnych):",
            ""
        ]

        for beat in beat_sheet.beats:
            lines.append(f"**Beat {beat.beat_number}: {beat.beat_type.value.upper()}**")
            lines.append(f"- Co się dzieje: {beat.description}")
            lines.append(f"- Postacie: {', '.join(beat.characters_involved)}")
            lines.append(f"- Konflikt: {beat.conflict}")
            lines.append(f"- Zmiana ({beat.change_type}): {beat.change_description}")
            lines.append(f"- Ton: {beat.emotional_tone}")
            lines.append("")

        lines.append("### WYMÓG KOŃCOWY:")
        lines.append(f"**{beat_sheet.required_progress}**")
        lines.append("")
        lines.append("### ZAKAZANE:")
        for forbidden in beat_sheet.forbidden_elements[:5]:
            lines.append(f"- {forbidden}")

        return "\n".join(lines)


def get_beat_sheet_architect() -> BeatSheetArchitect:
    """Zwraca instancję architekta Beat Sheet"""
    return BeatSheetArchitect()


__all__ = [
    'BeatType',
    'Beat',
    'BeatSheet',
    'BeatSheetValidation',
    'BeatSheetArchitect',
    'get_beat_sheet_architect',
]
