from watermark_lab.attacks import add_noise, reorder_sentences, replace_synonyms, truncate


def test_attacks_are_deterministic_and_bounded():
    text = "This is important. The quick method can help."
    assert replace_synonyms(text, 1, seed=7) == replace_synonyms(text, 1, seed=7)
    assert reorder_sentences(text).startswith("The quick")
    assert truncate(text, 0.5).split() == text.split()[-4:]
    assert add_noise(text, 1, seed=7) == add_noise(text, 1, seed=7)
