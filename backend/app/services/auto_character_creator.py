"""
Auto Character Creator for NarraForge 2.0

Automatically creates unique, psychologically deep characters from title analysis
when characters are not explicitly specified by the user.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import random
import json

from app.services.ai_service import AIService
from app.services.titan_analyzer import TITANAnalysis, TITANDimension
from app.models.project import GenreType


@dataclass
class CharacterPsychology:
    """Deep psychological profile of a character"""
    wound: str = ""  # Past trauma
    ghost: str = ""  # What haunts them
    lie: str = ""  # False belief they hold
    want: str = ""  # External goal
    need: str = ""  # Internal need
    fear: str = ""  # Deepest fear
    strength: str = ""  # Core strength
    flaw: str = ""  # Fatal flaw


@dataclass
class CharacterProfile:
    """Complete character profile"""
    name: str
    role: str  # protagonist, antagonist, supporting, etc.
    age: int
    gender: str
    physical_description: str
    personality_traits: List[str]
    psychology: CharacterPsychology
    backstory: str
    voice_style: str  # How they speak
    signature_phrases: List[str]
    relationships: Dict[str, str] = field(default_factory=dict)
    arc_type: str = ""  # positive change, negative change, flat, etc.
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
            "relationships": self.relationships,
            "arc_type": self.arc_type,
            "cultural_background": self.cultural_background
        }


# Name pools by cultural region (for diverse character creation)
NAME_POOLS = {
    "polish": {
        "male": ["Jakub", "Antoni", "Jan", "Aleksander", "Filip", "Mikołaj", "Wojciech", "Kacper", "Adam", "Szymon", "Bartosz", "Mateusz", "Piotr", "Tomasz", "Michał"],
        "female": ["Zuzanna", "Julia", "Maja", "Zofia", "Hanna", "Lena", "Alicja", "Maria", "Amelia", "Oliwia", "Natalia", "Wiktoria", "Martyna", "Karolina", "Anna"]
    },
    "japanese": {
        "male": ["Haruki", "Takeshi", "Kenji", "Yuki", "Ryo", "Daiki", "Shun", "Hiroshi", "Kazuki", "Sota", "Akira", "Ren", "Kaito", "Yamato", "Hayate"],
        "female": ["Sakura", "Yuki", "Hana", "Aoi", "Mei", "Rin", "Mio", "Yuna", "Saki", "Akane", "Nozomi", "Ayaka", "Mika", "Emi", "Nanami"]
    },
    "african": {
        "male": ["Kwame", "Chibuike", "Oluwaseun", "Mandla", "Kofi", "Jabari", "Tau", "Dayo", "Emeka", "Thabo", "Amara", "Zaire", "Jelani", "Ayo", "Tendai"],
        "female": ["Amina", "Zainab", "Adaeze", "Thandiwe", "Aisha", "Chiamaka", "Fatima", "Nana", "Nneka", "Precious", "Blessing", "Khadija", "Yewande", "Oluwakemi", "Lindiwe"]
    },
    "latin_american": {
        "male": ["Santiago", "Mateo", "Sebastian", "Diego", "Leonardo", "Nicolas", "Miguel", "Daniel", "Alejandro", "Carlos", "Gabriel", "Andres", "Lucas", "Rafael", "Francisco"],
        "female": ["Sofia", "Valentina", "Isabella", "Camila", "Luciana", "Mariana", "Victoria", "Regina", "Jimena", "Fernanda", "Daniela", "Paula", "Gabriela", "Valeria", "Andrea"]
    },
    "arabic": {
        "male": ["Omar", "Ahmed", "Yusuf", "Hassan", "Khalid", "Ibrahim", "Tariq", "Malik", "Samir", "Rashid", "Faisal", "Karim", "Nabil", "Zaid", "Bilal"],
        "female": ["Fatima", "Aisha", "Layla", "Noor", "Sara", "Mariam", "Yasmin", "Hana", "Amira", "Lina", "Dalia", "Rania", "Salma", "Zeina", "Nadia"]
    },
    "indian": {
        "male": ["Arjun", "Vikram", "Rohan", "Aarav", "Vivaan", "Aditya", "Vihaan", "Sai", "Krishna", "Ishaan", "Aryan", "Kabir", "Shaurya", "Atharv", "Dhruv"],
        "female": ["Aanya", "Ananya", "Aadhya", "Ishita", "Priya", "Kavya", "Avni", "Riya", "Saanvi", "Diya", "Mira", "Anvi", "Tara", "Siya", "Kiara"]
    },
    "chinese": {
        "male": ["Wei", "Jian", "Ming", "Chen", "Lei", "Feng", "Hao", "Long", "Jun", "Tao", "Kai", "Bo", "Liang", "Cheng", "Yang"],
        "female": ["Mei", "Ling", "Yan", "Xia", "Hui", "Jing", "Xue", "Hong", "Yun", "Fang", "Qing", "Lan", "Zhen", "Ying", "Wen"]
    },
    "fantasy": {
        "male": ["Thorin", "Aldric", "Kael", "Draven", "Zephyr", "Ragnar", "Lysander", "Theron", "Caspian", "Fenris", "Vaelin", "Gideon", "Orion", "Silas", "Corvus"],
        "female": ["Elara", "Seraphina", "Astrid", "Lyra", "Freya", "Isolde", "Morgana", "Rhiannon", "Thalia", "Celestia", "Elowen", "Ariadne", "Niamh", "Aelwyn", "Ravenna"]
    },
    "scifi": {
        "male": ["Zane", "Axel", "Nova", "Orion", "Cade", "Atlas", "Phoenix", "Kel", "Jett", "Rex", "Vector", "Blaze", "Cyrus", "Echo", "Kai"],
        "female": ["Nova", "Lyra", "Zara", "Aria", "Luna", "Nyx", "Stellar", "Aurora", "Vega", "Sage", "Ember", "Raven", "Jade", "Quinn", "Zero"]
    }
}


class AutoCharacterCreator:
    """
    Automatically creates unique characters based on TITAN analysis.
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()

    async def create_characters_from_title(
        self,
        title: str,
        titan_analysis: TITANAnalysis,
        genre: GenreType,
        main_count: int = 4,
        supporting_count: int = 10,
        cultural_setting: str = "diverse"
    ) -> Dict[str, List[CharacterProfile]]:
        """
        Create complete character cast based on TITAN analysis.

        Returns dict with 'main' and 'supporting' character lists.
        """
        # Determine cultural pool based on setting
        name_pool = self._get_name_pool(cultural_setting, genre)

        # Create main characters
        main_characters = await self._create_main_characters(
            title, titan_analysis, genre, main_count, name_pool
        )

        # Create supporting characters
        supporting_characters = await self._create_supporting_characters(
            title, titan_analysis, genre, supporting_count, name_pool, main_characters
        )

        # Build relationships between characters
        self._build_relationships(main_characters, supporting_characters)

        return {
            "main": main_characters,
            "supporting": supporting_characters
        }

    def _get_name_pool(self, cultural_setting: str, genre: GenreType) -> Dict[str, List[str]]:
        """Get appropriate name pool based on cultural setting."""
        setting_lower = cultural_setting.lower()

        # Genre-specific pools
        if genre == GenreType.FANTASY:
            return NAME_POOLS["fantasy"]
        if genre == GenreType.SCI_FI:
            return NAME_POOLS["scifi"]

        # Culture-based pools
        if "azja" in setting_lower or "asian" in setting_lower:
            return random.choice([NAME_POOLS["japanese"], NAME_POOLS["chinese"], NAME_POOLS["indian"]])
        if "afryk" in setting_lower or "african" in setting_lower:
            return NAME_POOLS["african"]
        if "latin" in setting_lower or "america" in setting_lower:
            return NAME_POOLS["latin_american"]
        if "arab" in setting_lower or "middle" in setting_lower:
            return NAME_POOLS["arabic"]
        if "słowiań" in setting_lower or "polish" in setting_lower or "slav" in setting_lower:
            return NAME_POOLS["polish"]
        if "indi" in setting_lower:
            return NAME_POOLS["indian"]

        # Random selection for diverse setting
        pools = list(NAME_POOLS.keys())
        pools = [p for p in pools if p not in ["fantasy", "scifi"]]
        return NAME_POOLS[random.choice(pools)]

    async def _create_main_characters(
        self,
        title: str,
        titan: TITANAnalysis,
        genre: GenreType,
        count: int,
        name_pool: Dict[str, List[str]]
    ) -> List[CharacterProfile]:
        """Create main characters with deep psychology."""
        characters = []

        # Get archetype hints from TITAN
        implied = titan.get_dimension(TITANDimension.IMPLIED_CHARACTERS)
        protagonist_archetype = "Hero"
        antagonist_type = "Shadow"
        if implied:
            protagonist_archetype = implied.output.get("protagonist_archetype", "Hero")
            antagonist_type = implied.output.get("antagonist_type", "Shadow")

        # Create protagonist first
        protagonist = await self._create_single_character(
            title=title,
            titan=titan,
            genre=genre,
            role="protagonist",
            archetype=protagonist_archetype,
            name_pool=name_pool
        )
        characters.append(protagonist)

        # Create antagonist if count > 1
        if count > 1:
            antagonist = await self._create_single_character(
                title=title,
                titan=titan,
                genre=genre,
                role="antagonist",
                archetype=antagonist_type,
                name_pool=name_pool,
                existing_names=[protagonist.name]
            )
            characters.append(antagonist)

        # Create remaining main characters
        existing_names = [c.name for c in characters]
        remaining_roles = ["deuteragonist", "love_interest", "mentor", "ally", "rival"]
        for i in range(count - 2):
            if i < len(remaining_roles):
                role = remaining_roles[i]
            else:
                role = "main_character"

            char = await self._create_single_character(
                title=title,
                titan=titan,
                genre=genre,
                role=role,
                archetype=None,
                name_pool=name_pool,
                existing_names=existing_names
            )
            characters.append(char)
            existing_names.append(char.name)

        return characters

    async def _create_supporting_characters(
        self,
        title: str,
        titan: TITANAnalysis,
        genre: GenreType,
        count: int,
        name_pool: Dict[str, List[str]],
        main_characters: List[CharacterProfile]
    ) -> List[CharacterProfile]:
        """Create supporting characters."""
        characters = []
        existing_names = [c.name for c in main_characters]

        supporting_roles = [
            "family_member", "friend", "colleague", "informant",
            "authority_figure", "helper", "obstacle", "comic_relief",
            "wise_elder", "innocent", "trickster", "herald"
        ]

        for i in range(count):
            role = supporting_roles[i % len(supporting_roles)]

            char = await self._create_single_character(
                title=title,
                titan=titan,
                genre=genre,
                role=role,
                archetype=None,
                name_pool=name_pool,
                existing_names=existing_names,
                is_supporting=True
            )
            characters.append(char)
            existing_names.append(char.name)

        return characters

    async def _create_single_character(
        self,
        title: str,
        titan: TITANAnalysis,
        genre: GenreType,
        role: str,
        archetype: Optional[str],
        name_pool: Dict[str, List[str]],
        existing_names: List[str] = None,
        is_supporting: bool = False
    ) -> CharacterProfile:
        """Create a single character with AI assistance."""
        existing_names = existing_names or []

        # Get psychological context from TITAN
        psychology_context = ""
        psych_dim = titan.get_dimension(TITANDimension.DEEP_PSYCHOLOGY)
        if psych_dim:
            themes = psych_dim.output.get("psychological_themes", [])
            growth = psych_dim.output.get("growth_arc_type", "")
            psychology_context = f"""
Tematy psychologiczne do eksploracji: {', '.join(themes[:3]) if themes else 'typowe dla gatunku'}
Typ łuku rozwoju: {growth or 'transformacja pozytywna'}
"""

        # Get world context
        world_context = ""
        spatial_dim = titan.get_dimension(TITANDimension.SPATIAL_WORLD)
        if spatial_dim:
            locations = spatial_dim.output.get("location_hints", [])
            atmosphere = spatial_dim.output.get("atmosphere", "")
            world_context = f"""
Lokalizacje sugerowane: {', '.join(locations[:2]) if locations else 'różnorodne'}
Atmosfera świata: {atmosphere or 'do określenia przez AI'}
"""

        prompt = f"""Stwórz UNIKALNĄ postać dla książki "{title}" w gatunku {genre.value}.

ROLA: {role}
{'ARCHETYP: ' + archetype if archetype else ''}
{psychology_context}
{world_context}

WYMAGANIA:
1. Unikalne imię (NIE używaj: {', '.join(existing_names) if existing_names else 'brak ograniczeń'})
2. Głęboka psychologia z WOUND (rana z przeszłości), GHOST (co ich prześladuje), LIE (fałszywe przekonanie), WANT (cel zewnętrzny), NEED (potrzeba wewnętrzna), FEAR (najgłębszy strach)
3. Unikalna osobowość i sposób mówienia
4. Charakterystyczne frazy (2-3)
5. {'Krótki backstory' if is_supporting else 'Rozbudowany backstory'}

Odpowiedz TYLKO w formacie JSON:
{{
    "name": "Unikalne imię",
    "age": 30,
    "gender": "male/female/other",
    "physical_description": "Krótki opis wyglądu",
    "personality_traits": ["cecha1", "cecha2", "cecha3"],
    "psychology": {{
        "wound": "Rana z przeszłości",
        "ghost": "Co ich prześladuje",
        "lie": "Fałszywe przekonanie",
        "want": "Cel zewnętrzny",
        "need": "Potrzeba wewnętrzna",
        "fear": "Najgłębszy strach",
        "strength": "Główna siła",
        "flaw": "Główna słabość"
    }},
    "backstory": "Historia postaci",
    "voice_style": "Jak mówi ta postać",
    "signature_phrases": ["fraza1", "fraza2"],
    "arc_type": "positive_change/negative_change/flat/etc",
    "cultural_background": "Pochodzenie kulturowe"
}}"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=2,  # Use Tier 2 for character creation
                max_tokens=1500,
                temperature=0.8  # Higher creativity
            )

            # Parse response
            char_data = self._parse_character_json(response)

            # Create profile
            psychology = CharacterPsychology(
                wound=char_data.get("psychology", {}).get("wound", ""),
                ghost=char_data.get("psychology", {}).get("ghost", ""),
                lie=char_data.get("psychology", {}).get("lie", ""),
                want=char_data.get("psychology", {}).get("want", ""),
                need=char_data.get("psychology", {}).get("need", ""),
                fear=char_data.get("psychology", {}).get("fear", ""),
                strength=char_data.get("psychology", {}).get("strength", ""),
                flaw=char_data.get("psychology", {}).get("flaw", "")
            )

            return CharacterProfile(
                name=char_data.get("name", self._generate_fallback_name(name_pool, existing_names)),
                role=role,
                age=char_data.get("age", random.randint(20, 50)),
                gender=char_data.get("gender", random.choice(["male", "female"])),
                physical_description=char_data.get("physical_description", ""),
                personality_traits=char_data.get("personality_traits", []),
                psychology=psychology,
                backstory=char_data.get("backstory", ""),
                voice_style=char_data.get("voice_style", ""),
                signature_phrases=char_data.get("signature_phrases", []),
                arc_type=char_data.get("arc_type", "positive_change"),
                cultural_background=char_data.get("cultural_background", "")
            )

        except Exception as e:
            # Fallback: create basic character
            return self._create_fallback_character(role, name_pool, existing_names)

    def _parse_character_json(self, response: str) -> Dict:
        """Parse character JSON from AI response."""
        import re

        # Try direct parse
        try:
            return json.loads(response)
        except:
            pass

        # Try to extract JSON from code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # Try to find raw JSON
        json_match = re.search(r'\{[^{}]*"name"[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass

        return {}

    def _generate_fallback_name(
        self,
        name_pool: Dict[str, List[str]],
        existing_names: List[str]
    ) -> str:
        """Generate a fallback name if AI fails."""
        gender = random.choice(["male", "female"])
        available = [n for n in name_pool.get(gender, []) if n not in existing_names]

        if available:
            return random.choice(available)

        # Generate unique name
        base_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Quinn", "Avery"]
        for name in base_names:
            if name not in existing_names:
                return name

        return f"Character_{len(existing_names) + 1}"

    def _create_fallback_character(
        self,
        role: str,
        name_pool: Dict[str, List[str]],
        existing_names: List[str]
    ) -> CharacterProfile:
        """Create a basic fallback character."""
        gender = random.choice(["male", "female"])
        name = self._generate_fallback_name(name_pool, existing_names)

        return CharacterProfile(
            name=name,
            role=role,
            age=random.randint(20, 50),
            gender=gender,
            physical_description="Do uzupełnienia",
            personality_traits=["odważny", "zdeterminowany"],
            psychology=CharacterPsychology(
                wound="Trauma z przeszłości",
                ghost="Wspomnienia",
                lie="Fałszywe przekonanie o sobie",
                want="Osiągnąć cel",
                need="Zaakceptować siebie",
                fear="Porażka",
                strength="Determinacja",
                flaw="Upór"
            ),
            backstory="Do rozwinięcia",
            voice_style="Bezpośredni",
            signature_phrases=[]
        )

    def _build_relationships(
        self,
        main_characters: List[CharacterProfile],
        supporting_characters: List[CharacterProfile]
    ):
        """Build relationship network between characters."""
        relationship_types = [
            "family", "friend", "rival", "mentor", "student",
            "love_interest", "enemy", "colleague", "ally", "acquaintance"
        ]

        # Build relationships between main characters
        for i, char1 in enumerate(main_characters):
            for j, char2 in enumerate(main_characters):
                if i < j:  # Avoid duplicates
                    rel_type = random.choice(relationship_types)
                    char1.relationships[char2.name] = rel_type
                    # Reverse relationship
                    reverse_map = {
                        "mentor": "student",
                        "student": "mentor",
                        "family": "family",
                        "friend": "friend",
                        "enemy": "enemy",
                        "rival": "rival",
                        "love_interest": "love_interest",
                        "colleague": "colleague",
                        "ally": "ally",
                        "acquaintance": "acquaintance"
                    }
                    char2.relationships[char1.name] = reverse_map.get(rel_type, rel_type)

        # Connect supporting characters to main characters
        for supporting in supporting_characters:
            # Each supporting character knows at least one main character
            main_char = random.choice(main_characters)
            rel_type = random.choice(relationship_types)
            supporting.relationships[main_char.name] = rel_type


# Singleton instance
_character_creator: Optional[AutoCharacterCreator] = None


def get_character_creator() -> AutoCharacterCreator:
    """Get or create character creator instance."""
    global _character_creator
    if _character_creator is None:
        _character_creator = AutoCharacterCreator()
    return _character_creator
