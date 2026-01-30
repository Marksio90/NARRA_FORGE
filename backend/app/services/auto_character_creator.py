"""
Auto Character Creator v2.0 for NarraForge 2.0

ENHANCED: Creates characters ENTIRELY from title semantics.
NO FALLBACKS - every character must emerge from the title's essence.
Characters are not generated randomly - they are DERIVED from the title's DNA.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
import re

from app.services.ai_service import AIService
from app.services.titan_analyzer import TITANAnalysis, TITANDimension, ImpliedCharacter, TitleEssence
from app.models.project import GenreType


@dataclass
class CharacterPsychology:
    """Deep psychological profile derived from title themes"""
    wound: str = ""  # Past trauma - connected to title's emotional core
    ghost: str = ""  # What haunts them - connected to title's conflict
    lie: str = ""  # False belief - thematic opposition to title's truth
    want: str = ""  # External goal - derived from title's narrative promise
    need: str = ""  # Internal need - the title's thematic lesson
    fear: str = ""  # Deepest fear - shadow of the title's hope
    strength: str = ""  # Core strength - embodies title's positive theme
    flaw: str = ""  # Fatal flaw - embodies title's warning


@dataclass
class CharacterProfile:
    """Complete character profile - every element traces back to the title"""
    name: str  # Name that RESONATES with title's essence
    role: str  # Role determined by title's narrative needs
    age: int
    gender: str
    physical_description: str  # Appearance that SYMBOLIZES their title connection
    personality_traits: List[str]  # Traits that EMBODY title themes
    psychology: CharacterPsychology  # Psychology DERIVED from title
    backstory: str  # History that EXPLAINS their title connection
    voice_style: str  # Speech that REFLECTS title's tone
    signature_phrases: List[str]  # Phrases that ECHO title themes
    title_connection: str = ""  # EXPLICIT connection to title
    must_embody: List[str] = field(default_factory=list)  # What they MUST represent
    relationships: Dict[str, str] = field(default_factory=dict)
    arc_type: str = ""
    cultural_background: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "age": self.age,
            "gender": self.gender,
            "physical_description": self.physical_description,
            "personality_traits": self.personality_traits,
            "psychology": {
                "wound": self.psychology.wound,
                "ghost": self.psychology.ghost,
                "lie": self.psychology.lie,
                "want": self.psychology.want,
                "need": self.psychology.need,
                "fear": self.psychology.fear,
                "strength": self.psychology.strength,
                "flaw": self.psychology.flaw
            },
            "backstory": self.backstory,
            "voice_style": self.voice_style,
            "signature_phrases": self.signature_phrases,
            "title_connection": self.title_connection,
            "must_embody": self.must_embody,
            "relationships": self.relationships,
            "arc_type": self.arc_type,
            "cultural_background": self.cultural_background
        }


# Master prompt for title-driven character creation
CHARACTER_FROM_TITLE_PROMPT = """Jesteś ekspertem od tworzenia postaci literackich.

TYTUŁ KSIĄŻKI: "{title}"
GATUNEK: {genre}

ESENCJA TYTUŁU (DNA z którego WSZYSTKO musi wynikać):
- Rdzeń znaczeniowy: {core_meaning}
- Rdzeń emocjonalny: {emotional_core}
- Centralne pytanie: {central_question}
- Filary tematyczne: {thematic_pillars}
- Elementy symboliczne: {symbolic_elements}
- Elementy zakazane: {forbidden_elements}

POSTAĆ DO STWORZENIA:
- Rola: {role}
- Esencja (z analizy TITAN): {character_essence}
- Połączenie z tytułem: {title_connection}
- MUSI uosabiać: {must_embody}
- Sugerowane imiona (pasujące do tytułu): {name_suggestions}
- Psychologiczny profil wyjściowy: {psychological_seed}

TWOJA MISJA: Stwórz PEŁNY profil postaci, gdzie KAŻDY element jest BEZPOŚREDNIO powiązany z tytułem.

