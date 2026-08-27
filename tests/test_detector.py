from watermark_lab.config import WatermarkConfig
from watermark_lab.detector import WatermarkDetector
from watermark_lab.seeding import greenlist


def test_detector_recovers_signal_from_self_generated_ids():
    config = WatermarkConfig("test-secret", delta=4, min_tokens=10)
    detector = WatermarkDetector(config)
    token_ids = [1]
    for _ in range(1, 100):
        token_ids.append(greenlist(100, config.secret, token_ids[-1],
                                   config.greenlist_ratio, config.hash_name)[0])
    result = detector.detect_ids(token_ids, 100)
    assert result.detected


def test_wrong_secret_does_not_recover_signal():
    config = WatermarkConfig("test-secret", min_tokens=10)
    detector = WatermarkDetector(config)
    token_ids = [1]
    for _ in range(1, 100):
        token_ids.append(greenlist(100, "different-secret", token_ids[-1])[0])
    result = detector.detect_ids(token_ids, 100)
    assert not result.detected


def test_generation_bias_and_detection_threshold_are_independent():
    config = WatermarkConfig("test-secret", delta=9.0, z_threshold=100.0, min_tokens=20)
    detector = WatermarkDetector(config)
    token_ids = [1]
    for _ in range(1, 60):
        token_ids.append(greenlist(100, config.secret, token_ids[-1])[0])
    result = detector.detect_ids(token_ids, 100)
    assert result.z_score > 4.0
    assert not result.detected
