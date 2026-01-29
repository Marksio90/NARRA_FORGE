# PLAN TRANSFORMACJI NARRAFORGE
## Platforma Generowania Książek na Poziomie Światowych Bestsellerów

**Wersja:** 2.0 QUANTUM LEAP
**Data:** 2026-01-29
**Cel:** Transformacja NarraForge w najzaawansowaną platformę AI do tworzenia literatury na świecie

---

# CZĘŚĆ I: WIZJA I FILOZOFIA

## 1.1 Manifest Platformy Jutra

NarraForge 2.0 to nie ewolucja - to rewolucja. Platforma, która:
- **Wyprzedza czas** - AI myśli o kontynuacjach zanim człowiek o nich pomyśli
- **Tworzy unikaty** - każdy tytuł = zupełnie nowa rzeczywistość literacka
- **Osiąga poziom bestsellerów** - jakość porównywalna z najlepszymi autorami świata
- **Jest multimodalna** - działa perfekcyjnie w każdym gatunku
- **Buduje uniwersa** - nie pojedyncze książki, ale całe światy z kontynuacjami

## 1.2 Kluczowe Zasady

```
ZASADA #1: ZERO POWTÓRZEŃ
Dwa różne tytuły NIGDY nie wygenerują podobnej książki.
Różne tytuły = różna ilość słów, bohaterów, lokacji, stylu.

ZASADA #2: TYTUŁ TO DNA
Tytuł zawiera w sobie całą książkę - AI musi to wyekstrahować.
Każdy wymiar analizy musi być odzwierciedlony w finalnym dziele.

ZASADA #3: JAKOŚĆ BESTSELLERA
Każde zdanie musi być warte przeczytania.
Czytelnik nie oderwie się od książki do ostatniej strony.

ZASADA #4: KONTEKST I KONTYNUACJA
Każda książka może mieć przeszłość i przyszłość.
System pamięta i buduje na tym, co stworzył.

ZASADA #5: UNIWERSALNOŚĆ DOSKONAŁOŚCI
Każdy gatunek - ten sam najwyższy poziom.
Fantasy, thriller, romans, religijne - wszystko na poziomie mistrzowskim.
```

---

# CZĘŚĆ II: ZAAWANSOWANA ANALIZA TYTUŁU

## 2.1 System TITAN (Title Intelligence & Transformation Analysis Network)

### Architektura 12-Wymiarowej Analizy

Każdy tytuł przechodzi przez 12 wymiarów analizy, które BEZPOŚREDNIO wpływają na parametry książki:

```python
class TITANAnalyzer:
    """
    12-wymiarowy system analizy tytułu.
    Każdy wymiar generuje konkretne parametry książki.
    """

    DIMENSIONS = {
        # WYMIAR 1: SEMANTYKA GŁĘBOKA
        "semantic_depth": {
            "description": "Wielowarstwowe znaczenia ukryte w tytule",
            "output": {
                "primary_meaning": str,      # Dosłowne znaczenie
                "secondary_meanings": List[str],  # Metafory, alegorie
                "hidden_symbols": List[str],  # Ukryte symbole
                "cultural_references": List[str],  # Odniesienia kulturowe
                "universal_themes": List[str],  # Tematy uniwersalne
            },
            "impact_on_book": {
                "thematic_layers": "Ilość warstw tematycznych (1-5)",
                "symbol_density": "Gęstość symboliki w tekście",
                "interpretation_depth": "Głębokość możliwych interpretacji"
            }
        },

        # WYMIAR 2: EMOCJONALNA REZONANCJA
        "emotional_resonance": {
            "description": "Jakie emocje wywołuje tytuł",
            "output": {
                "primary_emotion": str,       # Główna emocja
                "emotional_spectrum": List[str],  # Pełne spektrum
                "intensity_level": int,       # 1-10
                "catharsis_potential": str,   # Potencjał katarsis
                "reader_hook": str,           # Co przyciąga czytelnika
            },
            "impact_on_book": {
                "emotional_arc_complexity": "Złożoność łuku emocjonalnego",
                "tear_jerker_moments": "Ilość momentów wzruszających",
                "tension_peaks": "Ilość szczytów napięcia"
            }
        },

        # WYMIAR 3: TEMPORALNOŚĆ
        "temporality": {
            "description": "Wymiar czasowy zawarty w tytule",
            "output": {
                "time_period": str,           # Przeszłość/teraźniejszość/przyszłość
                "time_span": str,             # Jak długi okres obejmuje historia
                "temporal_complexity": str,    # Linearny/nielinearny/wielowątkowy
                "urgency_level": int,         # 1-10
                "nostalgia_factor": int,      # 1-10
            },
            "impact_on_book": {
                "chapter_time_jumps": "Czy i ile skoków czasowych",
                "flashback_frequency": "Ilość retrospekcji",
                "pacing_style": "Tempo narracji"
            }
        },

        # WYMIAR 4: PRZESTRZEŃ I ŚWIAT
        "spatial_world": {
            "description": "Geografia i świat sugerowany przez tytuł",
            "output": {
                "world_type": str,            # Realny/fantastyczny/mieszany
                "scale": str,                 # Intymny/lokalny/globalny/kosmiczny
                "location_hints": List[str],  # Sugestie lokalizacji
                "atmosphere": str,            # Atmosfera miejsca
                "world_uniqueness": int,      # 1-10 jak unikalny świat
            },
            "impact_on_book": {
                "locations_count": "Ilość unikalnych lokacji",
                "world_building_depth": "Głębokość budowania świata",
                "travel_narrative": "Czy jest motyw podróży"
            }
        },

        # WYMIAR 5: POSTACIE IMPLIKOWANE
        "implied_characters": {
            "description": "Postacie sugerowane przez tytuł",
            "output": {
                "protagonist_archetype": str,
                "antagonist_type": str,
                "relationship_dynamics": List[str],
                "character_count_suggestion": int,
                "ensemble_vs_solo": str,
            },
            "impact_on_book": {
                "main_characters": "Ilość głównych postaci",
                "supporting_cast": "Wielkość obsady drugoplanowej",
                "character_depth": "Głębokość charakteryzacji"
            }
        },

        # WYMIAR 6: KONFLIKT CENTRALNY
        "central_conflict": {
            "description": "Rodzaj konfliktu sugerowany przez tytuł",
            "output": {
                "conflict_type": str,         # Wewnętrzny/zewnętrzny/oba
                "conflict_scale": str,        # Osobisty/społeczny/kosmiczny
                "stakes_level": int,          # 1-10
                "moral_complexity": int,      # 1-10
                "resolution_type": str,       # Jednoznaczne/ambiwalentne
            },
            "impact_on_book": {
                "subplot_count": "Ilość wątków pobocznych",
                "conflict_layers": "Ilość warstw konfliktu",
                "climax_intensity": "Intensywność kulminacji"
            }
        },

        # WYMIAR 7: NARRACYJNA OBIETNICA
        "narrative_promise": {
            "description": "Co tytuł obiecuje czytelnikowi",
            "output": {
                "genre_signals": List[str],
                "reader_expectations": List[str],
                "hook_strength": int,         # 1-10
                "mystery_quotient": int,      # 1-10
                "satisfaction_type": str,     # Jaki rodzaj satysfakcji
            },
            "impact_on_book": {
                "twist_count": "Ilość zwrotów akcji",
                "mystery_depth": "Głębokość zagadki",
                "payoff_magnitude": "Wielkość wypłaty narracyjnej"
            }
        },

        # WYMIAR 8: STYL I TON
        "style_tone": {
            "description": "Styl i ton sugerowany przez tytuł",
            "output": {
                "formality_level": str,       # Formalny/nieformalny
                "prose_style": str,           # Poetycki/surowy/barokowy/minimalistyczny
                "humor_quotient": int,        # 0-10
                "darkness_level": int,        # 0-10
                "literary_ambition": int,     # 1-10
            },
            "impact_on_book": {
                "vocabulary_complexity": "Złożoność słownictwa",
                "sentence_structure": "Struktura zdań",
                "descriptive_density": "Gęstość opisów"
            }
        },

        # WYMIAR 9: PSYCHOLOGIA GŁĘBOKA
        "deep_psychology": {
            "description": "Psychologiczne warstwy w tytule",
            "output": {
                "psychological_themes": List[str],
                "trauma_indicators": List[str],
                "growth_arc_type": str,
                "shadow_work": str,           # Jungowskie cienie
                "collective_unconscious": List[str],
            },
            "impact_on_book": {
                "internal_monologue_depth": "Głębokość monologu wewnętrznego",
                "psychological_realism": "Realizm psychologiczny",
                "character_transformation": "Skala transformacji postaci"
            }
        },

        # WYMIAR 10: INTERTEKSTUALNOŚĆ
        "intertextuality": {
            "description": "Odniesienia do innych dzieł",
            "output": {
                "literary_echoes": List[str],  # Echa innych dzieł
                "mythological_roots": List[str],
                "archetypal_patterns": List[str],
                "genre_conventions": List[str],
                "subversion_potential": int,  # 1-10
            },
            "impact_on_book": {
                "homage_elements": "Elementy hołdu",
                "genre_innovation": "Innowacja gatunkowa",
                "meta_narrative": "Elementy metanarracyjne"
            }
        },

        # WYMIAR 11: KOMERCYJNY POTENCJAŁ
        "commercial_potential": {
            "description": "Potencjał rynkowy tytułu",
            "output": {
                "target_audience": List[str],
                "market_positioning": str,
                "series_potential": int,      # 1-10
                "adaptation_potential": str,  # Film/serial/gra
                "viral_hooks": List[str],
            },
            "impact_on_book": {
                "accessibility_level": "Poziom dostępności",
                "page_turner_quotient": "Współczynnik 'nie mogę odłożyć'",
                "sequel_setup": "Przygotowanie pod kontynuację"
            }
        },

        # WYMIAR 12: TRANSCENDENCJA
        "transcendence": {
            "description": "Wymiar duchowy i transcendentny",
            "output": {
                "spiritual_dimension": str,
                "existential_questions": List[str],
                "meaning_of_life_touch": int,  # 1-10
                "hope_vs_despair": str,
                "legacy_theme": str,
            },
            "impact_on_book": {
                "philosophical_depth": "Głębokość filozoficzna",
                "spiritual_journey": "Czy jest podróż duchowa",
                "redemption_arc": "Czy jest łuk odkupienia"
            }
        }
    }
```

## 2.2 Dynamiczny Generator Parametrów

Na podstawie 12 wymiarów, system generuje UNIKALNE parametry dla każdej książki:

```python
class DynamicBookParameters:
    """
    Parametry książki generowane dynamicznie na podstawie analizy TITAN.
    NIGDY dwie książki nie będą miały identycznych parametrów.
    """

    def generate_from_titan(self, titan_analysis: TITANAnalysis) -> BookParameters:
        return BookParameters(
            # PARAMETRY OBJĘTOŚCI (dynamiczne!)
            word_count=self._calculate_word_count(titan_analysis),
            # Może być od 40,000 do 200,000 słów w zależności od tytułu!

            chapter_count=self._calculate_chapters(titan_analysis),
            # Od 10 do 60 rozdziałów

            scenes_per_chapter=self._calculate_scenes(titan_analysis),
            # Od 2 do 8 scen na rozdział

            # PARAMETRY POSTACI (dynamiczne!)
            main_characters=self._calculate_main_chars(titan_analysis),
            # Od 1 do 12 głównych postaci

            supporting_characters=self._calculate_supporting(titan_analysis),
            # Od 3 do 50 postaci drugoplanowych

            character_depth_level=titan_analysis.deep_psychology.growth_arc_type,

            # PARAMETRY ŚWIATA (dynamiczne!)
            locations_count=self._calculate_locations(titan_analysis),
            # Od 1 do 100 lokacji

            world_building_pages=self._calculate_world_pages(titan_analysis),

            # PARAMETRY FABUŁY (dynamiczne!)
            subplot_count=titan_analysis.central_conflict.impact["subplot_count"],
            twist_count=titan_analysis.narrative_promise.impact["twist_count"],

            # PARAMETRY STYLU (dynamiczne!)
            prose_style=titan_analysis.style_tone.prose_style,
            vocabulary_level=titan_analysis.style_tone.impact["vocabulary_complexity"],

            # PARAMETRY EMOCJONALNE (dynamiczne!)
            emotional_intensity=titan_analysis.emotional_resonance.intensity_level,

            # PARAMETRY GEOGRAFICZNE (dynamiczne - nie zawsze Europa!)
            primary_location=self._determine_location(titan_analysis),
            # Może być: Azja, Afryka, Ameryka, wymyślony świat, kosmos...

            cultural_setting=self._determine_culture(titan_analysis),
            # Unikalna kultura dla każdej książki
        )

    def _calculate_word_count(self, titan: TITANAnalysis) -> int:
        """
        Dynamiczne obliczanie ilości słów na podstawie analizy.
        """
        base = 50000  # Minimum

        # Dodaj za złożoność emocjonalną
        base += titan.emotional_resonance.intensity_level * 5000

        # Dodaj za złożoność świata
        base += titan.spatial_world.world_uniqueness * 7000

        # Dodaj za ilość postaci implikowanych
        base += titan.implied_characters.character_count_suggestion * 3000

        # Dodaj za złożoność konfliktu
        base += titan.central_conflict.moral_complexity * 4000

        # Dodaj za ambicje literackie
        base += titan.style_tone.literary_ambition * 6000

        # Dodaj za głębię psychologiczną
        base += len(titan.deep_psychology.psychological_themes) * 2000

        # Zrandomizuj lekko (+/- 10%) dla unikalności
        variance = random.uniform(0.9, 1.1)

        return int(base * variance)
```

