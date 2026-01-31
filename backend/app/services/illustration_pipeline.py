"""
AI Illustration Pipeline - NarraForge 3.0 Phase 2

System generowania ilustracji AI dla książek:
- Automatyczna ekstrakcja scen do ilustracji
- Konwersja opisów na prompty obrazowe
- Integracja z DALL-E 3 / Stable Diffusion
- Spójność stylistyczna przez całą książkę
- Zarządzanie galerią ilustracji
- Eksport w różnych formatach i rozdzielczościach

"Każda strona ożywa w obrazach"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
import asyncio
import base64
import httpx
from datetime import datetime

from app.services.llm_service import get_llm_service
from app.models.project import GenreType
from app.config import settings


# =============================================================================
# ENUMS
# =============================================================================

class IllustrationStyle(Enum):
    """Style ilustracji"""
    REALISTIC = "realistic"  # Fotorealistyczny
    PAINTERLY = "painterly"  # Malarski, olejny
    WATERCOLOR = "watercolor"  # Akwarela
    DIGITAL_ART = "digital_art"  # Cyfrowa grafika
    MANGA = "manga"  # Manga/Anime
    COMIC = "comic"  # Komiks zachodni
    SKETCH = "sketch"  # Szkic, rysunek
    FANTASY_ART = "fantasy_art"  # Fantasy art
    NOIR = "noir"  # Noir, ciemny
    VINTAGE = "vintage"  # Vintage, retro
    MINIMALIST = "minimalist"  # Minimalistyczny
    CHILDREN_BOOK = "children_book"  # Książka dla dzieci


class IllustrationType(Enum):
    """Typy ilustracji"""
    SCENE = "scene"  # Ilustracja sceny
    CHARACTER_PORTRAIT = "character_portrait"  # Portret postaci
    LANDSCAPE = "landscape"  # Krajobraz
    OBJECT = "object"  # Przedmiot, artefakt
    MAP = "map"  # Mapa
    CHAPTER_HEADER = "chapter_header"  # Nagłówek rozdziału
    SPOT_ILLUSTRATION = "spot_illustration"  # Mała ilustracja wstawka
    FULL_PAGE = "full_page"  # Pełna strona
    COVER = "cover"  # Okładka


class AspectRatio(Enum):
    """Proporcje ilustracji"""
    SQUARE = "1:1"  # Kwadrat
    PORTRAIT = "2:3"  # Portret (książkowy)
    LANDSCAPE = "3:2"  # Krajobraz
    WIDE = "16:9"  # Szeroki
    TALL = "9:16"  # Wysoki
    BOOK_PAGE = "5:8"  # Strona książki


class ImageProvider(Enum):
    """Dostawcy generowania obrazów"""
    OPENAI_DALLE = "openai_dalle"
    STABILITY_AI = "stability_ai"
    MIDJOURNEY = "midjourney"  # Via API
    REPLICATE = "replicate"
    LOCAL_SD = "local_sd"  # Lokalna instalacja


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class VisualStyle:
    """Definicja stylu wizualnego"""
    name: str
    base_style: IllustrationStyle
    color_palette: List[str]  # Kolory dominujące
    mood: str  # Nastrój
    lighting: str  # Oświetlenie
    texture: str  # Tekstura
    detail_level: str  # low, medium, high, ultra
    artistic_influences: List[str]  # Inspiracje artystyczne
    negative_prompts: List[str]  # Czego unikać
    custom_modifiers: List[str]  # Dodatkowe modyfikatory

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "base_style": self.base_style.value,
            "color_palette": self.color_palette,
            "mood": self.mood,
            "lighting": self.lighting,
            "texture": self.texture,
            "detail_level": self.detail_level,
            "artistic_influences": self.artistic_influences,
            "negative_prompts": self.negative_prompts,
            "custom_modifiers": self.custom_modifiers
        }

    def to_prompt_suffix(self) -> str:
        """Konwertuje styl na sufiks promptu"""
        parts = []

        # Base style
        style_map = {
            IllustrationStyle.REALISTIC: "photorealistic, highly detailed",
            IllustrationStyle.PAINTERLY: "oil painting style, painterly brushstrokes",
            IllustrationStyle.WATERCOLOR: "watercolor painting, soft edges, flowing colors",
            IllustrationStyle.DIGITAL_ART: "digital art, vibrant colors, sharp details",
            IllustrationStyle.MANGA: "manga style, anime aesthetics",
            IllustrationStyle.COMIC: "comic book style, bold lines, dynamic",
            IllustrationStyle.SKETCH: "pencil sketch, detailed linework",
            IllustrationStyle.FANTASY_ART: "epic fantasy art, magical atmosphere",
            IllustrationStyle.NOIR: "noir style, high contrast, dramatic shadows",
            IllustrationStyle.VINTAGE: "vintage illustration, retro aesthetics",
            IllustrationStyle.MINIMALIST: "minimalist, clean lines, simple composition",
            IllustrationStyle.CHILDREN_BOOK: "children's book illustration, whimsical, colorful"
        }
        parts.append(style_map.get(self.base_style, ""))

        # Mood and lighting
        parts.append(f"{self.mood} mood")
        parts.append(f"{self.lighting} lighting")

        # Detail level
        detail_map = {
            "low": "simple details",
            "medium": "moderate detail",
            "high": "highly detailed",
            "ultra": "ultra detailed, intricate"
        }
        parts.append(detail_map.get(self.detail_level, ""))

        # Artistic influences
        if self.artistic_influences:
            parts.append(f"inspired by {', '.join(self.artistic_influences[:3])}")

        # Custom modifiers
        parts.extend(self.custom_modifiers)

        return ", ".join(filter(None, parts))


@dataclass
class SceneDescription:
    """Opis sceny do ilustracji"""
    scene_id: str
    chapter_number: int
    scene_text: str  # Oryginalny tekst sceny
    setting: str  # Miejsce
    time_of_day: str  # Pora dnia
    weather: str  # Pogoda/atmosfera
    characters_present: List[str]  # Postacie w scenie
    key_action: str  # Główna akcja
    emotional_tone: str  # Ton emocjonalny
    important_objects: List[str]  # Ważne przedmioty
    suggested_composition: str  # Sugerowana kompozycja

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "chapter_number": self.chapter_number,
            "scene_text": self.scene_text[:500],
            "setting": self.setting,
            "time_of_day": self.time_of_day,
            "weather": self.weather,
            "characters_present": self.characters_present,
            "key_action": self.key_action,
            "emotional_tone": self.emotional_tone,
            "important_objects": self.important_objects,
            "suggested_composition": self.suggested_composition
        }


@dataclass
class IllustrationPrompt:
    """Prompt do generowania ilustracji"""
    prompt_id: str
    scene_id: str
    illustration_type: IllustrationType
    main_prompt: str  # Główny prompt
    style_suffix: str  # Sufiks stylu
    negative_prompt: str  # Negatywny prompt
    aspect_ratio: AspectRatio
    quality_settings: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "scene_id": self.scene_id,
            "illustration_type": self.illustration_type.value,
            "main_prompt": self.main_prompt,
            "style_suffix": self.style_suffix,
            "negative_prompt": self.negative_prompt,
            "aspect_ratio": self.aspect_ratio.value,
            "quality_settings": self.quality_settings
        }

    def get_full_prompt(self) -> str:
        """Zwraca pełny prompt"""
        return f"{self.main_prompt}, {self.style_suffix}"


@dataclass
class GeneratedIllustration:
    """Wygenerowana ilustracja"""
    illustration_id: str
    prompt: IllustrationPrompt
    image_url: Optional[str]  # URL lub ścieżka
    image_base64: Optional[str]  # Base64 encoded
    width: int
    height: int
    provider: ImageProvider
    generation_time: float  # Czas generowania w sekundach
    cost: float  # Koszt generowania
    metadata: Dict[str, Any]
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "illustration_id": self.illustration_id,
            "prompt": self.prompt.to_dict(),
            "image_url": self.image_url,
            "has_base64": self.image_base64 is not None,
            "width": self.width,
            "height": self.height,
            "provider": self.provider.value,
            "generation_time": self.generation_time,
            "cost": self.cost,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class IllustrationPlan:
    """Plan ilustracji dla książki"""
    project_id: str
    total_illustrations: int
    style: VisualStyle
    scenes_to_illustrate: List[SceneDescription]
    character_portraits_needed: List[str]
    maps_needed: List[str]
    chapter_headers: bool
    estimated_cost: float
    estimated_time: float  # W minutach

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "total_illustrations": self.total_illustrations,
            "style": self.style.to_dict(),
            "scenes_count": len(self.scenes_to_illustrate),
            "character_portraits": self.character_portraits_needed,
            "maps": self.maps_needed,
            "chapter_headers": self.chapter_headers,
            "estimated_cost": self.estimated_cost,
            "estimated_time": self.estimated_time
        }


# =============================================================================
# GENRE VISUAL PROFILES
# =============================================================================

GENRE_VISUAL_PROFILES: Dict[GenreType, Dict[str, Any]] = {
    GenreType.FANTASY: {
        "recommended_style": IllustrationStyle.FANTASY_ART,
        "color_palette": ["deep blue", "gold", "emerald green", "mystical purple"],
        "mood": "epic and magical",
        "lighting": "dramatic fantasy",
        "artistic_influences": ["Alan Lee", "John Howe", "Frazetta"],
        "negative_prompts": ["modern elements", "technology", "cars"]
    },
    GenreType.THRILLER: {
        "recommended_style": IllustrationStyle.NOIR,
        "color_palette": ["black", "dark grey", "blood red", "cold blue"],
        "mood": "tense and mysterious",
        "lighting": "high contrast noir",
        "artistic_influences": ["film noir", "detective pulp art"],
        "negative_prompts": ["bright colors", "cheerful", "cartoonish"]
    },
    GenreType.ROMANCE: {
        "recommended_style": IllustrationStyle.PAINTERLY,
        "color_palette": ["soft pink", "warm gold", "cream", "rose"],
        "mood": "romantic and dreamy",
        "lighting": "soft golden hour",
        "artistic_influences": ["romantic era paintings", "Pre-Raphaelites"],
        "negative_prompts": ["harsh", "violent", "dark"]
    },
    GenreType.HORROR: {
        "recommended_style": IllustrationStyle.NOIR,
        "color_palette": ["black", "blood red", "sickly green", "pale"],
        "mood": "terrifying and unsettling",
        "lighting": "harsh shadows, minimal light",
        "artistic_influences": ["Zdzisław Beksiński", "H.R. Giger", "Junji Ito"],
        "negative_prompts": ["cheerful", "bright", "cute"]
    },
    GenreType.SCI_FI: {
        "recommended_style": IllustrationStyle.DIGITAL_ART,
        "color_palette": ["neon blue", "chrome", "deep space black", "holographic"],
        "mood": "futuristic and sleek",
        "lighting": "neon and holographic",
        "artistic_influences": ["Syd Mead", "Moebius", "cyberpunk art"],
        "negative_prompts": ["medieval", "fantasy elements", "magic"]
    },
    GenreType.MYSTERY: {
        "recommended_style": IllustrationStyle.NOIR,
        "color_palette": ["sepia", "dark brown", "fog grey", "dim yellow"],
        "mood": "mysterious and intriguing",
        "lighting": "foggy, dim streetlights",
        "artistic_influences": ["classic detective illustrations", "Edward Hopper"],
        "negative_prompts": ["bright", "cheerful", "fantasy"]
    }
}


# =============================================================================
# ILLUSTRATION PIPELINE ENGINE
# =============================================================================

class IllustrationPipeline:
    """
    Pipeline do generowania ilustracji dla książek.

    Funkcje:
    - Ekstrakcja scen wartych ilustracji
    - Konwersja tekstu na prompty obrazowe
    - Generowanie ilustracji przez różnych dostawców
    - Utrzymanie spójności stylistycznej
    - Zarządzanie galerią ilustracji
    """

    def __init__(self):
        self.llm_service = get_llm_service()
        self.visual_styles: Dict[str, VisualStyle] = {}
        self.generated_illustrations: Dict[str, GeneratedIllustration] = {}
        self.default_provider = ImageProvider.OPENAI_DALLE

    def _get_llm(self, tier: str = "mid"):
        """Get appropriate LLM based on tier"""
        return self.llm_service.get_client(tier)

    # =========================================================================
    # SCENE EXTRACTION
    # =========================================================================

    async def extract_illustratable_scenes(
        self,
        chapter_text: str,
        chapter_number: int,
        max_scenes: int = 3,
        genre: GenreType = GenreType.DRAMA
    ) -> List[SceneDescription]:
        """
        Ekstrahuje sceny warte zilustrowania z rozdziału.
        """
        prompt = f"""Przeanalizuj poniższy rozdział i wybierz {max_scenes} NAJLEPSZYCH scen do zilustrowania.

