"""
Bestseller-level prompts - Prompty klasy światowego bestsellera

These prompts encode best practices from commercially successful fiction
to guide AI generation toward publishable quality.
"""

# ============== OPENING RULES ==============

BESTSELLER_OPENING_RULES = """
ZASADY OTWARC BESTSELLEROWYCH

PIERWSZE ZDANIE = HOOK, ktory:
1. Pokazuje konflikt lub napiecie
2. Stawia pytanie w umysle czytelnika
3. Wprowadza wyjatkowy glos narracji
4. Zawiera konkretny szczegol, nie ogolnik

ZABRONIONE otwarcia:
- Opis pogody ("Byl pochmurny dzien...")
- Ogolne wprowadzenie ("John byl zwyklym czlowiekiem...")
- Informacje biograficzne ("Urodzil sie w...")
- Filozoficzne rozwazania ("Zycie jest...")
- Budzenie sie ze snu
- Opis pokoju/miejsca bez akcji

DOBRE otwarcia:
- Akcja w toku: "Krew na liscie zwiastowala jego smierc."
- Dialog z konfliktem: "Jesli tego nie zrobisz, wszyscy zginiemy."
- Szczegol wyjatkowy: "Tego ranka znalazlem w szafie obca reke."
- Wewnetrzna walka: "Trzeci raz w tym tygodniu musialem zabic."
- In medias res: wrzucenie w srodek akcji

PRZYKLADY Z BESTSELLEROW:
- "Mr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much." (J.K. Rowling)
- "It was a bright cold day in April, and the clocks were striking thirteen." (George Orwell)
- "The man in black fled across the desert, and the gunslinger followed." (Stephen King)
- "Call me Ishmael." (Herman Melville)
"""

# ============== DIALOGUE RULES ==============

BESTSELLER_DIALOGUE_RULES = """
ZASADY DIALOGOW BESTSELLEROWYCH

KAZDA KWESTIA MUSI:
1. Posuwac akcje naprzod
2. Ujawniac charakter postaci
3. Tworzyc lub eskalowac konflikt
4. Brzmiec jak prawdziwa mowa

ZABRONIONE w dialogach:
- Small talk bez celu ("Czesc, jak sie masz?")
- Ekspozycja w dialogu ("Jak wiesz, jestesmy bracmi...")
- Perfekcyjne, ksiazkowe zdania
- Zbyt dlugie monologi bez przerw
- Wszyscy mowia tak samo
- "said bookisms" (wykrzyknał, wyszeptał, zakrzyknął - dla każdej kwestii)

DOBRE praktyki:
- Konflikt w kazdej wymianie
- Podtekst (mowia jedno, mysla drugie)
- Przerwania i nakladanie sie kwestii
- Beat-y akcji miedzy kwestiami
- Unikalny glos kazdej postaci
- Proste "powiedział/powiedziała" lub brak tagu

PRZYKLAD ZLEGO DIALOGU:
— Witaj, Johnie. Jak sie dzisiaj masz?
— Mam sie dobrze, dziekuje. A ty?
— Ja rowniez. Chcialem z toba porozmawiac o czyms waznym.

PRZYKLAD DOBREGO DIALOGU:
— Musimy porozmawiac.
John odwrocil sie gwaltownie, reka powedrowala do kieszeni.
— O czym?
— O tym, co zrobiles. — Sarah przesunela palcem po stole. — Wszyscy wiedza.
— Nie wiem, o czym mowisz.
— Przestan.
"""

# ============== CHARACTER VOICE ==============

BESTSELLER_CHARACTER_VOICE = """
UNIKALNE GLOSY POSTACI

KAZDA POSTAC MUSI MIEC:

1. **Unikalny slownik**
   - Ulubione slowa/wyrazenia
   - Poziom formalnosci
   - Zargon zawodowy/regionalny
   - Przeklenstwa lub ich brak

2. **Wzorce mowy**
   - Dlugosc zdan (krotkie vs rozbudowane)
   - Struktura (pytania retoryczne, wykrzyknienia)
   - Tiki jezykowe (powtarzane frazy)
   - Tempo mowy

3. **Manieryzmy**
   - Powtarzalne gesty podczas mowienia
   - Reakcje fizyczne na emocje
   - Zachowania pod presja
   - Nawyki nerwowe

PRZYKLAD - TRZY ROZNE POSTACIE:

VERGIL (mezny, doswiadczony mag):
- Krotkie, stanowcze zdania
- Militarne metafory
- Unika zbednych slow
- Manieryzm: Zaciska szczeke gdy jest zly
- "Ruszajmy. Nie mamy czasu."

MIRO (mlody, niepewny uczen):
- Dlugie, chaotyczne zdania
- Duzo pytan
- Nieukonkoczone mysli
- Manieryzm: Wachluje rekami gdy nerwowy
- "Ale mistrzu, czy to znaczy, ze... znaczy sie, czy my naprawde...?"

KAEL (cyniczna zlodziejka):
- Sarkazm w kazdym zdaniu
- Przezwiska zamiast imion
- Wulgaryzmy
- Manieryzm: Krzywy usmieszek
- "No jasne, 'wielki mag'. Bo przeciez nigdy cie to nie zawiodlo."
"""