## 2.3 Automatyczna Kreacja Postaci z Tytułu

Jeśli tytuł nie zawiera explicite postaci, system je TWORZY:

```python
class AutoCharacterCreator:
    """
    Automatycznie tworzy postacie gdy nie są explicite w tytule.
    """

    async def create_characters_from_title(
        self,
        title: str,
        titan_analysis: TITANAnalysis,
        genre: GenreType
    ) -> List[Character]:

        prompt = f"""
        Na podstawie tytułu "{title}" i analizy:

        WYMIARY TYTUŁU:
        - Archetyp protagonisty: {titan_analysis.implied_characters.protagonist_archetype}
        - Typ antagonisty: {titan_analysis.implied_characters.antagonist_type}
        - Dynamika relacji: {titan_analysis.implied_characters.relationship_dynamics}
        - Sugerowana ilość postaci: {titan_analysis.implied_characters.character_count_suggestion}
        - Głębokość psychologiczna: {titan_analysis.deep_psychology}

        GATUNEK: {genre}

        Stwórz UNIKALNE postacie, które:
        1. Idealnie pasują do tego konkretnego tytułu
        2. Mają głęboką psychologię (WOUND, GHOST, LIE, WANT, NEED, FEAR)
        3. Mają unikalne imiona odpowiednie do kultury/świata
        4. Mają unikalne cechy fizyczne
        5. Mają unikalne maniery mówienia
        6. Są ze sobą powiązane siecią relacji

        NIE KOPIUJ z innych książek!
        Każda postać musi być ORYGINALNA i NIEZAPOMNIANA!

        LOKALIZACJA/KULTURA: {titan_analysis.spatial_world.location_hints}
        (Jeśli brak wskazówek - wybierz LOSOWĄ kulturę świata, nie domyślnie europejską!)
        """

        return await self.ai_service.generate_characters(prompt)
```

---

# CZĘŚĆ III: SYSTEM KONTYNUACJI I SERII

## 3.1 Universe Memory System (UMS)

```python
class UniverseMemorySystem:
    """
    System pamięci uniwersum - pamięta wszystko co zostało stworzone.
    Pozwala na kontynuacje i odniesienia do poprzednich dzieł.
    """

    def __init__(self):
        self.vector_store = PGVector()  # Embeddingi dla semantic search
        self.graph_db = Neo4j()         # Graf relacji między dziełami
        self.fact_store = PostgreSQL()  # Konkretne fakty

    async def store_universe(self, project: Project):
        """
        Zapisuje całe uniwersum książki do pamięci.
        """
        universe_data = {
            "world": await self._extract_world_facts(project),
            "characters": await self._extract_character_facts(project),
            "events": await self._extract_plot_facts(project),
            "timeline": await self._build_timeline(project),
            "relationships": await self._map_relationships(project),
            "locations": await self._catalog_locations(project),
            "rules": await self._extract_world_rules(project),
            "unresolved": await self._find_unresolved_threads(project),
        }

        # Zapisz do vector store (dla semantic search)
        await self.vector_store.upsert(
            namespace=f"universe_{project.id}",
            vectors=await self._embed_universe(universe_data)
        )

        # Zapisz do grafu (dla relacji)
        await self.graph_db.create_universe_graph(project.id, universe_data)

        # Zapisz fakty (dla precyzyjnych lookupów)
        await self.fact_store.store_facts(project.id, universe_data)

    async def suggest_continuations(self, project: Project) -> List[ContinuationSuggestion]:
        """
        Sugeruje możliwe kontynuacje na podstawie:
        - Nierozwiązanych wątków
        - Postaci z potencjałem rozwoju
        - Świata z nieodkrytymi obszarami
        - Czasów przed/po historii
        """
        unresolved = await self._find_unresolved_threads(project)

        suggestions = []

        # Typ 1: Kontynuacja bezpośrednia
        if unresolved.plot_threads:
            suggestions.append(ContinuationSuggestion(
                type="DIRECT_SEQUEL",
                title_suggestions=await self._generate_sequel_titles(project),
                description="Bezpośrednia kontynuacja - co dzieje się potem?",
                starting_point=unresolved.plot_threads[0],
                characters_to_continue=unresolved.character_arcs,
            ))

        # Typ 2: Prequel
        if project.world_bible.history.has_rich_past:
            suggestions.append(ContinuationSuggestion(
                type="PREQUEL",
                title_suggestions=await self._generate_prequel_titles(project),
                description="Historia przed historią - jak to się zaczęło?",
                time_period=project.world_bible.history.interesting_past_era,
            ))

        # Typ 3: Spin-off (inna postać)
        interesting_side_chars = await self._find_spinoff_worthy_characters(project)
        for char in interesting_side_chars:
            suggestions.append(ContinuationSuggestion(
                type="SPINOFF",
                title_suggestions=await self._generate_spinoff_titles(project, char),
                description=f"Historia {char.name} - ich własna przygoda",
                focus_character=char,
            ))

        # Typ 4: Ten sam świat, nowi bohaterowie
        if project.world_bible.world_richness > 7:
            suggestions.append(ContinuationSuggestion(
                type="SAME_WORLD_NEW_STORY",
                title_suggestions=await self._generate_same_world_titles(project),
                description="Ten sam fascynujący świat, zupełnie nowa historia",
                world_elements_to_reuse=project.world_bible.most_interesting_elements,
            ))

        # Typ 5: Alternatywna wersja
        suggestions.append(ContinuationSuggestion(
            type="WHAT_IF",
            title_suggestions=await self._generate_what_if_titles(project),
            description="Co by było gdyby? Alternatywna wersja wydarzeń",
            divergence_point=await self._find_best_divergence_point(project),
        ))

        return suggestions

    async def create_continuation(
        self,
        original_project: Project,
        continuation_type: str,
        new_title: str
    ) -> Project:
        """
        Tworzy kontynuację z pełnym kontekstem poprzedniej książki.
        """
        # Załaduj całe uniwersum oryginału
        universe = await self.load_universe(original_project.id)

        new_project = Project(
            title=new_title,
            genre=original_project.genre,
            series_id=original_project.series_id or await self._create_series(original_project),
            book_number_in_series=original_project.book_number_in_series + 1,

            # Przekaż kontekst!
            inherited_universe=universe,
            continuation_type=continuation_type,

            # Postaci do kontynuacji
            returning_characters=await self._select_returning_characters(
                universe, continuation_type
            ),

            # Świat do reużycia
            inherited_world=universe.world if continuation_type != "WHAT_IF" else None,
        )

        return new_project
```

## 3.2 Interfejs Biblioteki Dzieł

```typescript
// frontend/src/pages/Library.tsx

interface LibraryProps {}

const Library: React.FC<LibraryProps> = () => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [series, setSeries] = useState<Series[]>([]);
    const [viewMode, setViewMode] = useState<'grid' | 'timeline' | 'universe'>('grid');

    return (
        <div className="library-container">
            <h1>Twoja Biblioteka Światów</h1>

            {/* Przełącznik widoków */}
            <ViewModeSelector
                mode={viewMode}
                onChange={setViewMode}
                options={[
                    { id: 'grid', label: 'Siatka', icon: <GridIcon /> },
                    { id: 'timeline', label: 'Oś czasu', icon: <TimelineIcon /> },
                    { id: 'universe', label: 'Mapa uniwersów', icon: <GalaxyIcon /> },
                ]}
            />

            {viewMode === 'grid' && (
                <ProjectGrid
                    projects={projects}
                    onProjectClick={handleProjectClick}
                    onContinue={handleContinue}  // NOWY PRZYCISK!
                />
            )}

            {viewMode === 'timeline' && (
                <TimelineView
                    projects={projects}
                    series={series}
                    // Pokazuje chronologię tworzenia i w-świecie
                />
            )}

            {viewMode === 'universe' && (
                <UniverseMap
                    projects={projects}
                    series={series}
                    // Interaktywna mapa połączeń między książkami
                />
            )}

            {/* Panel kontynuacji */}
            <ContinuationPanel
                selectedProject={selectedProject}
                suggestions={continuationSuggestions}
                onCreateContinuation={handleCreateContinuation}
            />
        </div>
    );
};
```

---

# CZĘŚĆ IV: PODGLĄD NA ŻYWO I REAL-TIME EXPERIENCE

## 4.1 WebSocket Live Preview System

```python
# backend/app/services/live_preview_service.py

class LivePreviewService:
    """
    System podglądu na żywo tworzenia książki.
    Użytkownik widzi każde słowo w momencie generowania.
    """

    def __init__(self):
        self.websocket_manager = WebSocketManager()
        self.active_streams: Dict[str, AsyncGenerator] = {}

    async def stream_generation(
        self,
        project_id: str,
        websocket: WebSocket
    ):
        """
        Streamuje generowanie w czasie rzeczywistym.
        """
        await self.websocket_manager.connect(websocket, project_id)

        try:
            async for event in self.generation_events(project_id):
                await websocket.send_json({
                    "type": event.type,
                    "data": event.data,
                    "timestamp": event.timestamp
                })
        except WebSocketDisconnect:
            self.websocket_manager.disconnect(websocket, project_id)

    async def generation_events(self, project_id: str) -> AsyncGenerator[LiveEvent, None]:
        """
        Generator eventów dla live preview.
        """
        project = await self.get_project(project_id)

        # EVENT: Rozpoczęcie analizy tytułu
        yield LiveEvent(
            type="TITAN_ANALYSIS_START",
            data={"title": project.title, "message": "Analizuję głębię tytułu..."}
        )

        # Streamuj każdy wymiar analizy TITAN
        async for dimension in self.stream_titan_analysis(project):
            yield LiveEvent(
                type="TITAN_DIMENSION",
                data={
                    "dimension": dimension.name,
                    "result": dimension.result,
                    "impact": dimension.impact_preview
                }
            )

        # EVENT: Parametry wygenerowane
        yield LiveEvent(
            type="PARAMETERS_GENERATED",
            data={
                "word_count": project.parameters.word_count,
                "chapters": project.parameters.chapter_count,
                "characters": project.parameters.main_characters,
                "locations": project.parameters.locations_count,
                "message": f"Ta książka będzie miała {project.parameters.word_count:,} słów!"
            }
        )

        # EVENT: Tworzenie świata
        yield LiveEvent(type="WORLD_BUILDING_START", data={})
        async for world_chunk in self.stream_world_building(project):
            yield LiveEvent(
                type="WORLD_CHUNK",
                data={"content": world_chunk, "section": world_chunk.section}
            )

        # EVENT: Tworzenie postaci (KLUCZOWE!)
        yield LiveEvent(type="CHARACTER_CREATION_START", data={})
        async for character in self.stream_character_creation(project):
            yield LiveEvent(
                type="CHARACTER_BORN",
                data={
                    "name": character.name,
                    "role": character.role,
                    "portrait_prompt": character.visual_description,
                    "first_line": character.signature_phrase,
                    "psychology_preview": {
                        "wound": character.wound[:100] + "...",
                        "want": character.want,
                        "fear": character.fear
                    }
                }
            )

        # EVENT: Pisanie rozdziałów (najbardziej ekscytujące!)
        for chapter_num in range(1, project.parameters.chapter_count + 1):
            yield LiveEvent(
                type="CHAPTER_START",
                data={
                    "chapter": chapter_num,
                    "title": project.chapters[chapter_num].title,
                    "preview": project.chapters[chapter_num].hook
                }
            )

            # Streamuj każdą scenę
            for scene_num in range(1, project.chapters[chapter_num].scene_count + 1):
                yield LiveEvent(
                    type="SCENE_START",
                    data={"chapter": chapter_num, "scene": scene_num}
                )

                # STREAM SŁOWO PO SŁOWIE!
                async for word_batch in self.stream_scene_writing(project, chapter_num, scene_num):
                    yield LiveEvent(
                        type="PROSE_STREAM",
                        data={
                            "chapter": chapter_num,
                            "scene": scene_num,
                            "text": word_batch,  # ~10-20 słów na raz
                            "word_count_so_far": self.get_current_word_count(project)
                        }
                    )

                yield LiveEvent(
                    type="SCENE_COMPLETE",
                    data={
                        "chapter": chapter_num,
                        "scene": scene_num,
                        "word_count": scene.word_count,
                        "quality_score": scene.qa_score
                    }
                )

            yield LiveEvent(
                type="CHAPTER_COMPLETE",
                data={
                    "chapter": chapter_num,
                    "word_count": chapter.word_count,
                    "cliffhanger_rating": chapter.cliffhanger_strength
                }
            )

        # EVENT: Zakończenie
        yield LiveEvent(
            type="BOOK_COMPLETE",
            data={
                "total_words": project.total_word_count,
                "total_chapters": project.chapter_count,
                "generation_time": project.generation_duration,
                "quality_score": project.overall_quality_score,
                "continuation_suggestions": await self.get_continuation_suggestions(project)
            }
        )
```

