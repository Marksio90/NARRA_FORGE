"""
MIRIX Procedural Memory Seeds - NarraForge 3.0

Initial procedural knowledge base with writing techniques,
narrative patterns, and style guidelines.

These seeds are loaded into the global MIRIX procedural memory
and can be applied across all projects.
"""

from typing import List, Dict, Any


# =============================================================================
# NARRATIVE TECHNIQUES
# =============================================================================

NARRATIVE_TECHNIQUES: List[Dict[str, Any]] = [
    # === SHOW DON'T TELL ===
    {
        "technique_name": "Show Don't Tell - Emotions",
        "technique_type": "style",
        "description": "Express character emotions through physical reactions, actions, and sensory details instead of stating feelings directly.",
        "when_to_use": ["emotional_scene", "character_moment", "revelation", "conflict"],
        "how_to_apply": """
Instead of: 'She was angry'
Write: 'Her hands trembled as she gripped the edge of the table, knuckles whitening. Her jaw clenched, words escaping through gritted teeth.'

Key elements:
1. Physical manifestations (trembling, sweating, tension)
2. Facial micro-expressions
3. Body language
4. Breathing changes
5. Voice quality changes
""",
        "examples": [
            "Strach: Serce łomotało jej w piersi, a oddech urywał się w płytkich, szybkich hausach.",
            "Radość: Uśmiech rozlał się po jego twarzy, a oczy zabłysły tym szczególnym światłem.",
            "Gniew: Żyła na skroni pulsowała niebezpiecznie, gdy cedził słowa przez zaciśnięte zęby."
        ],
        "genre_affinity": {
            "thriller": 0.95,
            "horror": 0.95,
            "romance": 0.9,
            "fantasy": 0.85,
            "drama": 0.9
        },
        "effectiveness_score": 0.95
    },

    # === MRU - MOTIVATION REACTION UNIT ===
    {
        "technique_name": "MRU - Motivation Reaction Unit",
        "technique_type": "structure",
        "description": "Structure scenes in Motivation-Reaction pairs: external stimulus triggers internal response (feeling, reflex, rational action, speech).",
        "when_to_use": ["action_scene", "dialogue", "tense_moment", "any_scene"],
        "how_to_apply": """
MRU Structure:
1. MOTIVATION (External) - Something happens in the world
2. REACTION (Internal, in order):
   a) Feeling/Emotion (involuntary, immediate)
   b) Reflex (physical, involuntary)
   c) Rational Action (deliberate)
   d) Speech (most rational response)

Example:
MOTIVATION: The door exploded inward, splinters flying.
REACTION:
- Feeling: Terror seized her heart.
- Reflex: She flinched, throwing her arms up.
- Action: She dove behind the overturned table.
- Speech: "They found us!"
""",
        "examples": [
            "Motywacja: Nóż błysnął w świetle księżyca.\nReakcja: Strach ścisnął mu gardło (uczucie). Cofnął się instynktownie (odruch). Sięgnął po leżącą obok butelkę (działanie). — Jeszcze jeden krok — warknął (mowa).",
        ],
        "genre_affinity": {
            "thriller": 0.98,
            "horror": 0.95,
            "fantasy": 0.9,
            "sci_fi": 0.85,
            "romance": 0.8
        },
        "effectiveness_score": 0.92
    },

    # === DEEP POV ===
    {
        "technique_name": "Deep POV - Narrative Intimacy",
        "technique_type": "style",
        "description": "Eliminate narrative distance by removing filter words and thought tags, placing reader directly in character's consciousness.",
        "when_to_use": ["character_scene", "emotional_moment", "internal_conflict", "revelation"],
        "how_to_apply": """
Remove filter words: saw, heard, felt, thought, wondered, realized, noticed, knew, seemed

Before (Distant): She saw the man standing by the door. She thought he looked dangerous.
After (Deep POV): The man by the door - tall, scarred, hand resting on his weapon. Dangerous.

Before: He wondered if she would forgive him.
After: Would she ever forgive him? The question burned.

Key principles:
1. No "she thought", "he felt", "she noticed"
2. Direct sensory experience
3. Character's voice in narrative
4. Immediate internal reactions
""",
        "examples": [
            "Zamiast: Zauważyła, że pokój był pusty.\nNapisz: Pusty pokój. Gdzie oni wszyscy się podziali?",
            "Zamiast: Poczuł smutek na myśl o niej.\nNapisz: Anna. Jej imię bolało jak świeża rana."
        ],
        "genre_affinity": {
            "thriller": 0.95,
            "romance": 0.95,
            "horror": 0.9,
            "fantasy": 0.85,
            "drama": 0.9
        },
        "effectiveness_score": 0.93
    },

    # === CLIFFHANGER ===
    {
        "technique_name": "Cliffhanger Endings",
        "technique_type": "pacing",
        "description": "End chapters at moments of maximum tension, unresolved questions, or shocking revelations to compel continued reading.",
        "when_to_use": ["chapter_end", "scene_end", "act_break"],
        "how_to_apply": """
Types of cliffhangers:
1. DANGER: Character in immediate peril
2. REVELATION: Shocking information revealed
3. DECISION: Critical choice about to be made
4. ARRIVAL: Unexpected character/threat appears
5. QUESTION: Unanswered question raised
6. REVERSAL: Expectation subverted

End on:
- Mid-action
- Mid-dialogue (especially before crucial response)
- Moment of realization
- Sound/movement that implies threat
""",
        "examples": [
            "Drzwi otworzyły się i stanął w nich... [koniec rozdziału]",
            "— Muszę ci coś powiedzieć. Twój ojciec... [koniec rozdziału]",
            "Odwróciła się. W ciemności błysnęły dwie pary oczu. [koniec rozdziału]"
        ],
        "genre_affinity": {
            "thriller": 0.98,
            "horror": 0.95,
            "mystery": 0.95,
            "fantasy": 0.85,
            "romance": 0.75
        },
        "effectiveness_score": 0.94
    },

    # === DIALOGUE SUBTEXT ===
    {
        "technique_name": "Dialogue Subtext",
        "technique_type": "dialogue",
        "description": "Characters say one thing but mean another. The real meaning lies beneath the surface, revealed through context and delivery.",
        "when_to_use": ["dialogue", "confrontation", "romance", "negotiation", "deception"],
        "how_to_apply": """
Layers of dialogue:
1. SURFACE: What is literally said
2. SUBTEXT: What is really meant
3. CONTEXT: What both characters know

Techniques:
- Characters avoid the real topic
- Questions that are really accusations
- Compliments that are insults
- Agreement that signals disagreement
- Talking about one thing, meaning another

Example:
Surface: "How was your trip?"
Subtext: "I know you lied about where you went."
Context: She found the hotel receipt from a different city.
""",
        "examples": [
            "— Piękna sukienka. Nowa?\n(Subtext: Wiem, że byłaś z nim. Widziałam ją na zdjęciu.)",
            "— Wszystko w porządku?\n— Oczywiście. Dlaczego miałoby nie być?\n(Subtext: Oboje wiemy, że nic nie jest w porządku, ale nie będziemy o tym rozmawiać.)"
        ],
        "genre_affinity": {
            "drama": 0.98,
            "romance": 0.95,
            "thriller": 0.9,
            "mystery": 0.9,
            "comedy": 0.85
        },
        "effectiveness_score": 0.91
    },

    # === SENSORY IMMERSION ===
    {
        "technique_name": "Five Senses Immersion",
        "technique_type": "description",
        "description": "Engage all five senses in descriptions to create vivid, immersive scenes that feel real to the reader.",
        "when_to_use": ["scene_opening", "new_location", "atmospheric_moment", "key_scene"],
        "how_to_apply": """
For each important scene, include:
1. SIGHT: Colors, light, movement, shapes
2. SOUND: Ambient sounds, voices, silence
3. SMELL: Scents that evoke memory/emotion
4. TOUCH: Textures, temperature, pressure
5. TASTE: (when appropriate) Often tied to smell

Priority order based on scene type:
- Action: Sight > Sound > Touch
- Romance: Touch > Smell > Sight
- Horror: Sound > Smell > Sight
- Mystery: Sight > Smell > Sound

Don't list all senses mechanically - weave them naturally.
""",
        "examples": [
            "Weszła do starej biblioteki. Kurz tańczył w snopach światła sączącego się przez brudne okna (wzrok). Pachniało starym papierem i lawendą od molich kulek (zapach). Gdzieś w głębi tykał zegar, odmierzając sekundy w ciszy (słuch). Przesunęła palcami po grzbietach książek — szorstkie, popękane okładki (dotyk)."
        ],
        "genre_affinity": {
            "horror": 0.95,
            "romance": 0.9,
            "fantasy": 0.9,
            "thriller": 0.85,
            "mystery": 0.85
        },
        "effectiveness_score": 0.89
    },

    # === PACING VARIATION ===
    {
        "technique_name": "Sentence Length Pacing",
        "technique_type": "pacing",
        "description": "Vary sentence length to control reading pace: short sentences for tension/action, longer for reflection/atmosphere.",
        "when_to_use": ["action_scene", "tense_moment", "calm_scene", "transition"],
        "how_to_apply": """
FAST PACING (Action/Tension):
- Short sentences. Fragments. Quick.
- One action per sentence
- Cut adjectives and adverbs
- Active voice only

SLOW PACING (Reflection/Atmosphere):
- Longer, flowing sentences with multiple clauses
- Rich descriptions with sensory details
- Allow time for the moment to breathe
- Internal monologue and observation

Example transition:
[Fast] He ran. Footsteps behind. Closer. The wall loomed ahead. Dead end.
[Slow] For a long moment, he simply stood there, back pressed against the cold stone, listening to his own ragged breathing and the distant drip of water somewhere in the darkness, wondering how it had all gone so terribly wrong.
""",
        "examples": [
            "[Szybko] Biegł. Kroki za nim. Bliżej. Ściana. Koniec.\n[Wolno] Stał tak przez długą chwilę, z plecami przy zimnym kamieniu, wsłuchując się w własny urywany oddech i odległy kapanie wody gdzieś w mroku, zastanawiając się, jak to wszystko mogło pójść tak źle."
        ],
        "genre_affinity": {
            "thriller": 0.95,
            "horror": 0.9,
            "fantasy": 0.85,
            "romance": 0.8,
            "drama": 0.85
        },
        "effectiveness_score": 0.90
    },

    # === FORESHADOWING ===
    {
        "technique_name": "Subtle Foreshadowing",
        "technique_type": "structure",
        "description": "Plant seeds early that will pay off later, making revelations feel earned rather than random.",
        "when_to_use": ["setup_scene", "early_chapters", "character_introduction", "world_building"],
        "how_to_apply": """
Types of foreshadowing:
1. SYMBOLIC: Objects, weather, animals that mirror future events
2. DIALOGUE: Offhand comments that gain significance later
3. CHARACTER: Small behaviors that hint at hidden nature
4. ENVIRONMENTAL: Details about setting that become crucial
5. PROPHECY: Direct but cryptic prediction

Rules:
- Plant at least 3 chapters before payoff
- Make it noticeable on re-read, invisible on first read
- Never let foreshadowing feel obvious
- Each major twist needs 2-3 seeds planted earlier
""",
        "examples": [
            "Symboliczne: Opisując pokój zdrajcy, wspomnij o pękniętym lustrze (rozbita tożsamość).",
            "Dialogowe: — Nigdy bym cię nie okłamał — powiedział, nie patrząc jej w oczy.",
            "Środowiskowe: Stary most trzeszczał pod ich stopami. Za kilka rozdziałów — most się zawali."
        ],
        "genre_affinity": {
            "mystery": 0.98,
            "thriller": 0.95,
            "fantasy": 0.9,
            "horror": 0.9,
            "drama": 0.85
        },
        "effectiveness_score": 0.93
    },

    # === CONFLICT IN EVERY SCENE ===
    {
        "technique_name": "Scene-Level Conflict",
        "technique_type": "structure",
        "description": "Every scene must have conflict - a goal, obstacle, and outcome that moves the story forward.",
        "when_to_use": ["any_scene", "scene_planning", "revision"],
        "how_to_apply": """
Scene conflict checklist:
1. GOAL: What does the POV character want in this scene?
2. OBSTACLE: What prevents them from getting it?
3. STAKES: What happens if they fail?
4. OUTCOME: Do they succeed, fail, or partial success with new complication?

Types of conflict:
- Person vs Person
- Person vs Self
- Person vs Nature
- Person vs Society
- Person vs Fate/Supernatural

If no conflict exists, either:
- Add conflict
- Merge scene with another
- Cut the scene
""",
        "examples": [
            "Cel: Bohaterka chce przeprosić siostrę.\nPrzeszkoda: Siostra nie chce słuchać.\nStawka: Relacja rodzinna.\nWynik: Częściowy sukces - siostra słucha, ale nie wybacza."
        ],
        "genre_affinity": {
            "thriller": 0.98,
            "drama": 0.95,
            "fantasy": 0.9,
            "romance": 0.85,
            "mystery": 0.9
        },
        "effectiveness_score": 0.95
    },

    # === CHARACTER VOICE ===
    {
        "technique_name": "Distinctive Character Voice",
        "technique_type": "dialogue",
        "description": "Each character should have a unique way of speaking, distinguishable without dialogue tags.",
        "when_to_use": ["dialogue", "character_creation", "internal_monologue"],
        "how_to_apply": """
Voice elements:
1. VOCABULARY: Education level, profession, era, region
2. SENTENCE STRUCTURE: Simple vs complex, questions vs statements
3. RHYTHM: Interrupted, flowing, clipped
4. VERBAL TICS: Repeated phrases, filler words, expressions
5. TOPIC PREFERENCE: What they talk about, avoid
6. ATTITUDE: How they address others, formality level

Create voice profile for each main character with:
- 3 signature phrases
- Typical sentence length
- 2-3 forbidden words (they'd never say)
- Emotional expression style
""",
        "examples": [
            "Profesor: 'Należy rozważyć, czy przypadkiem nie...' (długie, ostrożne zdania)",
            "Nastolatek: 'No i w ogóle to było mega dziwne, nie?' (slang, pytania retoryczne)",
            "Żołnierz: 'Tak jest. Wykonano.' (krótkie, bezpośrednie)"
        ],
        "genre_affinity": {
            "drama": 0.95,
            "comedy": 0.95,
            "romance": 0.9,
            "fantasy": 0.85,
            "thriller": 0.85
        },
        "effectiveness_score": 0.91
    },

    # === EMOTIONAL BEATS ===
    {
        "technique_name": "Emotional Beat Structure",
        "technique_type": "pacing",
        "description": "Structure emotional moments with setup, build, peak, and release for maximum impact.",
        "when_to_use": ["emotional_scene", "climax", "revelation", "character_moment"],
        "how_to_apply": """
Emotional beat structure:
1. SETUP: Establish emotional baseline
2. TRIGGER: The catalyst that starts the emotional shift
3. ESCALATION: Building intensity (3-5 beats)
4. PEAK: Maximum emotional intensity
5. RELEASE: Allow reader to process (don't cut away immediately)

Important:
- Don't rush the peak
- Give release beats time
- Contrast heightens emotion (quiet before storm)
- Physical detail anchors emotion
""",
        "examples": [
            "Setup: Spokojny poranek, kawa.\nTrigger: List z wiadomością o śmierci.\nEskalacja: Niedowierzanie → zaprzeczenie → rozpaczliwe sprawdzanie → zrozumienie.\nSzczyt: Krzyk, płacz, zniszczone naczynia.\nRelease: Cisza. Tylko tykanie zegara. Zimna kawa."
        ],
        "genre_affinity": {
            "drama": 0.98,
            "romance": 0.95,
            "horror": 0.9,
            "thriller": 0.85,
            "fantasy": 0.85
        },
        "effectiveness_score": 0.92
    },

    # === MYSTERY FAIR PLAY ===
    {
        "technique_name": "Mystery Fair Play Rules",
        "technique_type": "structure",
        "description": "In mystery/thriller, give readers all clues needed to solve the puzzle, but misdirect their attention.",
        "when_to_use": ["mystery", "thriller", "whodunit", "plot_twist"],
        "how_to_apply": """
Fair Play principles:
1. All clues must be available to reader
2. Plant clues at least once before reveal
3. Misdirection through:
   - Timing (bury clue in action scene)
   - Context (make it seem about something else)
   - Red herrings (false leads)
   - Character interpretation (detective misreads clue)

Knox's Decalogue modernized:
- No information withheld from reader
- No supernatural solution in realistic mystery
- Culprit must appear early
- Detective can't be the culprit
- Solution must be deducible from clues
""",
        "examples": [
            "Wskazówka ukryta w kontekście: Przy opisie pokoju wspomnieć o zegarze (który później okaże się dowodem alibi), koncentrując się na zdjęciu obok."
        ],
        "genre_affinity": {
            "mystery": 0.98,
            "thriller": 0.9,
            "horror": 0.7,
            "drama": 0.6
        },
        "effectiveness_score": 0.94
    }
]