# ============== SCENE STRUCTURE ==============

BESTSELLER_SCENE_STRUCTURE = """
STRUKTURA SCENY BESTSELLEROWEJ

KAZDA SCENA = 5 ELEMENTOW:

1. **GOAL** - Co bohater chce osiagnac?
   Musi byc konkretny, mierzalny
   ZLE: "Chce czuc sie lepiej"
   DOBRZE: "Chce ukrasc klucz z biurka"

2. **CONFLICT** - Przeszkoda lub opor
   Zewnetrzny (osoba, miejsce) + Wewnetrzny (lek, watpliwosc)
   Musi byc NATYCHMIASTOWY, nie hipotetyczny

3. **DISASTER** - Scena konczy sie GORZEJ niz zaczela
   ZLE: Bohater dostaje to czego chcial
   DOBRZE: Bohater dostaje cos GORSZEGO lub traci wiecej niz zyskal
   Wyjątek: sceny odpoczynku (ale rzadkie)

4. **REACTION** - Emocjonalna/fizyczna odpowiedz
   Najpierw FIZYCZNA (oddech, pot, drzenie)
   Potem EMOCJONALNA (mysli, uczucia)
   Potem RACJONALNA (analiza, plan)

5. **DILEMMA** - Nowy wybor (czesto miedzy zlym a gorszym)
   Prowadzi do nowego GOAL kolejnej sceny
   Nie ma idealnego rozwiazania

PRZYKLAD:
GOAL: Vergil chce przekonac Rade Magow do wyslania wojsk
CONFLICT: Rada jest podzielona, Archwizard jest przeciw, Vergil ma zerowy kredyt zaufania
DISASTER: Rada odmawia + Archwizard oskarza Vergila o zdrade
REACTION: Vergil czuje gniew (fizyczne: zacisnięte pięści), ale wie, ze musi dzialac sam
DILEMMA: Czy zaatakowac samotnie (pewna smierc) czy szukac nielegalnych sojusznikow (pewne wygnanie)?
-> Nowy GOAL nastepnej sceny: Vergil musi znalezc Czarnych Lowcow
"""

# ============== PACING RULES ==============

BESTSELLER_PACING = """
TEMPO BESTSELLEROWE

ZASADY TEMPA:

1. **SENTENCE LENGTH = EMOTIONAL INTENSITY**
   - Akcja/Napiecie -> Krotkie zdania (3-10 slow)
   - Opis/Refleksja -> Srednie zdania (10-20 slow)
   - Spokoj/World-building -> Dlugie zdania (20+ slow)

2. **PARAGRAPH LENGTH = TEMPO**
   - Szybka akcja: 1-3 zdania na akapit
   - Normalne tempo: 4-6 zdan
   - Wolne, refleksyjne: 7+ zdan

3. **SCENE LENGTH = IMPORTANCE**
   - Kluczowe sceny (zwroty akcji): 2000-3000 slow
   - Sceny przejsciowe: 1000-1500 slow
   - Krotkie interludia: 500-800 slow

4. **TENSION CURVE**
   Ksiazka = seria fal napiecia:
   - Kazda fala WYZSZA od poprzedniej
   - Po szczytach - krotki odpoczynek (ale nie za dlugi)
   - Kulminacja = najwyzszy szczyt

5. **NO FLATLINE**
   NIGDY 3+ sceny w tym samym poziomie napiecia
   Zawsze: Build -> Release -> Build wyzej

6. **CHAPTER ENDINGS**
   - Kazdy rozdzial konczy sie hookiem
   - Cliffhanger lub pytanie bez odpowiedzi
   - "Page-turner" effect
"""

# ============== CLIMAX RULES ==============

