from typing import Any, List, Sequence

from .config import WatermarkConfig
from .scoring import DetectionResult, score_signal, segment_scores
from .seeding import is_green


class WatermarkDetector:
    """Detect only the watermark generated with the matching private configuration."""

    def __init__(self, config: WatermarkConfig):
        self.config = config

    def token_signal(self, token_ids: Sequence[int], vocab_size: int) -> List[bool]:
        if vocab_size < 2:
            raise ValueError("vocab_size must be at least 2")
        return [
            is_green(
                token_id=current,
                token_count=vocab_size,
                secret=self.config.secret,
                previous_token_id=token_ids[index - 1],
                ratio=self.config.greenlist_ratio,
                hash_name=self.config.hash_name,
            )
            for index, current in enumerate(token_ids)
            if index > 0
        ]

    def detect_ids(self, token_ids: Sequence[int], vocab_size: int) -> DetectionResult:
        return score_signal(self.token_signal(token_ids, vocab_size), self.config.gamma,
                            self.config.z_threshold, self.config.min_tokens)

    def detect_text(self, text: str, tokenizer: Any) -> DetectionResult:
        token_ids = tokenizer.encode(text, add_special_tokens=False)
        vocab_size = getattr(tokenizer, "vocab_size", None)
        if vocab_size is None:
            vocab_size = len(tokenizer)
        return self.detect_ids(token_ids, vocab_size)

    def local_scores(self, token_ids: Sequence[int], vocab_size: int, window: int = 50,
                     step: int = 25):
        return segment_scores(self.token_signal(token_ids, vocab_size), window, step,
                              self.config.gamma, self.config.z_threshold,
                              self.config.min_tokens)
