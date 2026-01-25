"""
Narrative Anti-Patterns Module

Implementacja strategii przeciwdziałania patologiom generatywnym w narracji AI,
bazująca na analizie "Algorytmiczna Architektura Narracji: Kompleksowa Analiza
Patologii Generatywnych oraz Strategie Inżynierii Promptów".

Główne problemy rozwiązywane:
1. Pętla narracyjna ("Wieczne Otwarcie") - model powtarza scenę ucieczki/decyzji
2. Halucynacje postaci (Character Drift) - postacie pojawiają się i znikają
3. Stylistyczna monotonia (Purple Prose) - nadmiar klisz i melodramatycznych metafor
4. Brak progresji fabularnej - sceny nie posuwają akcji naprzód

Rozwiązania:
- Negative Constraints (zakazy frazowe)
- Forbidden Tropes (zakazane tropy)
- Progress Markers (markery postępu)
- Burstiness Controls (kontrola zmienności stylu)
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
import re


@dataclass
class NarrativeAntiPattern:
    """Definicja wzorca anty-narracyjnego do wykrycia i zablokowania"""
    name: str
    description: str
    patterns: List[str]  # Regex patterns do wykrycia
    severity: str  # "critical", "warning", "info"
    fix_suggestion: str


# =============================================================================
# SEKCJA 1: ZAKAZY FRAZOWE (Negative Constraints)
# =============================================================================

FORBIDDEN_OPENING_PHRASES = [
    # Pętla ucieczki - najczęstszy problem
    r"musz[eę] uciekać",
    r"trzeba uciekać",
    r"nie ma czasu",
    r"musi[m]?y się stąd wynosić",
    r"uciekaj(my)?!?",

    # Puste deliberacje
    r"wewnętrzna walka",
    r"ciężar przeznaczenia",
    r"co powinien zrobić",
    r"wahał się",
    r"zastanawiał się",
    r"nie wiedział co myśleć",

    # Nudne otwarcia
    r"^było ciemno",
    r"^słońce wstawało",
    r"^obudził się",
    r"^minęł[ao] kilka dni",
    r"^był[ao]? to",
]

FORBIDDEN_CLICHES = [
    # Fizyczne klisze (z analizy)
    r"serce bił?o jak młot",
    r"serce waliło",
    r"zimny pot",
    r"suche gardło",
    r"nogi się pod ni[mą] ugięły",
    r"krew zastygła w żyłach",
    r"czas stanął w miejscu",
    r"świat się zatrzymał",
    r"mrowie przeszło",
    r"dreszcz przeszedł",

    # Środowiskowe klisze
    r"wilgotna ziemia",
    r"gnijące liście",
    r"gęsta mgła",
    r"ciemny las",
    r"złowieszcza cisza",
    r"ponury mrok",
    r"przenikliwy chłód",
    r"duszna atmosfera",

    # Emocjonalne klisze (Tell, not Show)
    r"czuł?, że",
    r"wiedział?, że musi",
    r"zdał sobie sprawę",
    r"nagle zrozumiał?a?",
    r"ogarnął[ao]? [gj]o",
    r"wypełnił[ao]? [gj]o",
    r"przeszył[ao]? [gj]o",

    # Filter words (do eliminacji w Deep POV)
    r"zobaczył[ao]?,? (że|jak)",
    r"usłyszał[ao]?,? (że|jak)",
    r"poczuł[ao]?,? (że|jak)",
    r"zauważył[ao]?,? (że|jak)",
    r"obserwował[ao]?,? (że|jak)",
]

FORBIDDEN_DIALOGUE_PATTERNS = [
    # Info-dump w dialogu
    r"jak dobrze wiesz",
    r"jak obaj wiemy",
    r"pamiętasz,? gdy",
    r"muszę ci powiedzieć",
    r"posłuchaj mnie uważnie",

    # Melodramatyczne deklaracje
    r"to nasza jedyna szansa",
    r"nie ma innego wyjścia",
    r"los świata zależy",
    r"przeznaczenie nas wzywa",
    r"nadszedł czas",
]


# =============================================================================
# SEKCJA 2: ZAKAZANE TROPY NARRACYJNE (Forbidden Tropes)
# =============================================================================

FORBIDDEN_TROPES = {
    "mysterious_stranger": {
        "name": "Tajemniczy Nieznajomy",
        "description": "Postać pojawia się znikąd, oferuje enigmatyczne ostrzeżenie/pomoc, znika",
        "detection_patterns": [
            r"postać wyłoniła się z cienia",
            r"nieznajom[ya] zbliżył",
            r"tajemniczy głos",
            r"ktoś (go )?obserwował",
        ],
        "alternative": "Wprowadź postać PRZED sceną, daj jej imię i motywację od razu"
    },
    "dream_sequence_revelation": {
        "name": "Objawienie We Śnie",
        "description": "Ważna informacja przekazana przez sen/wizję",
        "detection_patterns": [
            r"śnił mu się",
            r"w? ?wizji zobaczył",
            r"głos w głowie",
            r"wspomnienie zalało",
        ],
        "alternative": "Informacja powinna wynikać z działania bohatera, nie być mu dana"
    },
    "villain_monologue": {
        "name": "Monolog Złoczyńcy",
        "description": "Antagonista wyjaśnia swój plan zamiast działać",
        "detection_patterns": [
            r"pozwól,? że ci wyjaśnię",
            r"chcę,? żebyś (wiedział|zrozumiał)",
            r"zanim (cię )?zabiję",
            r"mój genialny plan",
        ],
        "alternative": "Pokaż plan w akcji, niech bohater sam dedukuje"
    },
    "reset_loop": {
        "name": "Pętla Reset",
        "description": "Scena kończy się w tym samym miejscu gdzie zaczęła",
        "detection_patterns": [
            r"wrócił do punktu wyjścia",
            r"nic się nie zmieniło",
            r"wszystko na nic",
            r"z powrotem w",
        ],
        "alternative": "Scena MUSI kończyć się zmianą: lokalizacji, wiedzy, relacji lub stanu"
    }
}


# =============================================================================
# SEKCJA 3: MARKERY POSTĘPU NARRACYJNEGO
# =============================================================================

@dataclass
class SceneProgressMarker:
    """Marker postępu fabularnego - scena MUSI zawierać minimum jeden"""
    marker_type: str
    description: str
    verification_question: str


REQUIRED_PROGRESS_MARKERS = [
    SceneProgressMarker(
        marker_type="location_change",
        description="Fizyczna zmiana lokalizacji bohatera",
        verification_question="Czy bohater jest w INNYM miejscu niż na początku sceny?"
    ),
    SceneProgressMarker(
        marker_type="knowledge_gain",
        description="Bohater dowiaduje się czegoś nowego i ważnego",
        verification_question="Czy bohater wie teraz coś, czego nie wiedział na początku?"
    ),
    SceneProgressMarker(
        marker_type="relationship_shift",
        description="Zmiana w relacji między postaciami",
        verification_question="Czy relacja między postaciami jest INNA niż na początku?"
    ),
    SceneProgressMarker(
        marker_type="decision_made",
        description="Bohater podejmuje NIEODWRACALNĄ decyzję",
        verification_question="Czy bohater podjął decyzję, której nie może cofnąć?"
    ),
    SceneProgressMarker(
        marker_type="stakes_raised",
        description="Stawka wzrosła - sytuacja się pogorszyła lub polepszyła",
        verification_question="Czy sytuacja jest BARDZIEJ desperacka/obiecująca niż wcześniej?"
    ),
]


# =============================================================================
# SEKCJA 4: KONTROLA STYLU (Burstiness & Perplexity)
# =============================================================================

BURSTINESS_RULES = """
## KONTROLA ZMIENNOŚCI STYLU (BURSTINESS)

