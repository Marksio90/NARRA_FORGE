"""
AI Cover Art Generator - NarraForge 3.0 Phase 2

System generowania okładek książek:
- Automatyczna analiza zawartości dla koncepcji okładki
- Integracja z DALL-E 3 / Midjourney
- Szablony gatunkowe
- Warianty kolorystyczne
- Integracja z typografią
- Eksport w różnych formatach

"Okładka, która sprzedaje książkę zanim ją przeczytasz"
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

class CoverStyle(Enum):
    """Style okładek"""
    ILLUSTRATED = "illustrated"  # Ilustrowana
    PHOTOGRAPHIC = "photographic"  # Fotograficzna
    ABSTRACT = "abstract"  # Abstrakcyjna
    MINIMALIST = "minimalist"  # Minimalistyczna
    TYPOGRAPHIC = "typographic"  # Dominująca typografia
    SYMBOLIC = "symbolic"  # Symboliczna
    CHARACTER_FOCUSED = "character_focused"  # Skupiona na postaci
    LANDSCAPE = "landscape"  # Krajobraz
    OBJECT_FOCUSED = "object_focused"  # Skupiona na przedmiocie
    COLLAGE = "collage"  # Kolaż


class CoverMood(Enum):
    """Nastrój okładki"""
    DARK = "dark"
    LIGHT = "light"
    MYSTERIOUS = "mysterious"
    ROMANTIC = "romantic"
    DRAMATIC = "dramatic"
    WHIMSICAL = "whimsical"
    ELEGANT = "elegant"
    INTENSE = "intense"
    SERENE = "serene"
    OMINOUS = "ominous"


class CoverFormat(Enum):
    """Formaty okładek"""
    EBOOK = "ebook"  # 1600x2560 px
    PAPERBACK = "paperback"  # 6x9 inch
    HARDCOVER = "hardcover"  # 6x9 inch + spine
    AUDIOBOOK = "audiobook"  # Square 3000x3000
    SOCIAL_MEDIA = "social_media"  # Various
    PRINT_READY = "print_ready"  # CMYK, 300 DPI


class ColorPalette(Enum):
    """Palety kolorów"""
    WARM = "warm"
    COOL = "cool"
    MONOCHROME = "monochrome"
    COMPLEMENTARY = "complementary"
    ANALOGOUS = "analogous"
    TRIADIC = "triadic"
    DARK_ACADEMIA = "dark_academia"
    PASTEL = "pastel"
    NEON = "neon"
    EARTHY = "earthy"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CoverConcept:
    """Koncepcja okładki"""
    concept_id: str
    title: str
    author: str
    genre: GenreType
    style: CoverStyle
    mood: CoverMood
    main_visual_element: str
    secondary_elements: List[str]
    color_palette: ColorPalette
    dominant_colors: List[str]
    typography_style: str
    composition: str  # centered, off-center, full-bleed, etc.
    symbolism: List[str]
    target_audience: str
    marketing_angle: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre.value,
            "style": self.style.value,
            "mood": self.mood.value,
            "main_visual_element": self.main_visual_element,
            "secondary_elements": self.secondary_elements,
            "color_palette": self.color_palette.value,
            "dominant_colors": self.dominant_colors,
            "typography_style": self.typography_style,
            "composition": self.composition,
            "symbolism": self.symbolism,
            "target_audience": self.target_audience,
            "marketing_angle": self.marketing_angle
        }


@dataclass
class CoverPrompt:
    """Prompt do generowania okładki"""
    prompt_id: str
    concept: CoverConcept
    main_prompt: str
    style_modifiers: str
    negative_prompt: str
    format: CoverFormat
    dimensions: Tuple[int, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "concept": self.concept.to_dict(),
            "main_prompt": self.main_prompt,
            "style_modifiers": self.style_modifiers,
            "negative_prompt": self.negative_prompt,
            "format": self.format.value,
            "dimensions": self.dimensions
        }

    def get_full_prompt(self) -> str:
        return f"{self.main_prompt}, {self.style_modifiers}"


@dataclass
class GeneratedCover:
    """Wygenerowana okładka"""
    cover_id: str
    concept: CoverConcept
    image_url: Optional[str]
    image_base64: Optional[str]
    width: int
    height: int
    format: CoverFormat
    variant: str  # A, B, C, etc.
    generation_time: float
    cost: float
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cover_id": self.cover_id,
            "concept": self.concept.to_dict(),
            "image_url": self.image_url,
            "has_base64": self.image_base64 is not None,
            "width": self.width,
            "height": self.height,
            "format": self.format.value,
            "variant": self.variant,
            "generation_time": self.generation_time,
            "cost": self.cost,
            "created_at": self.created_at.isoformat()
        }


# =============================================================================
# GENRE COVER PROFILES
# =============================================================================

GENRE_COVER_PROFILES = {
    GenreType.THRILLER: {
        "recommended_styles": [CoverStyle.PHOTOGRAPHIC, CoverStyle.SYMBOLIC, CoverStyle.CHARACTER_FOCUSED],
        "moods": [CoverMood.DARK, CoverMood.MYSTERIOUS, CoverMood.INTENSE],
        "color_palettes": [ColorPalette.COOL, ColorPalette.MONOCHROME, ColorPalette.DARK_ACADEMIA],
        "typical_elements": ["silhouette", "shadows", "urban landscape", "blood", "weapon"],
        "typography": "bold sans-serif, metallic effects"
    },
    GenreType.ROMANCE: {
        "recommended_styles": [CoverStyle.ILLUSTRATED, CoverStyle.PHOTOGRAPHIC, CoverStyle.CHARACTER_FOCUSED],
        "moods": [CoverMood.ROMANTIC, CoverMood.LIGHT, CoverMood.DRAMATIC],
        "color_palettes": [ColorPalette.WARM, ColorPalette.PASTEL, ColorPalette.COMPLEMENTARY],
        "typical_elements": ["couple", "flowers", "sunset", "intimate moment", "elegant dress"],
        "typography": "script fonts, elegant serif"
    },
    GenreType.FANTASY: {
        "recommended_styles": [CoverStyle.ILLUSTRATED, CoverStyle.LANDSCAPE, CoverStyle.CHARACTER_FOCUSED],
        "moods": [CoverMood.DRAMATIC, CoverMood.MYSTERIOUS, CoverMood.WHIMSICAL],
        "color_palettes": [ColorPalette.COMPLEMENTARY, ColorPalette.COOL, ColorPalette.TRIADIC],
        "typical_elements": ["castle", "magic", "mythical creatures", "sword", "forest"],
        "typography": "fantasy fonts, metallic or glowing effects"
    },
    GenreType.HORROR: {
        "recommended_styles": [CoverStyle.SYMBOLIC, CoverStyle.PHOTOGRAPHIC, CoverStyle.ABSTRACT],
        "moods": [CoverMood.DARK, CoverMood.OMINOUS, CoverMood.MYSTERIOUS],
        "color_palettes": [ColorPalette.MONOCHROME, ColorPalette.COOL, ColorPalette.DARK_ACADEMIA],
        "typical_elements": ["skull", "haunted house", "shadows", "blood", "eyes"],
        "typography": "distressed, horror fonts, dripping text"
    },
    GenreType.SCIFI: {
        "recommended_styles": [CoverStyle.ILLUSTRATED, CoverStyle.ABSTRACT, CoverStyle.LANDSCAPE],
        "moods": [CoverMood.INTENSE, CoverMood.DRAMATIC, CoverMood.MYSTERIOUS],
        "color_palettes": [ColorPalette.COOL, ColorPalette.NEON, ColorPalette.MONOCHROME],
        "typical_elements": ["spaceship", "planet", "technology", "futuristic city", "stars"],
        "typography": "futuristic sans-serif, holographic effects"
    },
    GenreType.MYSTERY: {
        "recommended_styles": [CoverStyle.SYMBOLIC, CoverStyle.PHOTOGRAPHIC, CoverStyle.OBJECT_FOCUSED],
        "moods": [CoverMood.MYSTERIOUS, CoverMood.DARK, CoverMood.ELEGANT],
        "color_palettes": [ColorPalette.DARK_ACADEMIA, ColorPalette.MONOCHROME, ColorPalette.EARTHY],
        "typical_elements": ["magnifying glass", "old book", "key", "shadows", "vintage"],
        "typography": "classic serif, vintage feel"
    },
    GenreType.HISTORICAL: {
        "recommended_styles": [CoverStyle.ILLUSTRATED, CoverStyle.PHOTOGRAPHIC, CoverStyle.CHARACTER_FOCUSED],
        "moods": [CoverMood.ELEGANT, CoverMood.DRAMATIC, CoverMood.SERENE],
        "color_palettes": [ColorPalette.EARTHY, ColorPalette.WARM, ColorPalette.DARK_ACADEMIA],
        "typical_elements": ["period costume", "historical building", "antique objects", "battlefield"],
        "typography": "period-appropriate serif fonts"
    }
}


# =============================================================================
# COVER ART GENERATOR ENGINE
# =============================================================================

class CoverArtGenerator:
    """
    Silnik generowania okładek książek.

    Funkcje:
    - Analiza książki dla koncepcji okładki
    - Generowanie promptów dla DALL-E
    - Tworzenie wariantów okładek
    - Integracja z typografią
    - Eksport w różnych formatach
    """

    def __init__(self):
        self.llm_service = get_llm_service()
        self.concepts: Dict[str, CoverConcept] = {}
        self.covers: Dict[str, GeneratedCover] = {}

    def _get_llm(self, tier: str = "mid"):
        """Get appropriate LLM based on tier"""
        return self.llm_service.get_client(tier)

    # =========================================================================
    # CONCEPT GENERATION
    # =========================================================================

    async def generate_cover_concept(
        self,
        title: str,
        author: str,
        genre: GenreType,
        book_summary: str,
        target_audience: str = "adult readers",
        style_preference: CoverStyle = None
    ) -> CoverConcept:
        """
        Generuje koncepcję okładki na podstawie informacji o książce.
        """
        genre_profile = GENRE_COVER_PROFILES.get(genre, GENRE_COVER_PROFILES[GenreType.DRAMA])

        prompt = f"""Zaprojektuj koncepcję okładki książki na podstawie poniższych informacji.

