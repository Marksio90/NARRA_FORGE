"""
NarraForge Prompt Engineering System

Moduły:
- agent_prompts: System prompts for all 8 specialized agents
- narrative_anti_patterns: Detection and prevention of narrative pathologies
- divine_prompts: Three-module "Divine Prompt" system for bestseller-quality prose

Based on the analysis: "Algorytmiczna Architektura Narracji: Kompleksowa Analiza
Patologii Generatywnych oraz Strategie Inżynierii Promptów dla Osiągnięcia
Literackiej Jakości Klasy Bestsellera"
"""

from app.prompts.agent_prompts import (
    get_agent_prompt,
    ORCHESTRATOR_PROMPT,
    WORLD_ARCHITECT_PROMPT,
    CHARACTER_SMITH_PROMPT,
    PLOT_MASTER_PROMPT,
    PROSE_WEAVER_PROMPT,
    CONTINUITY_GUARDIAN_PROMPT,
    STYLE_MASTER_PROMPT,
    GENRE_EXPERT_PROMPT,
    GENRE_CONVENTIONS,
)

from app.prompts.narrative_anti_patterns import (
    FORBIDDEN_OPENING_PHRASES,
    FORBIDDEN_CLICHES,
    FORBIDDEN_DIALOGUE_PATTERNS,
    FORBIDDEN_TROPES,
    REQUIRED_PROGRESS_MARKERS,
    BURSTINESS_RULES,
    PERPLEXITY_RULES,
    NarrativeAntiPatternValidator,
    generate_character_lock_prompt,
    generate_negative_constraints_prompt,
    get_full_anti_pattern_prompt,
)

from app.prompts.divine_prompts import (
    DivinePromptModule,
    DivinePromptSystem,
    ARCHITECT_SYSTEM_PROMPT,
    EDITOR_SYSTEM_PROMPT,
    get_architect_prompt,
    get_writer_system_prompt,
    get_writer_prompt,
    get_editor_prompt,
    get_divine_prompt_system,
)

__all__ = [
    # Agent prompts
    'get_agent_prompt',
    'ORCHESTRATOR_PROMPT',
    'WORLD_ARCHITECT_PROMPT',
    'CHARACTER_SMITH_PROMPT',
    'PLOT_MASTER_PROMPT',
    'PROSE_WEAVER_PROMPT',
    'CONTINUITY_GUARDIAN_PROMPT',
    'STYLE_MASTER_PROMPT',
    'GENRE_EXPERT_PROMPT',
    'GENRE_CONVENTIONS',

    # Narrative anti-patterns
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

    # Divine prompts
    'DivinePromptModule',
    'DivinePromptSystem',
    'ARCHITECT_SYSTEM_PROMPT',
    'EDITOR_SYSTEM_PROMPT',
    'get_architect_prompt',
    'get_writer_system_prompt',
    'get_writer_prompt',
    'get_editor_prompt',
    'get_divine_prompt_system',
]
