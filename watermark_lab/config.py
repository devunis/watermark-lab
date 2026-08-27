from dataclasses import dataclass


@dataclass(frozen=True)
class WatermarkConfig:
    """Shared parameters that must match between generation and detection."""

    secret: str
    gamma: float = 0.5
    delta: float = 2.0
    z_threshold: float = 4.0
    greenlist_ratio: float = 0.5
    min_tokens: int = 20
    hash_name: str = "sha256"

    def __post_init__(self) -> None:
        if not self.secret:
            raise ValueError("secret must not be empty")
        if not 0 < self.gamma < 1:
            raise ValueError("gamma must be between 0 and 1")
        if self.delta < 0:
            raise ValueError("delta must be non-negative")
        if self.z_threshold < 0:
            raise ValueError("z_threshold must be non-negative")
        if not 0 < self.greenlist_ratio < 1:
            raise ValueError("greenlist_ratio must be between 0 and 1")
        if self.min_tokens < 1:
            raise ValueError("min_tokens must be positive")
