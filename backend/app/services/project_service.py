"""
Project service - core business logic for project management
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import re
from datetime import datetime, timedelta

from app.models.project import Project, ProjectStatus, GenreType
from app.models.world_bible import WorldBible
from app.models.character import Character
from app.models.plot_structure import PlotStructure
from app.models.chapter import Chapter
from app.schemas.project import ProjectCreate, ProjectSimulation
from app.config import settings, genre_config, model_tier_config

logger = logging.getLogger(__name__)


def create_project(db: Session, project_data: ProjectCreate) -> Project:
    """
    Create a new project
    
    User provides ONLY genre.
    AI will decide everything else in the simulation step.
    """
    # Generate default name if not provided
    name = project_data.name or f"{project_data.genre.value.title()} Story - {datetime.now().strftime('%Y%m%d_%H%M')}"
    
    project = Project(
        name=name,
        genre=GenreType(project_data.genre.value),
        status=ProjectStatus.INITIALIZING,
        parameters={},  # Will be filled by AI in simulation
        estimated_cost=0.0,
        actual_cost=0.0,
        current_step=0,
        progress_percentage=0.0,
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)

    logger.info(f"Created project {project.id}: {project.name} ({project.genre})")

    return project


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    """Get list of projects with pagination"""
    return db.query(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()


def count_projects(db: Session) -> int:
    """Count total projects"""
    return db.query(Project).count()


def get_project(db: Session, project_id: int) -> Optional[Project]:
    """Get project by ID"""
    return db.query(Project).filter(Project.id == project_id).first()


async def _semantic_analyze_title_with_ai(title: str, genre: str) -> dict:
    """
    ADVANCED: Use AI to deeply analyze title meaning, metaphors, symbolism

    This provides MUCH richer insights than keyword matching:
    - Semantic meaning and metaphors
    - Emotional core and themes
    - Symbolism and hidden meanings
    - Character archetypes implied
    - World/setting implications
    - Conflict suggestions
    """
    from app.services.ai_service import get_ai_service, ModelTier

    ai_service = get_ai_service()

    prompt = f"""🏆 BESTSELLER-LEVEL TITLE ANALYSIS - Extract EVERYTHING for world-class book creation

═══════════════════════════════════════════════════════════════════════════════
📖 TYTUŁ: "{title}"
🎭 GATUNEK: {genre}
═══════════════════════════════════════════════════════════════════════════════

🇵🇱 WSZYSTKIE odpowiedzi MUSZĄ być PO POLSKU!

Jesteś ekspertem od bestsellerów. Przeanalizuj ten tytuł tak, jakbyś był:
- Redaktorem z Big Five (Penguin, HarperCollins, etc.)
- Scenarzystą Hollywood szukającym adaptacji
- Psychologiem analizującym głębię postaci
- Historykiem szukającym kulturowych odniesień

═══════════════════════════════════════════════════════════════════════════════
🎯 CZĘŚĆ 1: HOOK - CO CHWYTA CZYTELNIKA W PIERWSZEJ SEKUNDZIE?
═══════════════════════════════════════════════════════════════════════════════

Bestsellery mają NATYCHMIASTOWY hook. Znajdź go w tym tytule:

1. **Emocjonalny Hook**: Jaką emocję budzi tytuł? (ciekawość, strach, nadzieję, tęsknotę?)
2. **Obietnica Intrygi**: Co czytelnik MUSI się dowiedzieć?
3. **Napięcie Wbudowane**: Jaki konflikt jest już sugerowany?
4. **Unikalność**: Co wyróżnia ten tytuł spośród tysięcy innych?

═══════════════════════════════════════════════════════════════════════════════
🧠 CZĘŚĆ 2: GŁĘBOKA PSYCHOLOGIA POSTACI (KLUCZOWE DLA BESTSELLERA!)
═══════════════════════════════════════════════════════════════════════════════

Bestsellery mają postacie z GŁĘBIĄ PSYCHOLOGICZNĄ. Wyciągnij z tytułu:

**KLASYFIKACJA RÓL (KRYTYCZNE!):**
- PROTAGONIST (main) = Aktywnie podejmuje decyzje, ma cele, zmienia się
- CATALYST = Wyzwala akcję, ale nie jest aktywnym bohaterem (dzieci 0-6 lat, osoby martwe/w śpiączce)
- DEUTERAGONIST = Drugi najważniejszy bohater, często w konflikcie/sojuszu z protagonistą
- ANTAGONIST = Źródło opozycji (osoba, system, okoliczności, własne demony)

**DLA KAŻDEJ POSTACI WYKRYTEJ W TYTULE określ:**
- WOUND (Rana): Trauma z przeszłości kształtująca zachowanie
- GHOST (Duch): Konkretne wydarzenie, które spowodowało ranę
- LIE (Kłamstwo): Fałszywe przekonanie o sobie/świecie
- WANT (Pragnienie): Świadomy cel zewnętrzny
- NEED (Potrzeba): Nieświadoma potrzeba wewnętrzna (często przeciwna do WANT)
- FEAR (Lęk): Najgłębszy strach napędzający działanie

Przykład dla "Rozalia, 1,5 roczna, długo oczekiwana":
- Hanna (matka): WOUND=lata bezpłodności, GHOST=poronienia?, LIE="nie zasługuję na szczęście",
  WANT=być idealną matką, NEED=zaakceptować niedoskonałość, FEAR=stracić dziecko
- Mateusz (ojciec): WOUND=bezsilność wobec cierpienia żony, GHOST=patrzenie jak żona płacze,
  LIE="muszę być silny", WANT=ochronić rodzinę, NEED=pozwolić sobie na słabość, FEAR=nie wystarczyć

═══════════════════════════════════════════════════════════════════════════════
💔 CZĘŚĆ 3: SYGNAŁY TRAUMY I BACKSTORY (KOPALNIA ZŁOTA!)
═══════════════════════════════════════════════════════════════════════════════

KAŻDE słowo w tytule może kryć CAŁĄ HISTORIĘ. Szukaj:

**Sygnały Płodności/Rodzicielstwa:**
- "długo oczekiwana/y" → IVF, poronienia, lata starań, trauma medyczna
- "upragniona/y" → obsesyjne pragnienie, możliwa depresja
- "jedyna/y" → strata innych dzieci, niemożność posiadania więcej
- "cud" → cudowne uzdrowienie, niespodziewana ciąża, adopcja
- "późna córka/syn" → ciąża po 40-tce, ryzyko, społeczna presja

**Sygnały Straty/Żałoby:**
- "po śmierci" → żałoba, dziedzictwo, nierozwiązane konflikty
- "ostatni/a" → wymieranie, samotność, ciężar odpowiedzialności
- "wdowa/wdowiec" → strata partnera, samotne rodzicielstwo, nowa miłość?
- "sierota" → trauma porzucenia, poszukiwanie tożsamości

**Sygnały Rodzinnych Sekretów:**
- "córka/syn X i Y" → OBOJE rodzice ważni = konflikt między nimi?
- nazwisko w tytule → dziedzictwo, oczekiwania, ciężar tradycji
- "nieślubna/y" → tajemnica, wstyd, poszukiwanie ojca/matki
- "adoptowana/y" → podwójna tożsamość, poszukiwanie korzeni

**Sygnały Wieku/Etapu Życia:**
- wiek dziecka (1,5 roku) → konkretne wyzwania rozwojowe, sen, jedzenie, choroba?
- "nastoletnia" → bunt, tożsamość, pierwszy raz
- "starsza" → przemijanie, mądrość, żal za przeszłością

**Sygnały Miejsca/Czasu:**
- miasto/wieś w tytule → kontrast kultur, ucieczka, powrót do korzeni
- "w czasie wojny" → trauma historyczna, rozłąka, przetrwanie
- "przed świtem/o północy" → tajemnica, transgresja, ukryte życie

═══════════════════════════════════════════════════════════════════════════════
🌍 CZĘŚĆ 4: UNIWERSALNE TEMATY (DNA BESTSELLERÓW!)
═══════════════════════════════════════════════════════════════════════════════

Bestsellery poruszają UNIWERSALNE tematy. Które są w tym tytule?

**Tematy Egzystencjalne:**
- Miłość (romantyczna, rodzinna, przyjacielska, do siebie)
- Śmierć i przemijanie
- Tożsamość (kim jestem? skąd pochodzę?)
- Przynależność (gdzie jest mój dom? moja rodzina?)
- Wolność vs obowiązek
- Sens życia/cierpienia

**Tematy Relacyjne:**
- Rodzic-dziecko (najsilniejsza więź!)
- Partner-partner (miłość, zdrada, wybaczenie)
- Rodzeństwo (rywalizacja, lojalność)
- Przyjaciele (lojalność, zdrada)
- Ja-społeczeństwo (konformizm, bunt)

**Tematy Transformacji:**
- Od słabości do siły
- Od niewiedzy do mądrości
- Od samotności do wspólnoty
- Od nienawiści do miłości
- Od zemsty do przebaczenia

═══════════════════════════════════════════════════════════════════════════════
⚔️ CZĘŚĆ 5: KONFLIKTY WIELOWARSTWOWE (SILNIK FABUŁY!)
═══════════════════════════════════════════════════════════════════════════════

Bestsellery mają MINIMUM 3 warstwy konfliktu działające JEDNOCZEŚNIE:

1. **Zewnętrzny (EXTERNAL)**: Protagonista vs świat/antagonista
   - Fizyczne przeszkody, wrogowie, katastrofy, systemy

2. **Wewnętrzny (INTERNAL)**: Protagonista vs siebie
   - Lęki, wątpliwości, uzależnienia, traumy, kłamstwa o sobie

3. **Interpersonalny (RELATIONAL)**: Protagonista vs bliscy
   - Konflikty z rodziną, przyjaciółmi, partnerem - nawet gdy się kochają!

4. **Filozoficzny (PHILOSOPHICAL)**: Pytanie bez łatwej odpowiedzi
   - Czy cel uświęca środki? Co jest ważniejsze - prawda czy szczęście?

5. **Moralny (MORAL)**: Wybór między dwoma "dobrami" lub dwoma "złami"
   - Kłamać żeby chronić? Zdradzić jednego żeby uratować drugiego?

**Dla gatunku {genre} SZCZEGÓLNIE WAŻNE są:**
- Fantasy/Sci-Fi: zewnętrzny (świat) + wewnętrzny (moc/tożsamość) + filozoficzny
- Drama: wewnętrzny + interpersonalny + moralny
- Thriller: zewnętrzny (zagrożenie) + wewnętrzny (przeszłość) + moralny
- Romans: interpersonalny + wewnętrzny + moralny
- Horror: zewnętrzny (zło) + wewnętrzny (strach) + filozoficzny (natura zła)

