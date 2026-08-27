"""Hugging Face integration for inserting the self-owned watermark during sampling."""

from typing import Any, Optional

from .config import WatermarkConfig
from .seeding import greenlist

try:
    from transformers import LogitsProcessor
except ImportError:  # pragma: no cover - exercised only without optional runtime deps
    class LogitsProcessor:  # type: ignore
        pass


class WatermarkLogitsProcessor(LogitsProcessor):
    """Bias green-list logits so generated tokens carry a reproducible signal."""

    def __init__(self, config: WatermarkConfig, vocab_size: int):
        self.config = config
        self.vocab_size = vocab_size

    def __call__(self, input_ids: Any, scores: Any) -> Any:
        batch_size = input_ids.shape[0]
        for row in range(batch_size):
            previous = int(input_ids[row, -1].item())
            allowed = greenlist(self.vocab_size, self.config.secret, previous,
                                position=int(input_ids.shape[1]), ratio=self.config.greenlist_ratio,
                                hash_name=self.config.hash_name)
            scores[row, allowed] += self.config.delta
        return scores


def generate_text(prompt: str, model_name: str, config: WatermarkConfig,
                  max_new_tokens: int = 128, temperature: float = 0.8,
                  top_p: float = 0.95, seed: Optional[int] = None) -> str:
    """Generate text with a local Hugging Face causal language model."""

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, LogitsProcessorList
    except ImportError as exc:
        raise RuntimeError("Install the project dependencies to use generation") from exc

    if seed is not None:
        torch.manual_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    inputs = tokenizer(prompt, return_tensors="pt")
    processor = WatermarkLogitsProcessor(config, int(model.config.vocab_size))
    output = model.generate(
        **inputs,
        do_sample=True,
        temperature=temperature,
        top_p=top_p,
        max_new_tokens=max_new_tokens,
        logits_processor=LogitsProcessorList([processor]),
        pad_token_id=tokenizer.eos_token_id,
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)