## 4.2 Frontend Live Preview Component

```typescript
// frontend/src/components/LivePreview/LivePreview.tsx

interface LivePreviewProps {
    projectId: string;
}

const LivePreview: React.FC<LivePreviewProps> = ({ projectId }) => {
    const [currentPhase, setCurrentPhase] = useState<GenerationPhase>('idle');
    const [titanAnalysis, setTitanAnalysis] = useState<TITANDimension[]>([]);
    const [parameters, setParameters] = useState<BookParameters | null>(null);
    const [characters, setCharacters] = useState<Character[]>([]);
    const [currentChapter, setCurrentChapter] = useState<number>(0);
    const [liveText, setLiveText] = useState<string>('');
    const [stats, setStats] = useState<GenerationStats>({
        wordsWritten: 0,
        chaptersComplete: 0,
        currentQuality: 0
    });

    const textRef = useRef<HTMLDivElement>(null);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        // Połącz WebSocket
        ws.current = new WebSocket(`${WS_URL}/projects/${projectId}/live`);

        ws.current.onmessage = (event) => {
            const { type, data } = JSON.parse(event.data);

            switch (type) {
                case 'TITAN_ANALYSIS_START':
                    setCurrentPhase('analyzing');
                    break;

                case 'TITAN_DIMENSION':
                    setTitanAnalysis(prev => [...prev, data]);
                    break;

                case 'PARAMETERS_GENERATED':
                    setParameters(data);
                    setCurrentPhase('parameters_ready');
                    break;

                case 'CHARACTER_BORN':
                    setCharacters(prev => [...prev, data]);
                    // Animacja "narodzin" postaci!
                    animateCharacterBirth(data);
                    break;

                case 'CHAPTER_START':
                    setCurrentChapter(data.chapter);
                    setCurrentPhase('writing');
                    break;

                case 'PROSE_STREAM':
                    // Dodaj tekst z efektem pisania
                    setLiveText(prev => prev + data.text);
                    setStats(prev => ({
                        ...prev,
                        wordsWritten: data.word_count_so_far
                    }));
                    // Auto-scroll
                    scrollToBottom();
                    break;

                case 'CHAPTER_COMPLETE':
                    setStats(prev => ({
                        ...prev,
                        chaptersComplete: data.chapter
                    }));
                    // Efekt zakończenia rozdziału
                    celebrateChapterComplete(data);
                    break;

                case 'BOOK_COMPLETE':
                    setCurrentPhase('complete');
                    celebrateBookComplete(data);
                    break;
            }
        };

        return () => ws.current?.close();
    }, [projectId]);

    return (
        <div className="live-preview-container">
            {/* Panel statusu */}
            <StatusPanel phase={currentPhase} stats={stats} />

            {/* Analiza TITAN - wizualizacja 12 wymiarów */}
            {currentPhase === 'analyzing' && (
                <TITANVisualization dimensions={titanAnalysis} />
            )}

            {/* Parametry książki - animowane karty */}
            {parameters && (
                <ParametersDisplay
                    parameters={parameters}
                    animated={true}
                />
            )}

            {/* Galeria postaci - pojawiają się jedna po drugiej */}
            {characters.length > 0 && (
                <CharacterGallery
                    characters={characters}
                    showPsychology={true}
                />
            )}

            {/* GŁÓWNY PANEL - Live tekst */}
            <div className="live-text-panel">
                <div className="chapter-header">
                    Rozdział {currentChapter}
                </div>
                <div
                    ref={textRef}
                    className="live-text-content"
                    dangerouslySetInnerHTML={{ __html: formatLiveText(liveText) }}
                />
                <div className="typing-cursor" />
            </div>

            {/* Statystyki w czasie rzeczywistym */}
            <RealTimeStats
                wordsWritten={stats.wordsWritten}
                targetWords={parameters?.word_count || 0}
                chaptersComplete={stats.chaptersComplete}
                totalChapters={parameters?.chapter_count || 0}
                currentQuality={stats.currentQuality}
            />
        </div>
    );
};
```

## 4.3 Wizualizacja Analizy TITAN

```typescript
// frontend/src/components/LivePreview/TITANVisualization.tsx

const TITANVisualization: React.FC<{ dimensions: TITANDimension[] }> = ({ dimensions }) => {
    return (
        <div className="titan-visualization">
            <h2>Analiza Głębi Tytułu</h2>
            <p className="subtitle">12 wymiarów odkrywanych w czasie rzeczywistym</p>

            <div className="dimensions-wheel">
                {DIMENSION_NAMES.map((name, index) => {
                    const dimension = dimensions.find(d => d.name === name);
                    const isActive = dimension !== undefined;
                    const angle = (index / 12) * 360;

                    return (
                        <DimensionNode
                            key={name}
                            name={name}
                            angle={angle}
                            isActive={isActive}
                            data={dimension?.result}
                            impact={dimension?.impact_preview}
                        />
                    );
                })}

                {/* Centrum - tytuł */}
                <div className="titan-center">
                    <span className="title-text">{title}</span>
                </div>

                {/* Połączenia między wymiarami */}
                <DimensionConnections dimensions={dimensions} />
            </div>

            {/* Lista odkrytych wymiarów */}
            <div className="dimensions-list">
                {dimensions.map(dim => (
                    <DimensionCard
                        key={dim.name}
                        dimension={dim}
                        showAnimation={true}
                    />
                ))}
            </div>
        </div>
    );
};
```

---

# CZĘŚĆ V: GATUNEK RELIGIJNY

## 5.1 Definicja Gatunku

```python
# backend/app/config.py - NOWY GATUNEK

class GenreType(str, enum.Enum):
    SCI_FI = "sci-fi"
    FANTASY = "fantasy"
    THRILLER = "thriller"
    HORROR = "horror"
    ROMANCE = "romance"
    DRAMA = "drama"
    COMEDY = "comedy"
    MYSTERY = "mystery"
    RELIGIOUS = "religious"  # NOWY!


GENRE_CONFIGS = {
    # ... istniejące gatunki ...

    GenreType.RELIGIOUS: GenreConfig(
        name="Religijne",
        description="Literatura religijna oparta na prawdziwych kerygmatach, Piśmie Świętym, nauce Kościoła",
        min_word_count=60000,
        max_word_count=150000,
        default_chapter_count=30,
        narrative_structure="spiritual_journey",  # Nowa struktura!
        key_elements=[
            "Autentyczne cytaty z Pisma Świętego",
            "Odniesienia do encyklik papieskich",
            "Prawdziwe cuda kościelne (zatwierdzone)",
            "Nauka Ojców Kościoła",
            "Kerygmat - głoszenie Dobrej Nowiny",
            "Świadectwa wiary",
            "Duchowa transformacja bohatera",
            "Walka duchowa (nie fizyczna)",
            "Łaska i odkupienie",
            "Komunia z Bogiem"
        ],
        tone="reverent_yet_accessible",
        pacing="contemplative_with_moments_of_grace",

        # SPECJALNE ŹRÓDŁA
        required_sources=[
            "Biblia (Stary i Nowy Testament)",
            "Katechizm Kościoła Katolickiego",
            "Encykliki papieskie",
            "Pisma Ojców Kościoła",
            "Zatwierdzone cuda",
            "Żywoty świętych",
            "Dokumenty Soboru Watykańskiego II"
        ],

        # STRUKTURA NARRACYJNA
        narrative_beats=[
            "Życie przed wiarą / kryzys",
            "Pierwsze dotknięcie łaski",
            "Opór i wątpliwości",
            "Spotkanie z autentycznym świadectwem",
            "Ciemna noc duszy",
            "Punkt nawrócenia",
            "Próba wiary",
            "Pogłębienie relacji z Bogiem",
            "Misja / dzielenie się wiarą",
            "Owoce Ducha Świętego"
        ]
    )
}
```

## 5.2 Baza Wiedzy Religijnej

```python
# backend/app/knowledge/religious_knowledge_base.py

class ReligiousKnowledgeBase:
    """
    Baza wiedzy religijnej - TYLKO sprawdzone, autentyczne źródła.
    """

    # PISMO ŚWIĘTE
    SCRIPTURE = {
        "old_testament": {
            "books": [...],  # Lista ksiąg
            "key_passages": {
                "creation": "Rdz 1-2",
                "fall": "Rdz 3",
                "abraham_covenant": "Rdz 12, 15, 17",
                "exodus": "Wj 14",
                "ten_commandments": "Wj 20",
                "psalms_of_trust": ["Ps 23", "Ps 91", "Ps 121"],
                "suffering_servant": "Iz 53",
                "new_covenant_prophecy": "Jr 31:31-34",
                # ... setki kluczowych fragmentów
            }
        },
        "new_testament": {
            "gospels": {
                "birth_narratives": ["Mt 1-2", "Łk 1-2"],
                "sermon_on_mount": "Mt 5-7",
                "parables": [...],  # Wszystkie przypowieści
                "miracles": [...],  # Wszystkie cuda
                "passion_narrative": ["Mt 26-27", "Mk 14-15", "Łk 22-23", "J 18-19"],
                "resurrection": ["Mt 28", "Mk 16", "Łk 24", "J 20-21"],
            },
            "pauline_letters": {
                "justification_by_faith": "Rz 3-5",
                "love_hymn": "1 Kor 13",
                "resurrection_chapter": "1 Kor 15",
                "fruits_of_spirit": "Ga 5:22-23",
                "armor_of_god": "Ef 6:10-18",
                # ...
            }
        }
    }

    # ENCYKLIKI PAPIESKIE (wybrane, najważniejsze)
    ENCYCLICALS = {
        "leon_xiii": {
            "rerum_novarum": {
                "year": 1891,
                "topic": "Kwestia robotnicza",
                "key_teachings": [...]
            }
        },
        "pius_xi": {
            "mit_brennender_sorge": {
                "year": 1937,
                "topic": "Przeciw nazizmowi",
                "key_teachings": [...]
            }
        },
        "jan_pawel_ii": {
            "redemptor_hominis": {"year": 1979, "topic": "Odkupiciel człowieka"},
            "dives_in_misericordia": {"year": 1980, "topic": "O Bożym miłosierdziu"},
            "laborem_exercens": {"year": 1981, "topic": "O pracy ludzkiej"},
            "slavorum_apostoli": {"year": 1985, "topic": "Apostołowie Słowian"},
            "dominum_et_vivificantem": {"year": 1986, "topic": "O Duchu Świętym"},
            "redemptoris_mater": {"year": 1987, "topic": "O Matce Bożej"},
            "sollicitudo_rei_socialis": {"year": 1987, "topic": "Troska społeczna"},
            "redemptoris_missio": {"year": 1990, "topic": "O misyjności"},
            "centesimus_annus": {"year": 1991, "topic": "W stulecie Rerum novarum"},
            "veritatis_splendor": {"year": 1993, "topic": "O moralności"},
            "evangelium_vitae": {"year": 1995, "topic": "O życiu"},
            "ut_unum_sint": {"year": 1995, "topic": "O ekumenizmie"},
            "fides_et_ratio": {"year": 1998, "topic": "Wiara i rozum"},
            "ecclesia_de_eucharistia": {"year": 2003, "topic": "O Eucharystii"},
        },
        "benedykt_xvi": {
            "deus_caritas_est": {"year": 2005, "topic": "Bóg jest miłością"},
            "spe_salvi": {"year": 2007, "topic": "O nadziei"},
            "caritas_in_veritate": {"year": 2009, "topic": "Miłość w prawdzie"},
        },
        "franciszek": {
            "lumen_fidei": {"year": 2013, "topic": "Światło wiary"},
            "laudato_si": {"year": 2015, "topic": "O trosce o wspólny dom"},
            "amoris_laetitia": {"year": 2016, "topic": "O miłości w rodzinie"},
            "gaudete_et_exsultate": {"year": 2018, "topic": "O świętości"},
            "fratelli_tutti": {"year": 2020, "topic": "O braterstwie"},
        }
    }

    # ZATWIERDZONE CUDA (przykłady)
    APPROVED_MIRACLES = {
        "marian_apparitions": {
            "guadalupe": {
                "year": 1531,
                "location": "Meksyk",
                "approved": True,
                "key_elements": ["Tilma Juana Diego", "Obraz Matki Bożej", "Nawrócenia"],
            },
            "lourdes": {
                "year": 1858,
                "location": "Francja",
                "approved": True,
                "miracles_count": 70,  # Oficjalnie uznanych uzdrowień
                "key_elements": ["Bernadetta Soubirous", "Źródło", "Uzdrowienia"],
            },
            "fatima": {
                "year": 1917,
                "location": "Portugalia",
                "approved": True,
                "key_elements": ["Trzej pastuszkowie", "Tajemnice", "Cud słońca"],
            },
        },
        "eucharistic_miracles": {
            "lanciano": {
                "year": "VIII wiek",
                "location": "Włochy",
                "scientific_verification": True,
                "details": "Przemiana hostii w tkankę serca",
            },
            "buenos_aires": {
                "year": 1996,
                "location": "Argentyna",
                "scientific_verification": True,
            },
        },
        "incorrupt_bodies": [
            {"saint": "Bernadetta Soubirous", "died": 1879},
            {"saint": "Padre Pio", "died": 1968},
            {"saint": "Jan Vianney", "died": 1859},
            # ...
        ],
        "healing_miracles": {
            # Cuda beatyfikacyjne i kanonizacyjne
        }
    }

    # OJCOWIE KOŚCIOŁA
    CHURCH_FATHERS = {
        "apostolic_fathers": ["Klemens Rzymski", "Ignacy Antiocheński", "Polikarp"],
        "greek_fathers": ["Atanazy", "Bazyli Wielki", "Grzegorz z Nazjanzu", "Jan Chryzostom"],
        "latin_fathers": ["Ambroży", "Hieronim", "Augustyn", "Grzegorz Wielki"],
        "key_writings": {
            "augustyn": {
                "wyznania": "Autobiografia duchowa",
                "panstwo_boze": "Teologia historii",
            },
            "tomasz_z_akwinu": {
                "summa_theologiae": "Synteza teologii",
            }
        }
    }

    # ŚWIĘCI I ICH ŻYCIORYSY
    SAINTS = {
        # Baza życiorysów świętych z kluczowymi momentami
    }

    async def get_relevant_scripture(self, theme: str, context: str) -> List[ScriptureReference]:
        """Zwraca odpowiednie cytaty biblijne dla danego tematu."""
        pass

    async def get_relevant_teaching(self, topic: str) -> List[ChurchTeaching]:
        """Zwraca nauczanie Kościoła na dany temat."""
        pass

    async def get_relevant_miracle(self, context: str) -> Optional[ApprovedMiracle]:
        """Zwraca odpowiedni cud do kontekstu (tylko zatwierdzone!)."""
        pass

    async def verify_theological_accuracy(self, text: str) -> TheologicalVerification:
        """Sprawdza poprawność teologiczną tekstu."""
        pass
```