Ludzkie pisanie charakteryzuje się ZMIENNOŚCIĄ rytmu i struktury.
AI ma tendencję do monotonnych, równych zdań. Musisz to przełamać.

### ZASADY BURSTINESS:

1. **Zmienność długości zdań**:
   - Przeplataj KRÓTKIE (3-5 słów) z DŁUGIMI (20+ słów)
   - Napięcie = krótkie, urywane zdania: "Cisza. Trzask. Krzyk."
   - Emocja/opis = dłuższe, płynące zdania

2. **Zmienność struktury akapitów**:
   - Niektóre akapity: 1 zdanie (dla efektu)
   - Inne: 5-7 zdań (dla rozwinięcia)
   - NIGDY: wszystkie akapity równej długości

3. **Fragmenty i urwania**:
   - Dozwolone niepełne zdania dla efektu dramatycznego
   - "A potem—" (przerwanie)
   - "Jeśli tylko..." (zawieszenie)

### PRZYKŁAD BURSTINESS:

❌ ZŁE (monotonne):
"Jan szedł przez las. Drzewa stały wokół niego. Słyszał ptaki. Czuł wilgoć. Widział mgłę."

✅ DOBRE (zmienne):
"Las. Ciemny, gęsty, żywy. Jan przedzierał się przez splątane korzenie, które
wyrastały z ziemi jak kostne palce — może martwe, może tylko uśpione. Gdzieś
w górze ptak. Krzyk. Cisza."
"""

PERPLEXITY_RULES = """
## KONTROLA NIEPRZEWIDYWALNOŚCI (PERPLEXITY)

Unikaj OCZYWISTYCH, statystycznie najprawdopodobniejszych fraz.
Model ma tendencję do wybierania "bezpiecznych" opcji. Musisz to przełamać.

### ZASADY PERPLEXITY:

