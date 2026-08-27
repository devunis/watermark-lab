import random
import re


def add_noise(text: str, probability: float = 0.05, seed: int = 0) -> str:
    """Add mild whitespace/typo noise for detector robustness experiments."""

    if not 0 <= probability <= 1:
        raise ValueError("probability must be between 0 and 1")
    rng = random.Random(seed)
    output = []
    for char in text:
        if char == " " and rng.random() < probability:
            output.append("  " if rng.random() < 0.5 else "")
        elif char.isalpha() and rng.random() < probability / 3:
            output.append(char + char)
        else:
            output.append(char)
    return re.sub(r" {3,}", "  ", "".join(output))