## 5.3 Agent Religijny

```python
# backend/app/agents/religious_content_agent.py

class ReligiousContentAgent(BaseAgent):
    """
    Specjalistyczny agent do tworzenia treści religijnych.
    Gwarantuje zgodność z nauczaniem Kościoła.
    """

    def __init__(self):
        super().__init__()
        self.knowledge_base = ReligiousKnowledgeBase()
        self.theological_validator = TheologicalValidator()

    async def generate_religious_scene(
        self,
        scene_outline: SceneOutline,
        context: ContextPack
    ) -> SceneContent:
        """
        Generuje scenę z treścią religijną.
        """
        # 1. Zidentyfikuj potrzebne elementy religijne
        religious_needs = await self._analyze_religious_needs(scene_outline)

        # 2. Pobierz odpowiednie źródła
        sources = await self._gather_sources(religious_needs)

        # 3. Generuj z głębokim kontekstem religijnym
        prompt = self._build_religious_prompt(scene_outline, sources, context)

        content = await self.ai_service.generate(
            prompt=prompt,
            tier=ModelTier.TIER_2,
            system_prompt=RELIGIOUS_SYSTEM_PROMPT
        )

        # 4. WALIDACJA TEOLOGICZNA
        validation = await self.theological_validator.validate(content)
        if not validation.is_valid:
            # Popraw błędy teologiczne
            content = await self._correct_theological_errors(content, validation.errors)

        # 5. Dodaj cytaty biblijne jeśli stosowne
        if religious_needs.scripture_opportunity:
            content = await self._integrate_scripture(content, sources.scripture)

        return SceneContent(
            text=content,
            sources_used=sources,
            theological_validation=validation
        )

    def _build_religious_prompt(
        self,
        scene: SceneOutline,
        sources: ReligiousSources,
        context: ContextPack
    ) -> str:
        return f"""
        Napisz scenę literatury religijnej, która:

        1. AUTENTYCZNOŚĆ DUCHOWA
        - Przedstawia autentyczne doświadczenie wiary
        - Unika taniego moralizatorstwa
        - Pokazuje PRAWDZIWĄ walkę duchową
        - Nie upraszcza trudnych pytań wiary

        2. ŹRÓDŁA DO WYKORZYSTANIA
        Pismo Święte:
        {self._format_scripture(sources.scripture)}

        Nauczanie Kościoła:
        {self._format_teaching(sources.church_teaching)}

        Świadectwa/Cuda (jeśli stosowne):
        {self._format_miracles(sources.miracles)}

        3. POSTAĆ I JEJ DROGA DUCHOWA
        {context.character_spiritual_state}

        4. SCENA DO NAPISANIA
        {scene.description}

        5. ZASADY:
        - Cytaty biblijne oznaczaj siglami (np. J 3,16)
        - Nie wymyślaj cudów - używaj tylko zatwierdzonych
        - Przedstawiaj wiarę jako RELACJĘ, nie zbiór zasad
        - Pokaż działanie łaski, ale i wolność człowieka
        - Unikaj sentymentalizmu - pisz z głębią
        - Bądź wierny Magisterium Kościoła

        6. TON
        - Pełen szacunku, ale nie sztywny
        - Dostępny dla każdego czytelnika
        - Poruszający serce, nie tylko intelekt
        """

RELIGIOUS_SYSTEM_PROMPT = """
Jesteś autorem literatury religijnej na najwyższym poziomie.

TWOJE ŹRÓDŁA (JEDYNE dozwolone):
- Pismo Święte (Biblia Tysiąclecia lub inna zatwierdzona)
- Katechizm Kościoła Katolickiego
- Encykliki i dokumenty papieskie
- Pisma Ojców Kościoła i Doktorów Kościoła
- Zatwierdzone cuda i objawienia
- Żywoty świętych (potwierdzone źródła)

NIGDY:
- Nie wymyślaj cudów
- Nie przekręcaj nauczania Kościoła
- Nie cytuj fałszywie Pisma Świętego
- Nie przedstawiaj herezji jako prawdy
- Nie trywializuj sakramentów
- Nie redukuj wiary do moralności

ZAWSZE:
- Pokaż miłosierdzie Boga
- Przedstaw wiarę jako relację z żywym Bogiem
- Uszanuj tajemnicę (nie wszystko da się wyjaśnić)
- Pisz z głębokim szacunkiem
- Dawaj nadzieję, nawet w ciemności

Twoje pisarstwo ma prowadzić czytelnika do spotkania z Bogiem,
nie tylko do wiedzy o Nim.
"""
```

---

# CZĘŚĆ VI: NAPRAWA WSZYSTKICH SŁABYCH PUNKTÓW

## 6.1 Naprawa Niedoszacowania Kosztów (KRYTYCZNE!)

```python
# backend/app/utils/cost_analysis_v2.py

class AccurateCostEstimator:
    """
    NOWY, dokładny estymator kosztów.
    Uwzględnia WSZYSTKIE koszty, nie tylko prose generation.
    """

    # POPRAWIONE współczynniki
    TOKENS_PER_WORD_POLISH = 1.6  # Polski = więcej tokenów (było 1.33)
    TOKENS_PER_WORD_ENGLISH = 1.3

    # Rzeczywiste koszty inputu per scena
    SCENE_INPUT_TOKENS = {
        "system_prompt": 2000,
        "context_pack": 4000,
        "beat_sheet": 1500,
        "previous_scene": 2000,
        "character_context": 2000,
        "world_context": 1500,
        "total": 13000  # Nie 5000!
    }

    # Koszty per krok
    STEP_COSTS = {
        "titan_analysis": {
            "calls": 12,  # 12 wymiarów
            "input_per_call": 500,
            "output_per_call": 1000,
            "tier": "TIER_1"
        },
        "world_building": {
            "calls": 1,
            "input": 3000,
            "output": 8000,
            "tier": "TIER_2"
        },
        "character_creation": {
            "calls_per_character": 1,
            "input": 2000,
            "output": 4000,
            "tier": "TIER_2"
        },
        "plot_architecture": {
            "calls": 1,
            "input": 5000,
            "output": 10000,
            "tier": "TIER_2"
        },
        "beat_sheet_per_scene": {
            "input": 2000,
            "output": 1500,
            "tier": "TIER_1"
        },
        "prose_per_scene": {
            "input": 13000,  # Rzeczywiste!
            "output": 1800,  # ~1200 słów * 1.5
            "tier": "TIER_2"
        },
        "qa_per_scene": {
            "input": 2500,
            "output": 500,
            "tier": "TIER_1"
        },
        "continuity_check": {
            "calls": 1,
            "input": 10000,
            "output": 2000,
            "tier": "TIER_1"
        }
    }

    def estimate_project_cost(
        self,
        parameters: BookParameters,
        include_margin: bool = True
    ) -> DetailedCostEstimate:
        """
        Dokładna estymacja kosztów projektu.
        """
        costs = {}

        # 1. Analiza TITAN
        titan = self.STEP_COSTS["titan_analysis"]
        costs["titan_analysis"] = self._calc_cost(
            titan["calls"] * titan["input_per_call"],
            titan["calls"] * titan["output_per_call"],
            titan["tier"]
        )

        # 2. World Building
        wb = self.STEP_COSTS["world_building"]
        costs["world_building"] = self._calc_cost(wb["input"], wb["output"], wb["tier"])

        # 3. Character Creation
        char = self.STEP_COSTS["character_creation"]
        total_chars = parameters.main_characters + parameters.supporting_characters
        costs["character_creation"] = self._calc_cost(
            char["input"] * total_chars,
            char["output"] * total_chars,
            char["tier"]
        )

        # 4. Plot Architecture
        plot = self.STEP_COSTS["plot_architecture"]
        costs["plot_architecture"] = self._calc_cost(plot["input"], plot["output"], plot["tier"])

        # 5. Scene Generation (NAJWIĘKSZY KOSZT!)
        total_scenes = parameters.chapter_count * parameters.scenes_per_chapter

        # Beat Sheets
        beat = self.STEP_COSTS["beat_sheet_per_scene"]
        costs["beat_sheets"] = self._calc_cost(
            beat["input"] * total_scenes,
            beat["output"] * total_scenes,
            beat["tier"]
        )

        # Prose Generation
        prose = self.STEP_COSTS["prose_per_scene"]
        costs["prose_generation"] = self._calc_cost(
            prose["input"] * total_scenes,
            prose["output"] * total_scenes,
            prose["tier"]
        )

        # QA
        qa = self.STEP_COSTS["qa_per_scene"]
        costs["quality_assurance"] = self._calc_cost(
            qa["input"] * total_scenes,
            qa["output"] * total_scenes,
            qa["tier"]
        )

        # 6. Continuity Check
        cont = self.STEP_COSTS["continuity_check"]
        costs["continuity_check"] = self._calc_cost(cont["input"], cont["output"], cont["tier"])

        # SUMA
        subtotal = sum(costs.values())

        # MARGINES BEZPIECZEŃSTWA (+20%)
        margin = subtotal * 0.20 if include_margin else 0

        total = subtotal + margin

        return DetailedCostEstimate(
            breakdown=costs,
            subtotal=subtotal,
            margin=margin,
            total=total,
            confidence_range={
                "min": total * 0.85,
                "max": total * 1.15
            },
            warnings=self._generate_warnings(parameters, total)
        )

    def _calc_cost(self, input_tokens: int, output_tokens: int, tier: str) -> float:
        """Oblicza koszt dla danej ilości tokenów."""
        prices = MODEL_PRICES[tier]
        input_cost = (input_tokens / 1_000_000) * prices["input"]
        output_cost = (output_tokens / 1_000_000) * prices["output"]
        return input_cost + output_cost

    def _generate_warnings(self, params: BookParameters, total: float) -> List[str]:
        """Generuje ostrzeżenia dla użytkownika."""
        warnings = []

        if total > 50:
            warnings.append(f"⚠️ Szacowany koszt (${total:.2f}) jest wysoki. Rozważ mniejszy zakres.")

        if params.word_count > 150000:
            warnings.append("⚠️ Bardzo długa książka - generowanie może potrwać 2+ godziny.")

        if params.main_characters > 10:
            warnings.append("⚠️ Duża ilość głównych postaci zwiększa ryzyko niespójności.")

        return warnings
```

## 6.2 System Auto-Repair dla Failed Chapters