1. **Unikalne metafory**:
   ❌ "serce biło jak młot" (klisze)
   ✅ "serce obijało się o żebra jak uwięziony ptak szukający wyjścia"

2. **Zaskakujące porównania**:
   ❌ "zimny jak lód"
   ✅ "zimny jak wnętrze opuszczonego kościoła w styczniu"

3. **Konkretność zamiast abstrakcji**:
   ❌ "czuł strach" (abstrakcja)
   ✅ "jego palce zdrętwiały, a gardło — gardło było za ciasne na oddech" (konkret)

4. **Sensoryka nieoczekiwana**:
   ❌ "pachniało lasem" (przewidywalne)
   ✅ "powietrze smakowało żywicą i czymś starszym — kurzem stuleci" (zaskakujące)

### TECHNIKA ZASTĄPIENIA KLISZ:

Gdy chcesz użyć kliszy, zatrzymaj się i zadaj pytanie:
"Jak by to opisał KONKRETNIE bohater z JEGO doświadczeniem życiowym?"

Żołnierz nie powie "serce mi wali". Powie "puls jak przed szturmem".
Kucharz nie powie "krew się zlała". Powie "jak czerwone wino na białym obrusie".
"""


# =============================================================================
# SEKCJA 5: WERYFIKACJA SPÓJNOŚCI POSTACI
# =============================================================================

@dataclass
class CharacterConsistencyCheck:
    """Sprawdzenie spójności postaci w scenie"""
    character_name: str
    entered_scene: bool
    exit_explained: bool
    dialogue_count: int
    last_action: str


def generate_character_lock_prompt(active_characters: List[str]) -> str:
    """
    Generuje prompt blokujący wprowadzanie nieautoryzowanych postaci.
    Rozwiązuje problem "karuzeli postaci" opisany w analizie.
    """
    char_list = ", ".join(active_characters)
    return f"""
## 🔒 BLOKADA POSTACI (CHARACTER LOCK)

AUTORYZOWANE POSTACIE W TEJ SCENIE: {char_list}

### ZASADY ABSOLUTNE:
1. TYLKO wymienione postacie mogą mówić lub działać
2. ŻADNYCH "tajemniczych głosów" z nikąd
3. ŻADNYCH "postaci wyłaniających się z cienia"
4. Jeśli potrzebujesz nowej postaci - ZATRZYMAJ SIĘ
5. Każda postać która weszła do sceny MUSI z niej wyjść (lub zostać)

### WERYFIKACJA PO NAPISANIU:
- Czy każda linia dialogu ma przypisaną postać z listy?
- Czy nikt "nowy" się nie pojawił?
- Czy wiemy gdzie jest każda postać na końcu sceny?

NARUSZENIE TEJ ZASADY = BŁĄD KRYTYCZNY
"""


# =============================================================================
# SEKCJA 6: GENERATOR NEGATYWNYCH OGRANICZEŃ
# =============================================================================

def generate_negative_constraints_prompt(
    scene_number: int,
    previous_scene_patterns: Optional[List[str]] = None
) -> str:
    """
    Generuje listę negatywnych ograniczeń dla sceny.
    Dynamicznie dostosowuje zakazy na podstawie poprzednich scen.
    """

    base_constraints = """
## ⛔ NEGATYWNE OGRANICZENIA (FORBIDDEN)

### ZAKAZY BEZWZGLĘDNE - NIGDY NIE UŻYWAJ:

**Frazy otwierające:**
- "Muszę uciekać" / "Musimy uciekać"
- "Nie ma czasu" / "Trzeba działać"
- "Co powinien zrobić?"
- Wewnętrzne wahanie/deliberacja

**Klisze fizyczne:**
- "serce biło jak młot"
- "zimny pot"
- "nogi się ugięły"
- "krew zastygła w żyłach"
- "wilgotna ziemia"
- "gęsta mgła"

**Filter words (DEEP POV - eliminuj!):**
- "zobaczył, że..."
- "usłyszał, że..."
- "poczuł, że..."
- "zdał sobie sprawę..."

