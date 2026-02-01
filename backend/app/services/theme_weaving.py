"""
Subconscious Theme Weaving Service - NarraForge 3.0
Nieświadome wplatanie głębokich tematów w narrację
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from datetime import datetime
import random
import math

logger = logging.getLogger(__name__)


class ThemeCategory(str, Enum):
    """Kategorie tematyczne"""
    EXISTENTIAL = "existential"  # Tematy egzystencjalne
    MORAL = "moral"  # Dylematy moralne
    PSYCHOLOGICAL = "psychological"  # Tematy psychologiczne
    SOCIAL = "social"  # Tematy społeczne
    SPIRITUAL = "spiritual"  # Tematy duchowe
    PHILOSOPHICAL = "philosophical"  # Tematy filozoficzne
    EMOTIONAL = "emotional"  # Tematy emocjonalne
    UNIVERSAL = "universal"  # Tematy uniwersalne


class WeavingIntensity(str, Enum):
    """Intensywność wplatania"""
    SUBTLE = "subtle"  # Delikatne, prawie niewidoczne
    MODERATE = "moderate"  # Umiarkowane
    PROMINENT = "prominent"  # Wyraźne
    DOMINANT = "dominant"  # Dominujące


class WeavingTechnique(str, Enum):
    """Techniki wplatania tematów"""
    SYMBOLISM = "symbolism"  # Przez symbole
    DIALOGUE = "dialogue"  # Przez dialog
    IMAGERY = "imagery"  # Przez obrazowanie
    MOTIF = "motif"  # Przez motywy przewodnie
    METAPHOR = "metaphor"  # Przez metafory
    FORESHADOWING = "foreshadowing"  # Przez zapowiedzi
    CONTRAST = "contrast"  # Przez kontrast
    PARALLEL = "parallel"  # Przez paralele
    SUBTEXT = "subtext"  # Przez podtekst
    ATMOSPHERE = "atmosphere"  # Przez atmosferę


@dataclass
class Theme:
    """Reprezentacja tematu"""
    theme_id: str
    name: str
    category: ThemeCategory
    description: str
    core_concepts: List[str]
    related_symbols: List[str]
    emotional_associations: List[str]
    philosophical_questions: List[str]
    literary_traditions: List[str]
    archetypal_patterns: List[str]


@dataclass
class ThemeOccurrence:
    """Wystąpienie tematu w tekście"""
    theme_id: str
    chapter: int
    scene: Optional[int]
    technique: WeavingTechnique
    intensity: WeavingIntensity
    manifestation: str  # Jak temat się manifestuje
    context: str  # Kontekst wystąpienia
    reader_perception: str  # Jak czytelnik może to odebrać


@dataclass
class ThemeArc:
    """Łuk tematyczny przez całą narrację"""
    theme_id: str
    introduction_chapter: int
    development_points: List[Tuple[int, str]]  # (rozdział, opis rozwoju)
    climax_chapter: int
    resolution_type: str  # "resolved", "open", "transformed", "echoing"
    total_occurrences: int
    intensity_curve: List[float]  # Intensywność w kolejnych rozdziałach


@dataclass
class WeavingPlan:
    """Plan wplatania tematu"""
    plan_id: str
    project_id: str
    themes: List[Theme]
    primary_theme: Theme
    secondary_themes: List[Theme]
    theme_arcs: Dict[str, ThemeArc]
    chapter_distribution: Dict[int, List[ThemeOccurrence]]
    recommended_techniques: Dict[str, List[WeavingTechnique]]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SubconsciousLayer:
    """Warstwa podświadoma narracji"""
    layer_id: str
    depth_level: int  # 1-5, gdzie 5 to najgłębszy
    hidden_meanings: List[str]
    symbol_network: Dict[str, List[str]]  # Symbol -> znaczenia
    emotional_undercurrent: str
    psychological_triggers: List[str]
    reader_subconscious_effects: List[str]


class SubconsciousThemeWeavingService:
    """
    Serwis do nieświadomego wplatania głębokich tematów w narrację.
    Tworzy wielowarstwowe znaczenia odczuwane podświadomie przez czytelnika.
    """

    def __init__(self):
        self.theme_library: Dict[str, Theme] = {}
        self.active_plans: Dict[str, WeavingPlan] = {}
        self.subconscious_layers: Dict[str, List[SubconsciousLayer]] = {}
        self._initialize_theme_library()
        logger.info("SubconsciousThemeWeavingService zainicjalizowany")

    def _initialize_theme_library(self):
        """Inicjalizuje bibliotekę tematów"""

        # Tematy egzystencjalne
        self._add_theme(Theme(
            theme_id="identity",
            name="Tożsamość",
            category=ThemeCategory.EXISTENTIAL,
            description="Poszukiwanie i definiowanie własnej tożsamości",
            core_concepts=["kim jestem", "autentyczność", "maska vs prawdziwe ja", "metamorfoza"],
            related_symbols=["lustro", "maska", "cień", "motyl", "wąż zrzucający skórę"],
            emotional_associations=["niepewność", "odkrycie", "akceptacja", "alienacja"],
            philosophical_questions=[
                "Kim jestem naprawdę?",
                "Czy tożsamość jest stała czy płynna?",
                "Jak definiują nas inni?"
            ],
            literary_traditions=["bildungsroman", "powieść psychologiczna"],
            archetypal_patterns=["podróż bohatera", "śmierć i odrodzenie", "zejście do podziemi"]
        ))

        self._add_theme(Theme(
            theme_id="mortality",
            name="Śmiertelność",
            category=ThemeCategory.EXISTENTIAL,
            description="Konfrontacja z nieuchronnością śmierci",
            core_concepts=["przemijanie", "dziedzictwo", "strach przed śmiercią", "akceptacja"],
            related_symbols=["zegar", "piasek", "jesień", "zachód słońca", "kwiaty więdnące"],
            emotional_associations=["lęk", "smutek", "pogodzenie", "desperacja", "spokój"],
            philosophical_questions=[
                "Co nadaje życiu sens wobec śmierci?",
                "Jak żyć świadomie wobec końca?",
                "Co pozostaje po nas?"
            ],
            literary_traditions=["memento mori", "elegia"],
            archetypal_patterns=["taniec śmierci", "podróż do zaświatów", "ostatnia podróż"]
        ))

        self._add_theme(Theme(
            theme_id="freedom_vs_fate",
            name="Wolność vs Przeznaczenie",
            category=ThemeCategory.EXISTENTIAL,
            description="Napięcie między wolną wolą a determinizmem",
            core_concepts=["wybór", "konsekwencje", "przepowiednia", "bunt przeciw losowi"],
            related_symbols=["skrzyżowanie dróg", "nić przeznaczenia", "klatka", "ptak"],
            emotional_associations=["determinacja", "bezsilność", "nadzieja", "rezygnacja"],
            philosophical_questions=[
                "Czy jesteśmy wolni w swoich wyborach?",
                "Czy możemy uciec przed przeznaczeniem?",
                "Co definiuje nasz los - wybory czy okoliczności?"
            ],
            literary_traditions=["tragedia grecka", "literatura egzystencjalna"],
            archetypal_patterns=["walka z losem", "samospełniająca się przepowiednia"]
        ))

        # Tematy moralne
        self._add_theme(Theme(
            theme_id="good_evil",
            name="Dobro i Zło",
            category=ThemeCategory.MORAL,
            description="Natura dobra i zła, ich granice i współistnienie",
            core_concepts=["moralna szarość", "pokusa", "odkupienie", "korupcja"],
            related_symbols=["światło/ciemność", "anioł/demon", "jabłko", "wąż"],
            emotional_associations=["konflikt wewnętrzny", "wina", "triumf", "upadek"],
            philosophical_questions=[
                "Czy istnieje absolutne dobro i zło?",
                "Czy cel uświęca środki?",
                "Czy można odkupić zło?"
            ],
            literary_traditions=["moralitet", "powieść gotycka"],
            archetypal_patterns=["upadek", "odkupienie", "kuszenie"]
        ))

        self._add_theme(Theme(
            theme_id="justice",
            name="Sprawiedliwość",
            category=ThemeCategory.MORAL,
            description="Poszukiwanie sprawiedliwości i jej natura",
            core_concepts=["zemsta vs przebaczenie", "prawo vs moralność", "kara", "nagroda"],
            related_symbols=["waga", "miecz", "oczy zasłonięte", "więzienie"],
            emotional_associations=["gniew", "satysfakcja", "rozczarowanie", "ulga"],
            philosophical_questions=[
                "Czym jest prawdziwa sprawiedliwość?",
                "Czy zemsta przynosi sprawiedliwość?",
                "Kto ma prawo osądzać?"
            ],
            literary_traditions=["tragedia zemsty", "dramat sądowy"],
            archetypal_patterns=["sędzia", "mściciel", "ofiara"]
        ))

        # Tematy duchowe
        self._add_theme(Theme(
            theme_id="faith",
            name="Wiara",
            category=ThemeCategory.SPIRITUAL,
            description="Wiara, zwątpienie i poszukiwanie transcendencji",
            core_concepts=["zaufanie", "zwątpienie", "objawienie", "łaska", "nawrócenie"],
            related_symbols=["światło", "krzyż", "gołębica", "ogień", "woda"],
            emotional_associations=["pokój", "niepewność", "zachwyt", "pocieszenie"],
            philosophical_questions=[
                "Czym jest wiara wobec cierpienia?",
                "Jak znaleźć sens w wierze?",
                "Czy wiara wymaga dowodów?"
            ],
            literary_traditions=["literatura religijna", "mistycyzm"],
            archetypal_patterns=["ciemna noc duszy", "objawienie", "pielgrzymka"]
        ))

        self._add_theme(Theme(
            theme_id="redemption",
            name="Odkupienie",
            category=ThemeCategory.SPIRITUAL,
            description="Droga od upadku do odkupienia",
            core_concepts=["grzech", "pokuta", "przebaczenie", "transformacja", "łaska"],
            related_symbols=["oczyszczenie wodą", "ogień", "światło po ciemności", "feniks"],
            emotional_associations=["wina", "nadzieja", "ulga", "wdzięczność"],
            philosophical_questions=[
                "Czy każdy zasługuje na odkupienie?",
                "Co jest ceną odkupienia?",
                "Czy można odkupić niewybaczalne?"
            ],
            literary_traditions=["literatura chrześcijańska", "dramat odkupienia"],
            archetypal_patterns=["śmierć i odrodzenie", "zejście i powrót", "przemiana"]
        ))

        # Tematy psychologiczne
        self._add_theme(Theme(
            theme_id="trauma",
            name="Trauma",
            category=ThemeCategory.PSYCHOLOGICAL,
            description="Wpływ traumy na psychikę i jej przepracowanie",
            core_concepts=["rana", "wspomnienia", "unikanie", "konfrontacja", "uzdrowienie"],
            related_symbols=["blizna", "rozbite lustro", "echo", "cień", "więzienie"],
            emotional_associations=["ból", "strach", "odrętwienie", "nadzieja na uzdrowienie"],
            philosophical_questions=[
                "Jak trauma kształtuje tożsamość?",
                "Czy można całkowicie się uzdrowić?",
                "Jak przekuć ból w siłę?"
            ],
            literary_traditions=["literatura traumy", "powieść psychologiczna"],
            archetypal_patterns=["rana pierwotna", "uzdrowiciel raniony", "powrót do źródła"]
        ))

        self._add_theme(Theme(
            theme_id="isolation",
            name="Izolacja",
            category=ThemeCategory.PSYCHOLOGICAL,
            description="Samotność, alienacja i potrzeba przynależności",
            core_concepts=["samotność", "wyobcowanie", "połączenie", "granice"],
            related_symbols=["wyspa", "mur", "okno", "most", "pustka"],
            emotional_associations=["tęsknota", "lęk", "spokój", "desperacja"],
            philosophical_questions=[
                "Czy samotność jest wyborem czy losem?",
                "Czy prawdziwe połączenie jest możliwe?",
                "Co tracimy w izolacji?"
            ],
            literary_traditions=["literatura egzystencjalna", "robinsonada"],
            archetypal_patterns=["pustelnik", "wyrzutek", "poszukiwanie domu"]
        ))

        # Tematy społeczne
        self._add_theme(Theme(
            theme_id="power",
            name="Władza",
            category=ThemeCategory.SOCIAL,
            description="Natura władzy, jej zdobywanie i korupcja",
            core_concepts=["kontrola", "odpowiedzialność", "tyrannia", "służba"],
            related_symbols=["korona", "tron", "miecz", "łańcuch", "wieża"],
            emotional_associations=["ambicja", "strach", "respekt", "bunt"],
            philosophical_questions=[
                "Czy władza korumpuje nieuchronnie?",
                "Kto zasługuje na władzę?",
                "Jaka jest cena władzy?"
            ],
            literary_traditions=["tragedia polityczna", "dystopia"],
            archetypal_patterns=["tyran", "król-sługa", "buntownik"]
        ))

        self._add_theme(Theme(
            theme_id="belonging",
            name="Przynależność",
            category=ThemeCategory.SOCIAL,
            description="Potrzeba bycia częścią społeczności",
            core_concepts=["wspólnota", "wykluczenie", "akceptacja", "tożsamość grupowa"],
            related_symbols=["krąg", "dom", "rodzina", "granica", "most"],
            emotional_associations=["ciepło", "odrzucenie", "bezpieczeństwo", "tęsknota"],
            philosophical_questions=[
                "Co definiuje naszą przynależność?",
                "Ile z siebie tracimy dla grupy?",
                "Czy można należeć do wielu światów?"
            ],
            literary_traditions=["saga rodzinna", "literatura diasporyczna"],
            archetypal_patterns=["powrót do domu", "poszukiwanie korzeni", "wybranie plemienia"]
        ))

        # Tematy uniwersalne
        self._add_theme(Theme(
            theme_id="love",
            name="Miłość",
            category=ThemeCategory.UNIVERSAL,
            description="Miłość we wszystkich jej formach",
            core_concepts=["poświęcenie", "tęsknota", "utrata", "połączenie", "wzajemność"],
            related_symbols=["serce", "ogień", "róża", "węzeł", "światło"],
            emotional_associations=["radość", "ból", "nadzieja", "spełnienie"],
            philosophical_questions=[
                "Czym jest prawdziwa miłość?",
                "Czy miłość może być bezwarunkowa?",
                "Jak miłość zmienia nas?"
            ],
            literary_traditions=["romans", "poezja miłosna"],
            archetypal_patterns=["połączenie dusz", "miłość niemożliwa", "poświęcenie"]
        ))

        self._add_theme(Theme(
            theme_id="sacrifice",
            name="Poświęcenie",
            category=ThemeCategory.UNIVERSAL,
            description="Gotowość do rezygnacji dla wyższego dobra",
            core_concepts=["ofiara", "wybór", "wartości", "altruizm", "koszt"],
            related_symbols=["krzyż", "ołtarz", "ogień", "krew", "dar"],
            emotional_associations=["ból", "szlachetność", "żal", "spełnienie"],
            philosophical_questions=[
                "Co warto poświęcić?",
                "Czy poświęcenie jest zawsze szlachetne?",
                "Kiedy poświęcenie staje się głupotą?"
            ],
            literary_traditions=["tragedia", "literatura religijna"],
            archetypal_patterns=["baranek ofiarny", "bohater-męczennik", "rodzicielskie poświęcenie"]
        ))

        self._add_theme(Theme(
            theme_id="truth",
            name="Prawda",
            category=ThemeCategory.PHILOSOPHICAL,
            description="Poszukiwanie prawdy i jej natura",
            core_concepts=["kłamstwo", "iluzja", "objawienie", "relatywizm", "pewność"],
            related_symbols=["światło", "lustro", "zasłona", "księga", "oko"],
            emotional_associations=["ciekawość", "szok", "ulga", "rozczarowanie"],
            philosophical_questions=[
                "Czy istnieje obiektywna prawda?",
                "Czy prawda zawsze wyzwala?",
                "Jak rozpoznać prawdę od iluzji?"
            ],
            literary_traditions=["powieść detektywistyczna", "literatura filozoficzna"],
            archetypal_patterns=["poszukiwacz prawdy", "zerwanie zasłony", "konfrontacja z rzeczywistością"]
        ))

        self._add_theme(Theme(
            theme_id="transformation",
            name="Transformacja",
            category=ThemeCategory.UNIVERSAL,
            description="Proces głębokiej zmiany i metamorfozy",
            core_concepts=["zmiana", "ewolucja", "kryzys", "odrodzenie", "nowa tożsamość"],
            related_symbols=["motyl", "feniks", "wąż", "jajo", "kokon"],
            emotional_associations=["niepewność", "nadzieja", "ból wzrostu", "triumf"],
            philosophical_questions=[
                "Co wywołuje prawdziwą zmianę?",
                "Czy możemy kontrolować naszą transformację?",
                "Co tracimy, gdy się zmieniamy?"
            ],
            literary_traditions=["bildungsroman", "literatura metamorfozy"],
            archetypal_patterns=["śmierć ego", "inicjacja", "odrodzenie"]
        ))

    def _add_theme(self, theme: Theme):
        """Dodaje temat do biblioteki"""
        self.theme_library[theme.theme_id] = theme

    async def create_weaving_plan(
        self,
        project_id: str,
        theme_ids: List[str],
        chapter_count: int,
        primary_theme_id: Optional[str] = None,
        intensity_preference: WeavingIntensity = WeavingIntensity.MODERATE
    ) -> WeavingPlan:
        """
        Tworzy plan wplatania tematów dla projektu.

        Args:
            project_id: ID projektu
            theme_ids: Lista ID tematów do wplecenia
            chapter_count: Liczba rozdziałów
            primary_theme_id: Opcjonalny główny temat
            intensity_preference: Preferowana intensywność

        Returns:
            WeavingPlan z kompletnym planem wplatania
        """
        logger.info(f"Tworzę plan wplatania dla projektu {project_id}")

        # Pobierz tematy
        themes = [self.theme_library[tid] for tid in theme_ids if tid in self.theme_library]

        if not themes:
            raise ValueError("Nie znaleziono żadnych tematów")

        # Ustal główny temat
        if primary_theme_id and primary_theme_id in self.theme_library:
            primary_theme = self.theme_library[primary_theme_id]
        else:
            primary_theme = themes[0]

        secondary_themes = [t for t in themes if t.theme_id != primary_theme.theme_id]

        # Generuj łuki tematyczne
        theme_arcs = {}
        for theme in themes:
            arc = await self._generate_theme_arc(
                theme, chapter_count,
                is_primary=(theme.theme_id == primary_theme.theme_id),
                intensity=intensity_preference
            )
            theme_arcs[theme.theme_id] = arc

        # Generuj dystrybucję w rozdziałach
        chapter_distribution = await self._generate_chapter_distribution(
            themes, theme_arcs, chapter_count, intensity_preference
        )

        # Rekomendowane techniki dla każdego tematu
        recommended_techniques = {
            theme.theme_id: self._get_recommended_techniques(theme, intensity_preference)
            for theme in themes
        }

        plan_id = f"weaving_{project_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        plan = WeavingPlan(
            plan_id=plan_id,
            project_id=project_id,
            themes=themes,
            primary_theme=primary_theme,
            secondary_themes=secondary_themes,
            theme_arcs=theme_arcs,
            chapter_distribution=chapter_distribution,
            recommended_techniques=recommended_techniques
        )

        self.active_plans[plan_id] = plan
        logger.info(f"Utworzono plan wplatania: {plan_id}")

        return plan

    async def _generate_theme_arc(
        self,
        theme: Theme,
        chapter_count: int,
        is_primary: bool,
        intensity: WeavingIntensity
    ) -> ThemeArc:
        """Generuje łuk tematyczny"""

        # Punkt wprowadzenia
        if is_primary:
            intro_chapter = 1
        else:
            intro_chapter = random.randint(2, max(3, chapter_count // 4))

        # Punkt kulminacyjny
        climax_chapter = int(chapter_count * 0.75) + random.randint(-2, 2)
        climax_chapter = max(intro_chapter + 2, min(climax_chapter, chapter_count - 1))

        # Punkty rozwoju
        development_count = 3 if is_primary else 2
        development_points = []

        for i in range(development_count):
            dev_chapter = intro_chapter + ((climax_chapter - intro_chapter) * (i + 1)) // (development_count + 1)
            development_points.append((
                dev_chapter,
                f"Rozwinięcie tematu '{theme.name}' - etap {i + 1}"
            ))

        # Typ rozwiązania
        resolution_types = ["resolved", "open", "transformed", "echoing"]
        resolution = random.choice(resolution_types) if not is_primary else "transformed"

        # Krzywa intensywności
        intensity_curve = self._generate_intensity_curve(
            chapter_count, intro_chapter, climax_chapter, intensity
        )

        # Całkowita liczba wystąpień
        base_occurrences = chapter_count // 2 if is_primary else chapter_count // 4
        total_occurrences = self._adjust_by_intensity(base_occurrences, intensity)

        return ThemeArc(
            theme_id=theme.theme_id,
            introduction_chapter=intro_chapter,
            development_points=development_points,
            climax_chapter=climax_chapter,
            resolution_type=resolution,
            total_occurrences=total_occurrences,
            intensity_curve=intensity_curve
        )

    def _generate_intensity_curve(
        self,
        chapter_count: int,
        intro: int,
        climax: int,
        intensity: WeavingIntensity
    ) -> List[float]:
        """Generuje krzywą intensywności tematu"""
        curve = []
        base_intensity = {
            WeavingIntensity.SUBTLE: 0.2,
            WeavingIntensity.MODERATE: 0.4,
            WeavingIntensity.PROMINENT: 0.6,
            WeavingIntensity.DOMINANT: 0.8
        }[intensity]

        for chapter in range(1, chapter_count + 1):
            if chapter < intro:
                # Przed wprowadzeniem - brak tematu
                curve.append(0.0)
            elif chapter == climax:
                # Kulminacja - maksymalna intensywność
                curve.append(min(1.0, base_intensity * 1.5))
            elif chapter < climax:
                # Narastanie
                progress = (chapter - intro) / (climax - intro)
                curve.append(base_intensity * (0.5 + 0.5 * progress))
            else:
                # Po kulminacji - stopniowe wyciszanie
                remaining = (chapter_count - chapter) / (chapter_count - climax)
                curve.append(base_intensity * (0.3 + 0.5 * remaining))

        return curve

    def _adjust_by_intensity(self, base: int, intensity: WeavingIntensity) -> int:
        """Dostosowuje wartość do intensywności"""
        multipliers = {
            WeavingIntensity.SUBTLE: 0.5,
            WeavingIntensity.MODERATE: 1.0,
            WeavingIntensity.PROMINENT: 1.5,
            WeavingIntensity.DOMINANT: 2.0
        }
        return max(1, int(base * multipliers[intensity]))

    async def _generate_chapter_distribution(
        self,
        themes: List[Theme],
        arcs: Dict[str, ThemeArc],
        chapter_count: int,
        intensity: WeavingIntensity
    ) -> Dict[int, List[ThemeOccurrence]]:
        """Generuje dystrybucję tematów w rozdziałach"""
        distribution = {chapter: [] for chapter in range(1, chapter_count + 1)}

        for theme in themes:
            arc = arcs[theme.theme_id]

            for chapter in range(1, chapter_count + 1):
                # Sprawdź czy temat powinien wystąpić
                intensity_value = arc.intensity_curve[chapter - 1] if chapter <= len(arc.intensity_curve) else 0

                if intensity_value > 0 and random.random() < intensity_value:
                    # Wybierz technikę
                    technique = random.choice(list(WeavingTechnique))

                    # Określ intensywność wystąpienia
                    if intensity_value > 0.7:
                        occurrence_intensity = WeavingIntensity.PROMINENT
                    elif intensity_value > 0.4:
                        occurrence_intensity = WeavingIntensity.MODERATE
                    else:
                        occurrence_intensity = WeavingIntensity.SUBTLE

                    occurrence = ThemeOccurrence(
                        theme_id=theme.theme_id,
                        chapter=chapter,
                        scene=random.randint(1, 3),
                        technique=technique,
                        intensity=occurrence_intensity,
                        manifestation=self._generate_manifestation(theme, technique),
                        context=self._generate_context(theme, chapter, arc),
                        reader_perception=self._generate_reader_perception(theme, technique, occurrence_intensity)
                    )

                    distribution[chapter].append(occurrence)

        return distribution

    def _generate_manifestation(self, theme: Theme, technique: WeavingTechnique) -> str:
        """Generuje opis manifestacji tematu"""
        manifestations = {
            WeavingTechnique.SYMBOLISM: f"Symbol {random.choice(theme.related_symbols)} reprezentujący {theme.name.lower()}",
            WeavingTechnique.DIALOGUE: f"Dialog poruszający {random.choice(theme.core_concepts)}",
            WeavingTechnique.IMAGERY: f"Obraz ewokujący {random.choice(theme.emotional_associations)}",
            WeavingTechnique.MOTIF: f"Powracający motyw związany z {theme.name.lower()}",
            WeavingTechnique.METAPHOR: f"Metafora {random.choice(theme.related_symbols)} dla {random.choice(theme.core_concepts)}",
            WeavingTechnique.FORESHADOWING: f"Zapowiedź odnosząca się do {random.choice(theme.core_concepts)}",
            WeavingTechnique.CONTRAST: f"Kontrast ukazujący {random.choice(theme.core_concepts)}",
            WeavingTechnique.PARALLEL: f"Paralela z {random.choice(theme.archetypal_patterns)}",
            WeavingTechnique.SUBTEXT: f"Podtekst sugerujący {random.choice(theme.philosophical_questions)}",
            WeavingTechnique.ATMOSPHERE: f"Atmosfera oddająca {random.choice(theme.emotional_associations)}"
        }
        return manifestations.get(technique, f"Manifestacja tematu {theme.name}")

    def _generate_context(self, theme: Theme, chapter: int, arc: ThemeArc) -> str:
        """Generuje kontekst wystąpienia"""
        if chapter == arc.introduction_chapter:
            return f"Wprowadzenie tematu {theme.name} - pierwsze zetknięcie czytelnika"
        elif chapter == arc.climax_chapter:
            return f"Kulminacja tematu {theme.name} - pełne rozwinięcie"
        elif any(chapter == dp[0] for dp in arc.development_points):
            return f"Rozwój tematu {theme.name} - pogłębienie rozumienia"
        else:
            return f"Kontynuacja wątku {theme.name} - wzmocnienie obecności"

    def _generate_reader_perception(
        self,
        theme: Theme,
        technique: WeavingTechnique,
        intensity: WeavingIntensity
    ) -> str:
        """Generuje opis percepcji czytelnika"""
        if intensity == WeavingIntensity.SUBTLE:
            return f"Podświadome odczucie {random.choice(theme.emotional_associations)} bez wyraźnej identyfikacji źródła"
        elif intensity == WeavingIntensity.MODERATE:
            return f"Niejasne poczucie głębszego znaczenia, intuicyjne wyczucie tematu {theme.name}"
        elif intensity == WeavingIntensity.PROMINENT:
            return f"Świadome rozpoznanie tematu {theme.name}, refleksja nad jego znaczeniem"
        else:
            return f"Pełna konfrontacja z tematem {theme.name}, intensywne przeżycie emocjonalne"

    def _get_recommended_techniques(
        self,
        theme: Theme,
        intensity: WeavingIntensity
    ) -> List[WeavingTechnique]:
        """Zwraca rekomendowane techniki dla tematu"""
        # Techniki bazowe zależne od kategorii tematu
        category_techniques = {
            ThemeCategory.EXISTENTIAL: [WeavingTechnique.SYMBOLISM, WeavingTechnique.METAPHOR, WeavingTechnique.SUBTEXT],
            ThemeCategory.MORAL: [WeavingTechnique.DIALOGUE, WeavingTechnique.CONTRAST, WeavingTechnique.PARALLEL],
            ThemeCategory.PSYCHOLOGICAL: [WeavingTechnique.IMAGERY, WeavingTechnique.SUBTEXT, WeavingTechnique.ATMOSPHERE],
            ThemeCategory.SOCIAL: [WeavingTechnique.DIALOGUE, WeavingTechnique.CONTRAST, WeavingTechnique.MOTIF],
            ThemeCategory.SPIRITUAL: [WeavingTechnique.SYMBOLISM, WeavingTechnique.IMAGERY, WeavingTechnique.ATMOSPHERE],
            ThemeCategory.PHILOSOPHICAL: [WeavingTechnique.DIALOGUE, WeavingTechnique.METAPHOR, WeavingTechnique.SUBTEXT],
            ThemeCategory.EMOTIONAL: [WeavingTechnique.IMAGERY, WeavingTechnique.ATMOSPHERE, WeavingTechnique.DIALOGUE],
            ThemeCategory.UNIVERSAL: [WeavingTechnique.MOTIF, WeavingTechnique.SYMBOLISM, WeavingTechnique.PARALLEL]
        }

        techniques = category_techniques.get(theme.category, list(WeavingTechnique)[:3])

        # Przy subtelnej intensywności preferuj mniej bezpośrednie techniki
        if intensity == WeavingIntensity.SUBTLE:
            subtle_preferred = [WeavingTechnique.SUBTEXT, WeavingTechnique.ATMOSPHERE, WeavingTechnique.SYMBOLISM]
            techniques = [t for t in techniques if t in subtle_preferred] or subtle_preferred[:2]

        return techniques

    async def create_subconscious_layer(
        self,
        project_id: str,
        plan_id: str,
        depth_level: int = 3
    ) -> SubconsciousLayer:
        """
        Tworzy warstwę podświadomą dla narracji.

        Args:
            project_id: ID projektu
            plan_id: ID planu wplatania
            depth_level: Poziom głębokości (1-5)

        Returns:
            SubconsciousLayer z ukrytymi znaczeniami
        """
        plan = self.active_plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan nie znaleziony: {plan_id}")

        # Zbierz wszystkie symbole z tematów
        symbol_network = {}
        for theme in plan.themes:
            for symbol in theme.related_symbols:
                if symbol not in symbol_network:
                    symbol_network[symbol] = []
                symbol_network[symbol].append(theme.name)
                symbol_network[symbol].extend(theme.core_concepts[:2])

        # Ukryte znaczenia
        hidden_meanings = []
        for theme in plan.themes:
            for question in theme.philosophical_questions:
                hidden_meanings.append(f"Podświadome pytanie: {question}")

        # Emocjonalny podprąd
        all_emotions = []
        for theme in plan.themes:
            all_emotions.extend(theme.emotional_associations)
        emotional_undercurrent = f"Dominujące emocje podświadome: {', '.join(set(all_emotions)[:5])}"

        # Wyzwalacze psychologiczne
        psychological_triggers = []
        for theme in plan.themes:
            if theme.category in [ThemeCategory.PSYCHOLOGICAL, ThemeCategory.EMOTIONAL]:
                psychological_triggers.extend(theme.core_concepts[:2])

        # Efekty na podświadomość czytelnika
        reader_effects = [
            "Podświadome poczucie głębi i wielowarstwowości",
            "Intuicyjne wyczucie ukrytych znaczeń",
            "Emocjonalny rezonans bez świadomej analizy",
            "Poczucie uniwersalności opowieści",
            "Podświadoma identyfikacja z archetypami"
        ]

        layer_id = f"layer_{project_id}_{depth_level}"

        layer = SubconsciousLayer(
            layer_id=layer_id,
            depth_level=depth_level,
            hidden_meanings=hidden_meanings[:depth_level * 2],
            symbol_network=symbol_network,
            emotional_undercurrent=emotional_undercurrent,
            psychological_triggers=psychological_triggers[:depth_level],
            reader_subconscious_effects=reader_effects[:depth_level]
        )

        if project_id not in self.subconscious_layers:
            self.subconscious_layers[project_id] = []
        self.subconscious_layers[project_id].append(layer)

        return layer

    async def analyze_theme_presence(
        self,
        plan_id: str,
        chapter_content: str,
        chapter_number: int
    ) -> Dict[str, Any]:
        """
        Analizuje obecność tematów w treści rozdziału.

        Args:
            plan_id: ID planu wplatania
            chapter_content: Treść rozdziału
            chapter_number: Numer rozdziału

        Returns:
            Analiza z oceną i rekomendacjami
        """
        plan = self.active_plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan nie znaleziony: {plan_id}")

        analysis = {
            "chapter": chapter_number,
            "themes_detected": {},
            "expected_vs_actual": {},
            "missing_elements": [],
            "overrepresented_elements": [],
            "recommendations": [],
            "overall_score": 0.0
        }

        content_lower = chapter_content.lower()

        for theme in plan.themes:
            # Szukaj symboli
            symbols_found = [s for s in theme.related_symbols if s.lower() in content_lower]

            # Szukaj konceptów
            concepts_found = [c for c in theme.core_concepts if c.lower() in content_lower]

            # Szukaj emocji
            emotions_found = [e for e in theme.emotional_associations if e.lower() in content_lower]

            total_found = len(symbols_found) + len(concepts_found) + len(emotions_found)

            analysis["themes_detected"][theme.theme_id] = {
                "symbols": symbols_found,
                "concepts": concepts_found,
                "emotions": emotions_found,
                "presence_score": min(1.0, total_found / 5)
            }

            # Porównaj z oczekiwaniami
            expected_occurrences = plan.chapter_distribution.get(chapter_number, [])
            expected_for_theme = [o for o in expected_occurrences if o.theme_id == theme.theme_id]

            if expected_for_theme and total_found == 0:
                analysis["missing_elements"].append(
                    f"Brak elementów tematu '{theme.name}' (oczekiwano {len(expected_for_theme)} wystąpień)"
                )
            elif not expected_for_theme and total_found > 3:
                analysis["overrepresented_elements"].append(
                    f"Nadmierna obecność tematu '{theme.name}' (nieplanowane)"
                )

        # Oblicz ogólny wynik
        detected_scores = [d["presence_score"] for d in analysis["themes_detected"].values()]
        analysis["overall_score"] = sum(detected_scores) / len(detected_scores) if detected_scores else 0.0

        # Generuj rekomendacje
        if analysis["missing_elements"]:
            analysis["recommendations"].append(
                "Rozważ dodanie subtelnych odniesień do brakujących tematów"
            )
        if analysis["overall_score"] < 0.3:
            analysis["recommendations"].append(
                "Rozdział wymaga wzmocnienia obecności tematycznej"
            )
        elif analysis["overall_score"] > 0.8:
            analysis["recommendations"].append(
                "Rozważ subtelniejsze podejście - tematy mogą być zbyt oczywiste"
            )

        return analysis

    def get_available_themes(self) -> List[Dict[str, Any]]:
        """Zwraca listę dostępnych tematów"""
        return [
            {
                "theme_id": theme.theme_id,
                "name": theme.name,
                "category": theme.category.value,
                "description": theme.description,
                "core_concepts": theme.core_concepts,
                "symbols": theme.related_symbols,
                "emotional_associations": theme.emotional_associations
            }
            for theme in self.theme_library.values()
        ]

    def get_themes_by_category(self, category: ThemeCategory) -> List[Theme]:
        """Zwraca tematy z danej kategorii"""
        return [t for t in self.theme_library.values() if t.category == category]

    def get_active_plan(self, plan_id: str) -> Optional[WeavingPlan]:
        """Pobiera aktywny plan"""
        return self.active_plans.get(plan_id)

    def list_active_plans(self) -> List[Dict[str, Any]]:
        """Listuje aktywne plany"""
        return [
            {
                "plan_id": p.plan_id,
                "project_id": p.project_id,
                "primary_theme": p.primary_theme.name,
                "themes_count": len(p.themes),
                "created_at": p.created_at.isoformat()
            }
            for p in self.active_plans.values()
        ]


# Singleton instance
def get_theme_weaving_service() -> SubconsciousThemeWeavingService:
    """Pobiera instancję serwisu Theme Weaving"""
    return SubconsciousThemeWeavingService()


# Export dla API
theme_weaving_service = get_theme_weaving_service()