ZASADY:
1. IMIĘ musi REZONOWAĆ z esencją tytułu - nie może być przypadkowe
2. WYGLĄD musi SYMBOLIZOWAĆ połączenie z tytułem
3. PSYCHOLOGIA musi WYNIKAĆ z tematyki tytułu:
   - WOUND (rana) - trauma związana z tematem tytułu
   - GHOST (duch przeszłości) - co prześladuje, związane z konfliktem tytułu
   - LIE (kłamstwo) - fałszywe przekonanie będące przeciwieństwem prawdy tytułu
   - WANT (pragnienie) - cel zewnętrzny wynikający z obietnicy tytułu
   - NEED (potrzeba) - lekcja którą tytuł chce przekazać
   - FEAR (strach) - cień nadziei którą tytuł daje
4. BACKSTORY musi WYJAŚNIAĆ dlaczego ta postać MUSI istnieć w historii o tym tytule
5. GŁOS i FRAZY muszą ODZWIERCIEDLAĆ ton tytułu
6. ŁUK POSTACI musi służyć ODPOWIEDZI na centralne pytanie tytułu

ODPOWIEDZ W FORMACIE JSON:
{{
    "name": "Imię rezonujące z tytułem",
    "name_reasoning": "DLACZEGO to imię pasuje do tytułu",
    "age": 30,
    "gender": "male/female/other",
    "physical_description": "Wygląd SYMBOLIZUJĄCY połączenie z tytułem",
    "appearance_symbolism": "Co wygląd SYMBOLIZUJE w kontekście tytułu",
    "personality_traits": ["cecha uosabiająca temat1", "cecha uosabiająca temat2", "cecha uosabiająca temat3"],
    "psychology": {{
        "wound": "Rana związana z tematyką tytułu",
        "ghost": "Co prześladuje - związane z konfliktem tytułu",
        "lie": "Fałszywe przekonanie - przeciwieństwo prawdy tytułu",
        "want": "Cel zewnętrzny - z obietnicy narracyjnej tytułu",
        "need": "Potrzeba wewnętrzna - lekcja tytułu",
        "fear": "Strach - cień nadziei tytułu",
        "strength": "Siła uosabiająca pozytywny temat tytułu",
        "flaw": "Słabość uosabiająca ostrzeżenie tytułu"
    }},
    "backstory": "Historia WYJAŚNIAJĄCA połączenie z tytułem",
    "backstory_title_connection": "Jak backstory łączy się z tytułem",
    "voice_style": "Sposób mówienia ODZWIERCIEDLAJĄCY ton tytułu",
    "signature_phrases": ["fraza echująca temat1", "fraza echująca temat2"],
    "arc_type": "positive_change/negative_change/flat/testing - służący odpowiedzi na pytanie tytułu",
    "arc_connection_to_title": "Jak łuk postaci służy tytułowi",
    "cultural_background": "Pochodzenie PASUJĄCE do świata tytułu",
    "title_embodiment_summary": "Jak ta postać UCIELEŚNIA tytuł - podsumowanie"
}}"""


class AutoCharacterCreator:
    """
    Creates characters ENTIRELY from title semantics.
    NO FALLBACKS - every character emerges from the title's DNA.
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()

    async def create_characters_from_title(
        self,
        title: str,
        titan_analysis: TITANAnalysis,
        genre: GenreType,
        main_count: int = 4,
        supporting_count: int = 8
    ) -> Dict[str, List[CharacterProfile]]:
        """
        Create complete character cast DERIVED from title semantics.
        Every character traces back to the title's essence.
        """
        if not titan_analysis.essence:
            raise ValueError("TITAN analysis must include title essence for character creation")

        essence = titan_analysis.essence
        implied_characters = titan_analysis.get_implied_characters()

        # Phase 1: Create main characters from implied characters
        main_characters = await self._create_main_characters_from_essence(
            title=title,
            essence=essence,
            implied_characters=implied_characters,
            genre=genre,
            count=main_count
        )

        # Phase 2: Create supporting characters that serve the title's themes
        supporting_characters = await self._create_supporting_characters_from_essence(
            title=title,
            essence=essence,
            main_characters=main_characters,
            genre=genre,
            count=supporting_count
        )

        # Phase 3: Build relationships based on title dynamics
        await self._build_title_driven_relationships(
            main_characters,
            supporting_characters,
            essence
        )

        return {
            "main": main_characters,
            "supporting": supporting_characters
        }

    async def _create_main_characters_from_essence(
        self,
        title: str,
        essence: TitleEssence,
        implied_characters: List[ImpliedCharacter],
        genre: GenreType,
        count: int
    ) -> List[CharacterProfile]:
        """Create main characters from the title's implied characters."""
        characters = []

        # Use implied characters from TITAN analysis
        for i, implied in enumerate(implied_characters[:count]):
            char = await self._create_character_from_implied(
                title=title,
                essence=essence,
                implied=implied,
                genre=genre,
                existing_names=[c.name for c in characters]
            )
            characters.append(char)

        # If we need more characters, derive them from title themes
        if len(characters) < count:
            additional_roles = self._derive_additional_roles_from_title(
                essence=essence,
                existing_roles=[c.role for c in characters],
                needed=count - len(characters)
            )

            for role_info in additional_roles:
                char = await self._create_character_from_theme(
                    title=title,
                    essence=essence,
                    role_info=role_info,
                    genre=genre,
                    existing_names=[c.name for c in characters]
                )
                characters.append(char)

        return characters

    async def _create_supporting_characters_from_essence(
        self,
        title: str,
        essence: TitleEssence,
        main_characters: List[CharacterProfile],
        genre: GenreType,
        count: int
    ) -> List[CharacterProfile]:
        """Create supporting characters that serve the title's thematic needs."""
        characters = []
        existing_names = [c.name for c in main_characters]

        # Determine what supporting roles the title needs
        supporting_needs = self._analyze_supporting_needs_from_title(
            essence=essence,
            main_characters=main_characters,
            count=count
        )

        for need in supporting_needs:
            char = await self._create_supporting_character(
                title=title,
                essence=essence,
                need=need,
                genre=genre,
                existing_names=existing_names
            )
            characters.append(char)
            existing_names.append(char.name)

        return characters

    async def _create_character_from_implied(
        self,
        title: str,
        essence: TitleEssence,
        implied: ImpliedCharacter,
        genre: GenreType,
        existing_names: List[str]
    ) -> CharacterProfile:
        """Create a full character profile from an implied character seed."""
        prompt = CHARACTER_FROM_TITLE_PROMPT.format(
            title=title,
            genre=genre.value,
            core_meaning=essence.core_meaning,
            emotional_core=essence.emotional_core,
            central_question=essence.central_question,
            thematic_pillars=", ".join(essence.thematic_pillars),
            symbolic_elements=", ".join(essence.symbolic_elements),
            forbidden_elements=", ".join(essence.forbidden_elements),
            role=implied.role_in_story,
            character_essence=implied.essence,
            title_connection=implied.title_connection,
            must_embody=", ".join(implied.must_embody),
            name_suggestions=", ".join(implied.name_suggestions) if implied.name_suggestions else "do wygenerowania na podstawie tytułu",
            psychological_seed=json.dumps(implied.psychological_profile, ensure_ascii=False)
        )

        if existing_names:
            prompt += f"\n\nNIE UŻYWAJ tych imion (już zajęte): {', '.join(existing_names)}"

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=2,
                max_tokens=2000,
                temperature=0.75
            )

            data = self._parse_character_json(response)
            return self._build_character_profile(data, implied.role_in_story, implied)

        except Exception as e:
            # Even in error case, derive character from title - NO random fallbacks
            return await self._create_character_from_title_only(
                title=title,
                essence=essence,
                role=implied.role_in_story,
                genre=genre,
                existing_names=existing_names
            )

    async def _create_character_from_theme(
        self,
        title: str,
        essence: TitleEssence,
        role_info: Dict[str, Any],
        genre: GenreType,
        existing_names: List[str]
    ) -> CharacterProfile:
        """Create a character from a thematic role derived from the title."""
        # Create an implied character from the role info
        implied = ImpliedCharacter(
            essence=role_info.get("essence", ""),
            role_in_story=role_info.get("role", "supporting"),
            title_connection=role_info.get("title_connection", ""),
            archetypal_function=role_info.get("function", ""),
            psychological_profile={},
            name_suggestions=[],
            must_embody=role_info.get("must_embody", [])
        )

        return await self._create_character_from_implied(
            title=title,
            essence=essence,
            implied=implied,
            genre=genre,
            existing_names=existing_names
        )

    async def _create_supporting_character(
        self,
        title: str,
        essence: TitleEssence,
        need: Dict[str, Any],
        genre: GenreType,
        existing_names: List[str]
    ) -> CharacterProfile:
        """Create a supporting character that fulfills a thematic need."""
        prompt = f"""Stwórz WSPIERAJĄCĄ postać dla książki "{title}" w gatunku {genre.value}.

ESENCJA TYTUŁU:
- Rdzeń: {essence.core_meaning}
- Emocja: {essence.emotional_core}
- Tematy: {', '.join(essence.thematic_pillars)}

TA POSTAĆ MUSI SŁUŻYĆ:
- Funkcja: {need.get('function', 'supporting')}
- Tematyczne powiązanie: {need.get('thematic_connection', '')}
- MUSI reprezentować: {need.get('must_represent', '')}
- Relacja z głównymi postaciami: {need.get('relationship_purpose', '')}

NIE UŻYWAJ imion: {', '.join(existing_names)}

STWÓRZ postać gdzie WSZYSTKO wynika z tytułu - imię, wygląd, psychologia.

Odpowiedz w JSON:
{{
    "name": "Imię pasujące do tytułu",
    "name_reasoning": "Dlaczego to imię pasuje",
    "age": 35,
    "gender": "male/female",
    "physical_description": "Wygląd symbolizujący powiązanie z tytułem",
    "personality_traits": ["cecha1", "cecha2", "cecha3"],
    "psychology": {{
        "wound": "Rana związana z tytułem",
        "ghost": "Co prześladuje",
        "lie": "Fałszywe przekonanie",
        "want": "Cel zewnętrzny",
        "need": "Potrzeba wewnętrzna",
        "fear": "Strach",
        "strength": "Siła",
        "flaw": "Słabość"
    }},
    "backstory": "Krótka historia",
    "voice_style": "Sposób mówienia",
    "signature_phrases": ["fraza1"],
    "title_connection": "Jak łączy się z tytułem"
}}"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=1,
                max_tokens=1500,
                temperature=0.8
            )

            data = self._parse_character_json(response)
            return self._build_character_profile(data, need.get('function', 'supporting'), None)

        except Exception:
            return await self._create_character_from_title_only(
                title=title,
                essence=essence,
                role=need.get('function', 'supporting'),
                genre=genre,
                existing_names=existing_names
            )

    async def _create_character_from_title_only(
        self,
        title: str,
        essence: TitleEssence,
        role: str,
        genre: GenreType,
        existing_names: List[str]
    ) -> CharacterProfile:
        """Emergency character creation - still derives from title, never random."""
        prompt = f"""KRYTYCZNE: Stwórz postać WYŁĄCZNIE na podstawie tytułu "{title}".

