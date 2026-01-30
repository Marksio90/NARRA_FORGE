"""
Character Visual Consistency System - NarraForge 3.0 Phase 2

System zapewnienia spójności wizualnej postaci:
- Generowanie szczegółowych opisów wizualnych
- Tworzenie reference sheets dla postaci
- Śledzenie wyglądu przez całą książkę
- Obsługa zmian wyglądu (rany, starzenie, transformacje)
- Integracja z pipeline'em ilustracji

"Każda postać wygląda tak samo w każdej scenie"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
from datetime import datetime

from app.services.llm_service import get_llm_service
from app.models.project import GenreType


# =============================================================================
# ENUMS
# =============================================================================

class BodyType(Enum):
    """Typ budowy ciała"""
    SLIM = "slim"
    ATHLETIC = "athletic"
    AVERAGE = "average"
    STOCKY = "stocky"
    MUSCULAR = "muscular"
    HEAVYSET = "heavyset"
    PETITE = "petite"
    TALL_SLIM = "tall_slim"


class FaceShape(Enum):
    """Kształt twarzy"""
    OVAL = "oval"
    ROUND = "round"
    SQUARE = "square"
    HEART = "heart"
    OBLONG = "oblong"
    DIAMOND = "diamond"
    RECTANGULAR = "rectangular"


class HairStyle(Enum):
    """Typ fryzury"""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    VERY_LONG = "very_long"
    BALD = "bald"
    SHAVED = "shaved"
    MOHAWK = "mohawk"
    BRAIDED = "braided"
    PONYTAIL = "ponytail"
    BUN = "bun"
    CURLY = "curly"
    WAVY = "wavy"
    STRAIGHT = "straight"
    DREADLOCKS = "dreadlocks"


class AgeCategory(Enum):
    """Kategoria wiekowa"""
    CHILD = "child"  # 0-12
    TEENAGER = "teenager"  # 13-19
    YOUNG_ADULT = "young_adult"  # 20-35
    ADULT = "adult"  # 36-55
    MIDDLE_AGED = "middle_aged"  # 56-70
    ELDERLY = "elderly"  # 71+


class AppearanceChangeType(Enum):
    """Typy zmian wyglądu"""
    INJURY = "injury"  # Rana, blizna
    AGING = "aging"  # Starzenie
    TRANSFORMATION = "transformation"  # Magiczna/fizyczna transformacja
    DISGUISE = "disguise"  # Przebranie
    EMOTIONAL_STATE = "emotional_state"  # Zmiana wyrazu twarzy
    CLOTHING_CHANGE = "clothing_change"  # Zmiana ubioru
    HAIR_CHANGE = "hair_change"  # Zmiana fryzury
    WEIGHT_CHANGE = "weight_change"  # Zmiana wagi


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class FacialFeatures:
    """Szczegóły twarzy"""
    face_shape: FaceShape
    eye_color: str
    eye_shape: str  # almond, round, hooded, etc.
    eyebrows: str  # thick, thin, arched, etc.
    nose: str  # straight, hooked, button, etc.
    lips: str  # full, thin, heart-shaped, etc.
    chin: str  # pointed, square, rounded, etc.
    cheekbones: str  # high, low, prominent, etc.
    skin_tone: str  # fair, olive, dark, etc.
    skin_texture: str  # smooth, freckled, weathered, etc.
    distinctive_marks: List[str] = field(default_factory=list)  # Blizny, znamiona, tatuaże

    def to_dict(self) -> Dict[str, Any]:
        return {
            "face_shape": self.face_shape.value,
            "eye_color": self.eye_color,
            "eye_shape": self.eye_shape,
            "eyebrows": self.eyebrows,
            "nose": self.nose,
            "lips": self.lips,
            "chin": self.chin,
            "cheekbones": self.cheekbones,
            "skin_tone": self.skin_tone,
            "skin_texture": self.skin_texture,
            "distinctive_marks": self.distinctive_marks
        }

    def to_prompt_string(self) -> str:
        """Konwertuje na string promptu"""
        parts = [
            f"{self.face_shape.value} face shape",
            f"{self.eye_color} {self.eye_shape} eyes",
            f"{self.eyebrows} eyebrows",
            f"{self.nose} nose",
            f"{self.lips} lips",
            f"{self.skin_tone} {self.skin_texture} skin"
        ]
        if self.distinctive_marks:
            parts.append(f"distinctive marks: {', '.join(self.distinctive_marks)}")
        return ", ".join(parts)


@dataclass
class HairDescription:
    """Opis włosów"""
    color: str
    style: HairStyle
    length: str  # inches or descriptive
    texture: str  # silky, coarse, fine, etc.
    additional_details: str = ""  # Highlights, streaks, etc.

    def to_dict(self) -> Dict[str, Any]:
        return {
            "color": self.color,
            "style": self.style.value,
            "length": self.length,
            "texture": self.texture,
            "additional_details": self.additional_details
        }

    def to_prompt_string(self) -> str:
        parts = [f"{self.color} {self.texture} hair", f"{self.style.value} hairstyle"]
        if self.additional_details:
            parts.append(self.additional_details)
        return ", ".join(parts)


@dataclass
class BodyDescription:
    """Opis ciała"""
    height: str  # descriptive or cm
    body_type: BodyType
    posture: str  # upright, slouched, confident, etc.
    distinctive_features: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height": self.height,
            "body_type": self.body_type.value,
            "posture": self.posture,
            "distinctive_features": self.distinctive_features
        }

    def to_prompt_string(self) -> str:
        parts = [
            f"{self.height} height",
            f"{self.body_type.value} build",
            f"{self.posture} posture"
        ]
        if self.distinctive_features:
            parts.extend(self.distinctive_features)
        return ", ".join(parts)


@dataclass
class ClothingStyle:
    """Styl ubioru"""
    typical_style: str  # formal, casual, military, etc.
    signature_items: List[str]  # Charakterystyczne elementy
    colors: List[str]  # Dominujące kolory
    accessories: List[str]  # Akcesoria
    current_outfit: Optional[str] = None  # Aktualny strój (jeśli określony)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "typical_style": self.typical_style,
            "signature_items": self.signature_items,
            "colors": self.colors,
            "accessories": self.accessories,
            "current_outfit": self.current_outfit
        }

    def to_prompt_string(self) -> str:
        if self.current_outfit:
            return self.current_outfit
        parts = [f"{self.typical_style} clothing style"]
        if self.signature_items:
            parts.append(f"wearing {', '.join(self.signature_items[:3])}")
        if self.accessories:
            parts.append(f"with {', '.join(self.accessories[:2])}")
        return ", ".join(parts)


@dataclass
class AppearanceChange:
    """Zmiana wyglądu w określonym momencie"""
    change_type: AppearanceChangeType
    chapter_number: int
    description: str
    affected_features: List[str]
    is_permanent: bool
    revert_chapter: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_type": self.change_type.value,
            "chapter_number": self.chapter_number,
            "description": self.description,
            "affected_features": self.affected_features,
            "is_permanent": self.is_permanent,
            "revert_chapter": self.revert_chapter
        }


@dataclass
class CharacterVisualProfile:
    """Pełny profil wizualny postaci"""
    character_name: str
    age_category: AgeCategory
    apparent_age: int  # Wiek w latach
    gender: str
    ethnicity: str

    face: FacialFeatures
    hair: HairDescription
    body: BodyDescription
    clothing: ClothingStyle

    # Wyrażanie emocji
    default_expression: str
    expression_tendencies: Dict[str, str] = field(default_factory=dict)  # emotion -> how they show it

    # Mowa ciała
    typical_gestures: List[str] = field(default_factory=list)
    stance: str = "neutral"

    # Zmiany w czasie
    appearance_changes: List[AppearanceChange] = field(default_factory=list)

    # Metadata
    reference_images: List[str] = field(default_factory=list)  # URLs do reference images
    visual_inspiration: List[str] = field(default_factory=list)  # Aktorzy, postacie, etc.

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_name": self.character_name,
            "age_category": self.age_category.value,
            "apparent_age": self.apparent_age,
            "gender": self.gender,
            "ethnicity": self.ethnicity,
            "face": self.face.to_dict(),
            "hair": self.hair.to_dict(),
            "body": self.body.to_dict(),
            "clothing": self.clothing.to_dict(),
            "default_expression": self.default_expression,
            "expression_tendencies": self.expression_tendencies,
            "typical_gestures": self.typical_gestures,
            "stance": self.stance,
            "appearance_changes": [c.to_dict() for c in self.appearance_changes],
            "reference_images": self.reference_images,
            "visual_inspiration": self.visual_inspiration
        }

    def get_prompt_for_chapter(self, chapter_number: int) -> str:
        """
        Generuje prompt uwzględniający zmiany wyglądu do danego rozdziału.
        """
        # Base appearance
        parts = [
            f"{self.gender}, {self.apparent_age} years old",
            f"{self.ethnicity} ethnicity",
            self.face.to_prompt_string(),
            self.hair.to_prompt_string(),
            self.body.to_prompt_string(),
            self.clothing.to_prompt_string(),
            f"{self.default_expression} expression"
        ]

        # Apply changes up to this chapter
        for change in self.appearance_changes:
            if change.chapter_number <= chapter_number:
                if change.is_permanent or (change.revert_chapter is None or chapter_number < change.revert_chapter):
                    parts.append(f"({change.description})")

        return ", ".join(parts)

    def get_full_description(self) -> str:
        """Zwraca pełny opis tekstowy"""
        return f"""
{self.character_name.upper()} - Visual Profile

