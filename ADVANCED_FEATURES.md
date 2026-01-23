# NarraForge Advanced Features - Bestseller Quality System

This document describes the advanced features added to elevate book generation to bestseller quality.

## 📚 Table of Contents

1. [Multi-Draft Revision System](#multi-draft-revision-system)
2. [Character Voice Consistency Validator](#character-voice-consistency-validator)
3. [Foreshadowing & Payoff Tracker](#foreshadowing--payoff-tracker)
4. [Emotional Arc Tracking](#emotional-arc-tracking)
5. [Scene Structure Validation](#scene-structure-validation)
6. [Prose Quality Control](#prose-quality-control)
7. [Opening Hook & Cliffhanger Optimization](#opening-hook--cliffhanger-optimization)
8. [Genre Reader Expectations](#genre-reader-expectations)

---

## 🔄 Multi-Draft Revision System

**Location**: `/backend/app/agents/chapter_revision_agent.py`

### What It Does

Transforms first drafts into polished, bestseller-quality chapters through intelligent revision.

### Features

**Two-Step Process**:
1. **Analysis Phase**: Identifies 5-10 critical improvements with maximum reader impact
2. **Rewrite Phase**: Incorporates all improvements while maintaining story integrity

**Focus Areas**:
- Opening hook strength (killer first lines)
- Cliffhanger effectiveness (magnetic chapter endings)
- Dialogue quality (subtext, unique voices, Polish EM DASH format)
- Show-don't-tell ratio (body language over emotion labels)
- Pacing variety (paragraph length control)
- Sensory immersion (all 5 senses engaged)
- Character voice consistency
- Scene structure (Goal→Conflict→Disaster)
- Cliché elimination
- Polish language naturalness

### How To Use

```python
from app.agents.chapter_revision_agent import ChapterRevisionAgent

revision_agent = ChapterRevisionAgent()

# Revise a chapter
result = await revision_agent.revise_chapter(
    first_draft=chapter_content,
    chapter_number=5,
    chapter_outline=outline,
    genre="thriller",
    pov_character=protagonist,
    target_word_count=3000,
    book_title="Tytuł Książki",
    quality_issues=["Weak opening", "No cliffhanger"]  # Optional
)

revised_chapter = result['revised_content']
improvements = result['improvements_made']
```

### Output

Returns:
- `revised_content`: Improved chapter prose
- `improvements_made`: List of improvements applied
- `analysis`: Detailed analysis of first draft
- `original_word_count`: First draft length
- `revised_word_count`: Revised version length

### When To Use

- After ProseWriterAgent generates first draft
- When quality score < 85/100
- For critical chapters (opening, climax, ending)
- When specific quality issues detected

### Model Tier

Uses **TIER 3** (Claude Opus 4.5 / GPT-4) for revision to ensure maximum quality improvement.

---

## 🎭 Character Voice Consistency Validator

**Location**: `/backend/app/agents/voice_consistency_validator.py`

### What It Does

Ensures characters sound the same throughout the entire book by validating voice consistency across chapters.

### Features

**Cross-Chapter Analysis**:
- Compares character dialogue from different chapters
- Detects voice drift (character sounds different later)
- Validates vocabulary level consistency
- Checks for signature phrases and verbal tics
- Ensures emotional speech variations match character profile

**Validation Checks**:
- Speech pattern consistency
- Vocabulary level maintenance
- Signature phrase appearance frequency
- Emotional variation appropriateness
- Educational/social background consistency

### How To Use

```python
from app.agents.voice_consistency_validator import VoiceConsistencyValidator

validator = VoiceConsistencyValidator()

# Validate character across chapters
chapters_with_dialogue = [
    {
        "chapter_number": 1,
        "dialogue_samples": [
            "— To niemożliwe — powiedziała Anna.",
            "— Muszę to sprawdzić — dodała po chwili."
        ]
    },
    {
        "chapter_number": 10,
        "dialogue_samples": [
            "— Nie wierzę w to — szepnęła Anna.",
            "— Potrzebuję więcej informacji — stwierdziła."
        ]
    }
]

report = await validator.validate_character_voice(
    character=anna_profile,
    chapters_with_dialogue=chapters_with_dialogue,
    genre="thriller"
)

consistency_score = report['consistency_score']
issues = report['inconsistencies']
```

### Output

Returns validation report with:
- `consistency_score`: 0-100 (100 = perfect consistency)
- `consistency_strengths`: What's working well
- `inconsistencies`: List of voice drift issues with specific examples
- `overall_assessment`: Summary
- `recommendations`: Actionable fixes
- `voice_drift_detected`: Boolean flag
- `voice_drift_details`: Description of how voice changed

### When To Use

- After generating multiple chapters
- Before finalizing manuscript
- When readers report character doesn't "sound right"
- As part of quality control pipeline

### Quick Comparison

For spot-checking two chapters:

```python
comparison = await validator.compare_two_chapters(
    character_name="Anna",
    chapter_early_dialogue=["..."],
    chapter_late_dialogue=["..."],
    early_chapter_num=1,
    late_chapter_num=15
)
```

---

## 🎯 Foreshadowing & Payoff Tracker

**Location**: `/backend/app/agents/plot_architect_agent.py` (integrated)

### What It Does

Ensures every Chekhov's Gun fires! Tracks all foreshadowing elements and validates that each setup has its payoff.

### 7 Types of Foreshadowing

1. **Direct Foreshadowing**: Obvious hint reader notices
2. **Subtle Foreshadowing**: Easy to miss first read, "OH!" on reread
3. **Red Herring**: False trail (Mystery/Thriller)
4. **Symbolic Foreshadowing**: Thematic objects/images
5. **Chekhov's Gun**: Object mentioned early, crucial later
6. **Prophecy/Promise**: Explicit prediction that comes true
7. **Character Skill/Knowledge**: Ability shown early, used later

### Tracking Details

Each foreshadowing element includes:
- Type
- Setup chapter number
- Setup description (specific!)
- Subtlety level (1-10 scale)
- Payoff chapter number
- Payoff description
- Time gap (chapters between setup and payoff)
- Reader impact (emotion created)
- Mandatory flag (must pay off!)

### Validation Checklist

Ensures:
- ✅ All mandatory setups have explicit payoffs
- ✅ Payoffs occur in last 25% of book
- ✅ Time gaps sufficient (minimum 3-5 chapters)
- ✅ No deus ex machina (crucial items seeded early)
- ✅ Red herrings mislead fairly
- ✅ Readers feel smart noticing connections

### Example

```json
{
  "type": "Chekhov's Gun",
  "setup_chapter": 3,
  "setup_description": "Anna notices father's old revolver in drawer",
  "subtlety_level": 4,
  "payoff_chapter": 18,
  "payoff_description": "Anna uses gun in self-defense during climax",
  "time_gap": 15,
  "reader_impact": "Satisfaction - 'Oh! The gun from chapter 3!'",
  "mandatory": true
}
```

---

## 💓 Emotional Arc Tracking

**Location**: `/backend/app/agents/plot_architect_agent.py` (integrated)

### What It Does

Maps the reader's emotional journey per chapter to optimize for addictive, can't-put-down reading.

### 14 Specific Emotions

Tracks specific emotions (not vague!):
- Curiosity, Anticipation, Anxiety, Fear
- Hope, Triumph, Devastation, Anger
- Grief, Relief, Dread, Joy
- Betrayal, Resolve

### 5 Act Checkpoints

Validates reader investment at critical points:
1. **End of Act 1**: Does reader CARE about protagonist?
2. **Midpoint**: Is reader INVESTED in outcome?
3. **End of Act 2**: Is reader DESPERATE to know what happens?
4. **Climax**: Does reader FEEL the emotional weight?
5. **Resolution**: Does reader feel SATISFIED?

### Genre-Specific Baselines

**Tension Level** (1-10) varies by genre:
- **Thriller**: Start ~6, climb to 10
- **Romance**: Start ~3, peaks at 7-8
- **Horror**: Start ~4, slow build to 9-10
- **Drama**: Start ~2, gradual to 7-8

### Emotional Variety Rule

Minimum 3 different emotions per 5-chapter span prevents monotony and reader fatigue.

---

## ✅ Scene Structure Validation

**Location**: `/backend/app/agents/plot_architect_agent.py` (integrated)

### What It Does

Eliminates filler scenes by validating every chapter has clear structure and purpose.

### Scene/Sequel Framework

**Scene** (Action chapters):
1. Goal: Character wants something
2. Conflict: Obstacles prevent it
3. Disaster: Failure OR success with bad consequences

**Sequel** (Reflection chapters):
1. Reaction: Emotional response to disaster
2. Dilemma: All options are bad
3. Decision: Choice leading to next scene

### Purpose Validation

Every chapter MUST answer YES to:
- Advances plot? (new information, events, decisions)
- **OR**
- Develops character? (personality reveal, growth, relationships)

If NO to both → **DELETE** (it's filler!)

### Causality Chain

Enforces "therefore/but" logic, prohibits "and then":
- Chapter 1 leads to Chapter 2 **because**...
- Each event **causes** the next
- No random occurrences

---

## 🎨 Prose Quality Control

**Location**: `/backend/app/agents/prose_writer_agent.py` (Section 10A)

### What It Does

Active prose polishing DURING first draft, not just editing later.

### Features

**Cliché Detection**:
- Common Polish clichés identified
- Fresh replacement suggestions
- Metaphor creation guidelines

**Repetition Awareness**:
- Word variety rules (3+ repetitions = fix)
- Paragraph-level checks
- Sentence opening variety

**Adverb Elimination**:
- Show instead of label ("gniewnie" → action)

**Word Choice Precision**:
- Generic → Specific transformations
- "Dom" → "Kamienica/willa/rudera"

**Overwriting Detection**:
- "Kill your darlings" principle
- Purple prose identification

**Self-Correction Habit**:
6 questions to ask per paragraph:
1. Any clichés? → Replace
2. Word repeated 3+ times? → Vary
3. All sentences same length? → Mix
4. Any adverbs? → Show instead
5. Too fancy/purple? → Simplify
6. Sounds awkward aloud? → Rewrite

---

## 🪝 Opening Hook & Cliffhanger Optimization

**Location**: `/backend/app/agents/prose_writer_agent.py`

### 6 Types of Killer Opening Hooks

1. **Action Hook**: Start mid-action
2. **Dialogue Hook**: Intriguing conversation
3. **Character Hook**: Compelling detail
4. **Setting Hook**: Vivid, unusual world
5. **Mystery Hook**: Question demanding answer
6. **Conflict Hook**: Stakes established immediately

**NEVER Start With**:
- ❌ Weather
- ❌ Waking up
- ❌ Alarm clocks
- ❌ Throat-clearing
- ❌ Info dumps

### 7 Types of Magnetic Cliffhangers

1. **Revelation**: Shocking discovery
2. **Decision**: Character must choose
3. **Danger**: Imminent threat
4. **Mystery**: Unanswered question
5. **Dialogue**: Shocking statement
6. **Internal**: Character realization
7. **Action**: Mid-crisis freeze

**Requirements**:
- ✅ Last sentence = maximum tension
- ✅ Raise new question OR complicate existing
- ✅ Create NEED to read next chapter
- ✅ Never fully resolve tension

---

## 📖 Genre Reader Expectations

**Location**: `/backend/app/agents/prose_writer_agent.py` (GENRE_PROSE_STYLES)

### What It Does

Ensures each genre satisfies specific reader expectations.

### 5 Expectations Per Genre

**Sci-Fi**:
- Sense of wonder
- Internal consistency (tech/science follows rules)
- Exploration of "what if?" scenarios
- Social/philosophical commentary
- Smart protagonists solving problems with logic

**Fantasy**:
- Epic scope (hero's journey, world-changing stakes)
- Magic system with clear rules and limitations
- Rich world with mythology and history
- Good vs evil (or moral complexity if subverting)
- Emotional catharsis through grand finale

**Thriller**:
- Fast pace from page 1
- Constant danger/tension
- Ticking clock (deadline)
- Major twists every 50-70 pages
- Protagonist in constant motion/action

**Horror**:
- Atmosphere over jump scares
- Isolation (characters cut off from help)
- Unknown threat scarier than seen monster
- Psychological impact on characters
- Disturbing imagery that lingers

**Romance**:
- Chemistry between leads from first meeting
- Emotional vulnerability and intimacy
- Obstacles preventing relationship (believable!)
- HEA/HFN ending (Happily Ever After or For Now)
- Emotional beats: first kiss, first fight, dark moment, reconciliation

**Drama**:
- Character transformation through adversity
- Moral/ethical dilemmas without easy answers
- Realistic human behavior and consequences
- Thematic depth - story MEANS something
- Emotional catharsis even if bittersweet

**Comedy**:
- Laugh-out-loud moments regularly
- Likeable, relatable characters (even if flawed)
- Happy ending - uplifting overall tone
- Humor from character not forced jokes
- Light stakes - fun escapism

**Mystery**:
- Fair play - reader can solve with clues given
- Red herrings that mislead without cheating
- Clever detective/sleuth with unique method
- Satisfying reveal - surprising yet logical
- All loose ends tied up in resolution

---

## 🚀 Implementation Status

All features are **IMPLEMENTED** and ready to use:

- ✅ Multi-Draft Revision System
- ✅ Voice Consistency Validator
- ✅ Foreshadowing Tracker
- ✅ Emotional Arc Tracking
- ✅ Scene Structure Validation
- ✅ Prose Quality Control
- ✅ Opening Hooks & Cliffhangers
- ✅ Genre Reader Expectations

## 📊 Quality Impact

These features collectively ensure:

1. **First Sentences Hook** - 6 types of killer openings
2. **Last Sentences Pull** - 7 types of magnetic cliffhangers
3. **Dialogue Crackles** - Subtext, unique voices, Polish EM DASHES
4. **Zero Filler** - Every scene earns its place
5. **Emotional Optimization** - Addictive reader journey
6. **Chekhov's Guns Fire** - All setups have payoffs
7. **Fresh Prose** - No clichés, active polishing
8. **Voice Consistency** - Characters sound like themselves
9. **Genre Promises Kept** - Reader expectations satisfied
10. **Revision Excellence** - Multi-draft polish to bestseller level

---

## 🎯 Result

Books generated with these features:
- Start with immediate engagement (killer hooks)
- End chapters with magnetic pull (cliffhangers)
- Maintain consistent character voices
- Have tight, purposeful structure (no filler)
- Track reader emotional journey optimally
- Pay off all foreshadowing (no hanging threads)
- Use fresh, polished prose (no clichés)
- Can go through multiple drafts (revision system)
- Satisfy genre-specific reader expectations

**Quality Level**: Publication-ready, bestseller-competitive fiction.
