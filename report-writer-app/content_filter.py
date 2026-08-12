import re

BAD_WORDS = {
    "fuck", "fucking", "fucker", "shit", "shitty", "bitch", "bastard",
    "asshole", "ass", "dick", "piss", "cunt", "cock", "prick", "wanker",
    "twat", "slut", "whore", "retard", "retarded", "faggot", "fag",
    "nigger", "nigga", "spastic", "crap", "bloody", "bugger", "arse",
    "douche", "douchebag", "motherfucker",
}


def find_bad_words(text: str) -> list:
    lower = text.lower()
    return [word for word in BAD_WORDS if re.search(r"\b" + re.escape(word) + r"\b", lower)]
