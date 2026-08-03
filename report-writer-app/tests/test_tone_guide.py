from tone_guide import find_tempered_words


def test_find_tempered_words_detects_trigger_word():
    answers = {"person": "He can be rude to his peers sometimes."}
    assert find_tempered_words(answers) == ["rude"]


def test_find_tempered_words_no_match():
    answers = {"person": "Kind and thoughtful.", "learner": "Improving steadily."}
    assert find_tempered_words(answers) == []


def test_find_tempered_words_whole_word_only():
    answers = {"person": "He is a rudimentary reader but improving."}
    assert find_tempered_words(answers) == []


def test_find_tempered_words_multiple_matches():
    answers = {"person": "Lazy and messy with his belongings."}
    found = find_tempered_words(answers)
    assert "lazy" in found
    assert "messy" in found
