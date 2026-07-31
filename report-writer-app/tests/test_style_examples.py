from style_examples import TUTOR_EXAMPLES


def test_tutor_examples_not_empty():
    assert len(TUTOR_EXAMPLES) >= 4


def test_tutor_examples_are_strings():
    assert all(isinstance(example, str) for example in TUTOR_EXAMPLES)


def test_tutor_examples_use_placeholder():
    for example in TUTOR_EXAMPLES:
        assert "[student name]" in example


def test_tutor_examples_no_real_names_leak():
    banned_names = ["Alistair", "Chloe"]
    for example in TUTOR_EXAMPLES:
        for name in banned_names:
            assert name not in example