TYTUŁ: {title}
AUTOR: {author}
GATUNEK: {genre.value}
STRESZCZENIE: {book_summary[:1500]}
DOCELOWA GRUPA: {target_audience}

PROFILE GATUNKOWE:
- Zalecane style: {[s.value for s in genre_profile.get('recommended_styles', [])]}
- Nastroje: {[m.value for m in genre_profile.get('moods', [])]}
- Typowe elementy: {genre_profile.get('typical_elements', [])}

Stwórz koncepcję okładki zawierającą:

1. GŁÓWNY ELEMENT WIZUALNY: Co dominuje na okładce?
2. ELEMENTY DRUGORZĘDNE: Jakie dodatkowe elementy wizualne?
3. STYL: {style_preference.value if style_preference else 'wybierz najlepszy'}
   (illustrated/photographic/abstract/minimalist/typographic/symbolic/character_focused/landscape/object_focused/collage)
4. NASTRÓJ: (dark/light/mysterious/romantic/dramatic/whimsical/elegant/intense/serene/ominous)
5. PALETA KOLORÓW: (warm/cool/monochrome/complementary/analogous/triadic/dark_academia/pastel/neon/earthy)
6. DOMINUJĄCE KOLORY: Lista 3-4 głównych kolorów
7. STYL TYPOGRAFII: Jaki styl czcionki dla tytułu i autora
8. KOMPOZYCJA: Układ elementów (centered, off-center, full-bleed, etc.)
9. SYMBOLIKA: Jakie symbole/metafory wykorzystać
10. KĄT MARKETINGOWY: Jaki przekaz ma przyciągnąć czytelnika

