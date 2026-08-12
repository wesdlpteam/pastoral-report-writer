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