BASIC INFO:
- Gender: {self.gender}
- Age: {self.apparent_age} years ({self.age_category.value})
- Ethnicity: {self.ethnicity}

FACE:
- Shape: {self.face.face_shape.value}
- Eyes: {self.face.eye_color}, {self.face.eye_shape}
- Eyebrows: {self.face.eyebrows}
- Nose: {self.face.nose}
- Lips: {self.face.lips}
- Skin: {self.face.skin_tone}, {self.face.skin_texture}
- Distinctive marks: {', '.join(self.face.distinctive_marks) if self.face.distinctive_marks else 'None'}

HAIR:
- Color: {self.hair.color}
- Style: {self.hair.style.value}
- Length: {self.hair.length}
- Texture: {self.hair.texture}

BODY:
- Height: {self.body.height}
- Build: {self.body.body_type.value}
- Posture: {self.body.posture}

CLOTHING:
- Style: {self.clothing.typical_style}
- Signature items: {', '.join(self.clothing.signature_items)}
- Colors: {', '.join(self.clothing.colors)}

EXPRESSION & BODY LANGUAGE:
- Default expression: {self.default_expression}
- Typical gestures: {', '.join(self.typical_gestures)}
"""


# =============================================================================
# CHARACTER VISUAL CONSISTENCY SYSTEM
# =============================================================================

class CharacterVisualSystem:
    """
    System zarządzania spójnością wizualną postaci.

    Funkcje:
    - Generowanie profili wizualnych z opisów tekstowych
    - Utrzymywanie spójności między ilustracjami
    - Śledzenie zmian wyglądu w czasie
    - Generowanie promptów dla różnych scen
    - Tworzenie reference sheets
    """

    def __init__(self):
        self.llm_service = get_llm_service()
        self.profiles: Dict[str, CharacterVisualProfile] = {}

    def _get_llm(self, tier: str = "mid"):
        """Get appropriate LLM based on tier"""
        return self.llm_service.get_client(tier)

    # =========================================================================
    # PROFILE GENERATION
    # =========================================================================

    async def generate_visual_profile(
        self,
        character_name: str,
        character_description: str,
        genre: GenreType = GenreType.DRAMA
    ) -> CharacterVisualProfile:
        """
        Generuje szczegółowy profil wizualny na podstawie opisu postaci.
        """
        prompt = f"""Na podstawie opisu postaci stwórz SZCZEGÓŁOWY profil wizualny.

