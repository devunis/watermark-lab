from watermark_lab.seeding import greenlist, seed_for_position


def test_seed_and_greenlist_are_deterministic():
    assert seed_for_position("secret", 3, 4) == seed_for_position("secret", 3, 4)
    assert greenlist(100, "secret", 3, 4) == greenlist(100, "secret", 3, 4)
    assert greenlist(100, "secret", 3, 4) != greenlist(100, "other", 3, 4)


def test_greenlist_size_is_controlled_by_ratio():
    values = greenlist(10, "secret", 3, ratio=0.3)
    assert len(values) == 3
    assert len(set(values)) == 3