# =============================================================================
# GENRE-SPECIFIC TECHNIQUES
# =============================================================================

GENRE_TECHNIQUES: Dict[str, List[Dict[str, Any]]] = {
    "fantasy": [
        {
            "technique_name": "Magic System Consistency",
            "technique_type": "world_building",
            "description": "Maintain consistent rules for magic/supernatural elements throughout the narrative.",
            "how_to_apply": "Define clear costs, limitations, and rules for magic. Every use should follow established principles.",
            "examples": ["Jeśli magia wymaga energii życiowej, pokaż konsekwencje jej nadużycia."],
            "effectiveness_score": 0.95
        },
        {
            "technique_name": "Wonder Preservation",
            "technique_type": "style",
            "description": "Maintain sense of wonder by not over-explaining magical elements.",
            "how_to_apply": "Leave some mystery. Not everything needs scientific explanation in fantasy.",
            "examples": ["Smoki po prostu LATAJĄ. Nie wyjaśniaj aerodynamiki."],
            "effectiveness_score": 0.88
        }
    ],
    "thriller": [
        {
            "technique_name": "Ticking Clock",
            "technique_type": "pacing",
            "description": "Create urgency through time pressure - deadline, countdown, limited window.",
            "how_to_apply": "Establish clear deadline early. Remind readers of time passing. Complications eat time.",
            "examples": ["Ma 24 godziny, by znaleźć antidotum. Każdy rozdział = mniej czasu."],
            "effectiveness_score": 0.96
        },
        {
            "technique_name": "Paranoia Building",
            "technique_type": "atmosphere",
            "description": "Make reader distrust everyone, including trusted characters.",
            "how_to_apply": "Give every character a secret, potential motive, unexplained behavior.",
            "examples": ["Najlepszy przyjaciel — ale dlaczego nie odbiera telefonów w środku nocy?"],
            "effectiveness_score": 0.93
        }
    ],
    "horror": [
        {
            "technique_name": "Dread vs Terror",
            "technique_type": "atmosphere",
            "description": "Build dread (anticipation of horror) longer than terror (direct horror). Dread is more effective.",
            "how_to_apply": "Delay the reveal. Let imagination work. The unseen is scarier than the seen.",
            "examples": ["Kroki na schodach. Bliżej. Bliżej. Cisza... [nie pokazuj potwora jeszcze]"],
            "effectiveness_score": 0.95
        },
        {
            "technique_name": "Normality Corruption",
            "technique_type": "style",
            "description": "Horror is most effective when it corrupts the familiar and safe.",
            "how_to_apply": "Start in comfortable, safe environment. Slowly introduce wrongness.",
            "examples": ["Dom rodzinny — ale drzwi do piwnicy, których nie pamiętasz."],
            "effectiveness_score": 0.92
        }
    ],
    "romance": [
        {
            "technique_name": "Tension Through Obstacles",
            "technique_type": "structure",
            "description": "Keep lovers apart through meaningful obstacles, not miscommunication.",
            "how_to_apply": "Create real barriers: duty, circumstance, past trauma, conflicting goals.",
            "examples": ["Ona jest chirurgiem, on pacjentem z nieuleczalną chorobą — etyka vs miłość."],
            "effectiveness_score": 0.94
        },
        {
            "technique_name": "Longing Moments",
            "technique_type": "style",
            "description": "Stretch moments of almost-connection for maximum romantic tension.",
            "how_to_apply": "Near-touches, interrupted moments, lingering glances. Delay gratification.",
            "examples": ["Ich palce prawie się dotknęły, gdy sięgali po tę samą książkę..."],
            "effectiveness_score": 0.93
        }
    ],
    "mystery": [
        {
            "technique_name": "Red Herring Placement",
            "technique_type": "structure",
            "description": "Plant false leads that seem compelling but lead nowhere.",
            "how_to_apply": "Give 2-3 red herrings per mystery. Make them believable but ultimately refutable.",
            "examples": ["Podejrzany miał motyw i alibi z dziurą — ale to nie on. To odwraca uwagę od prawdziwego sprawcy."],
            "effectiveness_score": 0.94
        }
    ]
}