BESTSELLER_CLIMAX_RULES = """
ZASADY KULMINACJI

SCENA KULMINACYJNA MUSI:

1. **PAYOFF wszystkich setup-ow**
   - Bron pokazana w Akcie 1 -> uzyta w Akcie 3
   - Umiejetnosc trenowana -> zadecyduje o wyniku
   - Relacja budowana -> testowana maksymalnie

2. **NAJWIEKSZA STAWKA**
   - Nie moze byc "wieksza" scena pozniej
   - Bohater musi ryzykowac WSZYSTKO
   - Porazka = koniec (smierc, utrata duszy, etc.)

3. **CHARACTER ARC COMPLETION**
   - Bohater uzywa tego, czego sie nauczyl
   - Pokazuje zmiane z poczatku ksiazki
   - "Stary" bohater by przegral, "nowy" wygrywa

4. **EMOTIONAL MAXIMUM**
   - Czytelnik płacze lub wstrzymuje oddech
   - Kazde slowo liczy sie
   - Tempo maksymalne

5. **TWIST jesli gatunek wymaga**
   - Thriller/Mystery: Finalny zwrot
   - Musi byc zaskoczeniem ALE fair
   - Czytelnik mysli "Oczywiscie! Jak moglem nie zauwazyc?"

STRUKTURA KULMINACJI:

1. **Punkt wejscia** (1 akapit)
   Bohater stoi przed ostatecznym wyzwaniem.

2. **Ostatnie wahanie** (2-3 akapity)
   Wewnetrzna walka, wspomnienie drogi, zwatpienie

3. **Decision point** (1 zdanie)
   Decyzja podjeta. Nie ma odwrotu.

4. **Akcja maksymalna** (60% sceny)
   - Krotkie zdania
   - Duzo fizycznosci
   - Chaos, bol, desperacja
   - Wiele FALSE HOPE momentow (prawie wygral -> nope)

5. **Turning point** (1-2 akapity)
   Moment, kiedy uzywa tego, czego sie nauczyl

6. **Resolution** (2-3 akapity)
   Natychmiastowy efekt, fizyczny collapse, cisza po burzy

7. **Emotional landing** (1-2 akapity)
   Krotkie, mocne, uderza w serce
"""

# ============== SENSORY DETAILS ==============

BESTSELLER_SENSORY_RULES = """
DETALE SENSORYCZNE

KAZDA SCENA POTRZEBUJE MINIMUM 3 ZMYSLOW:

1. **WZROK** (nie tylko kolory!)
   - Swiatlo i cien
   - Ruch
   - Tekstury widziane
   - Odleglosc/perspektywa

2. **SLUCH**
   - Dzwieki tla
   - Cisza (opisana aktywnie)
   - Glosy (ton, nie tylko slowa)
   - Rytm/tempo

3. **DOTYK/CZUCIE**
   - Temperatura
   - Tekstura
   - Bol/przyjemnosc
   - Wlasne cialo (napiecie, oddech)

4. **ZAPACH** (najmocniejszy trigger pamieci!)
   - Konkretne zapachy, nie "pachnialo ladnie"
   - Kontrastowe (slodki i gnilny)
   - Powiazane z emocjami

5. **SMAK** (rzadziej, ale mocno)
   - Metaliczny smak strachu
   - Slony smak lez
   - Gorzki smak zdrady

ZASADA: Konkret > Abstrakcja
ZLE: "Pokoj pachniał stara."
DOBRZE: "Zastalay pot mieszal sie z zapachem zbutwiałego drewna i czegos slodkawego - moze zepsutych jablek, moze krwi."
"""

# ============== MASTER SCENE PROMPT ==============