NAZWA POSTACI: {character_name}

OPIS POSTACI:
{character_description}

GATUNEK: {genre.value}

Stwórz kompletny profil wizualny zawierający:

1. PODSTAWOWE INFO:
   - gender: płeć
   - apparent_age: wiek w latach (liczba)
   - age_category: child/teenager/young_adult/adult/middle_aged/elderly
   - ethnicity: etniczność (opisowo)

2. TWARZ (face):
   - face_shape: oval/round/square/heart/oblong/diamond/rectangular
   - eye_color: kolor oczu (szczegółowo, np. "deep emerald green")
   - eye_shape: kształt oczu (almond, round, hooded, upturned, etc.)
   - eyebrows: brwi (thick, thin, arched, straight, etc.)
   - nose: nos (straight, aquiline, button, roman, etc.)
   - lips: usta (full, thin, heart-shaped, etc.)
   - chin: podbródek (pointed, square, rounded, etc.)
   - cheekbones: kości policzkowe (high, low, prominent, etc.)
   - skin_tone: odcień skóry (fair, olive, tan, dark, etc.)
   - skin_texture: tekstura (smooth, freckled, weathered, scarred, etc.)
   - distinctive_marks: lista znaków szczególnych (blizny, znamiona, tatuaże)

3. WŁOSY (hair):
   - color: kolor (szczegółowo, np. "raven black with silver streaks")
   - style: short/medium/long/very_long/bald/shaved/mohawk/braided/ponytail/bun/curly/wavy/straight/dreadlocks
   - length: długość opisowo
   - texture: tekstura (silky, coarse, fine, thick, etc.)
   - additional_details: dodatkowe szczegóły

