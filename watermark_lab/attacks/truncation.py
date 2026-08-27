

def truncate(text: str, fraction: float = 0.75, from_end: bool = True) -> str:
    """Keep a fraction of the text to simulate clipping or partial copying."""

    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    words = text.split()
    count = max(1, int(len(words) * fraction)) if words else 0
    kept = words[-count:] if from_end else words[:count]
    return " ".join(kept)