═══════════════════════════════════════════════════════════════════════════════
🎭 CZĘŚĆ 6: SPECYFIKA GATUNKOWA - MUST-HAVES!
═══════════════════════════════════════════════════════════════════════════════

**Jeśli gatunek to DRAMA:**
- Emocjonalny rdzeń: Jaka emocja dominuje? (smutek, nadzieja, tęsknota, gniew)
- Katharsis: Jakie oczyszczenie czeka czytelnika?
- Momenty prawdy: Kiedy maska spada i widzimy prawdziwe ja?
- Ciche sceny: Momenty ciszy pełne znaczenia
- Antagonista = często okoliczności, przeszłość, własne demony (NIE osoba!)

**Jeśli gatunek to FANTASY:**
- System magii: Źródło, zasady, koszty, ograniczenia
- Worldbuilding: Co czyni ten świat unikalnym?
- Chosen One?: Czy protagonista jest wyjątkowy? Dlaczego?
- Stawka światowa: Co się stanie jeśli przegra?
- Mentor: Kto go/ją prowadzi?

**Jeśli gatunek to THRILLER:**
- Tykający zegar: Jaki jest deadline?
- Stawka: Kto umrze jeśli zawiedzie?
- Twist: Jaki zwrot akcji jest możliwy?
- Antagonista: Jak inteligentny? Jak bezwzględny?
- Past sin: Jaki grzech z przeszłości wraca?

**Jeśli gatunek to HORROR:**
- Źródło strachu: Zewnętrzne (potwór) czy wewnętrzne (szaleństwo)?
- Atmosfera: Izolacja, klaustrofobia, paranoja?
- Zasady zła: Czy można je pokonać? Jak?
- Ofiara vs Fighter: Kim jest protagonista?
- Cena przetrwania: Co musi poświęcić?

**Jeśli gatunek to ROMANS:**
- Przeszkoda: Co stoi między kochankami?
- Chemistry: Skąd przyciąganie? (przeciwieństwa? podobieństwa?)
- Moment wrażliwości: Kiedy mury padają?
- Grand gesture: Jak udowadnia miłość?
- Happy ending?: Czy razem? Czy osobno ale szczęśliwi?

**Jeśli gatunek to SCI-FI:**
- Technologia: Co definiuje ten świat?
- Pytanie społeczne: Jaką prawdę o nas pokazuje?
- Human element: Co pozostaje ludzkie?
- Dystopia/Utopia?: Który kierunek?
- Koszt postępu: Co straciliśmy?

**Jeśli gatunek to MYSTERY/KRYMINAŁ:**
- Zbrodnia: Co się stało?
- Detektyw: Dlaczego TA osoba musi to rozwiązać?
- Red herrings: Kto może być fałszywym podejrzanym?
- Prawdziwy motyw: Dlaczego morderca to zrobił?
- Koszt prawdy: Co zmienia się gdy prawda wyjdzie?

═══════════════════════════════════════════════════════════════════════════════
📊 CZĘŚĆ 7: STRUKTURA I PACING
═══════════════════════════════════════════════════════════════════════════════

**Sugerowana struktura na podstawie gatunku i tytułu:**
- 3-aktowa klasyczna
- Hero's Journey (12 kroków)
- Save the Cat (15 beats)
- 7-punktowa
- Kishotenketsu (4-aktowa japońska)

**Pacing:**
- Tempo ogólne: szybkie / średnie / wolne
- Gdzie przyspieszyć: akcja, odkrycia, konfrontacje
- Gdzie zwolnić: emocje, relacje, refleksja
- Najciemniejszy moment: który akt?
- Fałszywe zwycięstwo: gdzie?
- Prawdziwy klimaks: co jest ostatecznym testem?

═══════════════════════════════════════════════════════════════════════════════
🎬 CZĘŚĆ 8: SCENY MUST-HAVE (CZYTELNICY OCZEKUJĄ!)
═══════════════════════════════════════════════════════════════════════════════

Każdy gatunek ma OBOWIĄZKOWE sceny. Jakie dla tego tytułu?

Przykłady:
- Drama rodzinna: "scena przy stole" gdzie wybucha kłótnia
- Thriller: "tykający zegar" gdzie czas ucieka
- Romans: "pierwszy pocałunek" i "rozstanie przed finałem"
- Fantasy: "otrzymanie mocy" i "wszystko stracone"
- Horror: "pierwsze spotkanie ze złem" i "zostałem sam"

═══════════════════════════════════════════════════════════════════════════════
✨ CZĘŚĆ 9: CO SPRAWI ŻE TO BĘDZIE BESTSELLER?
═══════════════════════════════════════════════════════════════════════════════

**Unique Selling Point**: Co wyróżnia TĘ historię?
**Zeitgeist**: Dlaczego teraz? Co rezonuje z czasami?
**Uniwersalność**: Kto się z tym utożsami?
**Quotable moments**: Jakie zdania mogą stać się viralowe?
**Adaptation potential**: Czy to się nada na film/serial?

═══════════════════════════════════════════════════════════════════════════════
📋 ZWRÓĆ TEN JSON (WSZYSTKO PO POLSKU!):
═══════════════════════════════════════════════════════════════════════════════

{{
  "bestseller_hook": {{
    "emotional_hook": "Jaka emocja chwyta natychmiast",
    "intrigue_promise": "Co czytelnik MUSI się dowiedzieć",
    "built_in_tension": "Jaki konflikt jest już w tytule",
    "uniqueness": "Co wyróżnia tę historię"
  }},

  "detected_characters": [
    {{
      "name": "Imię",
      "role": "protagonist/catalyst/deuteragonist/antagonist",
      "gender": "female/male/neutral",
      "age_hint": "konkretny wiek lub przedział",
      "role_explanation": "dlaczego ta rola",
      "psychology": {{
        "wound": "Trauma z przeszłości",
        "ghost": "Konkretne wydarzenie które ją spowodowało",
        "lie": "Fałszywe przekonanie o sobie/świecie",
        "want": "Świadomy cel zewnętrzny",
        "need": "Nieświadoma potrzeba wewnętrzna",
        "fear": "Najgłębszy lęk"
      }}
    }}
  ],

  "backstory_signals": {{
    "detected_hints": ["sygnał 1 = interpretacja", "sygnał 2 = interpretacja"],
    "implied_trauma": "Szczegółowy opis domniemanej traumy",
    "emotional_weight": "Emocjonalny ciężar historii",
    "hidden_conflicts": ["ukryty konflikt 1", "ukryty konflikt 2"],
    "secrets_implied": ["możliwa tajemnica 1", "możliwa tajemnica 2"]
  }},

  "universal_themes": {{
    "primary_theme": "Główny temat uniwersalny",
    "secondary_themes": ["temat 2", "temat 3"],
    "existential_question": "Jakie pytanie egzystencjalne stawia ta historia?",
    "emotional_truth": "Jaka prawda emocjonalna jest w sercu?"
  }},

  "conflicts": {{
    "external": {{
      "description": "Protagonista vs co?",
      "stakes": "Co straci jeśli przegra?"
    }},
    "internal": {{
      "description": "Protagonista vs jakie demony?",
      "false_belief": "Jakie kłamstwo musi przezwyciężyć?"
    }},
    "relational": {{
      "description": "Z kim jest w konflikcie mimo miłości?",
      "source": "Skąd ten konflikt?"
    }},
    "philosophical": {{
      "question": "Jakie pytanie bez łatwej odpowiedzi?",
      "both_sides": "Argumenty obu stron"
    }},
    "moral": {{
      "dilemma": "Jaki niemożliwy wybór?",
      "cost": "Co musi poświęcić?"
    }}
  }},

  "genre_specific": {{
    "genre": "{genre}",
    "must_have_elements": ["element 1", "element 2", "element 3"],
    "must_have_scenes": ["scena 1", "scena 2", "scena 3"],
    "tropes_to_use": ["trop który działa", "trop który działa"],
    "tropes_to_subvert": ["trop do odwrócenia"],
    "tone": "ciemny/jasny/mieszany",
    "pacing": "szybkie/średnie/wolne"
  }},

  "antagonist_analysis": {{
    "type": "osoba/system/okoliczności/własne demony/choroba/przeszłość",
    "motivation": "Dlaczego się sprzeciwia?",
    "methods": "Jak działa?",
    "threat_level": "Jak niebezpieczny?",
    "mirror_to_protagonist": "Jak odzwierciedla protagonistę?"
  }},

  "structure_recommendation": {{
    "type": "3-akt/Hero's Journey/Save the Cat/inna",
    "darkest_moment": "Kiedy wszystko stracone?",
    "false_victory": "Gdzie fałszywe zwycięstwo?",
    "climax_type": "Jaki rodzaj kulminacji?",
    "resolution": "Jak się kończy?"
  }},

  "cultural_depth": {{
    "mythological_references": ["odniesienie 1", "odniesienie 2"],
    "literary_allusions": ["aluzja literacka 1"],
    "name_meanings": {{"imię": "znaczenie i konotacje"}},
    "archetypal_patterns": ["archetyp 1", "archetyp 2"]
  }},

  "cultural_analysis": {{
    "cultural_context": "Kontekst kulturowy tytułu",
    "mythological_references": ["mit 1", "mit 2"],
    "archetypal_patterns": ["archetyp 1", "archetyp 2"],
    "symbolic_depth": "Głębokość symboliczna"
  }},

  "magic_system": {{
    "magic_type": "typ magii wynikający z tytułu (lub 'brak' jeśli nie ma magii)",
    "power_source": "źródło mocy",
    "limitations": "ograniczenia systemu magii",
    "scope": "zasięg magii"
  }},

  "tone_and_maturity": {{
    "maturity_level": "Poziom dojrzałości treści (młodzieżowy/dorosły/mature)",
    "violence_level": "Poziom przemocy (niski/średni/wysoki)",
    "moral_complexity": "Złożoność moralna (prosta/średnia/złożona)",
    "emotional_intensity": "Intensywność emocjonalna (niska/średnia/wysoka)"
  }},

  "subgenre": {{
    "primary": "Główny podgatunek",
    "secondary": ["podgatunek 2", "podgatunek 3"],
    "magic_level": "niski/średni/wysoki (lub 'brak')",
    "focus": "character-driven/plot-driven/world-driven"
  }},

  "pacing_suggestions": {{
    "overall_pace": "szybkie/średnie/wolne",
    "structure_type": "3-akt/Hero's Journey/Save the Cat/inna",
    "darkest_act": "Który akt najciemniejszy?",
    "tension_curve": "Jak narasta napięcie?"
  }},

  "antagonist_predictions": [
    {{
      "type": "osoba/siła/idea/wewnętrzny/okoliczności",
      "motivation": "Co nim kieruje?",
      "opposition_nature": "Jak się sprzeciwia?"
    }}
  ],

  "character_arc": {{
    "starting_point": "Kim protagonista jest na początku?",
    "midpoint_shift": "Jaka zmiana w połowie?",
    "climax_challenge": "Najciemniejsza noc duszy",
    "transformation": "Kim się staje?",
    "arc_type": "pozytywny/negatywny/płaski"
  }},

  "setting_analysis": {{
    "environment": "Gdzie się dzieje?",
    "time_period": "Kiedy?",
    "atmosphere": "Jaka atmosfera?",
    "setting_as_character": "Jak miejsce wpływa na fabułę?",
    "contrast_potential": "Jaki kontrast można wykorzystać?"
  }},

  "emotional_journey": {{
    "reader_starts_feeling": "Co czuje czytelnik na początku?",
    "reader_ends_feeling": "Co czuje na końcu?",
    "catharsis_type": "Jakiego oczyszczenia doświadcza?",
    "memorable_emotions": ["emocja 1", "emocja 2"]
  }},

  "bestseller_potential": {{
    "unique_selling_point": "Co wyróżnia tę historię?",
    "zeitgeist_connection": "Dlaczego rezonuje z czasami?",
    "universal_appeal": "Kto się utożsami?",
    "quotable_potential": "Przykład zdania które może być viralne",
    "adaptation_potential": "Film/serial/inne"
  }},

  "character_arcs": {{
    "protagonist_arc": {{
      "starting_state": "Kim jest na początku?",
      "catalyst": "Co go zmusza do zmiany?",
      "struggle": "Z czym walczy przez całą historię?",
      "low_point": "Najgorszy moment",
      "transformation": "Kim się staje?",
      "arc_type": "pozytywny/negatywny/płaski"
    }},
    "supporting_arcs": [
      {{"character": "imię", "arc": "krótki opis łuku"}}
    ]
  }},

  "secondary_plots": [
    {{
      "type": "romans/mentorstwo/tajemnica/rywalizacja/redemption",
      "description": "Krótki opis",
      "connection_to_main": "Jak wspiera główną fabułę?",
      "key_characters": ["kto jest zaangażowany"]
    }}
  ],

  "core_meaning": "Jednozdaniowe podsumowanie głębokiego znaczenia tytułu",
  "reader_promise": "Co obiecujesz czytelnikowi który wybierze tę książkę?"
}}

