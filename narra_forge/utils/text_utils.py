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
    replacements = {
        # ą
        "Ä…": "ą",
        "Ä„": "Ą",
        # ć
        "Ä‡": "ć",
        "Ć": "Ć",
        # ę
        "Ä™": "ę",
        "Ę": "Ę",
        # ł
        "Ĺ‚": "ł",
        "Ĺ": "Ł",
        # ń
        "Ĺ„": "ń",
        "Ĺƒ": "Ń",
        # ó
        "Ăł": "ó",
        "Ă"": "Ó",
        # ś
        "Ĺ›": "ś",
        "Ĺš": "Ś",
        # ź
        "ĹĽ": "ź",
        "Ĺą": "Ź",
        # ż
        "ĹĽ": "ż",
        "Ĺ»": "Ż",
        # Additional common patterns
        "Ä™": "ę",
        "Ä…": "ą",
        "Ĺ›": "ś",
        "ciÄ™ĹĽ": "ciężkie",
        "ĹĽyc": "życ",
        "pamiÄ™": "pamię",
        "gĹ‚": "gł",
        "dĹ‚": "dł",
        "wĹ‚": "wł",
        "Ĺ›w": "św",
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
