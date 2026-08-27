import random
import re
from typing import Dict


def replace_selected_words(
    text: str,
    replacements: Dict[str, str],
    probability: float = 0.25,
    seed: int = 0,
) -> str:
    """Replace user-selected words while preserving surrounding punctuation."""

    if not 0 <= probability <= 1:
        raise ValueError("probability must be between 0 and 1")
    if not replacements:
        raise ValueError("replacements must not be empty")
    normalized = {
        source.casefold(): target
        for source, target in replacements.items()
        if source.strip() and target.strip()
    }
    if not normalized:
        raise ValueError("replacements must contain non-empty words")
    rng = random.Random(seed)

    def replace(match):
        word = match.group(0)
        replacement = normalized.get(word.casefold())
        if replacement is None or rng.random() >= probability:
            return word
        if word.isupper():
            return replacement.upper()
        if word.istitle():
            return replacement[:1].upper() + replacement[1:]
        return replacement

    return re.sub(r"[^\W\d_]+", replace, text, flags=re.UNICODE)
