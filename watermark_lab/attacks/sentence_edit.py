import re


def reorder_sentences(text: str, mode: str = "reverse") -> str:
    """Reorder sentences as a structural robustness test."""

    if mode not in {"reverse", "rotate"}:
        raise ValueError("mode must be 'reverse' or 'rotate'")
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]
    if len(sentences) < 2:
        return text
    if mode == "reverse":
        edited = list(reversed(sentences))
    else:
        edited = sentences[1:] + sentences[:1]
    return " ".join(edited)
