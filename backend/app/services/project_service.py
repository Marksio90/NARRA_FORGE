"""
Project service - core business logic for project management
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import logging
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

    prompt = f"""🎯 ADVANCED TITLE ANALYSIS - Extract MAXIMUM creative intelligence from: "{title}"

Genre: {genre}

🇵🇱 WSZYSTKIE pola w JSON MUSZĄ być PO POLSKU!

🔍 GRAMMAR: "Vergil, mag ognia" → "Vergil" = NAME, "mag ognia" = role/class

═════════════════════════════════════════════════════════════════
📚 PART 1: CULTURAL & MYTHOLOGICAL DEPTH
═════════════════════════════════════════════════════════════════

1. **Cultural/Literary References**: Does name reference mythology/history? (np. Vergil = Wergiliusz → epicka narracja, przewodnik)
2. **Symbolic Meanings**: Metafory beyond literal meaning
3. **Archetypal Significance**: Jakie archetypy są obecne?

═════════════════════════════════════════════════════════════════
🔥 PART 2: MAGIC/POWER SYSTEM (if applicable)
═════════════════════════════════════════════════════════════════

If title mentions powers:
- Element-based? (ogień, woda, etc.)
- Rare gift or common?
- Hierarchy (uczeń → mag → archimag)
- Costs of using magic (fizyczne/mentalne)
- Power dynamics (protagonist słaby czy potężny?)

═════════════════════════════════════════════════════════════════
🗺️ PART 3: DEEP SETTING ANALYSIS
═════════════════════════════════════════════════════════════════

1. **Physical & Historical**: Opis miejsca, co spowodowało ten stan?
2. **Emotional Landscape**: Dosłowne czy metaforyczne miejsce?
3. **Setting Role**: Antagonista/sojusznik/neutralne?
4. **Protagonist Relationship**: Uciec/zmienić/zrozumieć?

═════════════════════════════════════════════════════════════════
🎭 PART 4: TONE & MATURITY
═════════════════════════════════════════════════════════════════

- **Tone**: ciemny/neutralny/jasny
- **Maturity**: YA/Adult/Mature 16+/Mature 18+
- **Content**: violence level, moral complexity

═════════════════════════════════════════════════════════════════
👹 PART 5: ANTAGONIST PREDICTIONS
═════════════════════════════════════════════════════════════════

Based on protagonist, predict:
- Antagonist type (elemental opposite? tyrant? internal demon?)
- Opposition nature (physical/emotional/philosophical)

═════════════════════════════════════════════════════════════════
⚔️ PART 6: MULTI-LAYERED CONFLICTS
═════════════════════════════════════════════════════════════════

- External: vs world/villain
- Internal: vs self (fear, doubt)
- Philosophical: competing ideologies
- Moral: right action in impossible situation

═════════════════════════════════════════════════════════════════
🏷️ PART 7: SUBGENRE & READER EXPECTATIONS
═════════════════════════════════════════════════════════════════

- Subgenre: Epic Fantasy? Dark Fantasy? Character-driven?
- Magic level: High/Low magic
- Expected scenes (battles, training, political intrigue)
- Emotional journey readers expect

═════════════════════════════════════════════════════════════════
⏱️ PART 8: PACING & STRUCTURE
═════════════════════════════════════════════════════════════════

- Overall pace: fast/medium/slow
- Structure: 3-act? Hero's Journey?
- Which act should be darkest?

═════════════════════════════════════════════════════════════════
🧵 PART 9: SECONDARY PLOT THREADS
═════════════════════════════════════════════════════════════════

Suggest 3-5 subplots:
- Romance possibility
- Mentorship arc
- Political intrigue
- Mystery to uncover
- Redemption arc

═════════════════════════════════════════════════════════════════
📈 PART 10: CHARACTER ARC PREDICTION
═════════════════════════════════════════════════════════════════

- Starting point (emotional/skill state)
- Midpoint shift (major revelation)
- Climax challenge (ultimate test)
- Transformation (who they become)

