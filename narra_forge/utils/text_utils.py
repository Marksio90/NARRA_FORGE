"""
Text utilities for NARRA_FORGE V2

Utilities for text processing, encoding fixes, etc.
"""


def fix_polish_encoding(text: str) -> str:
    """
    Fix common UTF-8 mojibake issues with Polish characters.

    Sometimes OpenAI returns text with incorrect encoding interpretation.
    This function fixes common patterns.

    Args:
        text: Input text with potential encoding issues

    Returns:
        Fixed text with correct Polish characters
    """
    # Common UTF-8 to Latin1 mojibake patterns for Polish characters
    # Using only safe patterns that don't cause syntax errors
    replacements = {
        # ą - most common
        "Ä…": "ą",
        "Ä„": "Ą",
        # ć
        "Ä‡": "ć",
        # ę
        "Ä™": "ę",
        # ł
        "Ĺ‚": "ł",
        "Ĺ": "Ł",
        # ń
        "Ĺ„": "ń",
        "Ĺƒ": "Ń",
        # ś
        "Ĺ›": "ś",
        "Ĺš": "Ś",
        # ź/ż (same mojibake pattern unfortunately)
        "ĹĽ": "ż",  # More common
        "Ĺ»": "Ż",
        # Common multi-character patterns
        "ciÄ™ĹĽ": "cięż",
        "ĹĽyc": "życ",
        "pamiÄ™": "pamię",
        "gĹ‚": "gł",
        "dĹ‚": "dł",
        "wĹ‚": "wł",
        "Ĺ›w": "św",
        # Additional single patterns
        "sunÄ…Ĺ‚": "sunął",
        "byĹ‚": "był",
        "wiedziaĹ‚": "wiedział",
        "musiaĹ‚": "musiał",
    }

    fixed_text = text
    for wrong, correct in replacements.items():
        fixed_text = fixed_text.replace(wrong, correct)

    return fixed_text