```python
# backend/app/services/auto_repair_service.py

class AutoRepairService:
    """
    Automatyczna naprawa nieudanych generacji.
    NIGDY nie pozwól, by projekt upadł z powodu jednej sceny!
    """

    MAX_REPAIR_ATTEMPTS = 3

    async def generate_with_repair(
        self,
        scene: Scene,
        context: ContextPack,
        original_tier: ModelTier
    ) -> SceneResult:
        """
        Generuje scenę z automatyczną naprawą w razie problemów.
        """
        attempts = []

        for attempt in range(1, self.MAX_REPAIR_ATTEMPTS + 1):
            try:
                # Wybierz strategię na podstawie poprzednich prób
                strategy = self._select_strategy(attempt, attempts)

                result = await self._generate_scene(
                    scene=scene,
                    context=context,
                    strategy=strategy
                )

                # Walidacja wyniku
                validation = await self._validate_result(result)

                if validation.is_acceptable:
                    return SceneResult(
                        content=result,
                        attempts=attempt,
                        final_strategy=strategy,
                        quality_score=validation.score
                    )

                # Zapisz informacje o próbie
                attempts.append(AttemptInfo(
                    number=attempt,
                    strategy=strategy,
                    result_length=len(result),
                    validation=validation,
                    error=None
                ))

            except Exception as e:
                attempts.append(AttemptInfo(
                    number=attempt,
                    strategy=strategy,
                    error=str(e)
                ))

        # Wszystkie próby nieudane - użyj fallback
        return await self._generate_fallback(scene, context, attempts)

    def _select_strategy(
        self,
        attempt: int,
        previous_attempts: List[AttemptInfo]
    ) -> RepairStrategy:
        """
        Wybiera strategię naprawy na podstawie poprzednich prób.
        """
        if attempt == 1:
            return RepairStrategy(
                tier=ModelTier.TIER_2,
                context_size="full",
                temperature=0.7,
                approach="standard"
            )

        elif attempt == 2:
            # Uprość kontekst, zwiększ tier
            return RepairStrategy(
                tier=ModelTier.TIER_3,  # Upgrade do Claude Opus!
                context_size="simplified",
                temperature=0.6,
                approach="focused",
                additional_instructions="Skup się TYLKO na tej scenie. Ignoruj szczegóły."
            )

        elif attempt == 3:
            # Minimalistyczne podejście z najwyższym modelem
            return RepairStrategy(
                tier=ModelTier.TIER_3,
                context_size="minimal",
                temperature=0.5,
                approach="minimal",
                additional_instructions="""
                Napisz PROSTĄ wersję tej sceny.
                Maksymalnie 500 słów.
                Skup się na: kto, co, gdzie.
                """
            )

    async def _generate_fallback(
        self,
        scene: Scene,
        context: ContextPack,
        attempts: List[AttemptInfo]
    ) -> SceneResult:
        """
        Ostateczny fallback - generuje minimalną, ale funkcjonalną scenę.
        """
        fallback_prompt = f"""
        TRYB AWARYJNY - generacja minimalna.

        Scena {scene.number}: {scene.title}
        Cel: {scene.goal}
        Postacie: {', '.join(scene.characters)}

        Napisz KRÓTKĄ scenę (300-500 słów) która:
        1. Realizuje cel sceny
        2. Przesuwa fabułę do przodu
        3. Jest spójna z poprzednimi scenami

        NIE martw się o:
        - Bogate opisy
        - Głęboką psychologię
        - Perfekcyjny styl

        PRIORYTET: Funkcjonalność > Jakość
        """

        result = await self.ai_service.generate(
            prompt=fallback_prompt,
            tier=ModelTier.TIER_2,
            max_tokens=1000
        )

        return SceneResult(
            content=result,
            attempts=self.MAX_REPAIR_ATTEMPTS + 1,
            final_strategy="fallback",
            quality_score=60,  # Niższa ocena, ale działa
            is_fallback=True,
            fallback_reason="All repair attempts failed",
            requires_human_review=True
        )
```

## 6.3 Zaawansowany System Continuity z RAG

```python
# backend/app/services/continuity_rag_service.py

class ContinuityRAGService:
    """
    System ciągłości oparty na RAG (Retrieval-Augmented Generation).
    Wykrywa i naprawia sprzeczności w czasie rzeczywistym.
    """

    def __init__(self):
        self.vector_store = PGVector(
            connection_string=settings.DATABASE_URL,
            embedding_model="text-embedding-3-small"
        )
        self.fact_extractor = FactExtractor()

    async def initialize_for_project(self, project_id: str):
        """
        Inicjalizuje bazę wiedzy dla projektu.
        """
        # Stwórz namespace dla projektu
        await self.vector_store.create_namespace(f"project_{project_id}")

    async def extract_and_store_facts(
        self,
        project_id: str,
        content: str,
        source: str  # "world_bible", "character", "chapter_1", etc.
    ):
        """
        Ekstraktuje fakty z treści i zapisuje do wektora.
        """
        facts = await self.fact_extractor.extract(content)

        for fact in facts:
            embedding = await self._embed(fact.text)

            await self.vector_store.upsert(
                namespace=f"project_{project_id}",
                id=fact.id,
                vector=embedding,
                metadata={
                    "type": fact.type,  # character, location, event, rule, etc.
                    "source": source,
                    "entities": fact.entities,
                    "timestamp": fact.timestamp_in_story,
                    "confidence": fact.confidence
                }
            )

    async def check_consistency(
        self,
        project_id: str,
        new_content: str,
        source: str
    ) -> ConsistencyReport:
        """
        Sprawdza czy nowa treść jest spójna z istniejącymi faktami.
        """
        # Ekstraktuj fakty z nowej treści
        new_facts = await self.fact_extractor.extract(new_content)

        contradictions = []
        warnings = []

        for fact in new_facts:
            # Znajdź powiązane fakty w bazie
            related = await self._find_related_facts(project_id, fact)

            # Sprawdź sprzeczności
            for existing in related:
                contradiction = await self._check_contradiction(fact, existing)
                if contradiction:
                    contradictions.append(Contradiction(
                        new_fact=fact,
                        existing_fact=existing,
                        type=contradiction.type,
                        severity=contradiction.severity,
                        suggestion=contradiction.suggestion
                    ))

            # Sprawdź ostrzeżenia (potencjalne problemy)
            for existing in related:
                warning = await self._check_warning(fact, existing)
                if warning:
                    warnings.append(warning)

        return ConsistencyReport(
            is_consistent=len(contradictions) == 0,
            contradictions=contradictions,
            warnings=warnings,
            facts_added=len(new_facts),
            auto_fix_available=all(c.auto_fixable for c in contradictions)
        )

    async def auto_fix_contradictions(
        self,
        content: str,
        contradictions: List[Contradiction]
    ) -> str:
        """
        Automatycznie naprawia sprzeczności w treści.
        """
        fixed_content = content

        for contradiction in contradictions:
            if not contradiction.auto_fixable:
                continue

            fix_prompt = f"""
            NAPRAWA SPRZECZNOŚCI:

            ISTNIEJĄCY FAKT (KANONICZNY):
            {contradiction.existing_fact.text}
            Źródło: {contradiction.existing_fact.source}

            SPRZECZNOŚĆ W NOWYM TEKŚCIE:
            {contradiction.new_fact.text}

            TYP SPRZECZNOŚCI: {contradiction.type}

            TEKST DO NAPRAWY:
            {fixed_content}

            Popraw tekst tak, by był zgodny z kanonicznym faktem.
            Zachowaj styl i ton oryginału.
            Zmień TYLKO to, co jest konieczne.
            """

            fixed_content = await self.ai_service.generate(
                prompt=fix_prompt,
                tier=ModelTier.TIER_1
            )

        return fixed_content

    FACT_TYPES = {
        "character_appearance": {
            "description": "Wygląd postaci",
            "examples": ["Ma niebieskie oczy", "Jest wysoka", "Ma bliznę na policzku"],
            "immutable": True  # Nie może się zmienić
        },
        "character_trait": {
            "description": "Cecha charakteru",
            "examples": ["Jest odważna", "Boi się wysokości"],
            "immutable": False  # Może się zmienić z rozwojem postaci
        },
        "character_knowledge": {
            "description": "Co postać wie",
            "examples": ["Wie o zdradzie brata", "Nie zna prawdy o ojcu"],
            "immutable": False
        },
        "location_geography": {
            "description": "Geografia miejsca",
            "examples": ["Zamek stoi na wzgórzu", "Rzeka płynie na wschód"],
            "immutable": True
        },
        "world_rule": {
            "description": "Zasada świata",
            "examples": ["Magia wymaga krwi", "Smoki są wymarłe"],
            "immutable": True
        },
        "timeline_event": {
            "description": "Wydarzenie w czasie",
            "examples": ["Wojna skończyła się 10 lat temu", "Spotkali się w środę"],
            "immutable": True
        },
        "relationship": {
            "description": "Relacja między postaciami",
            "examples": ["Są braćmi", "Nienawidzą się"],
            "immutable": False
        },
        "object_state": {
            "description": "Stan obiektu",
            "examples": ["Miecz jest złamany", "Klucz jest u Anny"],
            "immutable": False
        }
    }
```

## 6.4 Model Fallback Strategy

```python
# backend/app/services/model_fallback_service.py

class ModelFallbackService:
    """
    Automatyczny fallback między providerami AI.
    Jeśli OpenAI padnie - przełącz na Anthropic i vice versa.
    """

    PROVIDER_PRIORITY = [
        ("openai", "gpt-4o"),
        ("anthropic", "claude-sonnet-4-5-20251101"),
        ("openai", "gpt-4-turbo"),
        ("anthropic", "claude-opus-4-5-20251101"),
        ("openai", "gpt-4o-mini"),  # Last resort
    ]

    def __init__(self):
        self.provider_status: Dict[str, ProviderStatus] = {}
        self.last_health_check: datetime = None

    async def generate_with_fallback(
        self,
        prompt: str,
        preferred_tier: ModelTier,
        **kwargs
    ) -> AIResponse:
        """
        Generuje z automatycznym fallbackiem.
        """
        providers_to_try = self._get_providers_for_tier(preferred_tier)

        last_error = None

        for provider, model in providers_to_try:
            # Sprawdź status providera
            if self._is_provider_down(provider):
                continue

            try:
                response = await self._call_provider(
                    provider=provider,
                    model=model,
                    prompt=prompt,
                    **kwargs
                )

                # Sukces - zaznacz provider jako zdrowy
                self._mark_provider_healthy(provider)

                return response

            except RateLimitError as e:
                # Rate limit - poczekaj lub przełącz
                if e.retry_after and e.retry_after < 60:
                    await asyncio.sleep(e.retry_after)
                    continue
                else:
                    self._mark_provider_rate_limited(provider, e.retry_after)
                    last_error = e

            except ProviderUnavailableError as e:
                # Provider niedostępny - przełącz
                self._mark_provider_down(provider)
                last_error = e

            except Exception as e:
                last_error = e
                continue

        # Wszystkie providery zawiodły
        raise AllProvidersFailedError(
            message="Wszystkie providery AI są niedostępne",
            last_error=last_error,
            tried_providers=[p[0] for p in providers_to_try]
        )

    def _is_provider_down(self, provider: str) -> bool:
        """Sprawdza czy provider jest oznaczony jako niedostępny."""
        status = self.provider_status.get(provider)
        if not status:
            return False

        if status.is_down:
            # Sprawdź czy minął czas karencji
            if datetime.now() > status.retry_after:
                status.is_down = False
                return False
            return True

        return False

    def _mark_provider_down(self, provider: str):
        """Oznacza provider jako niedostępny."""
        self.provider_status[provider] = ProviderStatus(
            is_down=True,
            retry_after=datetime.now() + timedelta(minutes=5),
            failure_count=self.provider_status.get(provider, ProviderStatus()).failure_count + 1
        )

        # Log for monitoring
        logger.warning(f"Provider {provider} marked as DOWN. Retry after 5 minutes.")

    async def health_check_all_providers(self):
        """Sprawdza status wszystkich providerów."""
        for provider, model in self.PROVIDER_PRIORITY:
            try:
                await self._call_provider(
                    provider=provider,
                    model=model,
                    prompt="Hello",
                    max_tokens=5
                )
                self._mark_provider_healthy(provider)
            except Exception:
                self._mark_provider_down(provider)

        self.last_health_check = datetime.now()
```

## 6.5 Poprawki Frontendu - WebSocket Integration

```typescript
// frontend/src/hooks/useProjectWebSocket.ts

import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketMessage {
    type: string;
    data: any;
    timestamp: number;
}

export const useProjectWebSocket = (projectId: string) => {
    const ws = useRef<WebSocket | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
    const [connectionError, setConnectionError] = useState<string | null>(null);

    const reconnectAttempts = useRef(0);
    const maxReconnectAttempts = 5;

    const connect = useCallback(() => {
        if (ws.current?.readyState === WebSocket.OPEN) return;

        const wsUrl = `${process.env.REACT_APP_WS_URL}/ws/projects/${projectId}`;
        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            setIsConnected(true);
            setConnectionError(null);
            reconnectAttempts.current = 0;
            console.log('WebSocket connected');
        };

        ws.current.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                setLastMessage({
                    ...message,
                    timestamp: Date.now()
                });
            } catch (e) {
                console.error('Failed to parse WebSocket message:', e);
            }
        };

        ws.current.onerror = (error) => {
            console.error('WebSocket error:', error);
            setConnectionError('Błąd połączenia WebSocket');
        };

        ws.current.onclose = (event) => {
            setIsConnected(false);

            // Auto-reconnect z exponential backoff
            if (reconnectAttempts.current < maxReconnectAttempts) {
                const delay = Math.pow(2, reconnectAttempts.current) * 1000;
                reconnectAttempts.current++;

                console.log(`Reconnecting in ${delay}ms...`);
                setTimeout(connect, delay);
            } else {
                setConnectionError('Nie można połączyć się z serwerem. Odśwież stronę.');
            }
        };
    }, [projectId]);

    const disconnect = useCallback(() => {
        if (ws.current) {
            ws.current.close();
            ws.current = null;
        }
    }, []);

    const sendMessage = useCallback((message: object) => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(message));
        }
    }, []);

    useEffect(() => {
        connect();
        return () => disconnect();
    }, [connect, disconnect]);

    return {
        isConnected,
        lastMessage,
        connectionError,
        sendMessage,
        reconnect: connect
    };
};
```