═════════════════════════════════════════════════════════════════
📋 RETURN THIS JSON (ALL IN POLISH):
═════════════════════════════════════════════════════════════════

{{
  "core_meaning": "Pełna interpretacja...",
  "cultural_analysis": {{
    "mythological_references": ["Wergiliusz - przewodnik przez zaświaty", "Feniks - odrodzenie z ognia"],
    "cultural_context": "Odniesienia do klasycznej mitologii i epickich podróży",
    "symbolic_elements": ["ogień jako transformacja", "pustkowie jako izolacja"],
    "archetypal_patterns": ["Bohater odrzucony", "Mag poszukujący", "Podróż do ciemności"]
  }},
  "metaphors": ["zapomniany = odrzucony przez społeczeństwo", "ogień = niszcząca ale oczyszczająca moc"],
  "emotional_core": "samotność i poszukiwanie celu",
  "magic_system": {{
    "magic_type": "Elementarna magia ognia",
    "power_source": "Wewnętrzna energia emocjonalna",
    "limitations": "Wymaga kontroli emocji, niebezpieczna gdy niekontrolowana",
    "cost": "Fizyczne i mentalne wyczerpanie, ryzyko spalenia się od środka",
    "scope": "Od małych płomieni po niszczycielskie inferno"
  }},
  "setting_analysis": {{
    "environment": "Puste pustkowia, opuszczone tereny, izolacja",
    "time_period": "Nieokreślona fantastyczna era",
    "emotional_landscape": "Samotność, zapomnienie, odrzucenie",
    "setting_role": "Odzwierciedla stan wewnętrzny protagonisty",
    "protagonist_relationship": "Protagonista jest częścią pustkowia - zapomniany i odizolowany"
  }},
  "tone_and_maturity": {{
    "tone": "ciemny i melancholijny",
    "maturity_level": "Mature 16+",
    "violence_level": "średnia",
    "moral_complexity": "odcienie szarości",
    "emotional_intensity": "wysoka"
  }},
  "antagonist_predictions": [
    {{"type": "tyran krainy", "motivation": "utrzymać rozpacz", "opposition_nature": "fizyczna i filozoficzna"}}
  ],
  "conflicts": {{
    "external": "Vergil vs władca krainy",
    "internal": "kontrola nad ogniem i emocjami",
    "philosophical": "nadzieja vs rozpacz",
    "moral": "czy niszczyć ogniem dla dobra"
  }},
  "subgenre": {{
    "primary": "Dark Fantasy",
    "secondary": ["Epic Fantasy", "Character-driven"],
    "magic_level": "high magic",
    "focus": "character-driven"
  }},
  "reader_expectations": {{
    "expected_scenes": ["walka magią", "trening mocy", "emocjonalne przełomy"],
    "emotional_journey": "od rozpaczy do nadziei",
    "tropes": ["fallen hero", "magic training", "dark world redemption"]
  }},
  "pacing_suggestions": {{
    "overall_pace": "średnie",
    "structure_type": "Hero's Journey",
    "darkest_act": "akt 2",
    "tension_curve": "powolny wzrost do climaxu w akcie 2, wybuch w akcie 3"
  }},
  "secondary_plots": [
    {{"type": "romans", "description": "spotyka osobę dającą nadzieję", "key_characters": ["love interest"]}},
    {{"type": "mentorstwo", "description": "stary mag uczy kontroli", "key_characters": ["mentor"]}},
    {{"type": "tajemnica", "description": "co spowodowało rozpacz", "key_characters": ["ancient source"]}}
  ],
  "character_arc": {{
    "starting_point": "zagubiony mag ze słabą kontrolą",
    "midpoint_shift": "odkrywa prawdę o sobie i krainie",
    "climax_challenge": "musi użyć pełnej mocy by pokonać źródło rozpaczy",
    "transformation": "z zagubionego maga w beacon nadziei",
    "arc_type": "pozytywny"
  }},
  "character_implications": {{
    "protagonist_archetype": "Mag Ognia",
    "protagonist_journey": "od rozpaczy do nadziei poprzez opanowanie mocy",
    "suggested_names": ["Vergil"]
  }},
  "themes": ["odkrywanie siebie", "nadzieja w rozpaczy", "kontrola nad mocą", "transformacja poprzez cierpienie", "wybaczenie"],
  "reader_promise": "Epicka podróż od rozpaczy do nadziei z magią, emocjami i transformacją"
}}