ROZDZIAŁ {chapter_number}:
{chapter_text[:6000]}

GATUNEK: {genre.value}

Dla każdej sceny określ:
1. scene_text: Fragment tekstu opisujący scenę (max 200 słów)
2. setting: Dokładne miejsce akcji
3. time_of_day: Pora dnia (dawn, morning, noon, afternoon, evening, night, midnight)
4. weather: Pogoda/atmosfera
5. characters_present: Lista postaci obecnych w scenie
6. key_action: Główna akcja/wydarzenie
7. emotional_tone: Ton emocjonalny sceny
8. important_objects: Ważne przedmioty widoczne w scenie
9. suggested_composition: Sugerowana kompozycja (close-up, medium shot, wide shot, bird's eye, etc.)
10. illustration_worthiness: Dlaczego ta scena jest warta ilustracji (1-10)

KRYTERIA WYBORU:
- Wizualnie interesujące momenty
- Kluczowe punkty fabularne
- Emocjonalnie intensywne sceny
- Momenty wprowadzające ważne postacie/miejsca
- Sceny z unikalnym settingiem

Odpowiedz w JSON:
{{
    "scenes": [
        {{
            "scene_text": "...",
            "setting": "...",
            "time_of_day": "...",
            "weather": "...",
            "characters_present": ["..."],
            "key_action": "...",
            "emotional_tone": "...",
            "important_objects": ["..."],
            "suggested_composition": "...",
            "illustration_worthiness": 8
        }}
    ]
}}"""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        scenes = []
        for i, scene_data in enumerate(result.get("scenes", [])[:max_scenes]):
            scene = SceneDescription(
                scene_id=f"ch{chapter_number}_scene_{i+1}",
                chapter_number=chapter_number,
                scene_text=scene_data.get("scene_text", ""),
                setting=scene_data.get("setting", ""),
                time_of_day=scene_data.get("time_of_day", "day"),
                weather=scene_data.get("weather", "clear"),
                characters_present=scene_data.get("characters_present", []),
                key_action=scene_data.get("key_action", ""),
                emotional_tone=scene_data.get("emotional_tone", "neutral"),
                important_objects=scene_data.get("important_objects", []),
                suggested_composition=scene_data.get("suggested_composition", "medium shot")
            )
            scenes.append(scene)

        return scenes

    # =========================================================================
    # PROMPT GENERATION
    # =========================================================================

    async def generate_illustration_prompt(
        self,
        scene: SceneDescription,
        style: VisualStyle,
        illustration_type: IllustrationType = IllustrationType.SCENE,
        character_appearances: Dict[str, str] = None
    ) -> IllustrationPrompt:
        """
        Generuje prompt do ilustracji na podstawie opisu sceny.
        """
        # Build character descriptions if available
        character_desc = ""
        if character_appearances and scene.characters_present:
            for char in scene.characters_present:
                if char in character_appearances:
                    character_desc += f"\n- {char}: {character_appearances[char]}"

        prompt = f"""Stwórz SZCZEGÓŁOWY prompt do generowania ilustracji dla poniższej sceny.

OPIS SCENY:
{scene.scene_text}

USTAWIENIA:
- Miejsce: {scene.setting}
- Pora dnia: {scene.time_of_day}
- Atmosfera: {scene.weather}
- Akcja: {scene.key_action}
- Ton emocjonalny: {scene.emotional_tone}
- Kompozycja: {scene.suggested_composition}

POSTACIE W SCENIE:{character_desc if character_desc else " Brak zdefiniowanych"}

WAŻNE PRZEDMIOTY: {', '.join(scene.important_objects) if scene.important_objects else 'Brak'}

STYL WIZUALNY:
- Bazowy styl: {style.base_style.value}
- Nastrój: {style.mood}
- Oświetlenie: {style.lighting}
- Paleta kolorów: {', '.join(style.color_palette)}

ZASADY TWORZENIA PROMPTU:
1. Zacznij od głównego tematu/akcji
2. Opisz postacie szczegółowo (wygląd, pozycja, wyraz twarzy)
3. Opisz otoczenie i tło
4. Dodaj elementy atmosferyczne (światło, cienie, pogoda)
5. NIE używaj imion własnych - opisz postacie przez wygląd
6. Używaj języka angielskiego
7. Bądź konkretny i wizualny

Odpowiedz w JSON:
{{
    "main_prompt": "szczegółowy prompt po angielsku (200-300 słów)",
    "key_elements": ["element1", "element2"],
    "mood_keywords": ["keyword1", "keyword2"],
    "composition_notes": "notatki o kompozycji"
}}"""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Build negative prompt
        negative_parts = style.negative_prompts.copy()
        negative_parts.extend([
            "blurry", "low quality", "watermark", "signature",
            "text", "words", "letters", "deformed", "ugly"
        ])

        return IllustrationPrompt(
            prompt_id=f"prompt_{scene.scene_id}_{datetime.now().strftime('%H%M%S')}",
            scene_id=scene.scene_id,
            illustration_type=illustration_type,
            main_prompt=result.get("main_prompt", ""),
            style_suffix=style.to_prompt_suffix(),
            negative_prompt=", ".join(negative_parts),
            aspect_ratio=self._get_aspect_ratio_for_type(illustration_type),
            quality_settings={
                "quality": "hd",
                "detail_level": style.detail_level,
                "key_elements": result.get("key_elements", []),
                "mood_keywords": result.get("mood_keywords", [])
            }
        )

    def _get_aspect_ratio_for_type(self, illustration_type: IllustrationType) -> AspectRatio:
        """Zwraca odpowiedni aspect ratio dla typu ilustracji"""
        ratio_map = {
            IllustrationType.SCENE: AspectRatio.LANDSCAPE,
            IllustrationType.CHARACTER_PORTRAIT: AspectRatio.PORTRAIT,
            IllustrationType.LANDSCAPE: AspectRatio.WIDE,
            IllustrationType.OBJECT: AspectRatio.SQUARE,
            IllustrationType.MAP: AspectRatio.SQUARE,
            IllustrationType.CHAPTER_HEADER: AspectRatio.WIDE,
            IllustrationType.SPOT_ILLUSTRATION: AspectRatio.SQUARE,
            IllustrationType.FULL_PAGE: AspectRatio.BOOK_PAGE,
            IllustrationType.COVER: AspectRatio.PORTRAIT
        }
        return ratio_map.get(illustration_type, AspectRatio.LANDSCAPE)

    # =========================================================================
    # IMAGE GENERATION
    # =========================================================================

    async def generate_illustration(
        self,
        prompt: IllustrationPrompt,
        provider: ImageProvider = None
    ) -> GeneratedIllustration:
        """
        Generuje ilustrację używając wybranego dostawcy.
        """
        provider = provider or self.default_provider
        start_time = datetime.now()

        if provider == ImageProvider.OPENAI_DALLE:
            result = await self._generate_with_dalle(prompt)
        elif provider == ImageProvider.STABILITY_AI:
            result = await self._generate_with_stability(prompt)
        else:
            # Fallback to DALL-E
            result = await self._generate_with_dalle(prompt)

        generation_time = (datetime.now() - start_time).total_seconds()

        illustration = GeneratedIllustration(
            illustration_id=f"ill_{prompt.prompt_id}",
            prompt=prompt,
            image_url=result.get("url"),
            image_base64=result.get("base64"),
            width=result.get("width", 1024),
            height=result.get("height", 1024),
            provider=provider,
            generation_time=generation_time,
            cost=result.get("cost", 0.04),  # DALL-E 3 standard price
            metadata=result.get("metadata", {}),
            created_at=datetime.now()
        )

        # Store in cache
        self.generated_illustrations[illustration.illustration_id] = illustration

        return illustration

    async def _generate_with_dalle(self, prompt: IllustrationPrompt) -> Dict[str, Any]:
        """Generuje obrazek używając DALL-E 3"""
        try:
            client = self._get_llm("high")

            # Map aspect ratio to DALL-E sizes
            size_map = {
                AspectRatio.SQUARE: "1024x1024",
                AspectRatio.PORTRAIT: "1024x1792",
                AspectRatio.LANDSCAPE: "1792x1024",
                AspectRatio.WIDE: "1792x1024",
                AspectRatio.TALL: "1024x1792",
                AspectRatio.BOOK_PAGE: "1024x1792"
            }
            size = size_map.get(prompt.aspect_ratio, "1024x1024")

            response = await client.images.generate(
                model="dall-e-3",
                prompt=prompt.get_full_prompt(),
                size=size,
                quality="hd",
                n=1,
                response_format="url"
            )

            image_data = response.data[0]

            # Parse size
            width, height = map(int, size.split("x"))

            return {
                "url": image_data.url,
                "base64": None,
                "width": width,
                "height": height,
                "cost": 0.08 if "hd" else 0.04,  # HD pricing
                "metadata": {
                    "revised_prompt": getattr(image_data, "revised_prompt", None),
                    "model": "dall-e-3"
                }
            }

        except Exception as e:
            # Return placeholder on error
            return {
                "url": None,
                "base64": None,
                "width": 1024,
                "height": 1024,
                "cost": 0,
                "metadata": {"error": str(e)}
            }

    async def _generate_with_stability(self, prompt: IllustrationPrompt) -> Dict[str, Any]:
        """Generuje obrazek używając Stability AI"""
        # Placeholder - requires Stability AI API key
        return {
            "url": None,
            "base64": None,
            "width": 1024,
            "height": 1024,
            "cost": 0,
            "metadata": {"error": "Stability AI not configured"}
        }

    # =========================================================================
    # STYLE MANAGEMENT
    # =========================================================================

    def create_visual_style(
        self,
        name: str,
        genre: GenreType,
        customizations: Dict[str, Any] = None
    ) -> VisualStyle:
        """
        Tworzy styl wizualny dla projektu na podstawie gatunku.
        """
        profile = GENRE_VISUAL_PROFILES.get(genre, GENRE_VISUAL_PROFILES[GenreType.DRAMA])

        # Apply customizations
        customizations = customizations or {}

        style = VisualStyle(
            name=name,
            base_style=IllustrationStyle(customizations.get("base_style", profile["recommended_style"].value)),
            color_palette=customizations.get("color_palette", profile["color_palette"]),
            mood=customizations.get("mood", profile["mood"]),
            lighting=customizations.get("lighting", profile["lighting"]),
            texture=customizations.get("texture", "detailed"),
            detail_level=customizations.get("detail_level", "high"),
            artistic_influences=customizations.get("artistic_influences", profile["artistic_influences"]),
            negative_prompts=customizations.get("negative_prompts", profile["negative_prompts"]),
            custom_modifiers=customizations.get("custom_modifiers", [])
        )

        self.visual_styles[name] = style
        return style

    def get_style(self, name: str) -> Optional[VisualStyle]:
        """Pobiera styl wizualny"""
        return self.visual_styles.get(name)

    # =========================================================================
    # ILLUSTRATION PLANNING
    # =========================================================================

    async def create_illustration_plan(
        self,
        project_id: str,
        chapters: List[str],
        genre: GenreType,
        illustrations_per_chapter: int = 2,
        include_character_portraits: bool = True,
        include_maps: bool = False,
        include_chapter_headers: bool = False,
        character_list: List[str] = None
    ) -> IllustrationPlan:
        """
        Tworzy plan ilustracji dla całej książki.
        """
        # Create or get style
        style_name = f"project_{project_id}_style"
        style = self.create_visual_style(style_name, genre)

        # Extract scenes from each chapter
        all_scenes = []
        for i, chapter_text in enumerate(chapters):
            scenes = await self.extract_illustratable_scenes(
                chapter_text,
                chapter_number=i + 1,
                max_scenes=illustrations_per_chapter,
                genre=genre
            )
            all_scenes.extend(scenes)

        # Calculate totals
        scene_count = len(all_scenes)
        portrait_count = len(character_list) if include_character_portraits and character_list else 0
        map_count = 1 if include_maps else 0
        header_count = len(chapters) if include_chapter_headers else 0

        total = scene_count + portrait_count + map_count + header_count

        # Estimate costs (DALL-E 3 HD pricing)
        cost_per_image = 0.08
        estimated_cost = total * cost_per_image

        # Estimate time (roughly 15 seconds per image)
        estimated_time = total * 0.25  # minutes

        return IllustrationPlan(
            project_id=project_id,
            total_illustrations=total,
            style=style,
            scenes_to_illustrate=all_scenes,
            character_portraits_needed=character_list or [],
            maps_needed=["world_map"] if include_maps else [],
            chapter_headers=include_chapter_headers,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time
        )

    # =========================================================================
    # BATCH GENERATION
    # =========================================================================

    async def execute_illustration_plan(
        self,
        plan: IllustrationPlan,
        character_appearances: Dict[str, str] = None,
        progress_callback=None
    ) -> List[GeneratedIllustration]:
        """
        Wykonuje plan ilustracji, generując wszystkie obrazy.
        """
        illustrations = []
        total = plan.total_illustrations
        current = 0

        # Generate scene illustrations
        for scene in plan.scenes_to_illustrate:
            prompt = await self.generate_illustration_prompt(
                scene=scene,
                style=plan.style,
                character_appearances=character_appearances
            )
            illustration = await self.generate_illustration(prompt)
            illustrations.append(illustration)

            current += 1
            if progress_callback:
                progress_callback(current, total, f"Scene: {scene.scene_id}")

        # Generate character portraits
        for character_name in plan.character_portraits_needed:
            appearance = character_appearances.get(character_name, "") if character_appearances else ""
            portrait_prompt = await self._create_portrait_prompt(
                character_name,
                appearance,
                plan.style
            )
            illustration = await self.generate_illustration(portrait_prompt)
            illustrations.append(illustration)

            current += 1
            if progress_callback:
                progress_callback(current, total, f"Portrait: {character_name}")

        return illustrations

    async def _create_portrait_prompt(
        self,
        character_name: str,
        appearance: str,
        style: VisualStyle
    ) -> IllustrationPrompt:
        """Tworzy prompt dla portretu postaci"""
        prompt_text = f"Portrait of a character: {appearance if appearance else 'mysterious figure'}. "
        prompt_text += f"Detailed face and upper body, {style.mood} expression, "
        prompt_text += f"{style.lighting} lighting, professional character portrait"

        return IllustrationPrompt(
            prompt_id=f"portrait_{character_name}_{datetime.now().strftime('%H%M%S')}",
            scene_id=f"portrait_{character_name}",
            illustration_type=IllustrationType.CHARACTER_PORTRAIT,
            main_prompt=prompt_text,
            style_suffix=style.to_prompt_suffix(),
            negative_prompt=", ".join(style.negative_prompts + ["blurry", "deformed"]),
            aspect_ratio=AspectRatio.PORTRAIT,
            quality_settings={"quality": "hd"}
        )


# =============================================================================
# SINGLETON
# =============================================================================

_illustration_pipeline: Optional[IllustrationPipeline] = None

def get_illustration_pipeline() -> IllustrationPipeline:
    """Get singleton instance of illustration pipeline"""
    global _illustration_pipeline
    if _illustration_pipeline is None:
        _illustration_pipeline = IllustrationPipeline()
    return _illustration_pipeline
