"""Deterministic green-list construction shared by generation and detection."""

import hashlib
import random
from typing import List


def seed_for_token(secret: str, previous_token_id: int, hash_name: str = "sha256") -> int:
    """Derive a stable PRNG seed from the private key and token context."""

    material = f"{secret}:{previous_token_id}".encode("utf-8")
    digest = hashlib.new(hash_name, material).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def greenlist(token_count: int, secret: str, previous_token_id: int,
              ratio: float = 0.5, hash_name: str = "sha256") -> List[int]:
    """Return the deterministic subset of token IDs allowed by the watermark."""

    if token_count < 2:
        raise ValueError("token_count must be at least 2")
    if not 0 < ratio < 1:
        raise ValueError("ratio must be between 0 and 1")
    count = max(1, min(token_count - 1, int(token_count * ratio)))
    candidates = list(range(token_count))
    seed = seed_for_token(secret, previous_token_id, hash_name)
    random.Random(seed).shuffle(candidates)
    return candidates[:count]


def is_green(token_id: int, token_count: int, secret: str, previous_token_id: int,
             ratio: float = 0.5, hash_name: str = "sha256") -> bool:
    return token_id in greenlist(token_count, secret, previous_token_id, ratio, hash_name)
