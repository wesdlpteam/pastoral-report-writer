from word_count import count_words, get_range, is_in_range


def test_count_words_basic():
    assert count_words("This is five words total") == 5


def test_count_words_empty_string():
    assert count_words("") == 0


def test_count_words_extra_whitespace():
    assert count_words("  word   another   ") == 2


def test_get_range_tutor():
    assert get_range("tutor") == (100, 150)


def test_get_range_pyp():
    assert get_range("pyp") == (180, 300)


def test_is_in_range_true():
    assert is_in_range(120, "tutor") is True


def test_is_in_range_false_below():
    assert is_in_range(50, "tutor") is False


def test_is_in_range_false_above():
    assert is_in_range(200, "tutor") is False


def test_is_in_range_boundary_inclusive():
    assert is_in_range(100, "tutor") is True
    assert is_in_range(150, "tutor") is True
