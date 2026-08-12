from content_filter import find_bad_words, find_gibberish_words


def test_finds_bad_word_in_sentence():
    assert find_bad_words("this is such a shit attitude") == ["shit"]


def test_no_bad_words_in_clean_sentence():
    assert find_bad_words("shows great resilience and effort this term") == []


def test_does_not_flag_substring_matches():
    assert find_bad_words("the class assessment went well") == []


def test_finds_keyboard_mash():
    assert find_gibberish_words("asdfgh asdfgh asdfgh really good") == ["asdfgh", "asdfgh", "asdfgh"]


def test_finds_repeated_characters():
    assert find_gibberish_words("aaaaaaa is doing well this term") == ["aaaaaaa"]


def test_finds_no_vowel_word():
    assert find_gibberish_words("bcdfg is a strong student") == ["bcdfg"]


def test_no_gibberish_in_clean_sentence():
    assert find_gibberish_words("shows great resilience and effort this term") == []


def test_does_not_flag_real_words_without_common_vowels():
    assert find_gibberish_words("rhythm and sync are strong for them") == []