⚠️ KRYTYCZNE WYMAGANIA:
1. WSZYSTKIE pola JSON MUSZĄ być wypełnione - nie pomijaj żadnego!
2. Jeśli jakiś element nie pasuje do tytułu (np. magic_system dla dramatu rodzinnego),
   NADAL wypełnij pole ale zaznacz "brak" lub "nie dotyczy"
3. "cultural_analysis" i "cultural_depth" to DWA RÓŻNE pola - wypełnij OBA!
4. "antagonist_predictions" (lista) i "antagonist_analysis" (obiekt) - wypełnij OBA!
5. "character_arc" (obiekt) i "character_arcs" (obiekt z protagonist_arc) - wypełnij OBA!

BĄDŹ MAKSYMALNIE SZCZEGÓŁOWY. Każde pole wypełnij KONKRETNĄ, BOGATĄ treścią.
To musi być analiza na poziomie profesjonalnego redaktora z wydawnictwa Big Five!
System oczekuje 13 WYMIARÓW ANALIZY - dostarcz je wszystkie!"""

    try:
        response = await ai_service.generate(
            prompt=prompt,
            tier=ModelTier.TIER_2,  # Use good model for deep analysis
            temperature=0.7,
            max_tokens=12000,  # Large response for bestseller-level comprehensive analysis
            json_mode=True,
            prefer_anthropic=True,  # Claude excellent at deep analysis
            metadata={"task": "bestseller_title_analysis"}
        )

        import json
        semantic_analysis = json.loads(response.content)
        logger.info(f"🎯 SEMANTIC TITLE ANALYSIS: {semantic_analysis}")
        return semantic_analysis

    except Exception as e:
        logger.error(f"❌ Semantic title analysis failed: {e}")
        # Intelligent fallback - try to extract at least basic info
        words = title.split()
        first_capitalized = next((w.strip('.,;:!?') for w in words if w and w[0].isupper()), "Bohater")

        # Polish genre names
        genre_pl = {
            "fantasy": "fantasy",
            "sci-fi": "science fiction",
            "thriller": "thriller",
            "horror": "horror",
            "romance": "romans",
            "drama": "dramat",
            "comedy": "komedia",
            "mystery": "kryminał"
        }.get(genre, genre)

        return {
            "core_meaning": f"Historia {genre_pl} o {first_capitalized}",
            "cultural_analysis": {
                "mythological_references": [],
                "cultural_context": f"Typowa narracja {genre_pl}",
                "symbolic_elements": ["Podróż", "Transformacja"],
                "archetypal_patterns": ["Bohater" if genre == "fantasy" else "Protagonista"]
            },
            "metaphors": ["Podróż", "Transformacja"],
            "emotional_core": "przygoda" if genre == "fantasy" else "napięcie",
            "magic_system": {
                "magic_type": "Nieznany system magii" if genre in ["fantasy", "sci-fi"] else "Brak magii",
                "power_source": "Nieznane" if genre in ["fantasy", "sci-fi"] else "Nie dotyczy",
                "limitations": "Nieznane" if genre in ["fantasy", "sci-fi"] else "Nie dotyczy",
                "cost": "Nieznane" if genre in ["fantasy", "sci-fi"] else "Nie dotyczy",
                "scope": "Nieznany" if genre in ["fantasy", "sci-fi"] else "Nie dotyczy"
            },
            "setting_analysis": {
                "environment": "Nieznane miejsce akcji",
                "time_period": "Nieokreślony",
                "emotional_landscape": "Neutralny",
                "setting_role": "Tło dla akcji",
                "protagonist_relationship": "Protagonista odkrywa świat"
            },
            "tone_and_maturity": {
                "tone": "neutralny",
                "maturity_level": "Adult",
                "violence_level": "średnia",
                "moral_complexity": "zrównoważone",
                "emotional_intensity": "średnia"
            },
            "antagonist_predictions": [
                {
                    "type": "Niezidentyfikowany antagonista",
                    "motivation": "Nieznana",
                    "opposition_nature": "fizyczna"
                }
            ],
            "conflicts": {
                "external": "Protagonista vs nieznane zagrożenie",
                "internal": "Walka z wątpliwościami",
                "philosophical": "Dobro vs zło",
                "moral": "Wybór między pragnieniem a obowiązkiem"
            },
            "subgenre": {
                "primary": genre_pl,
                "secondary": [],
                "magic_level": "medium magic" if genre == "fantasy" else "no magic",
                "focus": "zrównoważony"
            },
            "reader_expectations": {
                "expected_scenes": ["akcja", "rozwój postaci", "konflikt"],
                "emotional_journey": "Od wyzwania do triumfu",
                "tropes": ["podróż bohatera"]
            },
            "pacing_suggestions": {
                "overall_pace": "średnie",
                "structure_type": "3-aktowa",
                "darkest_act": "akt 2",
                "tension_curve": "stopniowy wzrost"
            },
            "secondary_plots": [
                {"type": "rozwój postaci", "description": "Wewnętrzna transformacja", "key_characters": [first_capitalized]}
            ],
            "character_arc": {
                "starting_point": "Protagonista na początku podróży",
                "midpoint_shift": "Odkrycie prawdy",
                "climax_challenge": "Ostateczna konfrontacja",
                "transformation": "Rozwój i dojrzałość",
                "arc_type": "pozytywny"
            },
            "character_implications": {
                "protagonist_archetype": "Bohater" if genre == "fantasy" else "Protagonista",
                "protagonist_journey": f"Poszukiwanie prawdy przez {first_capitalized}",
                "suggested_names": [first_capitalized] if first_capitalized != "Bohater" else ["Aleksander", "Mateusz", "Kacper"]
            },
            "themes": ["tożsamość", "odwaga", "przeznaczenie"],
            "reader_promise": f"Wciągająca przygoda {genre_pl}"
        }


async def suggest_improved_titles(title: str, genre: str) -> dict:
    """
    AI-POWERED: Suggest improved/alternative titles that will work better with AI generation

    Takes user's original title and suggests:
    1. Improved version (cleaner, more impactful)
    2. Alternative variations (different angles)
    3. Why each suggestion is better for AI analysis

    This helps users whose titles might be:
    - Too complex/confusing for analysis
    - Lacking clear hooks for world/character/plot
    - Grammatically ambiguous
    """
    from app.services.ai_service import get_ai_service, ModelTier

    ai_service = get_ai_service()

    prompt = f"""Użytkownik podał tytuł książki: "{title}"
Gatunek: {genre}

Ten tytuł może być trudny do automatycznej analizy przez AI. Zasugeruj LEPSZE TYTUŁY.

Dla każdego sugerowanego tytułu wyjaśnij:
1. Dlaczego jest lepszy od oryginału
2. Jakie elementy są bardziej "AI-readable" (jasne imiona, jasna tematyka, jasny konflikt)
3. Jak pomoże to w generowaniu lepszej historii

Zwróć JSON:
{{
  "original_title": "{title}",
  "original_issues": ["Problem 1 z oryginalnym tytułem...", "Problem 2..."],
  "suggestions": [
    {{
      "title": "Lepszy Tytuł 1",
      "why_better": "Wyjaśnienie dlaczego lepszy...",
      "ai_improvements": ["Jasne imię protagonisty", "Wyraźny konflikt", "..."],
      "example_story_hook": "Krótki opis historii którą ten tytuł sugeruje..."
    }},
    {{
      "title": "Lepszy Tytuł 2",
      "why_better": "...",
      "ai_improvements": ["..."],
      "example_story_hook": "..."
    }},
    {{
      "title": "Lepszy Tytuł 3",
      "why_better": "...",
      "ai_improvements": ["..."],
      "example_story_hook": "..."
    }}
  ],
  "recommendation": "Który tytuł najbardziej polecasz i dlaczego"
}}

