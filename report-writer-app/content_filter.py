import re

BAD_WORDS = {
    "fuck", "fucking", "fucker", "shit", "shitty", "bitch", "bastard",
    "asshole", "ass", "dick", "piss", "cunt", "cock", "prick", "wanker",
    "twat", "slut", "whore", "retard", "retarded", "faggot", "fag",
    "nigger", "nigga", "spastic", "crap", "bloody", "bugger", "arse",
    "douche", "douchebag", "motherfucker",
}

KEYBOARD_MASH_PATTERNS = ["asdf", "qwert", "zxcv", "hjkl", "jklm", "qazwsx", "wasdw"]
VOWELS = set("aeiouy")


def find_bad_words(text: str) -> list:
    lower = text.lower()
    return [word for word in BAD_WORDS if re.search(r"\b" + re.escape(word) + r"\b", lower)]


def _is_gibberish_word(word: str) -> bool:
    clean = re.sub(r"[^a-zA-Z]", "", word).lower()
    if len(clean) < 3:
        return False
    if re.search(r"(.)\1{3,}", clean):
        return True
    if len(clean) >= 4 and not any(c in VOWELS for c in clean):
        return True
    return any(pattern in clean for pattern in KEYBOARD_MASH_PATTERNS)


def find_gibberish_words(text: str) -> list:
    return [word for word in text.split() if _is_gibberish_word(word)]


def has_low_word_diversity(text: str) -> bool:
    words = [w.lower() for w in text.split()]
    if len(words) < 5:
        return False
    distinct = len(set(words))
    return (distinct / len(words)) <= 0.4


COMMON_CAPITALIZED_WORDS = {
    "i", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december",
    "term", "semester", "wesley", "college", "house", "tutor", "group",
    "english", "maths", "mathematics", "science", "pe", "art", "music", "drama",
    "hass", "hpe", "naplan", "ib", "pyp", "myp", "dp",
    "adamson", "corrigan", "irving", "way",
    "roar", "respect", "opportunity", "achievement", "resilience",
    "inquirer", "knowledgeable", "thinker", "communicator", "principled",
    "caring", "balanced", "reflective",
    # common sentence-starting words, so ordinary writing isn't flagged
    "he", "she", "they", "it", "this", "that", "these", "those", "his", "her",
    "their", "its", "the", "a", "an", "when", "while", "during", "after",
    "before", "although", "since", "as", "overall", "throughout", "recently",
    "despite", "in", "on", "at", "with", "sometimes", "often", "generally",
    "occasionally", "however", "also", "both", "even", "given", "due",
    "because", "whenever", "once", "unless", "whether", "each", "every",
    "some", "most", "many", "several", "all", "there", "here", "we", "you",
    "if", "so", "and", "but", "yet", "still", "then", "though", "having",
}


def _looks_like_name(word: str) -> bool:
    clean = re.sub(r"[^A-Za-z]", "", word)
    if not re.match(r"^[A-Z][a-z]+$", clean):
        return False
    return clean.lower() not in COMMON_CAPITALIZED_WORDS


def find_possible_names(text: str) -> list:
    return [word for word in text.split() if _looks_like_name(word)]
