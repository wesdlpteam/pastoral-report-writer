from content_filter import (
    find_bad_words,
    find_gibberish_words,
    find_possible_names,
    has_low_word_diversity,
)


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


def test_flags_repeated_word_spam():
    assert has_low_word_diversity("poo poo poo poo poo") is True


def test_flags_alternating_repeated_words():
    assert has_low_word_diversity("poo bum poo bum poo") is True


def test_does_not_flag_genuine_sentence():
    assert has_low_word_diversity("shows great resilience and effort this term") is False


def test_does_not_flag_short_answers():
    assert has_low_word_diversity("poo poo poo") is False


def test_does_not_flag_natural_repetition():
    assert has_low_word_diversity("he is a lovely, lovely student") is False


def test_finds_name_at_start_of_sentence():
    assert find_possible_names("Jordan is a resilient and kind student.") == ["Jordan"]


def test_finds_name_mid_sentence():
    assert find_possible_names("The student is resilient, and Alex handled it well.") == ["Alex"]


def test_does_not_flag_genuine_sentence():
    text = (
        "The student handled it well, and their friend was there. "
        "When things got hard, they kept trying. He showed real resilience."
    )
    assert find_possible_names(text) == []


def test_does_not_flag_wesley_specific_terms():
    text = "In Term 2, they joined House Adamson and enjoyed Maths class."
    assert find_possible_names(text) == []
