from watermark_lab.attacks import (
    add_noise,
    reorder_sentences,
    replace_selected_words,
    replace_synonyms,
    truncate,
)


def test_attacks_are_deterministic_and_bounded():
    text = "This is important. The quick method can help."
    assert replace_synonyms(text, 1, seed=7) == replace_synonyms(text, 1, seed=7)
    assert reorder_sentences(text).startswith("The quick")
    assert truncate(text, 0.5).split() == text.split()[-4:]
    assert add_noise(text, 1, seed=7) == add_noise(text, 1, seed=7)


def test_selected_word_replacement_supports_korean_and_case():
    text = "중요한 연구 and Important WATERMARK research."
    result = replace_selected_words(
        text,
        {"중요한": "핵심적인", "연구": "실험", "important": "notable", "watermark": "signal"},
        probability=1,
        seed=7,
    )
    assert result == "핵심적인 실험 and Notable SIGNAL research."