# =============================================================================
# RESOURCE SEEDS (METAPHORS, DESCRIPTIONS)
# =============================================================================

RESOURCE_SEEDS: List[Dict[str, Any]] = [
    # Emotional metaphors
    {
        "resource_type": "metaphor",
        "content": "Strach ściskał mu gardło jak zimna dłoń",
        "emotional_context": ["strach", "lęk", "panika"],
        "genre_context": ["thriller", "horror"],
        "originality_score": 0.7,
        "impact_score": 0.85
    },
    {
        "resource_type": "metaphor",
        "content": "Nadzieja była jak pierwszy promień słońca po tygodniu deszczu",
        "emotional_context": ["nadzieja", "ulga", "radość"],
        "genre_context": ["drama", "romance"],
        "originality_score": 0.6,
        "impact_score": 0.8
    },
    {
        "resource_type": "metaphor",
        "content": "Gniew wzbierał w niej jak lawa pod skorupą wulkanu",
        "emotional_context": ["gniew", "frustracja", "wściekłość"],
        "genre_context": ["thriller", "drama"],
        "originality_score": 0.75,
        "impact_score": 0.88
    },
    {
        "resource_type": "metaphor",
        "content": "Smutek osiadł na jej sercu jak zimny popiół",
        "emotional_context": ["smutek", "żałoba", "melancholia"],
        "genre_context": ["drama", "romance"],
        "originality_score": 0.8,
        "impact_score": 0.9
    },
    {
        "resource_type": "metaphor",
        "content": "Jego słowa były nożami owiniętymi w jedwab",
        "emotional_context": ["zdrada", "manipulacja", "fałsz"],
        "genre_context": ["thriller", "drama", "mystery"],
        "originality_score": 0.85,
        "impact_score": 0.92
    },

    # Sensory descriptions
    {
        "resource_type": "description",
        "content": "Powietrze gęste od dymu i niewypowiedzianych słów",
        "emotional_context": ["napięcie", "konflikt"],
        "genre_context": ["drama", "thriller"],
        "originality_score": 0.8,
        "impact_score": 0.85
    },
    {
        "resource_type": "description",
        "content": "Cisza tak głęboka, że słyszał bicie własnego serca",
        "emotional_context": ["napięcie", "strach", "oczekiwanie"],
        "genre_context": ["thriller", "horror"],
        "originality_score": 0.65,
        "impact_score": 0.88
    },
    {
        "resource_type": "description",
        "content": "Zapach starej książki — kurz, wanilia i zapomniane sekrety",
        "emotional_context": ["nostalgia", "tajemnica", "spokój"],
        "genre_context": ["mystery", "fantasy", "romance"],
        "originality_score": 0.75,
        "impact_score": 0.82
    }
]


