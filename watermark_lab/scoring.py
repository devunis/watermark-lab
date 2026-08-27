"""Statistical scoring for the binary green/red token signal."""

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class DetectionResult:
    detected: bool
    confidence: float
    z_score: float
    p_value: float
    green_count: int
    tokens_analyzed: int
    green_fraction: float

    def as_dict(self):
        return {
            "detected": self.detected,
            "watermarked": self.detected,
            "confidence": round(self.confidence, 6),
            "z_score": round(self.z_score, 6),
            "p_value": round(self.p_value, 8),
            "green_count": self.green_count,
            "tokens_analyzed": self.tokens_analyzed,
            "green_fraction": round(self.green_fraction, 6),
        }


def _normal_upper_tail(z_score: float) -> float:
    return 0.5 * math.erfc(z_score / math.sqrt(2.0))


def score_signal(signal: Iterable[bool], gamma: float = 0.5, threshold: float = 4.0,
                 min_tokens: int = 20) -> DetectionResult:
    """Score a sequence of green/red observations with a one-sided z-test."""

    observations = [bool(value) for value in signal]
    total = len(observations)
    green = sum(observations)
    fraction = green / total if total else 0.0
    if total == 0:
        z_score = 0.0
        p_value = 1.0
    else:
        denominator = math.sqrt(total * gamma * (1.0 - gamma))
        z_score = (green - gamma * total) / denominator
        p_value = _normal_upper_tail(z_score)
    confidence = min(1.0, max(0.0, 1.0 - p_value))
    return DetectionResult(
        detected=total >= min_tokens and z_score >= threshold,
        confidence=confidence,
        z_score=z_score,
        p_value=p_value,
        green_count=green,
        tokens_analyzed=total,
        green_fraction=fraction,
    )


def segment_scores(signal: Sequence[bool], window: int = 50, step: int = 25,
                   gamma: float = 0.5, threshold: float = 4.0,
                   min_tokens: int = 20) -> List[DetectionResult]:
    """Return overlapping local scores to reveal where signal survives editing."""

    if window < 1 or step < 1:
        raise ValueError("window and step must be positive")
    return [
        score_signal(signal[start:start + window], gamma, threshold, min_tokens)
        for start in range(0, max(0, len(signal) - window + 1), step)
    ]