---

# CZĘŚĆ VII: SYSTEM JAKOŚCI NA POZIOMIE BESTSELLERÓW

## 7.1 Bestseller Quality Engine

```python
# backend/app/services/bestseller_quality_engine.py

class BestsellerQualityEngine:
    """
    System zapewniający jakość na poziomie bestsellerów.
    Analizuje tekst pod kątem cech wspólnych dla najlepszych książek.
    """

    BESTSELLER_CRITERIA = {
        # 1. HOOK - Pierwsze zdanie/akapit
        "opening_hook": {
            "weight": 0.15,
            "criteria": [
                "Intrygujące pierwsze zdanie",
                "Natychmiastowe wprowadzenie napięcia",
                "Unikalne, zapadające w pamięć otwarcie",
                "Brak kliszowych otwarć (ciemna burzowa noc...)"
            ]
        },

        # 2. PAGE-TURNER FACTOR
        "page_turner": {
            "weight": 0.20,
            "criteria": [
                "Każdy rozdział kończy się hakiem",
                "Stałe podnoszenie stawek",
                "Nierozwiązane pytania utrzymują napięcie",
                "Tempo nie pozwala odłożyć książki"
            ]
        },

        # 3. CHARACTER DEPTH
        "character_depth": {
            "weight": 0.20,
            "criteria": [
                "Postacie mają głębokie wewnętrzne konflikty",
                "Każda główna postać ma unikalne WANT/NEED",
                "Postacie zmieniają się przez historię",
                "Czytelnik czuje empatię z postaciami",
                "Antagonista ma zrozumiałe motywacje"
            ]
        },

        # 4. EMOTIONAL RESONANCE
        "emotional_resonance": {
            "weight": 0.15,
            "criteria": [
                "Historia wywołuje silne emocje",
                "Momenty katarsis są dobrze przygotowane",
                "Emocjonalne szczyty i doliny są zbalansowane",
                "Czytelnik czuje się poruszony"
            ]
        },

        # 5. PROSE QUALITY
        "prose_quality": {
            "weight": 0.15,
            "criteria": [
                "Show don't tell",
                "Unikalne metafory i porównania",
                "Brak filter words (czuł że, widział że)",
                "Naturalny dialog z subtelnym subtekstem",
                "Sensory details (5 zmysłów)"
            ]
        },

        # 6. THEMATIC DEPTH
        "thematic_depth": {
            "weight": 0.10,
            "criteria": [
                "Historia ma głębsze znaczenie",
                "Tematy są subtealnie wplecione",
                "Uniwersalne prawdy o ludzkiej naturze",
                "Wielowarstwowa interpretacja"
            ]
        },

        # 7. ORIGINALITY
        "originality": {
            "weight": 0.05,
            "criteria": [
                "Unikalna premisa lub twist",
                "Świeże podejście do gatunku",
                "Zaskakujące, ale logiczne rozwiązania",
                "Własny głos autora"
            ]
        }
    }

    async def analyze_quality(
        self,
        content: str,
        genre: GenreType,
        context: Optional[Dict] = None
    ) -> BestsellerQualityReport:
        """
        Kompleksowa analiza jakości pod kątem bestsellerów.
        """
        scores = {}

        for criterion_name, criterion in self.BESTSELLER_CRITERIA.items():
            score = await self._evaluate_criterion(
                content=content,
                criterion=criterion,
                genre=genre
            )
            scores[criterion_name] = CriterionScore(
                name=criterion_name,
                score=score.value,
                weight=criterion["weight"],
                weighted_score=score.value * criterion["weight"],
                feedback=score.feedback,
                improvements=score.improvements
            )

        total_score = sum(s.weighted_score for s in scores.values())

        # Określ poziom jakości
        quality_level = self._determine_quality_level(total_score)

        return BestsellerQualityReport(
            total_score=total_score,
            quality_level=quality_level,
            criteria_scores=scores,
            strengths=self._identify_strengths(scores),
            weaknesses=self._identify_weaknesses(scores),
            improvement_priority=self._prioritize_improvements(scores),
            bestseller_potential=self._calculate_bestseller_potential(total_score, genre)
        )

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Określa poziom jakości na podstawie wyniku."""
        if score >= 90:
            return QualityLevel.MASTERPIECE
        elif score >= 80:
            return QualityLevel.BESTSELLER
        elif score >= 70:
            return QualityLevel.PROFESSIONAL
        elif score >= 60:
            return QualityLevel.COMPETENT
        else:
            return QualityLevel.NEEDS_WORK

    async def improve_to_bestseller(
        self,
        content: str,
        quality_report: BestsellerQualityReport,
        max_iterations: int = 3
    ) -> ImprovedContent:
        """
        Iteracyjnie ulepsza tekst do poziomu bestsellera.
        """
        current_content = content
        current_score = quality_report.total_score
        iterations = []

        for i in range(max_iterations):
            if current_score >= 85:  # Cel: poziom bestsellera
                break

            # Znajdź największą słabość
            weakest = quality_report.improvement_priority[0]

            # Ulepsz w tym obszarze
            improved = await self._improve_criterion(
                content=current_content,
                criterion=weakest,
                feedback=quality_report.criteria_scores[weakest].feedback
            )

            # Re-evaluate
            new_report = await self.analyze_quality(improved, genre)

            iterations.append(ImprovementIteration(
                iteration=i + 1,
                focus=weakest,
                score_before=current_score,
                score_after=new_report.total_score,
                improvement=new_report.total_score - current_score
            ))

            current_content = improved
            current_score = new_report.total_score
            quality_report = new_report

        return ImprovedContent(
            original=content,
            improved=current_content,
            original_score=quality_report.total_score,
            final_score=current_score,
            iterations=iterations,
            quality_level=self._determine_quality_level(current_score)
        )
```

## 7.2 Genre-Specific Excellence Prompts

```python
# backend/app/prompts/excellence_prompts.py

GENRE_EXCELLENCE_PROMPTS = {
    GenreType.FANTASY: """
    FANTASY EXCELLENCE STANDARDS:

    WORLD-BUILDING:
    - Magia musi mieć KOSZTY i OGRANICZENIA (hard magic)
    - Każda kultura ma unikalną historię, język, zwyczaje
    - Geografia wpływa na politykę i konflikty
    - Ekosystem jest spójny i logiczny

    POSTACIE:
    - Bohater ma wady, które naprawdę szkodzą
    - Mentor nie rozwiązuje problemów za bohatera
    - Złoczyńca wierzy w słuszność swoich działań
    - Poboczne postacie mają własne cele

    FABUŁA:
    - Stawki rosną ORGANICZNIE, nie sztucznie
    - Każda bitwa ma konsekwencje
    - Magia nie jest deus ex machina
    - Zwycięstwo wymaga POŚWIĘCENIA

    STYL:
    - Opisy świata przez oczy postaci, nie wykłady
    - Akcja jest klarowna przestrzennie
    - Dialog ujawnia charakter i konflikt
    - Poetyckie momenty w właściwych miejscach
    """,

    GenreType.THRILLER: """
    THRILLER EXCELLENCE STANDARDS:

    NAPIĘCIE:
    - Rozpocznij IN MEDIA RES lub z silnym hakiem
    - Każda scena podnosi stawki
    - Tykający zegar - deadline jest realny
    - Red herrings są fair play (możliwe do odgadnięcia)

    PROTAGONISTA:
    - Ma specyficzne umiejętności, ale i SŁABOŚCI
    - Osobiste stawki + zewnętrzne stawki
    - Musi dokonywać MORALNIE TRUDNYCH wyborów
    - Trauma z przeszłości wpływa na decyzje

    ANTAGONISTA:
    - Jest o krok przed bohaterem (do kulminacji)
    - Ma logiczne motywacje (nie "bo jest zły")
    - Stanowi OSOBISTE zagrożenie dla bohatera
    - Zdolny do zaskakujących, ale logicznych posunięć

    STRUKTURA:
    - Cliffhangery na końcu rozdziałów
    - Przeplatanie wątków dla max napięcia
    - Fałszywe kulminacje przed prawdziwą
    - Rozwiązanie jest satysfakcjonujące ale nie przewidywalne
    """,

    GenreType.ROMANCE: """
    ROMANCE EXCELLENCE STANDARDS:

    CHEMIA:
    - Napięcie seksualne/romantyczne od pierwszego spotkania
    - Przeszkody są WEWNĘTRZNE, nie tylko zewnętrzne
    - Momenty intymności (niekoniecznie fizycznej)
    - Dialogi z subtekstem

    PROTAGONIŚCI:
    - Oboje mają pełne życie POZA związkiem
    - Każde ma "lie" do pokonania
    - Wzajemnie się ZMIENIAJĄ na lepsze
    - Mają chemię słowną (banter)

    STRUKTURA:
    - Meet cute lub intrygujące poznanie
    - Rosnąca bliskość mimo przeszkód
    - "Dark moment" gdy wszystko wydaje się stracone
    - Grand gesture + HEA/HFN

    EMOCJE:
    - Czytelnik KIBICUJE parze
    - Momenty słodkie, gorące i bolesne
    - Vulnerability obu stron
    - Cathartic payoff
    """,

    GenreType.HORROR: """
    HORROR EXCELLENCE STANDARDS:

    ATMOSFERA:
    - Dread > Jump scares
    - Sugestia > Explicitność
    - Normalne staje się dziwne
    - Cisza jest przerażająca

    PROTAGONISTA:
    - Ma coś do stracenia (family, sanity, life)
    - Decyzje są ZROZUMIAŁE (nie "idiotka idzie do piwnicy")
    - Strach jest RELATABLE
    - Walczy, nie jest tylko ofiarą

    ZAGROŻENIE:
    - Zasady są SPÓJNE (nawet jeśli nieznane)
    - Pokazuj mało, sugeruj dużo
    - Realny koszt dla bohaterów
    - Niekoniecznie pokonane na końcu

    PSYCHOLOGIA:
    - Lęki uniwersalne (śmierć, samotność, utrata kontroli)
    - Paranoja czytelnika
    - Granica realność/koszmaro zamazana
    - Końcówka pozostawia niepokój
    """,

    GenreType.RELIGIOUS: """
    RELIGIOUS LITERATURE EXCELLENCE STANDARDS:

    AUTENTYCZNOŚĆ DUCHOWA:
    - Wiara jako RELACJA, nie zbiór zasad
    - Wątpliwości są naturalne i pokazane
    - Łaska jest darem, nie nagrodą za zasługi
    - Nawrócenie to proces, nie moment

    POSTACIE:
    - Święci mieli słabości - pokazuj je
    - Grzesznicy mają godność - szanuj ją
    - Bóg działa przez ludzi, nie ZAMIAST nich
    - Ciemna noc duszy jest konieczna

    TEOLOGIA:
    - Zgodność z Magisterium
    - Cytaty biblijne w kontekście
    - Nauczanie przez historię, nie kazania
    - Tajemnica pozostaje tajemnicą

    TON:
    - Nadzieja nawet w ciemności
    - Szacunek bez sztywności
    - Radość wiary, nie tylko obowiązki
    - Miłosierdzie > Osąd
    """
}
```

## 7.3 Multi-Pass Quality Enhancement

```python
# backend/app/services/multi_pass_enhancement.py

class MultiPassQualityEnhancement:
    """
    Wieloprzebiegowe ulepszanie tekstu do najwyższej jakości.
    Każdy przebieg skupia się na innym aspekcie.
    """

    ENHANCEMENT_PASSES = [
        {
            "name": "STRUCTURE_PASS",
            "focus": "Struktura narracyjna i pacing",
            "checks": [
                "Czy każda scena ma cel?",
                "Czy napięcie rośnie?",
                "Czy są zbędne fragmenty?",
                "Czy przejścia są płynne?"
            ]
        },
        {
            "name": "CHARACTER_PASS",
            "focus": "Głębia postaci i dialog",
            "checks": [
                "Czy postacie są spójne?",
                "Czy dialog jest naturalny?",
                "Czy każda postać ma unikaty głos?",
                "Czy motywacje są jasne?"
            ]
        },
        {
            "name": "PROSE_PASS",
            "focus": "Jakość prozy i styl",
            "checks": [
                "Eliminacja filter words",
                "Show don't tell",
                "Unikanie klisz",
                "Rytm zdań"
            ]
        },
        {
            "name": "SENSORY_PASS",
            "focus": "Opisy zmysłowe i immersja",
            "checks": [
                "Wszystkie 5 zmysłów?",
                "Czy czytelnik 'widzi' scenę?",
                "Czy opisy są przez POV?",
                "Czy są unikalne detale?"
            ]
        },
        {
            "name": "EMOTIONAL_PASS",
            "focus": "Rezonans emocjonalny",
            "checks": [
                "Czy sceny wzruszają?",
                "Czy napięcie jest odczuwalne?",
                "Czy momenty radości działają?",
                "Czy katharsis jest przygotowana?"
            ]
        },
        {
            "name": "POLISH_PASS",
            "focus": "Finalne szlify",
            "checks": [
                "Gramatyka i interpunkcja",
                "Powtórzenia słów",
                "Konsystencja stylu",
                "Finalne dopieszczenie"
            ]
        }
    ]

    async def enhance_chapter(
        self,
        chapter_content: str,
        context: ChapterContext,
        target_quality: float = 85.0
    ) -> EnhancedChapter:
        """
        Przepuszcza rozdział przez wszystkie przebiegi ulepszające.
        """
        current_content = chapter_content
        pass_results = []

        for pass_config in self.ENHANCEMENT_PASSES:
            # Wykonaj przebieg
            result = await self._execute_pass(
                content=current_content,
                pass_config=pass_config,
                context=context
            )

            pass_results.append(result)
            current_content = result.enhanced_content

            # Sprawdź czy osiągnęliśmy cel
            quality_check = await self.quality_engine.analyze_quality(current_content)
            if quality_check.total_score >= target_quality:
                break

        return EnhancedChapter(
            original=chapter_content,
            enhanced=current_content,
            passes_executed=[p["name"] for p in pass_results],
            improvements_made=sum(p.improvements_count for p in pass_results),
            quality_before=pass_results[0].quality_before if pass_results else 0,
            quality_after=pass_results[-1].quality_after if pass_results else 0
        )
```