4. CIAŁO (body):
   - height: wzrost opisowo (np. "tall, around 185cm")
   - body_type: slim/athletic/average/stocky/muscular/heavyset/petite/tall_slim
   - posture: postura (upright, slouched, confident, guarded, etc.)
   - distinctive_features: lista cech (scars, tattoos, etc.)

5. UBIÓR (clothing):
   - typical_style: typowy styl (formal, casual, military, gothic, etc.)
   - signature_items: lista charakterystycznych elementów
   - colors: dominujące kolory
   - accessories: akcesoria

6. EKSPRESJA I MOWA CIAŁA:
   - default_expression: domyślny wyraz twarzy
   - expression_tendencies: jak pokazuje różne emocje
   - typical_gestures: typowe gesty
   - stance: postawa

7. INSPIRACJE WIZUALNE:
   - visual_inspiration: aktorzy/postacie fikcyjne podobne wizualnie

Odpowiedz w JSON zgodnym ze strukturą powyżej."""

        response = await self._get_llm("high").chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        # Parse face
        face_data = data.get("face", {})
        face = FacialFeatures(
            face_shape=FaceShape(face_data.get("face_shape", "oval")),
            eye_color=face_data.get("eye_color", "brown"),
            eye_shape=face_data.get("eye_shape", "almond"),
            eyebrows=face_data.get("eyebrows", "medium"),
            nose=face_data.get("nose", "straight"),
            lips=face_data.get("lips", "medium"),
            chin=face_data.get("chin", "rounded"),
            cheekbones=face_data.get("cheekbones", "medium"),
            skin_tone=face_data.get("skin_tone", "fair"),
            skin_texture=face_data.get("skin_texture", "smooth"),
            distinctive_marks=face_data.get("distinctive_marks", [])
        )

        # Parse hair
        hair_data = data.get("hair", {})
        try:
            hair_style = HairStyle(hair_data.get("style", "medium"))
        except ValueError:
            hair_style = HairStyle.MEDIUM

        hair = HairDescription(
            color=hair_data.get("color", "brown"),
            style=hair_style,
            length=hair_data.get("length", "medium length"),
            texture=hair_data.get("texture", "normal"),
            additional_details=hair_data.get("additional_details", "")
        )

        # Parse body
        body_data = data.get("body", {})
        try:
            body_type = BodyType(body_data.get("body_type", "average"))
        except ValueError:
            body_type = BodyType.AVERAGE

        body = BodyDescription(
            height=body_data.get("height", "average height"),
            body_type=body_type,
            posture=body_data.get("posture", "neutral"),
            distinctive_features=body_data.get("distinctive_features", [])
        )

        # Parse clothing
        clothing_data = data.get("clothing", {})
        clothing = ClothingStyle(
            typical_style=clothing_data.get("typical_style", "casual"),
            signature_items=clothing_data.get("signature_items", []),
            colors=clothing_data.get("colors", ["neutral"]),
            accessories=clothing_data.get("accessories", [])
        )

        # Parse age category
        try:
            age_category = AgeCategory(data.get("age_category", "adult"))
        except ValueError:
            age_category = AgeCategory.ADULT

        profile = CharacterVisualProfile(
            character_name=character_name,
            age_category=age_category,
            apparent_age=int(data.get("apparent_age", 30)),
            gender=data.get("gender", "unknown"),
            ethnicity=data.get("ethnicity", "unspecified"),
            face=face,
            hair=hair,
            body=body,
            clothing=clothing,
            default_expression=data.get("default_expression", "neutral"),
            expression_tendencies=data.get("expression_tendencies", {}),
            typical_gestures=data.get("typical_gestures", []),
            stance=data.get("stance", "neutral"),
            visual_inspiration=data.get("visual_inspiration", [])
        )

        # Store profile
        self.profiles[character_name] = profile

        return profile

    # =========================================================================
    # APPEARANCE CHANGES
    # =========================================================================

    def register_appearance_change(
        self,
        character_name: str,
        change_type: AppearanceChangeType,
        chapter_number: int,
        description: str,
        affected_features: List[str],
        is_permanent: bool = True,
        revert_chapter: Optional[int] = None
    ) -> bool:
        """
        Rejestruje zmianę wyglądu postaci.
        """
        if character_name not in self.profiles:
            return False

        change = AppearanceChange(
            change_type=change_type,
            chapter_number=chapter_number,
            description=description,
            affected_features=affected_features,
            is_permanent=is_permanent,
            revert_chapter=revert_chapter
        )

        self.profiles[character_name].appearance_changes.append(change)
        return True

    # =========================================================================
    # PROMPT GENERATION
    # =========================================================================

    def get_illustration_prompt(
        self,
        character_name: str,
        chapter_number: int,
        emotional_state: Optional[str] = None,
        specific_outfit: Optional[str] = None,
        action: Optional[str] = None
    ) -> Optional[str]:
        """
        Generuje prompt do ilustracji dla konkretnej postaci w danym rozdziale.
        """
        if character_name not in self.profiles:
            return None

        profile = self.profiles[character_name]

        # Get base prompt with changes applied
        base_prompt = profile.get_prompt_for_chapter(chapter_number)

        # Add emotional state if specified
        if emotional_state:
            base_prompt = base_prompt.replace(
                profile.default_expression,
                emotional_state
            )

        # Override outfit if specified
        if specific_outfit:
            # Find and replace clothing part
            base_prompt += f", wearing {specific_outfit}"

        # Add action if specified
        if action:
            base_prompt += f", {action}"

        return base_prompt

    def get_all_character_prompts(
        self,
        chapter_number: int
    ) -> Dict[str, str]:
        """
        Zwraca prompty dla wszystkich postaci na dany rozdział.
        """
        return {
            name: profile.get_prompt_for_chapter(chapter_number)
            for name, profile in self.profiles.items()
        }

    # =========================================================================
    # REFERENCE SHEET GENERATION
    # =========================================================================

    async def generate_reference_sheet_prompts(
        self,
        character_name: str
    ) -> List[Dict[str, str]]:
        """
        Generuje prompty do stworzenia reference sheet dla postaci.

        Reference sheet zawiera:
        1. Front view portret
        2. Side profile
        3. Full body
        4. Expression sheet (różne emocje)
        5. Clothing/outfit variations
        """
        if character_name not in self.profiles:
            return []

        profile = self.profiles[character_name]
        base_prompt = profile.get_prompt_for_chapter(1)

        sheets = [
            {
                "type": "front_portrait",
                "prompt": f"Front view portrait, {base_prompt}, neutral expression, white background, character reference sheet style, highly detailed face",
                "aspect_ratio": "1:1"
            },
            {
                "type": "side_profile",
                "prompt": f"Side profile view, {base_prompt}, white background, character reference sheet style, showing nose and chin profile",
                "aspect_ratio": "1:1"
            },
            {
                "type": "full_body",
                "prompt": f"Full body view, standing pose, {base_prompt}, white background, character reference sheet style, showing full outfit and proportions",
                "aspect_ratio": "2:3"
            },
            {
                "type": "expressions",
                "prompt": f"Expression sheet, multiple facial expressions (happy, sad, angry, surprised, fearful, thoughtful), {base_prompt}, white background, character reference sheet",
                "aspect_ratio": "3:2"
            }
        ]

        # Add outfit variations if character has signature items
        if profile.clothing.signature_items:
            sheets.append({
                "type": "outfits",
                "prompt": f"Outfit variations, {base_prompt}, showing different clothing options: {', '.join(profile.clothing.signature_items)}, white background, fashion reference sheet",
                "aspect_ratio": "3:2"
            })

        return sheets

    # =========================================================================
    # CONSISTENCY VALIDATION
    # =========================================================================

    async def validate_scene_consistency(
        self,
        scene_description: str,
        characters_in_scene: List[str],
        chapter_number: int
    ) -> Dict[str, Any]:
        """
        Waliduje spójność opisu sceny z profilami wizualnymi postaci.
        """
        # Gather character descriptions
        char_descriptions = {}
        for char_name in characters_in_scene:
            if char_name in self.profiles:
                char_descriptions[char_name] = self.profiles[char_name].get_full_description()

        if not char_descriptions:
            return {"valid": True, "issues": [], "suggestions": []}

        prompt = f"""Sprawdź spójność opisu sceny z profilami wizualnymi postaci.