def ensure_utf8_response(text: str) -> str:
    """
    Ensure text is properly UTF-8 encoded.

    Attempts to fix mojibake by re-encoding if needed.

    Args:
        text: Input text

    Returns:
        Properly encoded UTF-8 text
    """
    try:
        # Try to detect if we have mojibake by looking for common patterns
        if any(pattern in text for pattern in ["Ä…", "Ä™", "Ĺ›", "Ä‡", "Ĺ‚", "Ĺ„", "ĹĽ"]):
            # We likely have mojibake - apply fixes
            return fix_polish_encoding(text)

        # Text looks OK
        return text
    except Exception:
        # If anything fails, return original
        return text


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

    - Removes trailing whitespace
    - Normalizes multiple spaces to single
    - Fixes paragraph spacing

    Args:
        text: Input text

    Returns:
        Normalized text
    """
    lines = []
    for line in text.split('\n'):
        # Strip trailing whitespace
        line = line.rstrip()
        lines.append(line)

    # Join and normalize multiple newlines
    text = '\n'.join(lines)

    # Fix excessive blank lines (max 2 consecutive)
    import re
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    return text


def clean_narrative_text(text: str) -> str:
    """
    Clean narrative text for output.

    - Fixes encoding issues
    - Normalizes whitespace
    - Removes artifacts

    Args:
        text: Raw narrative text

    Returns:
        Cleaned text ready for output
    """
    # Fix encoding
    text = ensure_utf8_response(text)

    # Normalize whitespace
    text = normalize_whitespace(text)

    # Remove any potential BOM or other artifacts
    text = text.replace('\ufeff', '')  # BOM
    text = text.replace('\r\n', '\n')  # Windows line endings
    text = text.replace('\r', '\n')     # Old Mac line endings

    return text


# ═══════════════════════════════════════════════════════════
# QUALITY CONTROL: Cliché Detection & Repetition Analysis
# ═══════════════════════════════════════════════════════════

# Banned clichés list (from Agent 06 system prompt)
BANNED_CLICHES = [
    # Metaphor clichés
    "jak młot",
    "waliło jak młot",
    "biło jak młot",
    "krew zamarzła",
    "mroziło krew",
    "mroziło w żyłach",
    "struna gotowa do pęknięcia",
    "studnie pełne tajemnic",
    "studnia pełna tajemnic",
    "dziki ogień",
    "kaskadą",
    "spływał kaskadą",
    "ściekał kaskadą",
    "kusiła go jak nic",
    "kusiło go jak nic",
    "cienie tańczyły",
    "cień tańczył",
    "jak żywe",

    # Weak words
    "tajemniczy",
    "tajemnicza",
    "tajemnicze",
    "mroczny",
    "mroczna",
    "mroczne",
]


def detect_cliches(text: str) -> list[dict]:
    """
    Detect banned clichés in text.

    Returns list of detected clichés with their positions.

    Args:
        text: Text to analyze

    Returns:
        List of dicts with: {'cliche': str, 'count': int, 'positions': list[int]}
    """
    text_lower = text.lower()
    detected = []

    for cliche in BANNED_CLICHES:
        count = text_lower.count(cliche)
        if count > 0:
            # Find all positions
            positions = []
            start = 0
            while True:
                pos = text_lower.find(cliche, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1

            detected.append({
                'cliche': cliche,
                'count': count,
                'positions': positions,
            })

    return detected


def detect_repetitions(text: str, threshold: int = 3) -> dict:
    """
    Detect repetitive phrases and words in text.

    Analyzes:
    - "wiedział, że" / "czuł, że" constructions
    - "jakby" overuse
    - "serce biło/waliło" repetitions
    - Common word repetitions

    Args:
        text: Text to analyze
        threshold: Max acceptable count for flagging (default: 3)

    Returns:
        Dict with repetition analysis:
        {
            'high_risk': list of severely overused phrases,
            'warnings': list of moderately overused phrases,
            'stats': dict with counts
        }
    """
    import re

    text_lower = text.lower()
    word_count = len(text.split())

    # Count specific constructions
    stats = {
        'wiedział_że': len(re.findall(r'\bwiedział,?\s+że\b', text_lower)),
        'czuł_że': len(re.findall(r'\bczuł,?\s+że\b', text_lower)),
        'jakby': text_lower.count('jakby'),
        'serce_biło': text_lower.count('serce biło') + text_lower.count('serce waliło'),
        'niczym': text_lower.count('niczym'),
    }

    # Calculate per-1000-words rates
    if word_count > 0:
        rate_multiplier = 1000.0 / word_count
        stats['wiedział_że_per_1k'] = stats['wiedział_że'] * rate_multiplier
        stats['jakby_per_1k'] = stats['jakby'] * rate_multiplier

    # Flag issues
    high_risk = []
    warnings = []

    # "wiedział, że" - should be max 2x per 1000 words
    if word_count >= 1000 and stats['wiedział_że'] > 2:
        high_risk.append(f"'wiedział, że' używane {stats['wiedział_że']}x (limit: 2x/1000 słów)")
    elif word_count < 1000 and stats['wiedział_że'] > 1:
        warnings.append(f"'wiedział, że' używane {stats['wiedział_że']}x (zalecane: 1x max dla krótkiego tekstu)")

    # "jakby" - should be max 3x per 1000 words
    if word_count >= 1000 and stats['jakby'] > 3:
        high_risk.append(f"'jakby' używane {stats['jakby']}x (limit: 3x/1000 słów)")
    elif word_count < 1000 and stats['jakby'] > 2:
        warnings.append(f"'jakby' używane {stats['jakby']}x")

    # "serce biło/waliło" - should be 1x max per story
    if stats['serce_biło'] > 1:
        high_risk.append(f"'serce biło/waliło' używane {stats['serce_biło']}x (limit: 1x per story!)")

    # "niczym" - should be limited
    if stats['niczym'] > 3:
        warnings.append(f"'niczym' używane {stats['niczym']}x (lepiej limitować)")

    return {
        'high_risk': high_risk,
        'warnings': warnings,
        'stats': stats,
    }


def analyze_text_quality(text: str) -> dict:
    """
    Comprehensive text quality analysis.

    Combines cliché detection and repetition analysis.

    Args:
        text: Text to analyze

    Returns:
        Dict with quality report:
        {
            'passed': bool,
            'cliches': list,
            'repetitions': dict,
            'issues_count': int,
            'quality_score': float (0.0-1.0)
        }
    """
    cliches = detect_cliches(text)
    repetitions = detect_repetitions(text)

    # Count total issues
    issues_count = (
        len(cliches) +
        len(repetitions['high_risk']) +
        len(repetitions['warnings'])
    )

    # Calculate quality score (simple heuristic)
    # Start at 1.0, deduct for issues
    quality_score = 1.0
    quality_score -= len(cliches) * 0.05  # Each cliché: -0.05
    quality_score -= len(repetitions['high_risk']) * 0.10  # High risk: -0.10
    quality_score -= len(repetitions['warnings']) * 0.03  # Warning: -0.03
    quality_score = max(0.0, quality_score)

    # Pass if quality_score >= 0.85
    passed = quality_score >= 0.85

    return {
        'passed': passed,
        'cliches': cliches,
        'repetitions': repetitions,
        'issues_count': issues_count,
        'quality_score': quality_score,
    }