---

# CZĘŚĆ VIII: NOWY WYGLĄD PLATFORMY (UI/UX)

## 8.1 Dashboard - Strona Główna

```typescript
// frontend/src/pages/Dashboard.tsx - NOWY DESIGN

const Dashboard: React.FC = () => {
    return (
        <div className="dashboard-container">
            {/* HERO SECTION */}
            <section className="hero-section">
                <h1>NarraForge 2.0</h1>
                <p className="tagline">Twórz bestsellery z pomocą AI najwyższej klasy</p>

                {/* SZYBKI START - 3 OPCJE */}
                <div className="quick-start-grid">
                    <QuickStartCard
                        icon={<PenIcon />}
                        title="Nowa Książka"
                        description="Zacznij od tytułu, AI zrobi resztę"
                        action="/create"
                        color="primary"
                    />
                    <QuickStartCard
                        icon={<ContinueIcon />}
                        title="Kontynuuj Dzieło"
                        description="Napisz sequel, prequel lub spin-off"
                        action="/library?mode=continue"
                        color="secondary"
                    />
                    <QuickStartCard
                        icon={<LibraryIcon />}
                        title="Twoja Biblioteka"
                        description="Przeglądaj i eksportuj swoje książki"
                        action="/library"
                        color="tertiary"
                    />
                </div>
            </section>

            {/* STATYSTYKI UŻYTKOWNIKA */}
            <section className="user-stats">
                <StatCard
                    label="Stworzone książki"
                    value={stats.totalBooks}
                    icon={<BookIcon />}
                />
                <StatCard
                    label="Napisane słowa"
                    value={formatNumber(stats.totalWords)}
                    icon={<WordCountIcon />}
                />
                <StatCard
                    label="Średnia jakość"
                    value={`${stats.averageQuality}%`}
                    icon={<QualityIcon />}
                    color={stats.averageQuality >= 80 ? 'gold' : 'silver'}
                />
                <StatCard
                    label="Serie"
                    value={stats.totalSeries}
                    icon={<SeriesIcon />}
                />
            </section>

            {/* OSTATNIE PROJEKTY Z LIVE PREVIEW */}
            <section className="recent-projects">
                <h2>Ostatnie Projekty</h2>
                <div className="projects-grid">
                    {recentProjects.map(project => (
                        <ProjectCard
                            key={project.id}
                            project={project}
                            showProgress={project.status === 'in_progress'}
                            showContinueOptions={project.status === 'completed'}
                        />
                    ))}
                </div>
            </section>

            {/* AKTYWNE GENEROWANIE (jeśli jest) */}
            {activeGeneration && (
                <section className="active-generation">
                    <h2>Trwa Tworzenie</h2>
                    <LiveGenerationWidget
                        projectId={activeGeneration.id}
                        showFullPreview={false}
                    />
                </section>
            )}

            {/* SUGESTIE KONTYNUACJI */}
            {continuationSuggestions.length > 0 && (
                <section className="continuation-suggestions">
                    <h2>Sugerowane Kontynuacje</h2>
                    <div className="suggestions-carousel">
                        {continuationSuggestions.map(suggestion => (
                            <ContinuationSuggestionCard
                                key={suggestion.id}
                                suggestion={suggestion}
                                onAccept={handleAcceptSuggestion}
                            />
                        ))}
                    </div>
                </section>
            )}
        </div>
    );
};
```

## 8.2 Kreator Projektu - Zaawansowany Interfejs

```typescript
// frontend/src/pages/ProjectCreator.tsx - NOWY DESIGN

const ProjectCreator: React.FC = () => {
    const [step, setStep] = useState<CreationStep>('title');
    const [title, setTitle] = useState('');
    const [genre, setGenre] = useState<GenreType | null>(null);
    const [titanAnalysis, setTitanAnalysis] = useState<TITANAnalysis | null>(null);
    const [parameters, setParameters] = useState<BookParameters | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    // KROK 1: Wpisz tytuł
    const TitleStep = () => (
        <div className="creation-step title-step">
            <h2>Jak nazywa się Twoja książka?</h2>
            <p className="hint">
                Tytuł to DNA Twojej książki. Z niego AI wyekstrahuje całą historię.
            </p>

            <input
                type="text"
                className="title-input"
                placeholder="Wpisz tytuł..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                autoFocus
            />

            <div className="title-examples">
                <span>Przykłady:</span>
                <button onClick={() => setTitle("Ostatni strażnik zapomnianych bram")}>
                    Fantasy
                </button>
                <button onClick={() => setTitle("Trzy sekundy do północy")}>
                    Thriller
                </button>
                <button onClick={() => setTitle("Rozalia, 1,5 roczna, długo oczekiwana")}>
                    Drama
                </button>
            </div>

            <button
                className="primary-btn"
                onClick={handleAnalyzeTitle}
                disabled={title.length < 3 || isAnalyzing}
            >
                {isAnalyzing ? 'Analizuję głębię tytułu...' : 'Analizuj Tytuł'}
            </button>
        </div>
    );

    // KROK 2: Wybierz gatunek (z wizualizacją TITAN)
    const GenreStep = () => (
        <div className="creation-step genre-step">
            <div className="titan-preview">
                <h3>Analiza TITAN dla: "{title}"</h3>
                <TITANRadarChart analysis={titanAnalysis} />

                <div className="titan-highlights">
                    <Highlight
                        label="Emocjonalna głębia"
                        value={titanAnalysis.emotional_resonance.intensity_level}
                        max={10}
                    />
                    <Highlight
                        label="Potencjał świata"
                        value={titanAnalysis.spatial_world.world_uniqueness}
                        max={10}
                    />
                    <Highlight
                        label="Złożoność konfliktu"
                        value={titanAnalysis.central_conflict.moral_complexity}
                        max={10}
                    />
                </div>
            </div>

            <div className="genre-selection">
                <h3>Wybierz gatunek</h3>
                <p className="ai-suggestion">
                    AI sugeruje: <strong>{titanAnalysis.suggested_genre}</strong>
                </p>

                <div className="genre-grid">
                    {GENRES.map(g => (
                        <GenreCard
                            key={g.id}
                            genre={g}
                            isSelected={genre === g.id}
                            isSuggested={g.id === titanAnalysis.suggested_genre}
                            onClick={() => setGenre(g.id)}
                        />
                    ))}
                </div>
            </div>

            <button
                className="primary-btn"
                onClick={handleGenerateParameters}
                disabled={!genre}
            >
                Generuj Parametry Książki
            </button>
        </div>
    );

    // KROK 3: Przegląd i modyfikacja parametrów
    const ParametersStep = () => (
        <div className="creation-step parameters-step">
            <h2>Parametry Twojej Książki</h2>
            <p className="subtitle">
                Te parametry zostały wygenerowane specjalnie dla tytułu "{title}".
                Każdy tytuł generuje UNIKALNE parametry.
            </p>

            <div className="parameters-grid">
                {/* OBJĘTOŚĆ */}
                <ParameterCard
                    icon={<WordIcon />}
                    label="Ilość słów"
                    value={formatNumber(parameters.word_count)}
                    editable={true}
                    onChange={(v) => updateParameter('word_count', v)}
                    min={40000}
                    max={200000}
                    explanation="Dynamicznie obliczone na podstawie złożoności tytułu"
                />

                {/* ROZDZIAŁY */}
                <ParameterCard
                    icon={<ChapterIcon />}
                    label="Rozdziały"
                    value={parameters.chapter_count}
                    editable={true}
                    onChange={(v) => updateParameter('chapter_count', v)}
                    min={10}
                    max={60}
                />

                {/* GŁÓWNE POSTACIE */}
                <ParameterCard
                    icon={<CharacterIcon />}
                    label="Główne postacie"
                    value={parameters.main_characters}
                    editable={true}
                    onChange={(v) => updateParameter('main_characters', v)}
                    min={1}
                    max={12}
                />

                {/* LOKACJE */}
                <ParameterCard
                    icon={<LocationIcon />}
                    label="Lokacje"
                    value={parameters.locations_count}
                    explanation={`Główna lokalizacja: ${parameters.primary_location}`}
                />

                {/* WĄTKI POBOCZNE */}
                <ParameterCard
                    icon={<PlotIcon />}
                    label="Wątki poboczne"
                    value={parameters.subplot_count}
                />

                {/* STYL PROZY */}
                <ParameterCard
                    icon={<StyleIcon />}
                    label="Styl prozy"
                    value={parameters.prose_style}
                    type="select"
                    options={['poetycki', 'surowy', 'barokowy', 'minimalistyczny', 'klasyczny']}
                />
            </div>

            {/* SZACOWANY KOSZT */}
            <div className="cost-estimate">
                <h3>Szacowany koszt</h3>
                <CostBreakdown estimate={costEstimate} />
                <p className="cost-note">
                    Zakres: ${costEstimate.confidence_range.min.toFixed(2)} -
                    ${costEstimate.confidence_range.max.toFixed(2)}
                </p>
            </div>

            {/* OSTRZEŻENIA */}
            {costEstimate.warnings.length > 0 && (
                <div className="warnings">
                    {costEstimate.warnings.map((w, i) => (
                        <Warning key={i} message={w} />
                    ))}
                </div>
            )}

            <div className="action-buttons">
                <button className="secondary-btn" onClick={() => setStep('genre')}>
                    Wróć
                </button>
                <button className="primary-btn" onClick={handleStartGeneration}>
                    Rozpocznij Tworzenie
                </button>
            </div>
        </div>
    );

    return (
        <div className="project-creator">
            {/* PROGRESS BAR */}
            <CreationProgress
                steps={['Tytuł', 'Gatunek', 'Parametry', 'Tworzenie']}
                currentStep={step}
            />

            {/* AKTYWY KROK */}
            {step === 'title' && <TitleStep />}
            {step === 'genre' && <GenreStep />}
            {step === 'parameters' && <ParametersStep />}
            {step === 'generating' && (
                <LivePreview projectId={projectId} fullscreen={true} />
            )}
        </div>
    );
};
```

## 8.3 Biblioteka z Mapą Uniwersów

```typescript
// frontend/src/pages/Library.tsx - NOWY DESIGN

const Library: React.FC = () => {
    const [viewMode, setViewMode] = useState<'grid' | 'timeline' | 'universe'>('grid');
    const [filterGenre, setFilterGenre] = useState<GenreType | 'all'>('all');
    const [selectedProject, setSelectedProject] = useState<Project | null>(null);

    return (
        <div className="library-container">
            <header className="library-header">
                <h1>Twoja Biblioteka</h1>

                <div className="view-controls">
                    <ViewModeToggle
                        mode={viewMode}
                        onChange={setViewMode}
                    />

                    <GenreFilter
                        value={filterGenre}
                        onChange={setFilterGenre}
                    />

                    <SearchInput
                        placeholder="Szukaj po tytule..."
                        onChange={handleSearch}
                    />
                </div>
            </header>

            <main className="library-content">
                {/* WIDOK SIATKI */}
                {viewMode === 'grid' && (
                    <div className="books-grid">
                        {filteredProjects.map(project => (
                            <BookCard
                                key={project.id}
                                project={project}
                                onClick={() => setSelectedProject(project)}
                                showQualityBadge={true}
                                showSeriesInfo={true}
                            />
                        ))}
                    </div>
                )}

                {/* WIDOK OSI CZASU */}
                {viewMode === 'timeline' && (
                    <TimelineView projects={filteredProjects}>
                        {/* Pokazuje chronologię tworzenia */}
                        {/* Grupuje serie razem */}
                        {/* Pokazuje połączenia między kontynuacjami */}
                    </TimelineView>
                )}

                {/* WIDOK MAPY UNIWERSÓW */}
                {viewMode === 'universe' && (
                    <UniverseMapView projects={filteredProjects}>
                        {/* Interaktywna mapa 3D/2D */}
                        {/* Każda seria to "galaktyka" */}
                        {/* Książki to "planety" */}
                        {/* Połączenia pokazują relacje */}
                    </UniverseMapView>
                )}
            </main>

            {/* PANEL SZCZEGÓŁÓW */}
            {selectedProject && (
                <ProjectDetailPanel
                    project={selectedProject}
                    onClose={() => setSelectedProject(null)}
                    onContinue={handleContinue}
                    onExport={handleExport}
                    onDelete={handleDelete}
                />
            )}
        </div>
    );
};

// Komponent karty książki
const BookCard: React.FC<BookCardProps> = ({
    project,
    onClick,
    showQualityBadge,
    showSeriesInfo
}) => {
    return (
        <div className="book-card" onClick={onClick}>
            {/* Okładka (generowana lub placeholder) */}
            <div className="book-cover">
                {project.cover_url ? (
                    <img src={project.cover_url} alt={project.title} />
                ) : (
                    <GeneratedCover
                        title={project.title}
                        genre={project.genre}
                    />
                )}

                {/* Badge jakości */}
                {showQualityBadge && (
                    <QualityBadge
                        score={project.quality_score}
                        level={project.quality_level}
                    />
                )}
            </div>

            {/* Info */}
            <div className="book-info">
                <h3 className="book-title">{project.title}</h3>

                {showSeriesInfo && project.series && (
                    <span className="series-badge">
                        {project.series.name} #{project.book_number_in_series}
                    </span>
                )}

                <div className="book-meta">
                    <span className="genre-tag">{project.genre}</span>
                    <span className="word-count">
                        {formatNumber(project.word_count)} słów
                    </span>
                </div>

                <div className="book-date">
                    {formatDate(project.completed_at)}
                </div>
            </div>

            {/* Akcje */}
            <div className="book-actions">
                <IconButton icon={<ReadIcon />} tooltip="Czytaj" />
                <IconButton icon={<ExportIcon />} tooltip="Eksportuj" />
                <IconButton icon={<ContinueIcon />} tooltip="Kontynuuj" />
            </div>
        </div>
    );
};
```