Be COMPREHENSIVE. Fill EVERY field with rich, specific details."""

    try:
        response = await ai_service.generate(
            prompt=prompt,
            tier=ModelTier.TIER_2,  # Use good model for deep analysis
            temperature=0.7,
            max_tokens=6000,  # Increased for comprehensive advanced analysis
            json_mode=True,
            prefer_anthropic=True,  # Claude excellent at deep analysis
            metadata={"task": "advanced_title_analysis"}
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
                    insights["character_names"].append({
                        "name": word_clean,
                        "role": "main",
                        "gender": "female" if word_clean.endswith("a") else "neutral"
                    })
                if "Polska/Europa Wschodnia" not in insights["setting_hints"]:
                    insights["setting_hints"].append("Polska/Europa Wschodnia")

    # Generate title-based suggestions for AI decisions
    if insights["character_names"]:
        insights["title_suggestions"]["main_character_name"] = insights["character_names"][0]["name"]
        insights["title_suggestions"]["main_character_gender"] = insights["character_names"][0]["gender"]

        # If title has relationships, suggest family-focused plot
        if "family" in insights["themes"]:
            insights["title_suggestions"]["add_subplots"] = ["family_relationships", "generational_conflict"]
            insights["title_suggestions"]["character_count_modifier"] = 1  # Add one more main character for family member

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
    """
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
            "estimated_tokens_in": 1500,
            "estimated_tokens_out": 3000 * ai_decisions.get("main_character_count", 5),
        },
        {
            "step": 5,
            "name": "Kreacja Postaci Pobocznych",
            "task_type": "character_creation",
            "estimated_tokens_in": 1000,
            "estimated_tokens_out": 1500 * ai_decisions.get("supporting_character_count", 10),
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
            "estimated_tokens_in": 2000,
            "estimated_tokens_out": 3000 * ai_decisions.get("subplot_count", 3),
        },
        {
            "step": 8,
            "name": "Chapter Breakdown",
            "task_type": "plot_structure",
            "estimated_tokens_in": 2500,
            "estimated_tokens_out": 500 * ai_decisions.get("chapter_count", 25),
        },
        {
            "step": 9,
            "name": "Scene Detailing",
            "task_type": "simple_outline",
            "estimated_tokens_in": 2000,
            "estimated_tokens_out": 300 * ai_decisions.get("chapter_count", 25) * 3,  # ~3 scenes per chapter
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
            "estimated_tokens_in": 5000 * ai_decisions.get("chapter_count", 25),  # 500 system prompt + 4500 context per chapter
            "estimated_tokens_out": (ai_decisions.get("target_word_count", 90000) / 0.75),  # Words to tokens ~1.33
        },
        {
            "step": 12,
            "name": "Continuity Check (wszystkie rozdziały)",
            "task_type": "validation",
            "estimated_tokens_in": 100,  # Placeholder - not currently implemented with AI
            "estimated_tokens_out": 50,  # Placeholder - not currently implemented with AI
        },
        {
            "step": 13,
            "name": "Style Polishing (wszystkie rozdziały)",
            "task_type": "style_polish",
            "estimated_tokens_in": 100,  # Placeholder - currently done during generation
            "estimated_tokens_out": 50,  # Placeholder - currently done during generation
        },
        {
            "step": 14,
            "name": "Genre Compliance Audit",
            "task_type": "validation",
            "estimated_tokens_in": 100,  # Placeholder - not currently implemented with AI
            "estimated_tokens_out": 50,  # Placeholder - not currently implemented with AI
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