# =============================================================================
# INITIALIZATION FUNCTION
# =============================================================================

async def seed_mirix_procedural_memory(mirix_system) -> Dict[str, int]:
    """
    Seed MIRIX global procedural memory with writing techniques.

    Args:
        mirix_system: The MIRIXMemorySystem instance

    Returns:
        Dictionary with counts of seeded items
    """
    counts = {
        "techniques": 0,
        "genre_techniques": 0,
        "resources": 0
    }

    # Seed general narrative techniques
    for technique in NARRATIVE_TECHNIQUES:
        await mirix_system.store_technique(
            technique_name=technique["technique_name"],
            technique_type=technique["technique_type"],
            description=technique["description"],
            how_to_apply=technique.get("how_to_apply", ""),
            examples=technique.get("examples", []),
            genre_affinity=technique.get("genre_affinity", {}),
            effectiveness=technique.get("effectiveness_score", 0.7),
            global_learn=True
        )
        counts["techniques"] += 1

    # Seed genre-specific techniques
    for genre, techniques in GENRE_TECHNIQUES.items():
        for technique in techniques:
            await mirix_system.store_technique(
                technique_name=technique["technique_name"],
                technique_type=technique["technique_type"],
                description=technique["description"],
                how_to_apply=technique.get("how_to_apply", ""),
                examples=technique.get("examples", []),
                genre_affinity={genre: technique.get("effectiveness_score", 0.9)},
                effectiveness=technique.get("effectiveness_score", 0.7),
                global_learn=True
            )
            counts["genre_techniques"] += 1

    # Seed resources (metaphors, descriptions)
    for resource in RESOURCE_SEEDS:
        await mirix_system.store_resource(
            resource_type=resource["resource_type"],
            content=resource["content"],
            emotional_context=resource.get("emotional_context", []),
            genre_context=resource.get("genre_context", []),
            originality=resource.get("originality_score", 0.5),
            impact=resource.get("impact_score", 0.5)
        )
        counts["resources"] += 1

    return counts
