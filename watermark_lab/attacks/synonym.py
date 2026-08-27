import random
import re
from typing import Dict

DEFAULT_SYNONYMS = {
    "important": ["significant", "notable"],
    "quick": ["fast", "rapid"],
    "small": ["little", "compact"],
    "large": ["big", "substantial"],
    "use": ["utilize", "employ"],
    "show": ["display", "demonstrate"],
    "make": ["create", "produce"],
    "help": ["assist", "support"],
}


def replace_synonyms(text: str, probability: float = 0.25, seed: int = 0,
                     lexicon: Dict[str, list] = None) -> str:
    """Apply a small, transparent lexicon-based paraphrase perturbation."""

    if not 0 <= probability <= 1:
        raise ValueError("probability must be between 0 and 1")
    choices = lexicon or DEFAULT_SYNONYMS
    rng = random.Random(seed)

    def replace(match):
        word = match.group(0)
        options = choices.get(word.lower())
        if not options or rng.random() >= probability:
            return word
        replacement = rng.choice(options)
        return replacement.capitalize() if word[0].isupper() else replacement

    return re.sub(r"[A-Za-z]+", replace, text)
