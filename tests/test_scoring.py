from watermark_lab.scoring import score_signal


def test_green_heavy_signal_is_detected():
    result = score_signal([True] * 80 + [False] * 20, threshold=4, min_tokens=20)
    assert result.detected
    assert result.z_score > 5


def test_balanced_signal_is_not_detected():
    result = score_signal(([True, False] * 50), threshold=4, min_tokens=20)
    assert not result.detected
    assert result.z_score == 0


def test_short_signal_is_not_detected_even_when_green_heavy():
    result = score_signal([True] * 10, threshold=1, min_tokens=20)
    assert not result.detected