**Tropy zakazane:**
- Tajemniczy nieznajomy wyłaniający się z cienia
- Sen/wizja jako źródło informacji
- Monolog wyjaśniający złoczyńcy
"""

    # Dodaj dynamiczne zakazy na podstawie poprzednich scen
    if previous_scene_patterns:
        pattern_constraints = "\n\n**ZAKAZY SPECYFICZNE DLA TEJ SCENY (unikaj powtórzeń z poprzednich):**\n"
        for pattern in previous_scene_patterns[-5:]:  # Last 5 patterns
            pattern_constraints += f"- NIE POWTARZAJ: {pattern}\n"
        base_constraints += pattern_constraints

    return base_constraints


# =============================================================================
# SEKCJA 7: WALIDATOR ANTYPATTERNY
# =============================================================================

class NarrativeAntiPatternValidator:
    """
    Walidator wykrywający anty-wzorce narracyjne w wygenerowanym tekście.
    Używany do post-generacyjnej weryfikacji i QA.
    """

    def __init__(self):
        self.forbidden_patterns = (
            FORBIDDEN_OPENING_PHRASES +
            FORBIDDEN_CLICHES +
            FORBIDDEN_DIALOGUE_PATTERNS
        )
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.forbidden_patterns]

    def validate(self, text: str) -> Dict[str, any]:
        """
        Waliduje tekst pod kątem anty-wzorców.

        Returns:
            Dict z wynikami walidacji:
            - passed: bool
            - issues: List[Dict] z wykrytymi problemami
            - score: float (0-100)
        """
        issues = []

        # Sprawdź zakazane wzorce
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(text)
            if matches:
                issues.append({
                    "type": "forbidden_pattern",
                    "pattern": self.forbidden_patterns[i],
                    "matches": matches[:3],  # Max 3 przykłady
                    "severity": "warning"
                })

        # Sprawdź tropy narracyjne
        for trope_key, trope_data in FORBIDDEN_TROPES.items():
            for pattern in trope_data["detection_patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    issues.append({
                        "type": "forbidden_trope",
                        "trope": trope_data["name"],
                        "description": trope_data["description"],
                        "alternative": trope_data["alternative"],
                        "severity": "critical"
                    })

        # Sprawdź monotonię zdań (Burstiness check)
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if sentence_lengths:
            avg_len = sum(sentence_lengths) / len(sentence_lengths)
            variance = sum((l - avg_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            if variance < 20:  # Niska wariancja = monotonia
                issues.append({
                    "type": "low_burstiness",
                    "description": "Zdania mają zbyt podobną długość - brak zmienności rytmu",
                    "avg_length": avg_len,
                    "variance": variance,
                    "severity": "info"
                })

        # Oblicz score
        critical_count = len([i for i in issues if i["severity"] == "critical"])
        warning_count = len([i for i in issues if i["severity"] == "warning"])
        info_count = len([i for i in issues if i["severity"] == "info"])

        score = 100 - (critical_count * 15) - (warning_count * 5) - (info_count * 1)
        score = max(0, min(100, score))

        return {
            "passed": score >= 70,
            "issues": issues,
            "score": score,
            "critical_count": critical_count,
            "warning_count": warning_count,
            "info_count": info_count
        }

    def get_repair_suggestions(self, issues: List[Dict]) -> List[str]:
        """Generuje sugestie naprawy dla wykrytych problemów"""
        suggestions = []

        for issue in issues:
            if issue["type"] == "forbidden_pattern":
                suggestions.append(f"Zamień klisze '{issue['pattern']}' na unikalne, konkretne opisanie")
            elif issue["type"] == "forbidden_trope":
                suggestions.append(f"Unikaj tropu '{issue['trope']}': {issue['alternative']}")
            elif issue["type"] == "low_burstiness":
                suggestions.append("Zróżnicuj długość zdań - przeplataj krótkie (3-5 słów) z długimi (20+)")

        return suggestions


# =============================================================================
# SEKCJA 8: EKSPORT DLA PROMPTÓW
# =============================================================================

def get_full_anti_pattern_prompt() -> str:
    """
    Zwraca pełny prompt z wszystkimi regułami anty-patternowymi.
    Do włączenia w system prompt dla agenta piszącego.
    """
    return f"""
{generate_negative_constraints_prompt(1)}

{BURSTINESS_RULES}

{PERPLEXITY_RULES}

## WERYFIKACJA POSTĘPU NARRACYJNEGO

Każda scena MUSI zakończyć się przynajmniej JEDNĄ z tych zmian:
1. **Zmiana lokalizacji**: Bohater jest FIZYCZNIE w innym miejscu
2. **Zmiana wiedzy**: Bohater wie coś nowego i ważnego
3. **Zmiana relacji**: Relacja między postaciami się zmieniła
4. **Decyzja**: Bohater podjął nieodwracalną decyzję
5. **Zmiana stawki**: Sytuacja jest bardziej desperacka/obiecująca

SCENA BEZ POSTĘPU = SCENA DO USUNIĘCIA
"""


# Eksport głównych komponentów
__all__ = [
    'FORBIDDEN_OPENING_PHRASES',
    'FORBIDDEN_CLICHES',
    'FORBIDDEN_DIALOGUE_PATTERNS',
    'FORBIDDEN_TROPES',
    'REQUIRED_PROGRESS_MARKERS',
    'BURSTINESS_RULES',
    'PERPLEXITY_RULES',
    'NarrativeAntiPatternValidator',
    'generate_character_lock_prompt',
    'generate_negative_constraints_prompt',
    'get_full_anti_pattern_prompt',
]