OPIS SCENY:
{scene_description}

PROFILE WIZUALNE POSTACI:
{json.dumps(char_descriptions, ensure_ascii=False, indent=2)}

ROZDZIAŁ: {chapter_number}

Sprawdź:
1. Czy opisy wyglądu postaci w scenie są spójne z ich profilami?
2. Czy są jakieś sprzeczności (np. kolor oczu, włosów, wzrost)?
3. Czy ubiór pasuje do stylu postaci?
4. Czy ewentualne zmiany wyglądu są uzasadnione?

Odpowiedz w JSON:
{{
    "valid": true/false,
    "issues": [
        {{"character": "...", "issue": "...", "severity": "minor/major"}}
    ],
    "suggestions": ["..."]
}}"""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    # =========================================================================
    # PROFILE MANAGEMENT
    # =========================================================================

    def get_profile(self, character_name: str) -> Optional[CharacterVisualProfile]:
        """Pobiera profil wizualny"""
        return self.profiles.get(character_name)

    def list_profiles(self) -> List[str]:
        """Lista wszystkich profili"""
        return list(self.profiles.keys())

    def export_profile(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Eksportuje profil do słownika"""
        profile = self.profiles.get(character_name)
        if profile:
            return profile.to_dict()
        return None

    def export_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Eksportuje wszystkie profile"""
        return {name: profile.to_dict() for name, profile in self.profiles.items()}


# =============================================================================
# SINGLETON
# =============================================================================

_character_visual_system: Optional[CharacterVisualSystem] = None

def get_character_visual_system() -> CharacterVisualSystem:
    """Get singleton instance of character visual system"""
    global _character_visual_system
    if _character_visual_system is None:
        _character_visual_system = CharacterVisualSystem()
    return _character_visual_system