Tytuł oznacza: {essence.core_meaning}
Emocja tytułu: {essence.emotional_core}
Rola postaci: {role}
Gatunek: {genre.value}

NIE UŻYWAJ imion: {', '.join(existing_names)}

Wszystko - imię, wygląd, psychologia - MUSI wynikać BEZPOŚREDNIO z tytułu.

JSON:
{{
    "name": "Imię z esencji tytułu",
    "age": 30,
    "gender": "male/female",
    "physical_description": "Wygląd symboliczny",
    "personality_traits": ["cecha1", "cecha2"],
    "psychology": {{"wound": "", "ghost": "", "lie": "", "want": "", "need": "", "fear": "", "strength": "", "flaw": ""}},
    "backstory": "Historia",
    "voice_style": "Głos",
    "signature_phrases": [],
    "title_connection": "Połączenie z tytułem"
}}"""

        response = await self.ai_service.generate(
            prompt=prompt,
            model_tier=1,
            max_tokens=1000,
            temperature=0.7
        )

        data = self._parse_character_json(response)
        return self._build_character_profile(data, role, None)

    def _derive_additional_roles_from_title(
        self,
        essence: TitleEssence,
        existing_roles: List[str],
        needed: int
    ) -> List[Dict[str, Any]]:
        """Derive additional character roles from title themes."""
        additional_roles = []

        # Map themes to potential character roles
        theme_to_role = {
            "miłość": {"role": "love_interest", "function": "romantic partner", "must_embody": ["miłość", "połączenie"]},
            "strata": {"role": "lost_one", "function": "catalyst for grief", "must_embody": ["utrata", "pamięć"]},
            "władza": {"role": "authority", "function": "power figure", "must_embody": ["władza", "kontrola"]},
            "odkupienie": {"role": "redeemer", "function": "path to redemption", "must_embody": ["odkupienie", "przebaczenie"]},
            "tajemnica": {"role": "keeper_of_secrets", "function": "holds crucial information", "must_embody": ["tajemnica", "wiedza"]},
            "zdrada": {"role": "betrayer", "function": "source of betrayal", "must_embody": ["zdrada", "oszustwo"]},
            "nadzieja": {"role": "beacon", "function": "source of hope", "must_embody": ["nadzieja", "światło"]},
            "strach": {"role": "embodiment_of_fear", "function": "represents fear", "must_embody": ["strach", "zagrożenie"]},
            "rodzina": {"role": "family_member", "function": "family connection", "must_embody": ["rodzina", "więzy"]},
            "przemiana": {"role": "transformer", "function": "catalyzes change", "must_embody": ["przemiana", "transformacja"]},
        }

        for theme in essence.thematic_pillars:
            if len(additional_roles) >= needed:
                break

            theme_lower = theme.lower()
            for key, role_info in theme_to_role.items():
                if key in theme_lower and role_info["role"] not in existing_roles:
                    role_info["essence"] = f"Postać uosabiająca temat '{theme}' z tytułu"
                    role_info["title_connection"] = f"Reprezentuje tematyczny filar: {theme}"
                    additional_roles.append(role_info)
                    existing_roles.append(role_info["role"])
                    break

        # If still need more, create generic thematic roles
        while len(additional_roles) < needed:
            theme = essence.thematic_pillars[len(additional_roles) % len(essence.thematic_pillars)] if essence.thematic_pillars else "centralny temat"
            additional_roles.append({
                "role": f"thematic_character_{len(additional_roles)}",
                "function": "embodies theme",
                "essence": f"Ucieleśnienie tematu: {theme}",
                "title_connection": f"Reprezentuje: {theme}",
                "must_embody": [theme]
            })

        return additional_roles[:needed]

    def _analyze_supporting_needs_from_title(
        self,
        essence: TitleEssence,
        main_characters: List[CharacterProfile],
        count: int
    ) -> List[Dict[str, Any]]:
        """Analyze what supporting characters the title thematically requires."""
        needs = []

        # Each main character might need a mirror, ally, or obstacle
        character_functions = ["mirror", "ally", "obstacle", "confidant", "tempter"]

        for i, main_char in enumerate(main_characters):
            if len(needs) >= count:
                break

            func = character_functions[i % len(character_functions)]
            theme = essence.thematic_pillars[i % len(essence.thematic_pillars)] if essence.thematic_pillars else "temat"

            needs.append({
                "function": func,
                "thematic_connection": theme,
                "must_represent": f"Aspekt tematu '{theme}' w relacji do {main_char.name}",
                "relationship_purpose": f"Służy rozwojowi {main_char.name} przez funkcję {func}"
            })

        # Add characters for unrepresented themes
        represented_themes = set()
        for char in main_characters:
            represented_themes.update(char.must_embody)

        for theme in essence.thematic_pillars:
            if len(needs) >= count:
                break

            if theme not in represented_themes:
                needs.append({
                    "function": "thematic_anchor",
                    "thematic_connection": theme,
                    "must_represent": f"Główny przedstawiciel tematu: {theme}",
                    "relationship_purpose": "Wzmacnia tematykę poprzez interakcje"
                })

        # Fill remaining with world-building characters
        while len(needs) < count:
            needs.append({
                "function": "world_anchor",
                "thematic_connection": essence.core_meaning,
                "must_represent": "Element świata tytułu",
                "relationship_purpose": "Buduje autentyczność świata"
            })

        return needs[:count]

    async def _build_title_driven_relationships(
        self,
        main_characters: List[CharacterProfile],
        supporting_characters: List[CharacterProfile],
        essence: TitleEssence
    ):
        """Build relationships that serve the title's thematic needs."""
        # Relationships between main characters should reflect title's central dynamics
        for i, char1 in enumerate(main_characters):
            for j, char2 in enumerate(main_characters):
                if i < j:
                    # Determine relationship based on their thematic roles
                    rel_type = self._determine_thematic_relationship(char1, char2, essence)
                    char1.relationships[char2.name] = rel_type
                    char2.relationships[char1.name] = self._reverse_relationship(rel_type)

        # Connect supporting to main in ways that serve themes
        for support in supporting_characters:
            # Find the main character this supporting character best connects to
            best_main = self._find_best_thematic_connection(support, main_characters, essence)
            rel_type = self._determine_supporting_relationship(support, best_main, essence)
            support.relationships[best_main.name] = rel_type

    def _determine_thematic_relationship(
        self,
        char1: CharacterProfile,
        char2: CharacterProfile,
        essence: TitleEssence
    ) -> str:
        """Determine relationship type based on thematic roles."""
        roles_combo = {char1.role, char2.role}

        if "protagonist" in roles_combo and "antagonist" in roles_combo:
            return "nemesis"
        if "protagonist" in roles_combo and "love_interest" in roles_combo:
            return "romantic"
        if "protagonist" in roles_combo and "mentor" in roles_combo:
            return "student_of"
        if "antagonist" in roles_combo and "ally" in roles_combo:
            return "enemy_of"

        # Default: determine by shared themes
        shared_themes = set(char1.must_embody) & set(char2.must_embody)
        if shared_themes:
            return "bonded_by_theme"

        return "acquaintance"

    def _reverse_relationship(self, rel_type: str) -> str:
        """Get the reverse of a relationship."""
        reverses = {
            "nemesis": "nemesis",
            "romantic": "romantic",
            "student_of": "mentor_to",
            "mentor_to": "student_of",
            "enemy_of": "enemy_of",
            "ally_of": "ally_of",
            "bonded_by_theme": "bonded_by_theme",
            "acquaintance": "acquaintance"
        }
        return reverses.get(rel_type, rel_type)

    def _find_best_thematic_connection(
        self,
        support: CharacterProfile,
        main_characters: List[CharacterProfile],
        essence: TitleEssence
    ) -> CharacterProfile:
        """Find the main character best connected thematically to a supporting character."""
        if not main_characters:
            raise ValueError("No main characters to connect to")

        best_match = main_characters[0]
        best_score = 0

        for main in main_characters:
            # Score based on shared thematic elements
            shared = len(set(support.must_embody) & set(main.must_embody))
            if shared > best_score:
                best_score = shared
                best_match = main

        return best_match

    def _determine_supporting_relationship(
        self,
        support: CharacterProfile,
        main: CharacterProfile,
        essence: TitleEssence
    ) -> str:
        """Determine relationship between supporting and main character."""
        if "mirror" in support.role.lower():
            return "reflects"
        if "ally" in support.role.lower():
            return "ally_of"
        if "obstacle" in support.role.lower():
            return "obstacle_to"
        if "confidant" in support.role.lower():
            return "confidant_of"
        if "tempter" in support.role.lower():
            return "tempts"

        return "connected_to"

    def _build_character_profile(
        self,
        data: Dict[str, Any],
        role: str,
        implied: Optional[ImpliedCharacter]
    ) -> CharacterProfile:
        """Build a CharacterProfile from parsed data."""
        psych_data = data.get("psychology", {})

        psychology = CharacterPsychology(
            wound=psych_data.get("wound", ""),
            ghost=psych_data.get("ghost", ""),
            lie=psych_data.get("lie", ""),
            want=psych_data.get("want", ""),
            need=psych_data.get("need", ""),
            fear=psych_data.get("fear", ""),
            strength=psych_data.get("strength", ""),
            flaw=psych_data.get("flaw", "")
        )

        return CharacterProfile(
            name=data.get("name", ""),
            role=role,
            age=data.get("age", 30),
            gender=data.get("gender", ""),
            physical_description=data.get("physical_description", ""),
            personality_traits=data.get("personality_traits", []),
            psychology=psychology,
            backstory=data.get("backstory", ""),
            voice_style=data.get("voice_style", ""),
            signature_phrases=data.get("signature_phrases", []),
            title_connection=data.get("title_connection", implied.title_connection if implied else ""),
            must_embody=data.get("must_embody", implied.must_embody if implied else []),
            arc_type=data.get("arc_type", ""),
            cultural_background=data.get("cultural_background", "")
        )

    def _parse_character_json(self, response: str) -> Dict:
        """Parse character JSON from AI response."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return {}


# Singleton instance
_character_creator: Optional[AutoCharacterCreator] = None


def get_character_creator() -> AutoCharacterCreator:
    """Get or create character creator instance."""
    global _character_creator
    if _character_creator is None:
        _character_creator = AutoCharacterCreator()
    return _character_creator