Odpowiedz w JSON:
{{
    "main_visual_element": "...",
    "secondary_elements": ["...", "..."],
    "style": "...",
    "mood": "...",
    "color_palette": "...",
    "dominant_colors": ["#hex1", "#hex2", "..."],
    "typography_style": "...",
    "composition": "...",
    "symbolism": ["...", "..."],
    "marketing_angle": "..."
}}"""

        response = await self._get_llm("high").chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        # Parse enums
        try:
            style = CoverStyle(data.get("style", "illustrated"))
        except ValueError:
            style = CoverStyle.ILLUSTRATED

        try:
            mood = CoverMood(data.get("mood", "dramatic"))
        except ValueError:
            mood = CoverMood.DRAMATIC

        try:
            palette = ColorPalette(data.get("color_palette", "complementary"))
        except ValueError:
            palette = ColorPalette.COMPLEMENTARY

        concept = CoverConcept(
            concept_id=f"concept_{title.lower().replace(' ', '_')[:20]}_{datetime.now().strftime('%H%M%S')}",
            title=title,
            author=author,
            genre=genre,
            style=style,
            mood=mood,
            main_visual_element=data.get("main_visual_element", ""),
            secondary_elements=data.get("secondary_elements", []),
            color_palette=palette,
            dominant_colors=data.get("dominant_colors", ["#000000", "#FFFFFF"]),
            typography_style=data.get("typography_style", "modern serif"),
            composition=data.get("composition", "centered"),
            symbolism=data.get("symbolism", []),
            target_audience=target_audience,
            marketing_angle=data.get("marketing_angle", "")
        )

        self.concepts[concept.concept_id] = concept
        return concept

    # =========================================================================
    # PROMPT GENERATION
    # =========================================================================

    async def generate_cover_prompt(
        self,
        concept: CoverConcept,
        format: CoverFormat = CoverFormat.EBOOK,
        include_text: bool = False  # Whether to include title/author in image
    ) -> CoverPrompt:
        """
        Generuje prompt do wygenerowania okładki.
        """
        # Get dimensions for format
        dimensions = self._get_dimensions_for_format(format)

        # Build main prompt
        main_elements = [
            f"Book cover design for {concept.genre.value} novel",
            f"Main visual: {concept.main_visual_element}",
            f"Style: {concept.style.value}",
            f"Mood: {concept.mood.value}",
            f"Composition: {concept.composition}",
            f"Color scheme: {', '.join(concept.dominant_colors[:4])}"
        ]

        if concept.secondary_elements:
            main_elements.append(f"Including elements: {', '.join(concept.secondary_elements[:3])}")

        if concept.symbolism:
            main_elements.append(f"Symbolic elements: {', '.join(concept.symbolism[:2])}")

        main_prompt = ", ".join(main_elements)

        # Style modifiers
        style_modifiers = [
            "professional book cover",
            "high quality",
            "editorial design",
            "cinematic lighting",
            f"{concept.mood.value} atmosphere"
        ]

        if concept.style == CoverStyle.ILLUSTRATED:
            style_modifiers.append("digital illustration, detailed artwork")
        elif concept.style == CoverStyle.PHOTOGRAPHIC:
            style_modifiers.append("photorealistic, dramatic photography")
        elif concept.style == CoverStyle.MINIMALIST:
            style_modifiers.append("clean design, minimal elements, white space")
        elif concept.style == CoverStyle.ABSTRACT:
            style_modifiers.append("abstract art, artistic interpretation")

        # Negative prompt
        negative_elements = [
            "text", "words", "letters", "title", "watermark",
            "blurry", "low quality", "amateur", "cropped",
            "bad composition", "oversaturated"
        ]

        if not include_text:
            negative_elements.extend(["typography", "font", "writing"])

        return CoverPrompt(
            prompt_id=f"prompt_{concept.concept_id}",
            concept=concept,
            main_prompt=main_prompt,
            style_modifiers=", ".join(style_modifiers),
            negative_prompt=", ".join(negative_elements),
            format=format,
            dimensions=dimensions
        )

    def _get_dimensions_for_format(self, format: CoverFormat) -> Tuple[int, int]:
        """Zwraca wymiary dla formatu"""
        dimensions = {
            CoverFormat.EBOOK: (1600, 2560),  # 1:1.6 ratio
            CoverFormat.PAPERBACK: (1800, 2700),  # 6x9 at 300dpi
            CoverFormat.HARDCOVER: (1800, 2700),
            CoverFormat.AUDIOBOOK: (3000, 3000),  # Square
            CoverFormat.SOCIAL_MEDIA: (1200, 1200),
            CoverFormat.PRINT_READY: (1875, 2625)  # 6.25x8.75 at 300dpi
        }
        return dimensions.get(format, (1600, 2560))

    # =========================================================================
    # COVER GENERATION
    # =========================================================================

    async def generate_cover(
        self,
        prompt: CoverPrompt,
        variant: str = "A"
    ) -> GeneratedCover:
        """
        Generuje okładkę używając DALL-E.
        """
        start_time = datetime.now()

        try:
            client = self._get_llm("high")

            # DALL-E 3 size mapping (limited options)
            if prompt.dimensions[1] > prompt.dimensions[0]:
                size = "1024x1792"  # Portrait
            elif prompt.dimensions[0] > prompt.dimensions[1]:
                size = "1792x1024"  # Landscape
            else:
                size = "1024x1024"  # Square

            response = await client.images.generate(
                model="dall-e-3",
                prompt=prompt.get_full_prompt(),
                size=size,
                quality="hd",
                n=1,
                response_format="url"
            )

            image_data = response.data[0]
            generation_time = (datetime.now() - start_time).total_seconds()

            # Parse size
            width, height = map(int, size.split("x"))

            cover = GeneratedCover(
                cover_id=f"cover_{prompt.concept.concept_id}_{variant}",
                concept=prompt.concept,
                image_url=image_data.url,
                image_base64=None,
                width=width,
                height=height,
                format=prompt.format,
                variant=variant,
                generation_time=generation_time,
                cost=0.08,  # DALL-E 3 HD price
                created_at=datetime.now()
            )

            self.covers[cover.cover_id] = cover
            return cover

        except Exception as e:
            return GeneratedCover(
                cover_id=f"cover_{prompt.concept.concept_id}_{variant}_error",
                concept=prompt.concept,
                image_url=None,
                image_base64=None,
                width=0,
                height=0,
                format=prompt.format,
                variant=variant,
                generation_time=0,
                cost=0,
                created_at=datetime.now()
            )

    async def generate_cover_variants(
        self,
        concept: CoverConcept,
        num_variants: int = 3,
        format: CoverFormat = CoverFormat.EBOOK
    ) -> List[GeneratedCover]:
        """
        Generuje wiele wariantów okładki dla koncepcji.
        """
        variants = []
        variant_labels = ["A", "B", "C", "D", "E"]

        for i in range(min(num_variants, 5)):
            prompt = await self.generate_cover_prompt(concept, format)
            cover = await self.generate_cover(prompt, variant_labels[i])
            variants.append(cover)

        return variants

    # =========================================================================
    # QUICK GENERATION
    # =========================================================================

    async def quick_generate(
        self,
        title: str,
        author: str,
        genre: str,
        book_summary: str,
        format: CoverFormat = CoverFormat.EBOOK
    ) -> GeneratedCover:
        """
        Szybkie generowanie okładki - od informacji do obrazu w jednym wywołaniu.
        """
        try:
            genre_type = GenreType(genre.upper())
        except ValueError:
            genre_type = GenreType.DRAMA

        # Generate concept
        concept = await self.generate_cover_concept(
            title=title,
            author=author,
            genre=genre_type,
            book_summary=book_summary
        )

        # Generate prompt
        prompt = await self.generate_cover_prompt(concept, format)

        # Generate cover
        return await self.generate_cover(prompt)

    # =========================================================================
    # MANAGEMENT
    # =========================================================================

    def get_concept(self, concept_id: str) -> Optional[CoverConcept]:
        """Pobiera koncepcję"""
        return self.concepts.get(concept_id)

    def get_cover(self, cover_id: str) -> Optional[GeneratedCover]:
        """Pobiera okładkę"""
        return self.covers.get(cover_id)

    def list_concepts(self) -> List[str]:
        """Lista koncepcji"""
        return list(self.concepts.keys())

    def list_covers(self) -> List[str]:
        """Lista okładek"""
        return list(self.covers.keys())


# =============================================================================
# SINGLETON
# =============================================================================

_cover_generator: Optional[CoverArtGenerator] = None

def get_cover_art_generator() -> CoverArtGenerator:
    """Get singleton instance of cover art generator"""
    global _cover_generator
    if _cover_generator is None:
        _cover_generator = CoverArtGenerator()
    return _cover_generator