def get_master_scene_prompt(
    scene_number: int,
    total_scenes: int,
    context: str,
    beat_sheet: str,
    characters: str,
    genre: str,
    target_words: int,
    language: str = "polski"
) -> str:
    """
    Generate master prompt for bestseller-quality scene writing.
    """
    if language == "polski":
        return f"""Jestes MISTRZEM NARRACJI piszacym scene klasy swiatowego bestsellera.

{BESTSELLER_OPENING_RULES}

{BESTSELLER_DIALOGUE_RULES}

{BESTSELLER_CHARACTER_VOICE}

{BESTSELLER_SCENE_STRUCTURE}

{BESTSELLER_PACING}

{BESTSELLER_SENSORY_RULES}

---

TWOJE ZADANIE:
Napisz scene {scene_number} z {total_scenes} scen rozdzialu.

GATUNEK: {genre}

KONTEKST:
{context}

BEAT SHEET:
{beat_sheet}

POSTACIE W SCENIE:
{characters}

WYMAGANIA:
1. Otworz scene HOOKIEM (nie pogoda, nie budzenie sie!)
2. Kazdy dialog MUSI posuwac akcje lub ujawniac postac
3. Kazda postac brzmi INACZEJ (unikalny glos)
4. Scena konczy sie GORZEJ niz zaczela (lub z nowym pytaniem)
5. Tempo dopasowane do gatunku i emocji
6. SHOW nie TELL - konkretne obrazy, nie abstrakcje
7. ZERO klisz - oryginalne metafory i porownania
8. Konkretne detale sensoryczne (min. 3 zmysly)
9. Dynamiczna akcja sceniczna miedzy dialogami

Dlugosc: {target_words} slow (+-10%)

PISZ TERAZ - tylko tresc sceny, bez komentarzy:"""

    else:  # English
        return f"""You are a MASTER NARRATOR writing a world-bestseller quality scene.

{BESTSELLER_OPENING_RULES}

{BESTSELLER_DIALOGUE_RULES}

{BESTSELLER_CHARACTER_VOICE}

{BESTSELLER_SCENE_STRUCTURE}

{BESTSELLER_PACING}

{BESTSELLER_SENSORY_RULES}

---

YOUR TASK:
Write scene {scene_number} of {total_scenes} scenes in this chapter.

GENRE: {genre}

CONTEXT:
{context}

BEAT SHEET:
{beat_sheet}

CHARACTERS IN SCENE:
{characters}

REQUIREMENTS:
1. Open with a HOOK (not weather, not waking up!)
2. Every dialogue line MUST advance plot or reveal character
3. Each character sounds DIFFERENT (unique voice)
4. Scene ends WORSE than it began (or with new question)
5. Pacing matched to genre and emotion
6. SHOW don't TELL - concrete images, not abstractions
7. ZERO cliches - original metaphors and comparisons
8. Concrete sensory details (minimum 3 senses)
9. Dynamic scene action between dialogues

Length: {target_words} words (+-10%)

WRITE NOW - scene content only, no commentary:"""


def get_chapter_opening_prompt(
    chapter_number: int,
    total_chapters: int,
    previous_chapter_end: str,
    chapter_goal: str,
    pov_character: str,
    genre: str,
    language: str = "polski"
) -> str:
    """
    Generate prompt for chapter opening that hooks readers.
    """
    if language == "polski":
        return f"""Napisz otwarcie rozdzialu {chapter_number}/{total_chapters}.

POPRZEDNI ROZDZIAL KONCZYL SIE:
{previous_chapter_end}

CEL TEGO ROZDZIALU:
{chapter_goal}

POSTAC POV:
{pov_character}

GATUNEK: {genre}

WYMAGANIA DLA OTWARCIA:
1. HOOK w pierwszym zdaniu - natychmiast wciagnij czytelnika
2. NIE POWTARZAJ informacji z konca poprzedniego rozdzialu
3. Wprowadz napięcie/pytanie od razu
4. Zacznij w AKCJI lub MOMENCIE DECYZJI
5. Ustanow POV od pierwszego zdania

ZABRONIONE:
- Opis pogody jako otwarcie
- Budzenie sie ze snu
- Dlugie opisy miejsca bez akcji
- "Minely trzy dni..."
- Powtarzanie tego co juz wiemy

Napisz pierwsze 2-3 akapity rozdzialu (200-400 slow):"""

    else:
        return f"""Write the opening of chapter {chapter_number}/{total_chapters}.

PREVIOUS CHAPTER ENDED WITH:
{previous_chapter_end}

THIS CHAPTER'S GOAL:
{chapter_goal}

POV CHARACTER:
{pov_character}

GENRE: {genre}

OPENING REQUIREMENTS:
1. HOOK in the first sentence - grab the reader immediately
2. DON'T REPEAT information from the previous chapter ending
3. Introduce tension/question right away
4. Start in ACTION or DECISION MOMENT
5. Establish POV from the first sentence

FORBIDDEN:
- Weather description as opening
- Waking up from sleep
- Long place descriptions without action
- "Three days passed..."
- Repeating what we already know

Write the first 2-3 paragraphs of the chapter (200-400 words):"""


