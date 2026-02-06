"""
Style Marketplace Service - NarraForge 3.0
Marketplace stylów pisania AI - kupowanie, sprzedawanie i udostępnianie niestandardowych stylów
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from datetime import datetime
import uuid
import json

logger = logging.getLogger(__name__)


class StyleCategory(str, Enum):
    """Kategorie stylów"""
    AUTHOR_INSPIRED = "author_inspired"  # Inspirowane konkretnymi autorami
    GENRE_SPECIFIC = "genre_specific"  # Specyficzne dla gatunków
    CULTURAL = "cultural"  # Kulturowo specyficzne
    HISTORICAL = "historical"  # Style z różnych epok
    EXPERIMENTAL = "experimental"  # Eksperymentalne
    COMMERCIAL = "commercial"  # Komercyjne, bestsellerowe
    LITERARY = "literary"  # Wysokolitewrackie
    CUSTOM = "custom"  # Niestandardowe, stworzone przez użytkowników


class StyleTier(str, Enum):
    """Poziomy stylów"""
    FREE = "free"  # Darmowe
    BASIC = "basic"  # Podstawowe
    PREMIUM = "premium"  # Premium
    EXCLUSIVE = "exclusive"  # Ekskluzywne


class LicenseType(str, Enum):
    """Typy licencji"""
    PERSONAL = "personal"  # Tylko do użytku osobistego
    COMMERCIAL = "commercial"  # Komercyjne użycie dozwolone
    UNLIMITED = "unlimited"  # Bez ograniczeń
    SUBSCRIPTION = "subscription"  # Wymaga subskrypcji


@dataclass
class StyleProfile:
    """Profil stylu pisania"""
    vocabulary_complexity: float  # 0-1, złożoność słownictwa
    sentence_length_avg: str  # "short", "medium", "long", "varied"
    paragraph_structure: str  # "tight", "flowing", "fragmented"
    dialogue_style: str  # "minimal", "balanced", "heavy"
    description_density: float  # 0-1, gęstość opisów
    emotional_intensity: float  # 0-1, intensywność emocjonalna
    pacing: str  # "fast", "moderate", "slow", "dynamic"
    narrative_voice: str  # "first_person", "third_limited", "third_omniscient", "second_person"
    tone: List[str]  # ["dark", "light", "ironic", "serious", etc.]
    literary_devices: List[str]  # Preferowane środki stylistyczne


@dataclass
class WritingStyle:
    """Kompletny styl pisania"""
    style_id: str
    name: str
    description: str
    category: StyleCategory
    tier: StyleTier
    profile: StyleProfile
    creator_id: str
    creator_name: str
    price: float  # 0 dla darmowych
    currency: str
    license_type: LicenseType
    tags: List[str]
    sample_text: str
    rating: float  # 0-5
    reviews_count: int
    downloads_count: int
    is_verified: bool  # Zweryfikowany przez NarraForge
    is_featured: bool  # Wyróżniony
    created_at: datetime
    updated_at: datetime
    prompt_template: str  # Szablon promptu dla AI
    fine_tuning_parameters: Dict[str, Any]
    compatibility: List[str]  # Kompatybilne gatunki


@dataclass
class StylePurchase:
    """Zakup stylu"""
    purchase_id: str
    user_id: str
    style_id: str
    price_paid: float
    currency: str
    license_type: LicenseType
    purchased_at: datetime
    expires_at: Optional[datetime]  # Dla subskrypcji
    is_active: bool


@dataclass
class StyleReview:
    """Recenzja stylu"""
    review_id: str
    style_id: str
    user_id: str
    user_name: str
    rating: int  # 1-5
    title: str
    content: str
    helpful_votes: int
    created_at: datetime
    verified_purchase: bool


@dataclass
class StyleBundle:
    """Pakiet stylów"""
    bundle_id: str
    name: str
    description: str
    styles: List[WritingStyle]
    original_price: float
    bundle_price: float
    discount_percentage: float
    tier: StyleTier
    is_active: bool


class StyleMarketplaceService:
    """
    Serwis marketplace'u stylów pisania.
    Umożliwia kupowanie, sprzedawanie i udostępnianie niestandardowych stylów AI.
    """

    def __init__(self):
        self.styles: Dict[str, WritingStyle] = {}
        self.purchases: Dict[str, List[StylePurchase]] = {}  # user_id -> purchases
        self.reviews: Dict[str, List[StyleReview]] = {}  # style_id -> reviews
        self.bundles: Dict[str, StyleBundle] = {}
        self.featured_styles: List[str] = []
        self._initialize_default_styles()
        logger.info("StyleMarketplaceService zainicjalizowany")

    def _initialize_default_styles(self):
        """Inicjalizuje domyślne style"""

        # Style inspirowane autorami
        self._add_style(WritingStyle(
            style_id="style_hemingway",
            name="Hemingway Minimalism",
            description="Zwięzły, oszczędny styl Ernesta Hemingwaya. Krótkie zdania, silne czasowniki, minimalne przymiotniki.",
            category=StyleCategory.AUTHOR_INSPIRED,
            tier=StyleTier.FREE,
            profile=StyleProfile(
                vocabulary_complexity=0.4,
                sentence_length_avg="short",
                paragraph_structure="tight",
                dialogue_style="heavy",
                description_density=0.3,
                emotional_intensity=0.6,
                pacing="fast",
                narrative_voice="third_limited",
                tone=["understated", "masculine", "direct"],
                literary_devices=["iceberg_theory", "repetition", "simple_vocabulary"]
            ),
            creator_id="system",
            creator_name="NarraForge",
            price=0.0,
            currency="USD",
            license_type=LicenseType.UNLIMITED,
            tags=["minimalist", "classic", "literary", "masculine"],
            sample_text="Starzec był chudy i wyschnięty. Miał głębokie zmarszczki na karku. Przebarwienia od słońca znaczyły jego policzki.",
            rating=4.8,
            reviews_count=1250,
            downloads_count=15000,
            is_verified=True,
            is_featured=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            prompt_template="Pisz w stylu Hemingwaya: krótkie, zwięzłe zdania. Unikaj przymiotników. Używaj silnych czasowników. Pokazuj emocje przez działania, nie opisy. Teoria góry lodowej - więcej pod powierzchnią niż na wierzchu.",
            fine_tuning_parameters={
                "temperature": 0.7,
                "max_sentence_length": 15,
                "adjective_ratio": 0.1
            },
            compatibility=["literary_fiction", "adventure", "war", "romance"]
        ))

        self._add_style(WritingStyle(
            style_id="style_tolkien",
            name="Tolkien Epic Fantasy",
            description="Rozbudowany, epicki styl J.R.R. Tolkiena. Bogaty w opisy, mitologiczny ton, archaiczne słownictwo.",
            category=StyleCategory.AUTHOR_INSPIRED,
            tier=StyleTier.BASIC,
            profile=StyleProfile(
                vocabulary_complexity=0.85,
                sentence_length_avg="long",
                paragraph_structure="flowing",
                dialogue_style="balanced",
                description_density=0.9,
                emotional_intensity=0.7,
                pacing="slow",
                narrative_voice="third_omniscient",
                tone=["epic", "mythological", "nostalgic", "noble"],
                literary_devices=["extensive_worldbuilding", "archaic_language", "songs_and_poems", "etymology"]
            ),
            creator_id="system",
            creator_name="NarraForge",
            price=4.99,
            currency="USD",
            license_type=LicenseType.COMMERCIAL,
            tags=["epic", "fantasy", "worldbuilding", "mythological"],
            sample_text="W jamie pod ziemią mieszkał pewien hobbit. Nie była to paskudna, brudna, mokra jama, pełna końców robaków i zapachu mułu, ani też sucha, naga, piaszczysta jama, gdzie nie ma na czym usiąść i nie ma co jeść: była to jama hobbicia, a to znaczy wygodna.",
            rating=4.9,
            reviews_count=2100,
            downloads_count=25000,
            is_verified=True,
            is_featured=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            prompt_template="Pisz w stylu Tolkiena: bogate opisy krajobrazów i kultur. Używaj archaicznego słownictwa. Buduj świat z historią i mitologią. Wprowadzaj pieśni i wiersze. Narracja epiczna, podniosła.",
            fine_tuning_parameters={
                "temperature": 0.8,
                "description_focus": True,
                "worldbuilding_depth": "extensive"
            },
            compatibility=["fantasy", "epic_fantasy", "adventure", "mythological"]
        ))

        self._add_style(WritingStyle(
            style_id="style_sienkiewicz",
            name="Sienkiewicz Historyczny",
            description="Pełen rozmachu styl Henryka Sienkiewicza. Dramatyczne sceny, patriotyczny ton, plastyczne opisy.",
            category=StyleCategory.AUTHOR_INSPIRED,
            tier=StyleTier.BASIC,
            profile=StyleProfile(
                vocabulary_complexity=0.75,
                sentence_length_avg="varied",
                paragraph_structure="flowing",
                dialogue_style="balanced",
                description_density=0.8,
                emotional_intensity=0.85,
                pacing="dynamic",
                narrative_voice="third_omniscient",
                tone=["dramatic", "patriotic", "heroic", "romantic"],
                literary_devices=["vivid_imagery", "dramatic_tension", "historical_detail", "heroic_characters"]
            ),
            creator_id="system",
            creator_name="NarraForge",
            price=4.99,
            currency="USD",
            license_type=LicenseType.COMMERCIAL,
            tags=["historical", "polish", "dramatic", "epic"],
            sample_text="Słońce zachodziło w purpurze i złocie, a na pobojowisku leżały jeszcze niepochowane ciała. Kmicic stał samotny wśród trupów, z szablą w dłoni, patrząc w dal, gdzie kurz znaczył drogę ucieczki wroga.",
            rating=4.7,
            reviews_count=850,
            downloads_count=12000,
            is_verified=True,
            is_featured=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            prompt_template="Pisz w stylu Sienkiewicza: dramatyczne sceny bitewne, plastyczne opisy. Heroiczne postacie z wadami i zaletami. Patriotyczny ton bez nachalności. Dialogi pełne charakteru. Szczegóły historyczne wplecione naturalnie.",
            fine_tuning_parameters={
                "temperature": 0.75,
                "dramatic_intensity": "high",
                "historical_accuracy": True
            },
            compatibility=["historical", "adventure", "war", "romance"]
        ))

        # Style gatunkowe
        self._add_style(WritingStyle(
            style_id="style_thriller_commercial",
            name="Thriller Bestsellerowy",
            description="Szybki, napięty styl thrillerów bestsellerowych. Krótkie rozdziały, cliffhangery, napięcie.",
            category=StyleCategory.COMMERCIAL,
            tier=StyleTier.PREMIUM,
            profile=StyleProfile(
                vocabulary_complexity=0.5,
                sentence_length_avg="varied",
                paragraph_structure="tight",
                dialogue_style="heavy",
                description_density=0.4,
                emotional_intensity=0.9,
                pacing="fast",
                narrative_voice="third_limited",
                tone=["tense", "urgent", "dark", "suspenseful"],
                literary_devices=["cliffhangers", "short_chapters", "multiple_pov", "time_pressure"]
            ),
            creator_id="system",
            creator_name="NarraForge",
            price=9.99,
            currency="USD",
            license_type=LicenseType.COMMERCIAL,
            tags=["thriller", "commercial", "fast-paced", "suspense"],
            sample_text="Trzy sekundy. Tyle zostało do detonacji. Marta patrzyła na czerwone cyfry, palce drżały nad klawiaturą. Zły przewód oznaczał śmierć. Nie tylko jej. Wszystkich w budynku.",
            rating=4.6,
            reviews_count=1800,
            downloads_count=22000,
            is_verified=True,
            is_featured=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            prompt_template="Pisz jak bestsellerowy thriller: krótkie rozdziały kończące się cliffhangerami. Szybkie tempo, ciągłe napięcie. Dialogi dynamiczne, oszczędne opisy. Wielowątkowa narracja. Czas zawsze ucieka.",
            fine_tuning_parameters={
                "temperature": 0.8,
                "chapter_length": "short",
                "cliffhanger_frequency": "every_chapter"
            },
            compatibility=["thriller", "crime", "mystery", "action"]
        ))

        self._add_style(WritingStyle(
            style_id="style_romance_contemporary",
            name="Romans Współczesny",
            description="Ciepły, emocjonalny styl współczesnego romansu. Dialog-driven, humor, napięcie romantyczne.",
            category=StyleCategory.GENRE_SPECIFIC,
            tier=StyleTier.BASIC,
            profile=StyleProfile(
                vocabulary_complexity=0.5,
                sentence_length_avg="medium",
                paragraph_structure="flowing",
                dialogue_style="heavy",
                description_density=0.5,
                emotional_intensity=0.8,
                pacing="moderate",
                narrative_voice="first_person",
                tone=["warm", "witty", "romantic", "hopeful"],
                literary_devices=["internal_monologue", "banter", "emotional_beats", "slow_burn"]
            ),
            creator_id="system",
            creator_name="NarraForge",
            price=4.99,
            currency="USD",
            license_type=LicenseType.COMMERCIAL,
            tags=["romance", "contemporary", "emotional", "dialogue"],
            sample_text="Kiedy nasze spojrzenia się spotkały, poczułam to dziwne trzepotanie w żołądku. Głupie, wiem. Miałam trzydzieści lat, a nie piętnaście. Ale on się uśmiechnął i wszystkie moje postanowienia poszły do kosza.",
            rating=4.5,
            reviews_count=1500,
            downloads_count=18000,
            is_verified=True,
            is_featured=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            prompt_template="Pisz współczesny romans: ciepły, emocjonalny ton. Dużo dialogu i wewnętrznego monologu. Napięcie romantyczne budowane powoli. Humor i dowcip. Autentyczne emocje bez melodramatu.",
            fine_tuning_parameters={
                "temperature": 0.75,
                "dialogue_ratio": 0.6,
                "romantic_tension": True
            },
            compatibility=["romance", "contemporary", "women_fiction", "new_adult"]
        ))

        self._add_style(WritingStyle(
            style_id="style_religious_inspirational",
            name="Duchowa Inspiracja",
            description="Refleksyjny, inspirujący styl literatury religijnej. Głębia duchowa, nadzieja, przesłanie.",
            category=StyleCategory.GENRE_SPECIFIC,
            tier=StyleTier.BASIC,
            profile=StyleProfile(
                vocabulary_complexity=0.6,
                sentence_length_avg="varied",
                paragraph_structure="flowing",
                dialogue_style="balanced",
                description_density=0.6,
                emotional_intensity=0.7,
                pacing="moderate",
                narrative_voice="third_limited",
                tone=["hopeful", "reflective", "spiritual", "compassionate"],
                literary_devices=["symbolism", "metaphor", "parables", "inner_transformation"]
            ),
            creator_id="system",
            creator_name="NarraForge",
            price=4.99,
            currency="USD",
            license_type=LicenseType.COMMERCIAL,
            tags=["religious", "inspirational", "spiritual", "hopeful"],
            sample_text="W ciszy kaplicy Maria poczuła, jak ciężar spada z jej ramion. Nie usłyszała słów, ale wiedziała. Był przy niej. Zawsze był. Nawet w najciemniejszych momentach, gdy jej wiara słabła, On czekał cierpliwie.",
            rating=4.8,
            reviews_count=950,
            downloads_count=14000,
            is_verified=True,
            is_featured=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            prompt_template="Pisz literaturę duchową: refleksyjny, ciepły ton. Symbole i metafory duchowe wplatane naturalnie. Postaci w drodze ku wierze lub jej odnalezieniu. Nadzieja nawet w trudnościach. Przesłanie bez moralizatorstwa.",
            fine_tuning_parameters={
                "temperature": 0.7,
                "spiritual_depth": True,
                "avoid_preachiness": True
            },
            compatibility=["religious", "inspirational", "literary_fiction", "historical"]
        ))

        self._add_style(WritingStyle(
            style_id="style_dark_fantasy",
            name="Mroczne Fantasy",
            description="Ponury, brutalny styl mrocznego fantasy. Moralna szarość, brutalna rzeczywistość, mroczna atmosfera.",
            category=StyleCategory.GENRE_SPECIFIC,
            tier=StyleTier.PREMIUM,
            profile=StyleProfile(
                vocabulary_complexity=0.7,
                sentence_length_avg="varied",
                paragraph_structure="tight",
                dialogue_style="balanced",
                description_density=0.7,
                emotional_intensity=0.85,
                pacing="dynamic",
                narrative_voice="third_limited",
                tone=["dark", "gritty", "cynical", "brutal"],
                literary_devices=["foreshadowing", "unreliable_narrator", "graphic_violence", "moral_ambiguity"]
            ),
            creator_id="system",
            creator_name="NarraForge",
            price=9.99,
            currency="USD",
            license_type=LicenseType.COMMERCIAL,
            tags=["dark_fantasy", "grimdark", "brutal", "complex"],
            sample_text="Krew na jego rękach dawno przestała go prześladować. Pierwsza ofiara - to był szok. Setna? Rutyna. Teraz, stojąc nad ciałem króla, czuł tylko pustkę. I może odrobinę głodu. Obiad mógł poczekać, tron nie.",
            rating=4.7,
            reviews_count=1200,
            downloads_count=16000,
            is_verified=True,
            is_featured=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            prompt_template="Pisz mroczne fantasy: moralna szarość, brak czarno-białych postaci. Brutalna rzeczywistość, konsekwencje czynów. Cyniczny humor. Świat jest okrutny, ale są przebłyski ludzkości. Nie szczędź czytelnika.",
            fine_tuning_parameters={
                "temperature": 0.8,
                "violence_level": "graphic",
                "moral_complexity": True
            },
            compatibility=["dark_fantasy", "fantasy", "grimdark", "epic_fantasy"]
        ))

        # Style eksperymentalne
        self._add_style(WritingStyle(
            style_id="style_stream_consciousness",
            name="Strumień Świadomości",
            description="Eksperymentalny styl strumienia świadomości. Bez interpunkcji, płynne myśli, subiektywna rzeczywistość.",
            category=StyleCategory.EXPERIMENTAL,
            tier=StyleTier.PREMIUM,
            profile=StyleProfile(
                vocabulary_complexity=0.8,
                sentence_length_avg="long",
                paragraph_structure="fragmented",
                dialogue_style="minimal",
                description_density=0.8,
                emotional_intensity=0.9,
                pacing="varied",
                narrative_voice="first_person",
                tone=["introspective", "chaotic", "raw", "intimate"],
                literary_devices=["stream_of_consciousness", "fragmentation", "free_association", "temporal_shifts"]
            ),
            creator_id="system",
            creator_name="NarraForge",
            price=7.99,
            currency="USD",
            license_type=LicenseType.COMMERCIAL,
            tags=["experimental", "literary", "modernist", "psychological"],
            sample_text="i znowu ten zapach kawy przypomina mi poranki z matką nie tę kawę co teraz piję ale tamtą z mleczarni gdzie kiedyś i dlaczego zawsze wracam myślami do tamtego miejsca jakby czas nie istniał",
            rating=4.3,
            reviews_count=450,
            downloads_count=5000,
            is_verified=True,
            is_featured=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            prompt_template="Pisz strumieniem świadomości: nieprzerwany przepływ myśli. Minimalna interpunkcja. Skojarzenia prowadzą narrację. Subiektywna percepcja czasu. Surowe, niefiltrowane emocje. Granica między myślą a rzeczywistością rozmyta.",
            fine_tuning_parameters={
                "temperature": 0.9,
                "punctuation": "minimal",
                "linear_narrative": False
            },
            compatibility=["literary_fiction", "psychological", "experimental"]
        ))

        # Ustaw wyróżnione
        self.featured_styles = [
            "style_hemingway",
            "style_tolkien",
            "style_sienkiewicz",
            "style_thriller_commercial",
            "style_religious_inspirational",
            "style_dark_fantasy"
        ]

    def _add_style(self, style: WritingStyle):
        """Dodaje styl do marketplace"""
        self.styles[style.style_id] = style

    async def browse_styles(
        self,
        category: Optional[StyleCategory] = None,
        tier: Optional[StyleTier] = None,
        min_rating: float = 0.0,
        max_price: Optional[float] = None,
        tags: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        sort_by: str = "popularity",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Przegląda style w marketplace.

        Args:
            category: Filtruj po kategorii
            tier: Filtruj po poziomie
            min_rating: Minimalna ocena
            max_price: Maksymalna cena
            tags: Filtruj po tagach
            search_query: Wyszukiwanie tekstowe
            sort_by: Sortowanie (popularity, rating, price, newest)
            page: Strona
            page_size: Rozmiar strony

        Returns:
            Lista stylów z paginacją
        """
        styles = list(self.styles.values())

        # Filtrowanie
        if category:
            styles = [s for s in styles if s.category == category]

        if tier:
            styles = [s for s in styles if s.tier == tier]

        if min_rating > 0:
            styles = [s for s in styles if s.rating >= min_rating]

        if max_price is not None:
            styles = [s for s in styles if s.price <= max_price]

        if tags:
            styles = [s for s in styles if any(t in s.tags for t in tags)]

        if search_query:
            query_lower = search_query.lower()
            styles = [
                s for s in styles
                if query_lower in s.name.lower() or query_lower in s.description.lower()
            ]

        # Sortowanie
        if sort_by == "popularity":
            styles.sort(key=lambda s: s.downloads_count, reverse=True)
        elif sort_by == "rating":
            styles.sort(key=lambda s: s.rating, reverse=True)
        elif sort_by == "price":
            styles.sort(key=lambda s: s.price)
        elif sort_by == "newest":
            styles.sort(key=lambda s: s.created_at, reverse=True)

        # Paginacja
        total_count = len(styles)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        styles = styles[start_idx:end_idx]

        return {
            "styles": [self._style_to_dict(s) for s in styles],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }

    def _style_to_dict(self, style: WritingStyle, include_full: bool = False) -> Dict[str, Any]:
        """Konwertuje styl do słownika"""
        result = {
            "style_id": style.style_id,
            "name": style.name,
            "description": style.description,
            "category": style.category.value,
            "tier": style.tier.value,
            "price": style.price,
            "currency": style.currency,
            "license_type": style.license_type.value,
            "tags": style.tags,
            "rating": style.rating,
            "reviews_count": style.reviews_count,
            "downloads_count": style.downloads_count,
            "is_verified": style.is_verified,
            "is_featured": style.is_featured,
            "creator_name": style.creator_name
        }

        if include_full:
            result.update({
                "sample_text": style.sample_text,
                "profile": {
                    "vocabulary_complexity": style.profile.vocabulary_complexity,
                    "sentence_length_avg": style.profile.sentence_length_avg,
                    "paragraph_structure": style.profile.paragraph_structure,
                    "dialogue_style": style.profile.dialogue_style,
                    "description_density": style.profile.description_density,
                    "emotional_intensity": style.profile.emotional_intensity,
                    "pacing": style.profile.pacing,
                    "narrative_voice": style.profile.narrative_voice,
                    "tone": style.profile.tone,
                    "literary_devices": style.profile.literary_devices
                },
                "compatibility": style.compatibility,
                "created_at": style.created_at.isoformat(),
                "updated_at": style.updated_at.isoformat()
            })

        return result

    async def get_style(self, style_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera szczegóły stylu"""
        style = self.styles.get(style_id)
        if style:
            return self._style_to_dict(style, include_full=True)
        return None

    async def get_featured_styles(self) -> List[Dict[str, Any]]:
        """Pobiera wyróżnione style"""
        featured = [self.styles[sid] for sid in self.featured_styles if sid in self.styles]
        return [self._style_to_dict(s) for s in featured]

    async def purchase_style(
        self,
        user_id: str,
        style_id: str,
        payment_method: str
    ) -> Dict[str, Any]:
        """
        Realizuje zakup stylu.

        Args:
            user_id: ID użytkownika
            style_id: ID stylu
            payment_method: Metoda płatności

        Returns:
            Informacje o zakupie
        """
        style = self.styles.get(style_id)
        if not style:
            raise ValueError(f"Styl nie znaleziony: {style_id}")

        # Sprawdź czy już zakupiony
        user_purchases = self.purchases.get(user_id, [])
        if any(p.style_id == style_id and p.is_active for p in user_purchases):
            raise ValueError("Styl już zakupiony")

        # Utwórz zakup
        purchase = StylePurchase(
            purchase_id=f"purchase_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            style_id=style_id,
            price_paid=style.price,
            currency=style.currency,
            license_type=style.license_type,
            purchased_at=datetime.now(),
            expires_at=None,  # Może być ustawione dla subskrypcji
            is_active=True
        )

        if user_id not in self.purchases:
            self.purchases[user_id] = []
        self.purchases[user_id].append(purchase)

        # Zwiększ licznik pobrań
        style.downloads_count += 1

        return {
            "success": True,
            "purchase_id": purchase.purchase_id,
            "style_id": style_id,
            "style_name": style.name,
            "price_paid": purchase.price_paid,
            "currency": purchase.currency,
            "license_type": purchase.license_type.value,
            "purchased_at": purchase.purchased_at.isoformat()
        }

    async def get_user_library(self, user_id: str) -> List[Dict[str, Any]]:
        """Pobiera bibliotekę stylów użytkownika"""
        user_purchases = self.purchases.get(user_id, [])
        active_purchases = [p for p in user_purchases if p.is_active]

        library = []
        for purchase in active_purchases:
            style = self.styles.get(purchase.style_id)
            if style:
                library.append({
                    "purchase_id": purchase.purchase_id,
                    "style": self._style_to_dict(style),
                    "purchased_at": purchase.purchased_at.isoformat(),
                    "license_type": purchase.license_type.value,
                    "expires_at": purchase.expires_at.isoformat() if purchase.expires_at else None
                })

        return library

    async def add_review(
        self,
        user_id: str,
        user_name: str,
        style_id: str,
        rating: int,
        title: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Dodaje recenzję stylu.

        Args:
            user_id: ID użytkownika
            user_name: Nazwa użytkownika
            style_id: ID stylu
            rating: Ocena (1-5)
            title: Tytuł recenzji
            content: Treść recenzji

        Returns:
            Informacje o recenzji
        """
        style = self.styles.get(style_id)
        if not style:
            raise ValueError(f"Styl nie znaleziony: {style_id}")

        if rating < 1 or rating > 5:
            raise ValueError("Ocena musi być między 1 a 5")

        # Sprawdź czy użytkownik kupił styl
        user_purchases = self.purchases.get(user_id, [])
        verified = any(p.style_id == style_id for p in user_purchases)

        review = StyleReview(
            review_id=f"review_{uuid.uuid4().hex[:12]}",
            style_id=style_id,
            user_id=user_id,
            user_name=user_name,
            rating=rating,
            title=title,
            content=content,
            helpful_votes=0,
            created_at=datetime.now(),
            verified_purchase=verified
        )

        if style_id not in self.reviews:
            self.reviews[style_id] = []
        self.reviews[style_id].append(review)

        # Aktualizuj średnią ocenę
        all_reviews = self.reviews[style_id]
        avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
        style.rating = round(avg_rating, 1)
        style.reviews_count = len(all_reviews)

        return {
            "success": True,
            "review_id": review.review_id,
            "verified_purchase": verified
        }

    async def get_style_reviews(
        self,
        style_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Pobiera recenzje stylu"""
        style = self.styles.get(style_id)
        if not style:
            raise ValueError(f"Styl nie znaleziony: {style_id}")

        reviews = self.reviews.get(style_id, [])
        reviews.sort(key=lambda r: r.created_at, reverse=True)

        total_count = len(reviews)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        reviews = reviews[start_idx:end_idx]

        return {
            "reviews": [
                {
                    "review_id": r.review_id,
                    "user_name": r.user_name,
                    "rating": r.rating,
                    "title": r.title,
                    "content": r.content,
                    "helpful_votes": r.helpful_votes,
                    "created_at": r.created_at.isoformat(),
                    "verified_purchase": r.verified_purchase
                }
                for r in reviews
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "average_rating": style.rating
        }

    async def create_custom_style(
        self,
        creator_id: str,
        creator_name: str,
        name: str,
        description: str,
        profile: Dict[str, Any],
        sample_text: str,
        price: float,
        tags: List[str],
        compatibility: List[str]
    ) -> Dict[str, Any]:
        """
        Tworzy niestandardowy styl użytkownika.

        Args:
            creator_id: ID twórcy
            creator_name: Nazwa twórcy
            name: Nazwa stylu
            description: Opis stylu
            profile: Profil stylu
            sample_text: Przykładowy tekst
            price: Cena (0 dla darmowych)
            tags: Tagi
            compatibility: Kompatybilne gatunki

        Returns:
            Utworzony styl
        """
        style_id = f"style_custom_{uuid.uuid4().hex[:12]}"

        style_profile = StyleProfile(
            vocabulary_complexity=profile.get("vocabulary_complexity", 0.5),
            sentence_length_avg=profile.get("sentence_length_avg", "medium"),
            paragraph_structure=profile.get("paragraph_structure", "flowing"),
            dialogue_style=profile.get("dialogue_style", "balanced"),
            description_density=profile.get("description_density", 0.5),
            emotional_intensity=profile.get("emotional_intensity", 0.5),
            pacing=profile.get("pacing", "moderate"),
            narrative_voice=profile.get("narrative_voice", "third_limited"),
            tone=profile.get("tone", ["neutral"]),
            literary_devices=profile.get("literary_devices", [])
        )

        # Automatycznie generuj szablon promptu
        prompt_template = self._generate_prompt_template(style_profile, description)

        style = WritingStyle(
            style_id=style_id,
            name=name,
            description=description,
            category=StyleCategory.CUSTOM,
            tier=StyleTier.BASIC if price > 0 else StyleTier.FREE,
            profile=style_profile,
            creator_id=creator_id,
            creator_name=creator_name,
            price=price,
            currency="USD",
            license_type=LicenseType.COMMERCIAL if price > 0 else LicenseType.PERSONAL,
            tags=tags,
            sample_text=sample_text,
            rating=0.0,
            reviews_count=0,
            downloads_count=0,
            is_verified=False,
            is_featured=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            prompt_template=prompt_template,
            fine_tuning_parameters={
                "temperature": 0.75,
                "custom_style": True
            },
            compatibility=compatibility
        )

        self.styles[style_id] = style

        return {
            "success": True,
            "style_id": style_id,
            "style": self._style_to_dict(style, include_full=True)
        }

    def _generate_prompt_template(self, profile: StyleProfile, description: str) -> str:
        """Generuje szablon promptu na podstawie profilu"""
        template_parts = [f"Pisz w następującym stylu: {description}"]

        if profile.vocabulary_complexity > 0.7:
            template_parts.append("Używaj bogatego, złożonego słownictwa.")
        elif profile.vocabulary_complexity < 0.3:
            template_parts.append("Używaj prostego, przystępnego słownictwa.")

        if profile.sentence_length_avg == "short":
            template_parts.append("Zdania powinny być krótkie i zwięzłe.")
        elif profile.sentence_length_avg == "long":
            template_parts.append("Używaj rozbudowanych, złożonych zdań.")

        if profile.pacing == "fast":
            template_parts.append("Utrzymuj szybkie tempo narracji.")
        elif profile.pacing == "slow":
            template_parts.append("Pozwól narracji płynąć powoli, z refleksją.")

        if profile.dialogue_style == "heavy":
            template_parts.append("Dużo dialogu, rozmowy napędzają akcję.")
        elif profile.dialogue_style == "minimal":
            template_parts.append("Minimalizuj dialog, skup się na narracji.")

        template_parts.append(f"Ton narracji: {', '.join(profile.tone)}.")

        if profile.literary_devices:
            template_parts.append(f"Wykorzystuj: {', '.join(profile.literary_devices)}.")

        return " ".join(template_parts)

    async def get_style_prompt(self, style_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera szablon promptu dla stylu (tylko dla zakupionych)"""
        style = self.styles.get(style_id)
        if not style:
            return None

        return {
            "style_id": style_id,
            "name": style.name,
            "prompt_template": style.prompt_template,
            "fine_tuning_parameters": style.fine_tuning_parameters,
            "profile": {
                "vocabulary_complexity": style.profile.vocabulary_complexity,
                "sentence_length_avg": style.profile.sentence_length_avg,
                "pacing": style.profile.pacing,
                "narrative_voice": style.profile.narrative_voice,
                "tone": style.profile.tone
            }
        }

    def get_categories(self) -> List[Dict[str, Any]]:
        """Zwraca kategorie stylów"""
        return [
            {
                "category": StyleCategory.AUTHOR_INSPIRED.value,
                "name": "Inspirowane Autorami",
                "description": "Style naśladujące wielkich pisarzy"
            },
            {
                "category": StyleCategory.GENRE_SPECIFIC.value,
                "name": "Gatunkowe",
                "description": "Style zoptymalizowane dla konkretnych gatunków"
            },
            {
                "category": StyleCategory.CULTURAL.value,
                "name": "Kulturowe",
                "description": "Style odzwierciedlające różne tradycje literackie"
            },
            {
                "category": StyleCategory.HISTORICAL.value,
                "name": "Historyczne",
                "description": "Style z różnych epok literackich"
            },
            {
                "category": StyleCategory.EXPERIMENTAL.value,
                "name": "Eksperymentalne",
                "description": "Nowatorskie i awangardowe style"
            },
            {
                "category": StyleCategory.COMMERCIAL.value,
                "name": "Komercyjne",
                "description": "Style optymalizowane pod bestsellery"
            },
            {
                "category": StyleCategory.LITERARY.value,
                "name": "Literackie",
                "description": "Style wysokiej literatury"
            },
            {
                "category": StyleCategory.CUSTOM.value,
                "name": "Niestandardowe",
                "description": "Style stworzone przez użytkowników"
            }
        ]

    def get_tiers(self) -> List[Dict[str, Any]]:
        """Zwraca poziomy stylów"""
        return [
            {
                "tier": StyleTier.FREE.value,
                "name": "Darmowe",
                "description": "Podstawowe style bez opłat",
                "price_range": "0"
            },
            {
                "tier": StyleTier.BASIC.value,
                "name": "Podstawowe",
                "description": "Rozbudowane style w przystępnej cenie",
                "price_range": "1-5 USD"
            },
            {
                "tier": StyleTier.PREMIUM.value,
                "name": "Premium",
                "description": "Zaawansowane style z dodatkowymi funkcjami",
                "price_range": "5-15 USD"
            },
            {
                "tier": StyleTier.EXCLUSIVE.value,
                "name": "Ekskluzywne",
                "description": "Unikalne style limitowanej dostępności",
                "price_range": "15+ USD"
            }
        ]


# Singleton instance
def get_style_marketplace_service() -> StyleMarketplaceService:
    """Pobiera instancję serwisu Style Marketplace"""
    return StyleMarketplaceService()


# Export dla API
style_marketplace_service = get_style_marketplace_service()
