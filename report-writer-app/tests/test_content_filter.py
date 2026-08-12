from content_filter import find_bad_words


def test_finds_bad_word_in_sentence():
    assert find_bad_words("this is such a shit attitude") == ["shit"]


def test_no_bad_words_in_clean_sentence():
    assert find_bad_words("shows great resilience and effort this term") == []


def test_does_not_flag_substring_matches():
    assert find_bad_words("the class assessment went well") == []
