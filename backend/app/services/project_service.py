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

    prompt = f"""Analyze this book title DEEPLY for maximum creative impact: "{title}"

Genre: {genre}

🇵🇱 **KRYTYCZNIE WAŻNE - JĘZYK ODPOWIEDZI**:
WSZYSTKIE pola w JSON MUSZĄ być wypełnione PO POLSKU!
- core_meaning → po polsku
- themes → po polsku
- protagonist_archetype → po polsku (np. "Mag Ognia", "Wojownik", "Wybrany")
- ALL fields → POLISH language!

🎯 **YOUR MISSION**: Extract EVERY piece of creative information from this title.

🔍 **CRITICAL - GRAMMAR & CONTEXT AWARENESS**:
- In Polish: "Marksio, mag ognia" → "Marksio" is the protagonist NAME, "mag ognia" = fire mage (his role/class)
- In Polish: "Mateusz, Mag Ognia" → "Mateusz" is protagonist, "Mag Ognia" = Mage of Fire
- Comma often separates NAME from DESCRIPTION/TITLE
- Genitive case (dopełniacz): "ognia" = OF fire (not a name!)
- Analyze STRUCTURE: [Name], [Title/Role] [Details]

🚨 **MANDATORY - ALWAYS identify the protagonist**:
- Look for proper names (capitalized, personal names)
- The protagonist is usually the FIRST major name in the title
- If title format is "Name, Description" → Name is the protagonist
- Provide AT LEAST one suggested name based on title analysis

Provide COMPLETE analysis for ALL fields (W JĘZYKU POLSKIM!):

1. **Core Meaning**: What is this story about? (Full interpretation IN POLISH)
2. **Metaphors & Symbolism**: What symbols/metaphors are present? (IN POLISH)
3. **Emotional Core**: Primary emotion this title evokes (IN POLISH - np. "tęsknota", "determinacja", "tajemnica")
4. **Character Implications** (CRITICAL - ALWAYS FILL THIS IN POLISH):
   - protagonist_archetype: What type of hero? (PO POLSKU - np. "Mag Ognia", "Wojownik", "Wybrany")
   - protagonist_journey: What journey does the title suggest? (PO POLSKU)
   - suggested_names: [ALWAYS provide at least 1-3 names from title OR genre-appropriate names]
5. **World/Setting**: What world type, atmosphere, key elements? (PO POLSKU)
6. **Central Conflict**: What's the main struggle/tension? (PO POLSKU)
7. **Themes**: 3-5 deep themes to explore (PO POLSKU - np. "odkrywanie siebie", "potęga zapomnianej wiedzy")
8. **Promise to Reader**: What experience does this promise? (PO POLSKU)

Return JSON (FILL ALL FIELDS IN POLISH, no empty arrays):
{{
  "core_meaning": "Historia o...",
  "metaphors": ["metafora 1", "metafora 2"],
  "emotional_core": "tęsknota i determinacja",
  "character_implications": {{
    "protagonist_archetype": "Mag Ognia",
    "protagonist_journey": "Podróż protagonisty ku...",
    "suggested_names": ["Imię1", "Imię2"]
  }},
  "world_setting": {{
    "type": "fantasy",
    "atmosphere": "tajemnicza",
    "key_elements": ["element1", "element2"]
  }},
  "central_conflict": "Główny konflikt...",
  "themes": ["temat1", "temat2", "temat3"],
  "reader_promise": "Obietnica dla czytelnika..."
}}

Make this INSIGHTFUL and IN POLISH. This will drive the entire story creation."""

    try:
        response = await ai_service.generate(
            prompt=prompt,
            tier=ModelTier.TIER_2,  # Use good model for deep analysis
            temperature=0.7,
            max_tokens=2500,  # Increased for thorough analysis
            json_mode=True,
            metadata={"task": "semantic_title_analysis"}
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
            "metaphors": ["Podróż", "Transformacja"],
            "emotional_core": "przygoda" if genre == "fantasy" else "napięcie",
            "character_implications": {
                "protagonist_archetype": "Bohater" if genre == "fantasy" else "Protagonista",
                "protagonist_journey": f"Poszukiwanie prawdy przez {first_capitalized}",
                "suggested_names": [first_capitalized] if first_capitalized != "Bohater" else ["Aleksander", "Mateusz", "Kacper"]
            },
            "world_setting": {
                "type": f"Świat {genre_pl}",
                "atmosphere": "tajemnicza",
                "key_elements": ["konflikt", "odkrycie", "rozwój"]
            },
            "central_conflict": "Protagonista kontra nieznane",
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
            # Use AI-extracted data primarily
            "character_names": [{"name": name, "role": "main", "gender": "neutral"} for name in suggested_names] if suggested_names else title_insights["character_names"],
            "themes": themes,
            "setting_hints": [world_setting_sem.get("type", "")] if world_setting_sem.get("type") else title_insights["setting_hints"],
            "tone": semantic_insights.get("emotional_core", title_insights["tone"]),
            "focus": "oparty na postaciach" if suggested_names else title_insights["focus"],
            # NESTED: Full semantic analysis for agents
            "semantic_title_analysis": semantic_insights
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
            "estimated_tokens_in": 2000 * ai_decisions.get("chapter_count", 25),  # Context per chapter
            "estimated_tokens_out": (ai_decisions.get("target_word_count", 90000) / 0.75),  # Words to tokens ~1.33
        },
        {
            "step": 12,
            "name": "Continuity Check (wszystkie rozdziały)",
            "task_type": "validation",
            "estimated_tokens_in": 10000 * ai_decisions.get("chapter_count", 25) // 5,  # Sample checking
            "estimated_tokens_out": 500 * ai_decisions.get("chapter_count", 25),
        },
        {
            "step": 13,
            "name": "Style Polishing (wszystkie rozdziały)",
            "task_type": "style_polish",
            "estimated_tokens_in": (ai_decisions.get("target_word_count", 90000) / 0.75) * 1.1,
            "estimated_tokens_out": (ai_decisions.get("target_word_count", 90000) / 0.75) * 0.3,
        },
        {
            "step": 14,
            "name": "Genre Compliance Audit",
            "task_type": "validation",
            "estimated_tokens_in": 15000,
            "estimated_tokens_out": 3000,
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