def get_climax_scene_prompt(
    setup_elements: list,
    character_arc: str,
    stakes: str,
    genre: str,
    target_words: int,
    language: str = "polski"
) -> str:
    """
    Generate prompt for climax scene with all payoffs.
    """
    setup_list = "\n".join([f"- {s}" for s in setup_elements])

    if language == "polski":
        return f"""Napisz scene KULMINACYJNA ksiazki.

{BESTSELLER_CLIMAX_RULES}

ELEMENTY DO ROZWIAZANIA (setup -> payoff):
{setup_list}

ARC BOHATERA:
{character_arc}

STAWKA:
{stakes}

GATUNEK: {genre}

Ta scena MUSI:
1. Rozwiazac WSZYSTKIE powyzsze elementy
2. Pokazac kulminacje arc bohatera
3. Byc najbardziej intensywna emocjonalnie w calej ksiazce
4. Nie pozostawiac czytelnika obojetnym

Struktura:
- 10% - Wejscie i ostatnie wahanie
- 60% - Akcja maksymalna z false hope momentami
- 20% - Turning point i rozwiazanie
- 10% - Emotional landing

Dlugosc: {target_words} slow

PISZ KULMINACJE:"""

    else:
        return f"""Write the CLIMAX scene of the book.

{BESTSELLER_CLIMAX_RULES}

ELEMENTS TO RESOLVE (setup -> payoff):
{setup_list}

CHARACTER ARC:
{character_arc}

STAKES:
{stakes}

GENRE: {genre}

This scene MUST:
1. Resolve ALL above elements
2. Show the culmination of the character arc
3. Be the most emotionally intense in the entire book
4. Not leave the reader indifferent

Structure:
- 10% - Entry and final hesitation
- 60% - Maximum action with false hope moments
- 20% - Turning point and resolution
- 10% - Emotional landing

Length: {target_words} words

WRITE THE CLIMAX:"""


# ============== GENRE-SPECIFIC PROMPTS ==============

GENRE_SPECIFIC_RULES = {
    "fantasy": """
ZASADY FANTASY:
- System magii musi miec koszty i ograniczenia
- Worldbuilding przez akcje, nie ekspozycje
- Archetypowe postacie z unikalnymi twistami
- Epicka skala, ale osobiste stawki
- Jezyk: moze byc bardziej poetycki, archaiczny
""",
    "sci-fi": """
ZASADY SCI-FI:
- Technologia ma konsekwencje spoleczne
- Hard science gdzie mozliwe, soft gdzie konieczne
- Pytania filozoficzne przez fabule
- Sense of wonder - pokaż niesamowite
- Jezyk: techniczny ale przystepny
""",
    "thriller": """
ZASADY THRILLERA:
- Napiecie od pierwszej strony
- Ticking clock - czas ucieka
- Kazdy rozdzial konczy sie cliffhangerem
- Plot twists musza byc fair
- Jezyk: szybki, krótkie zdania w akcji
""",
    "horror": """
ZASADY HORRORU:
- Strach budowany powoli, nie jump scares
- To co niewidoczne jest straszniejsze
- Izolacja bohatera
- Koszmar ma logike, ale jej nie znamy
- Jezyk: atmosferyczny, sugestywny
""",
    "romance": """
ZASADY ROMANCE:
- Chemia miedzy postaciami od poczatku
- Przeszkody wewnetrzne > zewnetrzne
- Emocjonalne beat-y sa kluczowe
- HEA/HFN (Happy Ending) wymagany
- Jezyk: emocjonalny, intymny
""",
    "mystery": """
ZASADY MYSTERY:
- Fair play - wszystkie wskazowki dane czytelnikowi
- Red herrings prowadza w slepą uliczkę
- Rozwiazanie zaskakujace ale logiczne
- Detektyw ma unikalną metodę
- Jezyk: obserwacyjny, analityczny
""",
    "drama": """
ZASADY DRAMY:
- Konflikty wewnetrzne > zewnetrzne
- Dylematy moralne bez latwych odpowiedzi
- Transformacja postaci jest historia
- Relacje sa skomplikowane
- Jezyk: literacki, introspektywny
""",
    "comedy": """
ZASADY KOMEDII:
- Timing jest wszystkim
- Postacie lovable losers
- Sytuacje eskalują absurdalnie
- Happy ending (lub bittersweet)
- Jezyk: lekki, z puentami
"""
}


def get_genre_rules(genre: str) -> str:
    """Get genre-specific writing rules."""
    return GENRE_SPECIFIC_RULES.get(genre.lower(), "")
