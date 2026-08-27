from dataclasses import dataclass
from typing import Callable, Dict

from .detector import WatermarkDetector


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    text: str
    result: dict


def run_benchmark(text: str, tokenizer, detector: WatermarkDetector,
                  attacks: Dict[str, Callable[[str], str]]) -> dict:
    """Compare original and attacked text using the same detector configuration."""

    original = detector.detect_text(text, tokenizer).as_dict()
    cases = []
    for name, attack in attacks.items():
        edited = attack(text)
        result = detector.detect_text(edited, tokenizer).as_dict()
        cases.append({
            "name": name,
            "result": result,
            "signal_drop": round(original["z_score"] - result["z_score"], 6),
        })
    detected_count = sum(case["result"]["detected"] for case in cases)
    return {
        "original": original,
        "cases": cases,
        "attacks_total": len(cases),
        "detected_after_attack": detected_count,
        "detection_rate_after_attack": detected_count / len(cases) if cases else 0.0,
    }