## 8.4 Style CSS - Nowoczesny Design

```css
/* frontend/src/styles/theme.css */

:root {
    /* KOLORY - Ciemny motyw */
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-tertiary: #1a1a25;
    --bg-card: #1e1e2a;
    --bg-card-hover: #252535;

    /* Akcenty */
    --accent-primary: #6366f1;    /* Indigo */
    --accent-secondary: #8b5cf6;  /* Violet */
    --accent-success: #10b981;    /* Emerald */
    --accent-warning: #f59e0b;    /* Amber */
    --accent-error: #ef4444;      /* Red */
    --accent-gold: #fbbf24;       /* Gold - dla wysokiej jakości */

    /* Tekst */
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;

    /* Gradienty */
    --gradient-primary: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    --gradient-gold: linear-gradient(135deg, #fbbf24, #f59e0b);
    --gradient-card: linear-gradient(180deg, var(--bg-card), var(--bg-tertiary));

    /* Cienie */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.5);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.5);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
    --shadow-glow: 0 0 20px rgba(99, 102, 241, 0.3);

    /* Zaokrąglenia */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 16px;
    --radius-full: 9999px;

    /* Animacje */
    --transition-fast: 150ms ease;
    --transition-normal: 300ms ease;
    --transition-slow: 500ms ease;
}

/* KOMPONENTY */

.book-card {
    background: var(--gradient-card);
    border-radius: var(--radius-lg);
    overflow: hidden;
    transition: transform var(--transition-normal),
                box-shadow var(--transition-normal);
    cursor: pointer;
}

.book-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-glow);
}

.quality-badge {
    position: absolute;
    top: 8px;
    right: 8px;
    padding: 4px 8px;
    border-radius: var(--radius-full);
    font-size: 12px;
    font-weight: 600;
}

.quality-badge.masterpiece {
    background: var(--gradient-gold);
    color: #000;
}

.quality-badge.bestseller {
    background: var(--accent-primary);
    color: white;
}

.primary-btn {
    background: var(--gradient-primary);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: var(--radius-md);
    font-weight: 600;
    cursor: pointer;
    transition: transform var(--transition-fast),
                box-shadow var(--transition-fast);
}

.primary-btn:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-glow);
}

.primary-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

/* LIVE PREVIEW */
.live-text-panel {
    background: var(--bg-secondary);
    border-radius: var(--radius-lg);
    padding: 24px;
    font-family: 'Crimson Text', Georgia, serif;
    font-size: 18px;
    line-height: 1.8;
    color: var(--text-primary);
    max-height: 60vh;
    overflow-y: auto;
}

.typing-cursor {
    display: inline-block;
    width: 2px;
    height: 1.2em;
    background: var(--accent-primary);
    margin-left: 2px;
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}

/* TITAN VISUALIZATION */
.titan-visualization {
    position: relative;
    width: 400px;
    height: 400px;
}

.dimension-node {
    position: absolute;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: var(--bg-card);
    border: 2px solid var(--bg-tertiary);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-normal);
}

.dimension-node.active {
    border-color: var(--accent-primary);
    box-shadow: var(--shadow-glow);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}
```

---

# CZĘŚĆ IX: HARMONOGRAM IMPLEMENTACJI

## 9.1 Fazy Wdrożenia

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    HARMONOGRAM TRANSFORMACJI NARRAFORGE 2.0                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  FAZA 1: FUNDAMENTY (Tydzień 1-2)                                            ║
║  ─────────────────────────────────                                            ║
║  [■] Naprawa estymacji kosztów (cost_analysis_v2.py)                         ║
║  [■] Auto-repair dla failed chapters                                         ║
║  [■] Model fallback strategy                                                 ║
║  [■] WebSocket backend implementation                                        ║
║  [■] Podstawowa integracja WebSocket w frontend                              ║
║                                                                               ║
║  FAZA 2: TITAN ANALYSIS (Tydzień 3-4)                                        ║
║  ────────────────────────────────────                                         ║
║  [■] Implementacja 12 wymiarów analizy                                       ║
║  [■] Dynamiczny generator parametrów                                         ║
║  [■] Auto-kreacja postaci z tytułu                                           ║
║  [■] Integracja TITAN z pipeline generacji                                   ║
║  [■] Frontend - wizualizacja TITAN                                           ║
║                                                                               ║
║  FAZA 3: CONTINUITY & SERIES (Tydzień 5-6)                                   ║
║  ─────────────────────────────────────────                                    ║
║  [■] RAG-based continuity system (pgvector)                                  ║
║  [■] Universe Memory System                                                  ║
║  [■] Continuation suggestions engine                                         ║
║  [■] Series management backend                                               ║
║  [■] Frontend - Library z Universe Map                                       ║
║                                                                               ║
║  FAZA 4: QUALITY ENGINE (Tydzień 7-8)                                        ║
║  ────────────────────────────────────                                         ║
║  [■] Bestseller Quality Engine                                               ║
║  [■] Multi-pass enhancement                                                  ║
║  [■] Genre-specific excellence prompts                                       ║
║  [■] Quality scoring integration                                             ║
║  [■] Frontend - quality dashboard                                            ║
║                                                                               ║
║  FAZA 5: LIVE PREVIEW (Tydzień 9-10)                                         ║
║  ───────────────────────────────────                                          ║
║  [■] Streaming generation service                                            ║
║  [■] Real-time WebSocket events                                              ║
║  [■] Frontend - Live Preview component                                       ║
║  [■] Character birth animations                                              ║
║  [■] Progress visualization                                                  ║
║                                                                               ║
║  FAZA 6: RELIGIOUS GENRE (Tydzień 11-12)                                     ║
║  ───────────────────────────────────────                                      ║
║  [■] Religious Knowledge Base                                                ║
║  [■] Theological validator                                                   ║
║  [■] Religious content agent                                                 ║
║  [■] Scripture integration                                                   ║
║  [■] Frontend - religious genre support                                      ║
║                                                                               ║
║  FAZA 7: UI/UX OVERHAUL (Tydzień 13-14)                                      ║
║  ──────────────────────────────────────                                       ║
║  [■] Nowy design system                                                      ║
║  [■] Dashboard redesign                                                      ║
║  [■] Project Creator redesign                                                ║
║  [■] Library z Timeline i Universe Map                                       ║
║  [■] Responsywność i animacje                                                ║
║                                                                               ║
║  FAZA 8: TESTING & POLISH (Tydzień 15-16)                                    ║
║  ────────────────────────────────────────                                     ║
║  [■] End-to-end testing                                                      ║
║  [■] Performance optimization                                                ║
║  [■] Bug fixing                                                              ║
║  [■] Documentation                                                           ║
║  [■] Beta testing z użytkownikami                                            ║
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 9.2 Priorytety Implementacji

```python
IMPLEMENTATION_PRIORITY = {
    "CRITICAL": [
        # Musi być NATYCHMIAST
        "Naprawa estymacji kosztów",        # Użytkownicy są wprowadzani w błąd
        "Auto-repair dla failed chapters",   # Projekty się crashują
        "Model fallback strategy",           # Brak reliability
    ],

    "HIGH": [
        # Kluczowe dla jakości
        "TITAN Analysis System",             # Core differentiation
        "Bestseller Quality Engine",         # Główna obietnica
        "RAG Continuity System",             # Eliminuje plot holes
    ],

    "MEDIUM": [
        # Ważne dla UX
        "WebSocket Live Preview",            # Wow factor
        "Universe Memory System",            # Kontynuacje
        "UI/UX Overhaul",                    # Profesjonalny wygląd
    ],

    "LOWER": [
        # Nice to have
        "Religious Genre",                   # Nowy gatunek
        "Universe Map View",                 # Fancy visualization
        "Character birth animations",        # Polish
    ]
}
```

---

# CZĘŚĆ X: PODSUMOWANIE

## 10.1 Kluczowe Transformacje

| Obszar | PRZED | PO |
|--------|-------|-----|
| **Analiza tytułu** | Podstawowa, 1-wymiarowa | TITAN: 12 wymiarów, głęboka semantyka |
| **Parametry książki** | Stałe per gatunek | Dynamiczne, unikalne dla każdego tytułu |
| **Ilość słów** | 70-150k (stała) | 40-200k (zależna od tytułu) |
| **Postacie** | Ręcznie lub podstawowe | Auto-kreacja z psychologią |
| **Lokalizacje** | Głównie Europa | Globalne, kosmiczne, fantastyczne |
| **Kontynuacje** | Brak | Pełny system serii i uniwersów |
| **Podgląd** | Polling co 5s | WebSocket real-time, słowo po słowie |
| **Jakość** | Bazowa walidacja | Bestseller Quality Engine, multi-pass |
| **Continuity** | Podstawowe sprawdzenia | RAG z pgvector, auto-fix |
| **Koszty** | Niedoszacowane 2-3x | Dokładne z marginesem |
| **Reliability** | Brak fallback | Multi-provider, auto-repair |
| **Gatunki** | 8 | 9 (+ religijne) |
| **UI** | Funkcjonalne | Premium, animowane |

## 10.2 Oczekiwane Rezultaty

```
Po wdrożeniu NarraForge 2.0:

✅ KAŻDY tytuł generuje UNIKALNĄ książkę
✅ Parametry dynamicznie dostosowane do treści
✅ Jakość na poziomie światowych bestsellerów
✅ Czytelnik nie oderwie się od książki
✅ Pełne wsparcie dla serii i kontynuacji
✅ Podgląd na żywo tworzenia
✅ Zero plot holes dzięki RAG
✅ Niezawodność - auto-repair i fallback
✅ Dokładne szacowanie kosztów
✅ Premium UI/UX
✅ Nowy gatunek: literatura religijna
```

## 10.3 Metryki Sukcesu

```python
SUCCESS_METRICS = {
    "quality": {
        "target_avg_score": 85,        # Poziom bestsellera
        "min_acceptable_score": 70,
        "masterpiece_rate": 0.10,      # 10% książek = arcydzieła
    },

    "uniqueness": {
        "parameter_variance": 0.30,    # Min 30% różnicy między książkami
        "no_duplicate_openings": True,
        "unique_character_names": True,
    },

    "reliability": {
        "generation_success_rate": 0.99,
        "max_fallback_rate": 0.05,
        "uptime": 0.999,
    },

    "user_experience": {
        "cost_accuracy": 0.85,         # W 85% przypadków w zakresie
        "live_preview_latency": 500,   # Max 500ms opóźnienia
        "page_load_time": 2000,        # Max 2s
    },

    "engagement": {
        "continuation_rate": 0.30,     # 30% książek ma kontynuację
        "return_user_rate": 0.50,      # 50% użytkowników wraca
        "avg_books_per_user": 5,
    }
}
```

---

## KONIEC PLANU TRANSFORMACJI

**Ten plan transformuje NarraForge z dobrej platformy w NAJLEPSZĄ na świecie.**

Każdy element został zaprojektowany z myślą o:
- **Unikalności** - żadne dwie książki nie będą takie same
- **Jakości** - poziom światowych bestsellerów
- **Niezawodności** - zero crashów, auto-naprawa
- **Doświadczeniu** - premium UI, live preview
- **Przyszłości** - kontynuacje, serie, uniwersa

**To jest plan JUTRA. Plan, który wyprzedza czas.**

---

*Dokument wygenerowany: 2026-01-29*
*Wersja: 2.0 QUANTUM LEAP*
