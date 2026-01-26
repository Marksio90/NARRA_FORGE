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

BĄDŹ MAKSYMALNIE SZCZEGÓŁOWY. Każde pole wypełnij KONKRETNĄ, BOGATĄ treścią.
To musi być analiza na poziomie profesjonalnego redaktora z wydawnictwa Big Five!"""

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
    relationship_keywords = {
        "córka": {"role": "córka", "gender": "female", "theme": "rodzina"},
        "syn": {"role": "syn", "gender": "male", "theme": "rodzina"},
        "matka": {"role": "matka", "gender": "female", "theme": "rodzina"},
        "ojciec": {"role": "ojciec", "gender": "male", "theme": "rodzina"},
        "daughter": {"role": "córka", "gender": "female", "theme": "rodzina"},
        "son": {"role": "syn", "gender": "male", "theme": "rodzina"},
        "mother": {"role": "matka", "gender": "female", "theme": "rodzina"},
        "father": {"role": "ojciec", "gender": "male", "theme": "rodzina"},
        "sister": {"role": "siostra", "gender": "female", "theme": "rodzina"},
        "siostra": {"role": "siostra", "gender": "female", "theme": "rodzina"},
        "brother": {"role": "brat", "gender": "male", "theme": "rodzina"},
        "brat": {"role": "brat", "gender": "male", "theme": "rodzina"},
        "wife": {"role": "żona", "gender": "female", "theme": "małżeństwo"},
        "żona": {"role": "żona", "gender": "female", "theme": "małżeństwo"},
        "husband": {"role": "mąż", "gender": "male", "theme": "małżeństwo"},
        "mąż": {"role": "mąż", "gender": "male", "theme": "małżeństwo"},
        "widow": {"role": "wdowa", "gender": "female", "theme": "strata"},
        "wdowa": {"role": "wdowa", "gender": "female", "theme": "strata"},
        "orphan": {"role": "sierota", "gender": "neutral", "theme": "strata"},
        "sierota": {"role": "sierota", "gender": "neutral", "theme": "strata"},
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

    # Age pattern detection for character role classification
    age_patterns = [
        (r'(\d+)[,.]?\s*(?:roczn[ayi]|letni[aey]|miesi[ęe]czn[ayi])', 'child_age'),
        (r'niemowl[ęe]', 'infant'),
        (r'noworod(?:ek|ka)', 'newborn'),
        (r'maluch|malutk[aiy]', 'toddler'),
    ]

    # Detect parent names from pattern "córka/syn X i Y" (e.g., "córka Hanny i Mateusza")
    parent_pattern = re.search(
        r'(?:córka|syn|dziecko)\s+(\w+)\s+i\s+(\w+)',
        title,
        re.IGNORECASE
    )
    if parent_pattern:
        parent1_name = parent_pattern.group(1).strip('.,')
        parent2_name = parent_pattern.group(2).strip('.,')

        # Determine genders from name endings
        parent1_gender = "female" if parent1_name.endswith(('y', 'i')) else ("male" if parent1_name.endswith('a') else "neutral")
        parent2_gender = "male" if parent2_name.endswith('a') else ("female" if parent2_name.endswith(('y', 'i')) else "neutral")

        # Polish genitive: Hanny (from Hanna), Mateusza (from Mateusz)
        # Try to convert from genitive to nominative
        def genitive_to_nominative(name: str) -> str:
            if name.endswith('y') or name.endswith('i'):
                # Hanny -> Hanna, Ani -> Ania
                return name[:-1] + 'a'
            elif name.endswith('a'):
                # Mateusza -> Mateusz, Tomasza -> Tomasz
                return name[:-1]
            return name

        parent1_nominative = genitive_to_nominative(parent1_name)
        parent2_nominative = genitive_to_nominative(parent2_name)

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
                        # Skip if already added from parent pattern
                        if not any(cn["name"] == next_word for cn in insights["character_names"]):
                            insights["character_names"].append({
                                "name": next_word,
                                "role": info["role"],
                                "gender": info["gender"]
                            })
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

                # Likely Polish name
                if not any(cn["name"] == word_clean for cn in insights["character_names"]):
                    # Determine role: if catalyst detected and this is the first name, it's likely the catalyst
                    char_role = "main"
                    if insights.get("catalyst_character_detected") and len(insights["character_names"]) == 0:
                        char_role = "catalyst"  # First character with age detected is the catalyst

                    insights["character_names"].append({
                        "name": word_clean,
                        "role": char_role,
                        "gender": "female" if word_clean.endswith("a") else "neutral"
                    })
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

    # Primary: semantic AI names, Fallback: keyword names
    suggested_names = char_implications.get("suggested_names", [])
    if not suggested_names and title_insights["character_names"]:
        suggested_names = [c["name"] for c in title_insights["character_names"]]

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
            # Basic fields (for backward compatibility)
            "character_names": [{"name": name, "role": "main", "gender": "neutral"} for name in suggested_names] if suggested_names else title_insights["character_names"],
            "themes": themes,
            "setting_hints": [world_setting_sem.get("type", "")] if world_setting_sem.get("type") else title_insights["setting_hints"],
            "tone": semantic_insights.get("emotional_core", title_insights["tone"]),
            "focus": "oparty na postaciach" if suggested_names else title_insights["focus"],
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

    FIXED (2026-01-25): Accurate estimation based on:
    - Polish text: ~1.5 tokens per word (not 1.33)
    - Scene-by-scene architecture: 5 scenes per chapter
    - Beat Sheet calls for Divine Prompt System
    - Proper input token accounting (context pack ~12K per scene)
    """
    chapter_count = ai_decisions.get("chapter_count", 25)
    target_words = ai_decisions.get("target_word_count", 90000)
    main_chars = ai_decisions.get("main_character_count", 5)
    supporting_chars = ai_decisions.get("supporting_character_count", 10)
    subplots = ai_decisions.get("subplot_count", 3)

    # Scene-by-scene architecture parameters
    SCENES_PER_CHAPTER = 5
    total_scenes = chapter_count * SCENES_PER_CHAPTER

    # Token estimation constants (Polish text)
    TOKENS_PER_WORD_POLISH = 1.5  # Polish inflection = more tokens

    # Context sizes per scene (input tokens)
    SYSTEM_PROMPT_TOKENS = 2000
    CONTEXT_PACK_TOKENS = 8000
    BEAT_SHEET_TOKENS = 500
    PREVIOUS_CONTENT_TOKENS = 500
    INPUT_PER_SCENE = SYSTEM_PROMPT_TOKENS + CONTEXT_PACK_TOKENS + BEAT_SHEET_TOKENS + PREVIOUS_CONTENT_TOKENS

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
            "estimated_tokens_in": 2000,
            "estimated_tokens_out": 4000,
        },
        {
            "step": 4,
            "name": "Kreacja Postaci Głównych",
            "task_type": "character_creation",
            "estimated_tokens_in": 2000 * main_chars,  # Each character needs full context
            "estimated_tokens_out": 3000 * main_chars,
        },
        {
            "step": 5,
            "name": "Kreacja Postaci Pobocznych",
            "task_type": "character_creation",
            "estimated_tokens_in": 1500 * supporting_chars,
            "estimated_tokens_out": 1500 * supporting_chars,
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
            "name": "Chapter Breakdown",
            "task_type": "plot_structure",
            "estimated_tokens_in": 3000,
            "estimated_tokens_out": 600 * chapter_count,
        },
        {
            "step": 9,
            "name": "Scene Detailing (Beat Sheets)",
            "task_type": "simple_outline",
            # Beat Sheet for each scene: ~2000 in, ~1500 out
            "estimated_tokens_in": 2000 * total_scenes,
            "estimated_tokens_out": 1500 * total_scenes,
        },
        {
            "step": 10,
            "name": "Pre-Writing Validation",
            "task_type": "validation",
            "estimated_tokens_in": 5000,
            "estimated_tokens_out": 2000,
        },
        {
            "step": 11,
            "name": "Prose Generation - Wszystkie Rozdziały",
            "task_type": "prose_writing",
            # FIXED: Scene-by-scene input + proper Polish token ratio
            "estimated_tokens_in": INPUT_PER_SCENE * total_scenes,
            "estimated_tokens_out": int(target_words * TOKENS_PER_WORD_POLISH),
        },
        {
            "step": 12,
            "name": "Continuity Check (wszystkie rozdziały)",
            "task_type": "validation",
            # RAG-based validation: ~2000 tokens per chapter
            "estimated_tokens_in": 2000 * chapter_count,
            "estimated_tokens_out": 500 * chapter_count,
        },
        {
            "step": 13,
            "name": "Style Polishing (sample chapters)",
            "task_type": "style_polish",
            # Style pass on ~20% of chapters (critical scenes)
            "estimated_tokens_in": int(target_words * 0.2 * TOKENS_PER_WORD_POLISH),
            "estimated_tokens_out": int(target_words * 0.05 * TOKENS_PER_WORD_POLISH),
        },
        {
            "step": 14,
            "name": "Genre Compliance Audit",
            "task_type": "validation",
            "estimated_tokens_in": 3000,
            "estimated_tokens_out": 1000,
        },
        {
            "step": 15,
            "name": "Final Assembly & Export",
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