Bądź KREATYWNY ale ZACHOWAJ esencję oryginalnego tytułu.
Jeśli oryginalny tytuł jest już dobry, zaproponuj subtelne ulepszenia."""

    try:
        response = await ai_service.generate(
            prompt=prompt,
            tier=ModelTier.TIER_2,  # Use good model for creative suggestions
            temperature=0.8,  # Higher creativity
            max_tokens=2000,
            json_mode=True,
            metadata={"task": "title_suggestions"}
        )

        import json
        suggestions = json.loads(response.content)
        logger.info(f"💡 TITLE SUGGESTIONS for '{title}': {len(suggestions.get('suggestions', []))} alternatives")
        return suggestions

    except Exception as e:
        logger.error(f"❌ Title suggestions failed: {e}")
        return {
            "original_title": title,
            "original_issues": ["Could not analyze"],
            "suggestions": [],
            "recommendation": "Use original title"
        }


def _analyze_title(title: str, genre: str) -> dict:
    """
    Analyze book title to extract intelligent insights for AI decisions

    NOTE: This is the BASIC keyword-based analysis.
    For SEMANTIC analysis, use _semantic_analyze_title_with_ai() instead.

    Extracts:
    - Character names and roles
    - Themes and relationships
    - Setting hints (cultural, geographic, temporal)
    - Emotional tone
    - Story focus

    Examples:
    - "Córka Rozalia" -> Main character: Rozalia, Theme: family, Setting: Polish
    - "The Last Starship" -> Setting: space, Theme: survival, Tone: epic
    - "Murder in Manhattan" -> Setting: NYC, Theme: crime, Main plot: investigation
    """
    insights = {
        "character_names": [],
        "themes": [],
        "setting_hints": [],
        "tone": "neutralny",
        "focus": "zrównoważony",  # oparty na postaciach, oparty na fabule, zrównoważony
        "title_suggestions": {}
    }

    title_lower = title.lower()
    words = title.split()

    # Detect character-focused titles (names, relationships)
    # COMPREHENSIVE Polish + English family relationship dictionary
    # Includes both formal and informal terms to work perfectly with ANY title
    relationship_keywords = {
        # POLISH - Parents (formal + informal)
        "córka": {"role": "córka", "gender": "female", "theme": "rodzina"},
        "syn": {"role": "syn", "gender": "male", "theme": "rodzina"},
        "matka": {"role": "matka", "gender": "female", "theme": "rodzina"},
        "ojciec": {"role": "ojciec", "gender": "male", "theme": "rodzina"},
        "tata": {"role": "ojciec", "gender": "male", "theme": "rodzina"},  # FIX: Added informal "dad"
        "tatuś": {"role": "ojciec", "gender": "male", "theme": "rodzina"},  # daddy
        "tatko": {"role": "ojciec", "gender": "male", "theme": "rodzina"},  # daddy
        "tato": {"role": "ojciec", "gender": "male", "theme": "rodzina"},  # dad (vocative)
        "mama": {"role": "matka", "gender": "female", "theme": "rodzina"},  # FIX: Added informal "mom"
        "mamusia": {"role": "matka", "gender": "female", "theme": "rodzina"},  # mommy
        "mamcia": {"role": "matka", "gender": "female", "theme": "rodzina"},  # mommy
        "mamo": {"role": "matka", "gender": "female", "theme": "rodzina"},  # mom (vocative)
        "rodzic": {"role": "rodzic", "gender": "neutral", "theme": "rodzina"},  # parent
        "rodzice": {"role": "rodzice", "gender": "neutral", "theme": "rodzina"},  # parents

        # POLISH - Grandparents
        "dziadek": {"role": "dziadek", "gender": "male", "theme": "rodzina"},
        "babcia": {"role": "babcia", "gender": "female", "theme": "rodzina"},
        "dziadzia": {"role": "dziadek", "gender": "male", "theme": "rodzina"},  # informal grandpa
        "babunia": {"role": "babcia", "gender": "female", "theme": "rodzina"},  # informal grandma
        "dziadkowie": {"role": "dziadkowie", "gender": "neutral", "theme": "rodzina"},  # grandparents

        # POLISH - Grandchildren
        "wnuk": {"role": "wnuk", "gender": "male", "theme": "rodzina"},
        "wnuczka": {"role": "wnuczka", "gender": "female", "theme": "rodzina"},

        # POLISH - Siblings
        "siostra": {"role": "siostra", "gender": "female", "theme": "rodzina"},
        "brat": {"role": "brat", "gender": "male", "theme": "rodzina"},
        "siostrzyczka": {"role": "siostra", "gender": "female", "theme": "rodzina"},  # little sister
        "braciszek": {"role": "brat", "gender": "male", "theme": "rodzina"},  # little brother
        "rodzeństwo": {"role": "rodzeństwo", "gender": "neutral", "theme": "rodzina"},  # siblings

        # POLISH - Extended family
        "wujek": {"role": "wujek", "gender": "male", "theme": "rodzina"},  # uncle (mother's brother)
        "wuj": {"role": "wujek", "gender": "male", "theme": "rodzina"},  # uncle (informal)
        "ciocia": {"role": "ciocia", "gender": "female", "theme": "rodzina"},  # aunt
        "ciotka": {"role": "ciocia", "gender": "female", "theme": "rodzina"},  # aunt (formal)
        "stryj": {"role": "stryj", "gender": "male", "theme": "rodzina"},  # uncle (father's brother)
        "stryjek": {"role": "stryj", "gender": "male", "theme": "rodzina"},  # uncle (father's brother)
        "kuzyn": {"role": "kuzyn", "gender": "male", "theme": "rodzina"},  # cousin (male)
        "kuzynka": {"role": "kuzynka", "gender": "female", "theme": "rodzina"},  # cousin (female)
        "bratanek": {"role": "bratanek", "gender": "male", "theme": "rodzina"},  # nephew (brother's son)
        "bratanica": {"role": "bratanica", "gender": "female", "theme": "rodzina"},  # niece (brother's daughter)
        "siostrzeniec": {"role": "siostrzeniec", "gender": "male", "theme": "rodzina"},  # nephew (sister's son)
        "siostrzenica": {"role": "siostrzenica", "gender": "female", "theme": "rodzina"},  # niece (sister's daughter)

        # POLISH - Marriage & Partnership
        "żona": {"role": "żona", "gender": "female", "theme": "małżeństwo"},
        "mąż": {"role": "mąż", "gender": "male", "theme": "małżeństwo"},
        "małżonek": {"role": "mąż", "gender": "male", "theme": "małżeństwo"},  # spouse (male)
        "małżonka": {"role": "żona", "gender": "female", "theme": "małżeństwo"},  # spouse (female)
        "mąż": {"role": "mąż", "gender": "male", "theme": "małżeństwo"},
        "narzeczony": {"role": "narzeczony", "gender": "male", "theme": "małżeństwo"},  # fiancé
        "narzeczona": {"role": "narzeczona", "gender": "female", "theme": "małżeństwo"},  # fiancée
        "żonka": {"role": "żona", "gender": "female", "theme": "małżeństwo"},  # wife (informal)

        # POLISH - Loss & Tragedy
        "wdowa": {"role": "wdowa", "gender": "female", "theme": "strata"},
        "wdowiec": {"role": "wdowiec", "gender": "male", "theme": "strata"},  # widower
        "sierota": {"role": "sierota", "gender": "neutral", "theme": "strata"},

        # POLISH - In-laws
        "teść": {"role": "teść", "gender": "male", "theme": "rodzina"},  # father-in-law
        "teściowa": {"role": "teściowa", "gender": "female", "theme": "rodzina"},  # mother-in-law
        "zięć": {"role": "zięć", "gender": "male", "theme": "rodzina"},  # son-in-law
        "synowa": {"role": "synowa", "gender": "female", "theme": "rodzina"},  # daughter-in-law

        # ENGLISH - Core family
        "daughter": {"role": "córka", "gender": "female", "theme": "rodzina"},
        "son": {"role": "syn", "gender": "male", "theme": "rodzina"},
        "mother": {"role": "matka", "gender": "female", "theme": "rodzina"},
        "father": {"role": "ojciec", "gender": "male", "theme": "rodzina"},
        "dad": {"role": "ojciec", "gender": "male", "theme": "rodzina"},
        "daddy": {"role": "ojciec", "gender": "male", "theme": "rodzina"},
        "mom": {"role": "matka", "gender": "female", "theme": "rodzina"},
        "mommy": {"role": "matka", "gender": "female", "theme": "rodzina"},
        "mum": {"role": "matka", "gender": "female", "theme": "rodzina"},
        "mummy": {"role": "matka", "gender": "female", "theme": "rodzina"},
        "parent": {"role": "rodzic", "gender": "neutral", "theme": "rodzina"},
        "parents": {"role": "rodzice", "gender": "neutral", "theme": "rodzina"},

        # ENGLISH - Grandparents
        "grandfather": {"role": "dziadek", "gender": "male", "theme": "rodzina"},
        "grandmother": {"role": "babcia", "gender": "female", "theme": "rodzina"},
        "grandpa": {"role": "dziadek", "gender": "male", "theme": "rodzina"},
        "grandma": {"role": "babcia", "gender": "female", "theme": "rodzina"},
        "gramps": {"role": "dziadek", "gender": "male", "theme": "rodzina"},
        "granny": {"role": "babcia", "gender": "female", "theme": "rodzina"},
        "grandparents": {"role": "dziadkowie", "gender": "neutral", "theme": "rodzina"},

        # ENGLISH - Grandchildren
        "grandson": {"role": "wnuk", "gender": "male", "theme": "rodzina"},
        "granddaughter": {"role": "wnuczka", "gender": "female", "theme": "rodzina"},

        # ENGLISH - Siblings
        "sister": {"role": "siostra", "gender": "female", "theme": "rodzina"},
        "brother": {"role": "brat", "gender": "male", "theme": "rodzina"},
        "siblings": {"role": "rodzeństwo", "gender": "neutral", "theme": "rodzina"},

        # ENGLISH - Extended family
        "uncle": {"role": "wujek", "gender": "male", "theme": "rodzina"},
        "aunt": {"role": "ciocia", "gender": "female", "theme": "rodzina"},
        "cousin": {"role": "kuzyn", "gender": "neutral", "theme": "rodzina"},
        "nephew": {"role": "bratanek", "gender": "male", "theme": "rodzina"},
        "niece": {"role": "bratanica", "gender": "female", "theme": "rodzina"},

        # ENGLISH - Marriage
        "wife": {"role": "żona", "gender": "female", "theme": "małżeństwo"},
        "husband": {"role": "mąż", "gender": "male", "theme": "małżeństwo"},
        "spouse": {"role": "małżonek", "gender": "neutral", "theme": "małżeństwo"},
        "fiancé": {"role": "narzeczony", "gender": "male", "theme": "małżeństwo"},
        "fiancée": {"role": "narzeczona", "gender": "female", "theme": "małżeństwo"},

        # ENGLISH - Loss
        "widow": {"role": "wdowa", "gender": "female", "theme": "strata"},
        "widower": {"role": "wdowiec", "gender": "male", "theme": "strata"},
        "orphan": {"role": "sierota", "gender": "neutral", "theme": "strata"},

        # ENGLISH - In-laws
        "father-in-law": {"role": "teść", "gender": "male", "theme": "rodzina"},
        "mother-in-law": {"role": "teściowa", "gender": "female", "theme": "rodzina"},
        "son-in-law": {"role": "zięć", "gender": "male", "theme": "rodzina"},
        "daughter-in-law": {"role": "synowa", "gender": "female", "theme": "rodzina"},
    }

    # Detect setting keywords (English + Polish)
    setting_keywords = {
        "manhattan": "NYC, współczesny",
        "new york": "NYC, współczesny",
        "london": "Brytyjski, miejski",
        "paris": "Francuski, romantyczny",
        "tokyo": "Japoński, współczesny",
        "starship": "kosmos, sci-fi",
        "galaxy": "kosmos, sci-fi",
        "kingdom": "fantasy, średniowiecze",
        "królestwo": "fantasy, średniowiecze",
        "castle": "fantasy, średniowiecze",
        "zamek": "fantasy, średniowiecze",
        "manor": "historyczny, gotycki",
        "village": "wiejski, tradycyjny",
        "wieś": "wiejski, tradycyjny",
        "city": "miejski, współczesny",
        "miasto": "miejski, współczesny",
    }

    # Detect theme keywords (English + Polish)
    theme_keywords = {
        "murder": "kryminał/tajemnica",
        "morderstwo": "kryminał/tajemnica",
        "love": "romans/relacje",
        "miłość": "romans/relacje",
        "war": "konflikt/walka",
        "wojna": "konflikt/walka",
        "quest": "przygoda/podróż",
        "wyprawa": "przygoda/podróż",
        "revenge": "zemsta/sprawiedliwość",
        "zemsta": "zemsta/sprawiedliwość",
        "secret": "tajemnica/odkrycie",
        "sekret": "tajemnica/odkrycie",
        "tajemnica": "tajemnica/odkrycie",
        "last": "przetrwanie/ostateczność",
        "ostatni": "przetrwanie/ostateczność",
        "lost": "poszukiwanie/odkrycie",
        "zagubiony": "poszukiwanie/odkrycie",
        "zapomniany": "odkrywanie siebie/zapomniana wiedza",
        "dark": "tajemnica/niebezpieczeństwo",
        "ciemny": "tajemnica/niebezpieczeństwo",
        "light": "nadzieja/odkrycie",
        "światło": "nadzieja/odkrycie",
        "shadow": "tajemnica/niebezpieczeństwo",
        "cień": "tajemnica/niebezpieczeństwo",
        "blood": "przemoc/rodzina",
        "krew": "przemoc/rodzina",
        "heart": "romans/emocje",
        "serce": "romans/emocje",
        "ognia": "magia żywiołów/opanowanie mocy",
        "ogień": "magia żywiołów/opanowanie mocy",
        "mag": "magia/wiedza tajemna",
        "czarodziej": "magia/wiedza tajemna",
    }

    # Detect backstory/trauma signals (CRITICAL for drama!)
    backstory_signals = {
        "długo oczekiwana": "problemy z płodnością/lata starań o dziecko",
        "długo oczekiwany": "problemy z płodnością/lata starań o dziecko",
        "upragniona": "desperackie pragnienie dziecka",
        "upragniony": "desperackie pragnienie dziecka",
        "jedyna": "możliwa utrata innych dzieci/niezdolność do posiadania więcej",
        "jedyny": "możliwa utrata innych dzieci/niezdolność do posiadania więcej",
        "ostatnia": "śmierć bliskich/koniec linii rodzinnej",
        "ostatni": "śmierć bliskich/koniec linii rodzinnej",
        "po powrocie": "separacja/więzienie/choroba/długa nieobecność",
        "wdowa": "śmierć męża",
        "wdowiec": "śmierć żony",
        "sierota": "śmierć rodziców",
        "adoptowana": "adopcja/poszukiwanie tożsamości",
        "adoptowany": "adopcja/poszukiwanie tożsamości",
        "cud": "niezwykłe okoliczności narodzin/poczęcia",
    }

    # Polish affectionate/diminutive terms that could appear in titles
    # These are merged into relationship_keywords for comprehensive coverage
    affectionate_terms = {
        # Children - affectionate
        "dziecko": {"role": "dziecko", "gender": "neutral", "theme": "rodzina"},
        "dzieciątko": {"role": "dziecko", "gender": "neutral", "theme": "rodzina"},
        "dziecię": {"role": "dziecko", "gender": "neutral", "theme": "rodzina"},
        "maleństwo": {"role": "dziecko", "gender": "neutral", "theme": "rodzina"},
        "dziecina": {"role": "dziecko", "gender": "neutral", "theme": "rodzina"},

        # Boys - affectionate
        "chłopiec": {"role": "syn", "gender": "male", "theme": "rodzina"},
        "chłopczyk": {"role": "syn", "gender": "male", "theme": "rodzina"},
        "synek": {"role": "syn", "gender": "male", "theme": "rodzina"},

        # Girls - affectionate
        "dziewczynka": {"role": "córka", "gender": "female", "theme": "rodzina"},
        "córeczka": {"role": "córka", "gender": "female", "theme": "rodzina"},
        "córunia": {"role": "córka", "gender": "female", "theme": "rodzina"},

        # Babies
        "niemowlę": {"role": "dziecko", "gender": "neutral", "theme": "rodzina"},
        "niemowlak": {"role": "dziecko", "gender": "neutral", "theme": "rodzina"},
        "noworodek": {"role": "dziecko", "gender": "male", "theme": "rodzina"},
        "noworodka": {"role": "dziecko", "gender": "female", "theme": "rodzina"},
        "bobas": {"role": "dziecko", "gender": "neutral", "theme": "rodzina"},
        "maluch": {"role": "dziecko", "gender": "male", "theme": "rodzina"},
        "maluszek": {"role": "dziecko", "gender": "male", "theme": "rodzina"},

        # Friends
        "przyjaciel": {"role": "przyjaciel", "gender": "male", "theme": "przyjaźń"},
        "przyjaciółka": {"role": "przyjaciel", "gender": "female", "theme": "przyjaźń"},
        "przyjaciele": {"role": "przyjaciele", "gender": "neutral", "theme": "przyjaźń"},
        "kumpel": {"role": "przyjaciel", "gender": "male", "theme": "przyjaźń"},
        "koleżanka": {"role": "przyjaciel", "gender": "female", "theme": "przyjaźń"},
        "kolega": {"role": "przyjaciel", "gender": "male", "theme": "przyjaźń"},

        # Lovers/romantic
        "ukochany": {"role": "ukochany", "gender": "male", "theme": "romans"},
        "ukochana": {"role": "ukochany", "gender": "female", "theme": "romans"},
        "kochanek": {"role": "kochanek", "gender": "male", "theme": "romans"},
        "kochanka": {"role": "kochanek", "gender": "female", "theme": "romans"},
        "ukochany": {"role": "partner", "gender": "male", "theme": "romans"},
        "ukochana": {"role": "partner", "gender": "female", "theme": "romans"},

        # English children terms
        "child": {"role": "dziecko", "gender": "neutral", "theme": "rodzina"},
        "children": {"role": "dzieci", "gender": "neutral", "theme": "rodzina"},
        "baby": {"role": "dziecko", "gender": "neutral", "theme": "rodzina"},
        "infant": {"role": "niemowlę", "gender": "neutral", "theme": "rodzina"},
        "boy": {"role": "syn", "gender": "male", "theme": "rodzina"},
        "girl": {"role": "córka", "gender": "female", "theme": "rodzina"},
        "kid": {"role": "dziecko", "gender": "neutral", "theme": "rodzina"},
        "kids": {"role": "dzieci", "gender": "neutral", "theme": "rodzina"},

        # English friends
        "friend": {"role": "przyjaciel", "gender": "neutral", "theme": "przyjaźń"},
        "friends": {"role": "przyjaciele", "gender": "neutral", "theme": "przyjaźń"},
        "lover": {"role": "kochanek", "gender": "neutral", "theme": "romans"},
        "beloved": {"role": "ukochany", "gender": "neutral", "theme": "romans"},
    }

    # Merge affectionate terms into relationship_keywords
    relationship_keywords.update(affectionate_terms)

    # Age pattern detection for character role classification
    age_patterns = [
        (r'(\d+)[,.]?\s*(?:roczn[ayi]|letni[aey]|miesi[ęe]czn[ayi])', 'child_age'),
        (r'niemowl[ęe]', 'infant'),
        (r'noworod(?:ek|ka)', 'newborn'),
        (r'maluch|malutk[aiy]', 'toddler'),
        (r'bobas', 'baby'),
        (r'dziecko|dziecię|dzieciątko', 'child'),
    ]

    # Detect parent names from pattern "córka/syn X i Y" (e.g., "córka Hanny i Mateusza")
    # Also track genitive forms to avoid adding them as duplicates later
    processed_genitive_forms = set()  # Track genitive forms we've processed

    parent_pattern = re.search(
        r'(?:córka|syn|dziecko)\s+(\w+)\s+i\s+(\w+)',
        title,
        re.IGNORECASE
    )
    if parent_pattern:
        parent1_name = parent_pattern.group(1).strip('.,')
        parent2_name = parent_pattern.group(2).strip('.,')

        # Track these genitive forms
        processed_genitive_forms.add(parent1_name.lower())
        processed_genitive_forms.add(parent2_name.lower())

        # Polish genitive: Hanny (from Hanna), Mateusza (from Mateusz)
        # Try to convert from genitive to nominative
        def genitive_to_nominative(name: str) -> str:
            # Known irregular genitive->nominative mappings
            irregular = {
                "pawła": "Paweł", "pawla": "Paweł",
                "piotra": "Piotr",
                "jakuba": "Jakub",
                "józefa": "Józef", "jozefa": "Józef",
                "michała": "Michał", "michala": "Michał",
                "rafała": "Rafał", "rafala": "Rafał",
                "gabriela": "Gabriel",
                "krzysztofa": "Krzysztof",
                "stanisława": "Stanisław", "stanislawa": "Stanisław",
            }
            if name.lower() in irregular:
                return irregular[name.lower()]

            # Pattern-based rules (ordered by specificity)
            if name.endswith('szy') or name.endswith('dzy'):
                # Grzegorzy -> doesn't happen, skip
                pass
            elif name.endswith('usza') or name.endswith('asza'):
                # Mateusza -> Mateusz, Tomasza -> Tomasz
                return name[:-2]
            elif name.endswith('ła') or name.endswith('la'):
                # Pawła -> Paweł (handled by irregular above)
                # Generic: Karola -> Karol
                return name[:-1]
            elif name.endswith('ny'):
                # Hanny -> Hanna
                return name[:-1] + 'a'
            elif name.endswith('y') and len(name) > 3:
                # Anny -> Anna (doubled consonant), Ewy -> Ewa
                if len(name) > 2 and name[-3] == name[-2]:
                    # Hanny -> Hanna (double consonant + y)
                    return name[:-1] + 'a'
                else:
                    # Ewy -> Ewa, Katarzyny -> Katarzyna
                    return name[:-1] + 'a'
            elif name.endswith('i') and len(name) > 3:
                # Ani -> Ania, Zosi -> Zosia
                return name[:-1] + 'a'
            elif name.endswith('a') and len(name) > 3:
                # Mateusza -> Mateusz (already handled above)
                # Adama -> Adam
                return name[:-1]
            return name

        parent1_nominative = genitive_to_nominative(parent1_name)
        parent2_nominative = genitive_to_nominative(parent2_name)

        # Also track nominative forms
        processed_genitive_forms.add(parent1_nominative.lower())
        processed_genitive_forms.add(parent2_nominative.lower())

        insights["character_names"].append({
            "name": parent1_nominative,
            "role": "main",  # Parent is a protagonist
            "gender": "female" if parent1_nominative.endswith('a') else "male"
        })
        insights["character_names"].append({
            "name": parent2_nominative,
            "role": "main",  # Parent is a protagonist
            "gender": "male" if not parent2_nominative.endswith('a') else "female"
        })
        insights["focus"] = "oparty na postaciach"

    # Helper function to check if a name (in any form) is already in our list
    def is_name_already_added(name: str) -> bool:
        name_lower = name.lower()
        # Check if this exact name or its genitive/nominative form is already processed
        if name_lower in processed_genitive_forms:
            return True
        # Check against existing character names
        for cn in insights["character_names"]:
            if cn["name"].lower() == name_lower:
                return True
        return False

    # Detect which name is associated with child age (for catalyst detection)
    child_name_pattern = re.search(
        r'(\w+)[,.]?\s*\d+[,.]?\s*(?:roczn[ayi]|letni[aey]|miesi[ęe]czn[ayi])',
        title,
        re.IGNORECASE
    )
    catalyst_name = child_name_pattern.group(1).strip('.,') if child_name_pattern else None

    # Extract character names (capitalized words, excluding first word if common article)
    for i, word in enumerate(words):
        word_clean = word.strip('.,!?;:"\'')

        # Check for relationship keywords
        for key, info in relationship_keywords.items():
            if key in word_clean.lower():
                insights["themes"].append(info["theme"])
                # Next capitalized word might be a name
                if i + 1 < len(words):
                    next_word = words[i + 1].strip('.,!?;:"\'')
                    if next_word and next_word[0].isupper() and len(next_word) > 2:
                        # Skip if already added (checking all forms)
                        if not is_name_already_added(next_word):
                            # Check if this is the catalyst child
                            is_catalyst = (catalyst_name and next_word.lower() == catalyst_name.lower())
                            insights["character_names"].append({
                                "name": next_word,
                                "role": "catalyst" if is_catalyst else info["role"],
                                "gender": info["gender"]
                            })
                            processed_genitive_forms.add(next_word.lower())
                        insights["focus"] = "oparty na postaciach"

        # Check for setting keywords
        for key, setting_info in setting_keywords.items():
            if key in word_clean.lower():
                insights["setting_hints"].append(setting_info)

        # Check for theme keywords
        for key, theme_info in theme_keywords.items():
            if key in word_clean.lower():
                if theme_info not in insights["themes"]:
                    insights["themes"].append(theme_info)

    # Check for backstory/trauma signals (multi-word phrases)
    detected_backstory = []
    for signal, meaning in backstory_signals.items():
        if signal in title_lower:
            detected_backstory.append({"signal": signal, "meaning": meaning})
            # Add related themes
            if "płodność" in meaning or "dziecko" in meaning:
                if "trudności rodzicielskie" not in insights["themes"]:
                    insights["themes"].append("trudności rodzicielskie")
            if "śmierć" in meaning or "utrata" in meaning:
                if "strata/żałoba" not in insights["themes"]:
                    insights["themes"].append("strata/żałoba")
            if "adopcja" in meaning:
                if "tożsamość/korzenie" not in insights["themes"]:
                    insights["themes"].append("tożsamość/korzenie")

    if detected_backstory:
        insights["backstory_signals"] = detected_backstory

    # Check for age patterns - classify young children as catalysts, not protagonists
    detected_ages = []
    for pattern, age_type in age_patterns:
        match = re.search(pattern, title_lower)
        if match:
            if age_type == 'child_age':
                age_value = float(match.group(1).replace(',', '.'))
                detected_ages.append({"type": age_type, "value": age_value})
                # Children under 6 should be catalysts, not protagonists
                if age_value < 6:
                    insights["catalyst_character_detected"] = True
            else:
                detected_ages.append({"type": age_type, "value": 0})
                insights["catalyst_character_detected"] = True

    if detected_ages:
        insights["detected_ages"] = detected_ages

    # Detect Polish names and set Polish/Eastern European setting
    polish_name_endings = ["a", "ia", "ka", "na", "ska"]

    # BLACKLIST: Common Polish words that are NOT names but end with name-like endings
    not_names_blacklist = [
        "ognia", "wody", "ziemia", "powietrza", "światła", "ciemności",  # Elements
        "magia", "siła", "moc", "energia",  # Powers
        "kraina", "ziemia", "wyspa", "góra",  # Places (genitive)
        "nocy", "dnia", "świta", "zmierzchu",  # Time (genitive)
        "wojna", "pokoju", "miłości", "nienawiści",  # Abstract (genitive)
        "mag", "król", "królowa", "wojownik", "czarodziej",  # Titles/roles
    ]

    for i, word in enumerate(words):
        word_clean = word.strip('.,!?;:"\'')
        word_lower = word_clean.lower()

        # Skip if it's in blacklist
        if word_lower in not_names_blacklist:
            continue

        if word_clean and word_clean[0].isupper() and len(word_clean) > 3:
            if any(word_clean.lower().endswith(ending) for ending in polish_name_endings):
                # Additional check: if previous word is a title/role, this might not be a name
                if i > 0:
                    prev_word = words[i-1].strip('.,!?;:"\'').lower()
                    if prev_word in ["mag", "król", "królowa", "rycerz", "lord", "lady", "sir", "master"]:
                        continue  # Skip this, it's likely genitive after a title

                # Likely Polish name - check if not already added (in any form)
                if not is_name_already_added(word_clean):
                    # Determine role: if this is the catalyst child name, mark as catalyst
                    char_role = "main"
                    if catalyst_name and word_clean.lower() == catalyst_name.lower():
                        char_role = "catalyst"  # This specific character is the catalyst

                    insights["character_names"].append({
                        "name": word_clean,
                        "role": char_role,
                        "gender": "female" if word_clean.endswith("a") else "neutral"
                    })
                    processed_genitive_forms.add(word_clean.lower())
                if "Polska/Europa Wschodnia" not in insights["setting_hints"]:
                    insights["setting_hints"].append("Polska/Europa Wschodnia")

    # Generate title-based suggestions for AI decisions
    if insights["character_names"]:
        first_char = insights["character_names"][0]

        # Check if first character is a catalyst (child) - then find the real protagonists
        if first_char.get("role") == "catalyst":
            insights["title_suggestions"]["catalyst_character"] = first_char["name"]
            insights["title_suggestions"]["catalyst_explanation"] = "Małe dziecko jest katalizatorem akcji, nie protagonistą"

            # Look for parent names (usually mentioned after "córka/syn X i Y")
            protagonist_names = [c["name"] for c in insights["character_names"] if c.get("role") != "catalyst"]
            if protagonist_names:
                insights["title_suggestions"]["suggested_protagonists"] = protagonist_names
                insights["title_suggestions"]["main_character_name"] = protagonist_names[0]
            else:
                insights["title_suggestions"]["main_character_name"] = "Rodzic (do określenia)"
                insights["title_suggestions"]["needs_protagonist_names"] = True
        else:
            insights["title_suggestions"]["main_character_name"] = first_char["name"]
            insights["title_suggestions"]["main_character_gender"] = first_char["gender"]

        # If title has relationships, suggest family-focused plot
        if "rodzina" in insights["themes"] or insights.get("catalyst_character_detected"):
            insights["title_suggestions"]["add_subplots"] = ["family_relationships", "generational_conflict", "parenting_challenges"]
            insights["title_suggestions"]["character_count_modifier"] = 2  # Add parents/family members

        # If backstory signals detected, add relevant themes
        if insights.get("backstory_signals"):
            insights["title_suggestions"]["implied_backstory"] = [s["meaning"] for s in insights["backstory_signals"]]
            insights["title_suggestions"]["add_subplots"] = insights["title_suggestions"].get("add_subplots", []) + ["past_trauma", "healing_journey"]

    if insights["setting_hints"]:
        insights["title_suggestions"]["world_setting"] = insights["setting_hints"][0]

    # Adjust tone based on genre and keywords
    if genre in ["horror", "thriller"]:
        if any(word in title_lower for word in ["dark", "shadow", "blood", "murder", "death", "ciemny", "cień", "krew", "morderstwo", "śmierć"]):
            insights["tone"] = "ciemny"
    elif genre in ["romance", "comedy"]:
        if any(word in title_lower for word in ["love", "heart", "wedding", "summer", "miłość", "serce", "ślub", "lato"]):
            insights["tone"] = "jasny"

    return insights


async def simulate_generation(db: Session, project: Project) -> ProjectSimulation:
    """
    INTELLIGENT SIMULATION - AI decides ALL parameters

    Based on genre AND title, AI determines:
    - Target word count (e.g., 85,000 - 120,000 words)
    - Number of chapters (e.g., 25-35)
    - Main character count (e.g., 4-7)
    - Supporting character count (e.g., 8-15)
    - Subplot count (e.g., 2-4)
    - World detail level (high/medium for genre)
    - Structure type (Hero's Journey, 7-Point, etc.)
    - Character names and themes from title

    Then calculates cost for each of 15 steps based on:
    - Complexity of step
    - Model tier required
    - Estimated token usage
    """
    logger.info(f"Running intelligent simulation for project {project.id}: '{project.name}'")

    # Update status to SIMULATING
    project.status = ProjectStatus.SIMULATING
    db.commit()

    # Get genre-specific config
    genre_cfg = genre_config.get_genre_config(project.genre.value)

    # 🚀 PRIMARY: SEMANTIC AI-POWERED TITLE ANALYSIS
    # This is the MAIN analysis - AI understands context, grammar, metaphors
    logger.info(f"🧠 Running PRIMARY AI semantic analysis for: '{project.name}'")
    semantic_insights = await _semantic_analyze_title_with_ai(project.name, project.genre.value)
    logger.info(f"✅ AI Analysis complete: protagonist={semantic_insights.get('character_implications', {}).get('suggested_names', 'unknown')}")

    # FALLBACK: Basic keyword analysis (only for supplementary data or if AI fails)
    title_insights = _analyze_title(project.name, project.genre.value)
    logger.info(f"📋 Keyword analysis (supplementary): {title_insights.get('character_names', [])}")

    # AI DECISIONS (in production, this would call GPT-4o-mini for intelligent decisions)
    # For now, using intelligent defaults based on genre + title analysis
    
    # Determine word count based on genre defaults
    word_count_ranges = {
        "sci-fi": (85000, 120000),
        "fantasy": (95000, 140000),
        "thriller": (70000, 90000),
        "horror": (70000, 90000),
        "romance": (70000, 90000),
        "drama": (80000, 100000),
        "comedy": (70000, 85000),
        "mystery": (70000, 90000),
    }
    
    min_words, max_words = word_count_ranges.get(project.genre.value, (80000, 100000))
    target_word_count = (min_words + max_words) // 2
    
    # Calculate chapter count (avg 3000-4000 words per chapter)
    avg_words_per_chapter = 3500
    chapter_count = target_word_count // avg_words_per_chapter
    
    # Character counts by genre
    if project.genre.value in ["fantasy", "sci-fi"]:
        main_char_count = 5
        supporting_count = 12
        minor_count = 20
    elif project.genre.value == "comedy":
        main_char_count = 3  # Comedy typically has fewer main characters for simpler dynamics
        supporting_count = 6
        minor_count = 10
    else:
        main_char_count = 4
        supporting_count = 8
        minor_count = 15

    # Apply title-based character count adjustments
    if "character_count_modifier" in title_insights["title_suggestions"]:
        modifier = title_insights["title_suggestions"]["character_count_modifier"]
        main_char_count += modifier
        logger.info(f"Title analysis suggests adding {modifier} main character(s). New count: {main_char_count}")

    # Subplot count
    subplot_count = 3 if project.genre.value in ["fantasy", "thriller"] else 2

    # Adjust subplot count if title suggests family themes
    if "family" in title_insights["themes"]:
        subplot_count += 1  # Add a family-related subplot
        logger.info(f"Title suggests family themes, increasing subplot count to {subplot_count}")

    # World detail
    world_detail = "high" if project.genre.value in ["fantasy", "sci-fi"] else "medium"

    # Enhance world detail if title provides setting hints
    if title_insights["setting_hints"]:
        logger.info(f"Title provides setting hints: {title_insights['setting_hints']}")
    
    # Determine style complexity based on genre
    style_complexity_map = {
        "literary": "high",
        "fantasy": "high",
        "sci-fi": "high",
        "thriller": "medium",
        "mystery": "medium",
        "horror": "medium",
        "drama": "medium",
        "romance": "medium",
        "comedy": "low",
    }
    style_complexity = style_complexity_map.get(project.genre.value, "medium")

    # AI-determined parameters (enhanced with BOTH basic AND semantic title analysis)
    # 🎯 MERGE: Use semantic (AI) as primary, keyword as fallback
    char_implications = semantic_insights.get("character_implications", {})
    world_setting_sem = semantic_insights.get("world_setting", {})

    # Primary: detected_characters from AI (has proper roles), Fallback: keyword-based analysis
    # IMPORTANT: Preserve role information (catalyst, protagonist, etc.) from both sources!
    detected_characters = semantic_insights.get("detected_characters", [])
    keyword_characters = title_insights.get("character_names", [])

    # Merge characters: AI detected_characters take priority, then keyword-based
    final_characters = []
    seen_names = set()

    # First add AI-detected characters (they have psychology info)
    for char in detected_characters:
        name = char.get("name", "")
        if name and name.lower() not in seen_names:
            final_characters.append({
                "name": name,
                "role": char.get("role", "main"),
                "gender": char.get("gender", "neutral"),
                "age_hint": char.get("age_hint", ""),
                "psychology": char.get("psychology", {})
            })
            seen_names.add(name.lower())

    # Then add keyword-based characters (with their catalyst/main roles preserved!)
    for char in keyword_characters:
        name = char.get("name", "")
        if name and name.lower() not in seen_names:
            final_characters.append({
                "name": name,
                "role": char.get("role", "main"),  # Preserve catalyst role!
                "gender": char.get("gender", "neutral")
            })
            seen_names.add(name.lower())

    # Fallback to old suggested_names only if nothing else found
    if not final_characters:
        suggested_names = char_implications.get("suggested_names", [])
        for name in suggested_names:
            if name and name.lower() not in seen_names:
                final_characters.append({"name": name, "role": "main", "gender": "neutral"})
                seen_names.add(name.lower())

    # Primary: semantic themes, Fallback: keyword themes
    themes = semantic_insights.get("themes", [])
    if not themes:
        themes = title_insights["themes"]

    ai_decisions = {
        "target_word_count": target_word_count,
        "planned_volumes": 1,
        "chapter_count": chapter_count,
        "main_character_count": main_char_count,
        "supporting_character_count": supporting_count,
        "minor_character_count": minor_count,
        "subplot_count": subplot_count,
        "world_detail_level": world_detail,
        "style_complexity": style_complexity,
        "structure_type": genre_cfg["structure"],
        "style_guidelines": genre_cfg["style"],
        # 🚀 TITLE-BASED ENHANCEMENTS (AI-powered primary, keyword fallback)
        "title_analysis": {
            # Basic fields (for backward compatibility) - NOW PRESERVING ROLES!
            "character_names": final_characters,
            "themes": themes,
            "setting_hints": [world_setting_sem.get("type", "")] if world_setting_sem.get("type") else title_insights["setting_hints"],
            "tone": semantic_insights.get("emotional_core", title_insights["tone"]),
            "focus": "oparty na postaciach" if final_characters else title_insights["focus"],
            # Include backstory signals from keyword analysis
            "backstory_signals": title_insights.get("backstory_signals", []),
            # 🔮 ADVANCED: Unpack all 10 dimensions from semantic_insights directly here (not nested!)
            **{k: v for k, v in semantic_insights.items() if k not in ["emotional_core", "themes"]}
        },
        # ALSO at top level for easy access by agents
        "semantic_title_analysis": semantic_insights
    }

    # Add specific title suggestions if available
    if title_insights["title_suggestions"]:
        ai_decisions["title_suggestions"] = title_insights["title_suggestions"]
    
    # Save parameters to project
    project.parameters = ai_decisions
    db.commit()
    
    # Calculate cost for each step
    estimated_steps = _calculate_step_costs(ai_decisions, project.genre.value)
    
    # Total cost and duration
    total_cost = sum(step["estimated_cost"] for step in estimated_steps)
    total_duration = sum(step["estimated_duration_minutes"] for step in estimated_steps)
    
    project.estimated_cost = total_cost
    project.estimated_duration_minutes = total_duration

    # Save simulation data to project for persistence
    simulation_dict = {
        "estimated_steps": estimated_steps,
        "estimated_total_cost": total_cost,
        "estimated_duration_minutes": total_duration,
        "ai_decisions": ai_decisions
    }
    project.simulation_data = simulation_dict

    db.commit()

    simulation = ProjectSimulation(
        estimated_steps=estimated_steps,
        estimated_total_cost=total_cost,
        estimated_duration_minutes=total_duration,
        ai_decisions=ai_decisions
    )

    logger.info(f"Simulation complete for project {project.id}: ${total_cost:.2f}, {total_duration} min")
    logger.info(f"Simulation data saved to project.simulation_data")

    return simulation


def _calculate_step_costs(ai_decisions: dict, genre: str) -> List[dict]:
    """
    Calculate estimated cost and duration for each of 15 pipeline steps

    Uses model tier config to determine which model for each step,
    then estimates token usage and calculates cost.

    FIXED (2026-02-06): Accurate estimation based on:
    - Polish text: ~1.5 tokens per word (not 1.33)
    - Scene-by-scene architecture: 5 scenes per chapter
    - Context reuse model: system prompt cached, ~40% context overlap between scenes
    - world_detail and style_complexity affect token estimates
    - Parallelization-aware duration estimation
    - Title analysis cost included
    """
    chapter_count = ai_decisions.get("chapter_count", 25)
    target_words = ai_decisions.get("target_word_count", 90000)
    main_chars = ai_decisions.get("main_character_count", 5)
    supporting_chars = ai_decisions.get("supporting_character_count", 10)
    subplots = ai_decisions.get("subplot_count", 3)
    world_detail = ai_decisions.get("world_detail_level", "medium")
    style_complexity = ai_decisions.get("style_complexity", "medium")

    # Scene-by-scene architecture parameters
    SCENES_PER_CHAPTER = 5
    total_scenes = chapter_count * SCENES_PER_CHAPTER

    # Token estimation constants (Polish text)
    TOKENS_PER_WORD_POLISH = 1.5  # Polish inflection = more tokens

    # Context sizes per scene (input tokens) - with REUSE MODEL
    # First scene in chapter: full context pack (11K tokens)
    # Subsequent scenes: system prompt cached, ~40% context overlap
    SYSTEM_PROMPT_TOKENS = 2000
    CONTEXT_PACK_TOKENS = 8000
    BEAT_SHEET_TOKENS = 500
    PREVIOUS_CONTENT_TOKENS = 500
    FULL_INPUT_PER_SCENE = SYSTEM_PROMPT_TOKENS + CONTEXT_PACK_TOKENS + BEAT_SHEET_TOKENS + PREVIOUS_CONTENT_TOKENS
    # Subsequent scenes reuse ~60% of context (system prompt cached + overlapping context)
    REUSE_INPUT_PER_SCENE = int(CONTEXT_PACK_TOKENS * 0.4 + BEAT_SHEET_TOKENS + PREVIOUS_CONTENT_TOKENS + 500)
    # Effective average: 1 full + 4 reused per chapter
    EFFECTIVE_INPUT_PER_SCENE = (FULL_INPUT_PER_SCENE + (SCENES_PER_CHAPTER - 1) * REUSE_INPUT_PER_SCENE) // SCENES_PER_CHAPTER

    # World detail multiplier: high detail = more tokens for world-building and context
    world_detail_multiplier = {"high": 1.3, "medium": 1.0, "low": 0.8}.get(world_detail, 1.0)
    # Style complexity multiplier: affects polishing and prose output
    style_complexity_multiplier = {"high": 1.2, "medium": 1.0, "low": 0.85}.get(style_complexity, 1.0)

    # Title analysis cost (GPT-4o call for semantic analysis, ~2K in / ~3K out)
    TITLE_ANALYSIS_INPUT = 2000
    TITLE_ANALYSIS_OUTPUT = 3000

    steps = [
        {
            "step": 1,
            "name": "Inicjalizacja Projektu",
            "task_type": "initialization",
            "estimated_tokens_in": 500,
            "estimated_tokens_out": 200,
        },
        {
            "step": 2,
            "name": "Parametryzacja (AI)",
            "task_type": "initialization",
            "estimated_tokens_in": 1000,
            "estimated_tokens_out": 500,
        },
        {
            "step": 3,
            "name": "Generowanie World Bible",
            "task_type": "world_building",
            "estimated_tokens_in": int(2000 * world_detail_multiplier),
            "estimated_tokens_out": int(4000 * world_detail_multiplier),
        },
        {
            "step": 4,
            "name": "Kreacja Postaci Głównych",
            "task_type": "character_creation",
            "estimated_tokens_in": int(2000 * main_chars * world_detail_multiplier),
            "estimated_tokens_out": int(3000 * main_chars),
        },
        {
            "step": 5,
            "name": "Kreacja Postaci Pobocznych",
            "task_type": "character_creation",
            "estimated_tokens_in": int(1500 * supporting_chars * world_detail_multiplier),
            "estimated_tokens_out": int(1500 * supporting_chars),
        },
        {
            "step": 6,
            "name": "Projektowanie Głównej Osi Fabularnej",
            "task_type": "plot_structure",
            "estimated_tokens_in": 3000,
            "estimated_tokens_out": 5000,
        },
        {
            "step": 7,
            "name": "Projektowanie Wątków Pobocznych",
            "task_type": "plot_structure",
            "estimated_tokens_in": 2500 * subplots,
            "estimated_tokens_out": 3000 * subplots,
        },
        {
            "step": 8,
            "name": "Podział na Rozdziały",
            "task_type": "plot_structure",
            "estimated_tokens_in": 3000,
            "estimated_tokens_out": 600 * chapter_count,
        },
        {
            "step": 9,
            "name": "Detale Scen (Beat Sheets)",
            "task_type": "simple_outline",
            # Beat Sheet for each scene: ~2000 in, ~1500 out
            "estimated_tokens_in": 2000 * total_scenes,
            "estimated_tokens_out": 1500 * total_scenes,
        },
        {
            "step": 10,
            "name": "Walidacja Przed Pisaniem",
            "task_type": "validation",
            "estimated_tokens_in": 5000,
            "estimated_tokens_out": 2000,
        },
        {
            "step": 11,
            "name": "Generowanie Prozy - Wszystkie Rozdziały",
            "task_type": "prose_writing",
            # Context reuse model: first scene/chapter = full context, subsequent = ~40% new
            "estimated_tokens_in": EFFECTIVE_INPUT_PER_SCENE * total_scenes,
            "estimated_tokens_out": int(target_words * TOKENS_PER_WORD_POLISH * style_complexity_multiplier),
        },
        {
            "step": 12,
            "name": "Weryfikacja Spójności (wszystkie rozdziały)",
            "task_type": "validation",
            # RAG-based validation: ~2000 tokens per chapter
            "estimated_tokens_in": 2000 * chapter_count,
            "estimated_tokens_out": 500 * chapter_count,
        },
        {
            "step": 13,
            "name": "Polerowanie Stylu (wybrane rozdziały)",
            "task_type": "style_polish",
            # Style pass on ~20% of chapters (more for high complexity)
            "estimated_tokens_in": int(target_words * 0.2 * TOKENS_PER_WORD_POLISH * style_complexity_multiplier),
            "estimated_tokens_out": int(target_words * 0.05 * TOKENS_PER_WORD_POLISH * style_complexity_multiplier),
        },
        {
            "step": 14,
            "name": "Audyt Zgodności Gatunkowej",
            "task_type": "validation",
            "estimated_tokens_in": 3000,
            "estimated_tokens_out": 1000,
        },
        {
            "step": 15,
            "name": "Końcowy Montaż i Eksport",
            "task_type": "formatting",
            "estimated_tokens_in": 2000,
            "estimated_tokens_out": 1000,
        },
    ]

    estimated_steps = []

    for step_data in steps:
        # Determine model tier
        tier = model_tier_config.get_tier_for_task(step_data["task_type"])

        # Get model costs
        if tier == 1:
            input_cost = settings.TIER1_INPUT_COST
            output_cost = settings.TIER1_OUTPUT_COST
            model_name = settings.GPT_4O_MINI
        elif tier == 2:
            input_cost = settings.TIER2_INPUT_COST
            output_cost = settings.TIER2_OUTPUT_COST
            model_name = settings.GPT_4O
        else:  # tier 3
            input_cost = settings.TIER3_INPUT_COST
            output_cost = settings.TIER3_OUTPUT_COST
            model_name = settings.GPT_4

        # Calculate cost
        cost = (
            (step_data["estimated_tokens_in"] / 1_000_000) * input_cost +
            (step_data["estimated_tokens_out"] / 1_000_000) * output_cost
        )

        # Estimate duration (rough approximation)
        # Tier 1: ~10k tokens/min, Tier 2: ~8k tokens/min, Tier 3: ~5k tokens/min
        tokens_per_min = {1: 10000, 2: 8000, 3: 5000}[tier]
        duration = max(1, int((step_data["estimated_tokens_in"] + step_data["estimated_tokens_out"]) / tokens_per_min))

        # Parallelization factor: steps processing multiple independent items
        # (characters, chapters, scenes) can be partially parallelized
        parallelizable_steps = {4, 5, 7, 9, 11, 12}  # Independent items per step
        if step_data["step"] in parallelizable_steps:
            # Assume ~3x parallelization (Celery concurrency=4, minus overhead)
            duration = max(1, int(duration / 3))

        estimated_steps.append({
            "step": step_data["step"],
            "name": step_data["name"],
            "estimated_cost": round(cost, 4),
            "estimated_tokens": step_data["estimated_tokens_out"],
            "estimated_tokens_in": step_data["estimated_tokens_in"],
            "model_tier": f"tier{tier}",
            "model_name": model_name,
            "estimated_duration_minutes": duration,
            "description": f"Model: {model_name} | ~{step_data['estimated_tokens_out']//1000}K tokens output"
        })

    # Add title analysis cost as a pre-step (GPT-4o call)
    title_analysis_cost = round(
        (TITLE_ANALYSIS_INPUT / 1_000_000) * settings.TIER2_INPUT_COST +
        (TITLE_ANALYSIS_OUTPUT / 1_000_000) * settings.TIER2_OUTPUT_COST,
        4
    )
    # Add to step 2 (Parametryzacja) since title analysis happens during simulation
    for step in estimated_steps:
        if step["step"] == 2:
            step["estimated_cost"] = round(step["estimated_cost"] + title_analysis_cost, 4)
            step["description"] += f" + analiza tytułu (${title_analysis_cost:.4f})"
            break

    return estimated_steps


def start_generation_task(project_id: int) -> str:
    """
    Start the generation task in background (Celery)
    
    Returns task ID for tracking
    """
    # Import here to avoid circular dependency
    from app.tasks.generation_tasks import run_full_pipeline
    
    task = run_full_pipeline.delay(project_id)
    logger.info(f"Started generation task {task.id} for project {project_id}")
    
    return task.id


def get_project_status(db: Session, project: Project) -> dict:
    """
    Get real-time status of project generation
    """
    eta = None
    if project.started_at and project.estimated_cost > 0:
        # Rough ETA based on cost progress
        if project.actual_cost > 0:
            progress_ratio = project.actual_cost / project.estimated_cost
            # This is a simplified calculation
            eta = datetime.now() + timedelta(minutes=30)  # Placeholder
    
    return {
        "project_id": project.id,
        "status": project.status,
        "current_step": project.current_step,
        "total_steps": 15,
        "progress_percentage": project.progress_percentage,
        "current_activity": project.current_activity,
        "estimated_cost": project.estimated_cost,
        "actual_cost": project.actual_cost,
        "started_at": project.started_at,
        "estimated_completion": eta,
    }


def get_world_bible(db: Session, project_id: int) -> Optional[WorldBible]:
    """Get World Bible for project"""
    return db.query(WorldBible).filter(WorldBible.project_id == project_id).first()


def get_characters(db: Session, project_id: int) -> List[Character]:
    """Get all characters for project"""
    return db.query(Character).filter(Character.project_id == project_id).all()


def get_character(db: Session, character_id: int) -> Optional[Character]:
    """Get character by ID"""
    return db.query(Character).filter(Character.id == character_id).first()


def get_plot_structure(db: Session, project_id: int) -> Optional[PlotStructure]:
    """Get plot structure for project"""
    return db.query(PlotStructure).filter(PlotStructure.project_id == project_id).first()


def get_chapters(db: Session, project_id: int) -> List[Chapter]:
    """Get all chapters for project"""
    return db.query(Chapter).filter(Chapter.project_id == project_id).order_by(Chapter.number).all()


def get_chapter_by_number(db: Session, project_id: int, chapter_number: int) -> Optional[Chapter]:
    """Get specific chapter by number"""
    return db.query(Chapter).filter(
        Chapter.project_id == project_id,
        Chapter.number == chapter_number
    ).first()


async def export_project(db: Session, project_id: int, format: str) -> str:
    """
    Export project to specified format
    
    Returns path to exported file
    """
    # Import export service
    from app.services.export_service import export_to_format
    
    file_path = await export_to_format(db, project_id, format)
    logger.info(f"Exported project {project_id} to {format}: {file_path}")
    
    return file_path


def delete_project(db: Session, project_id: int):
    """Delete project and all associated data"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()
        logger.info(f"Deleted project {project_id}")
