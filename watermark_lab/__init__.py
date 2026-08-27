"""Research tooling for a self-owned text watermark scheme."""

from .config import WatermarkConfig
from .detector import WatermarkDetector
from .scoring import DetectionResult

__all__ = ["DetectionResult", "WatermarkConfig", "WatermarkDetector"]
