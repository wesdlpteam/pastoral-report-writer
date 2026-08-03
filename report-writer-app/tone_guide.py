import re

TONE_SOFTEN = {
    "rude": "still developing respectful communication",
    "disrespectful": "still developing respectful communication",
    "lazy": "still building consistency and motivation",
    "unmotivated": "still building consistency and motivation",
    "disruptive": "finding it challenging to meet classroom expectations",
    "naughty": "working on following expectations",
    "aggressive": "developing ways to manage frustration",
    "selfish": "developing consideration for others",
    "messy": "developing attention to detail",
    "careless": "developing attention to detail",
    "weak": "an area for growth",
    "immature": "developing maturity",
    "dishonest": "working on honesty and trust",
    "liar": "working on honesty and trust",
    "failed": "did not yet meet the expected standard",
    "failure": "did not yet meet the expected standard",
    "stupid": "still developing understanding",
    "dumb": "still developing understanding",
    "annoying": "still learning to read social cues",
    "irritating": "still learning to read social cues",
    "difficult": "still developing self-regulation",
}

TONE_GUARD = (
    "TONE: If the teacher's notes below contain blunt or negative "
    "character-judgment words (for example: rude, lazy, disruptive, "
    "naughty, aggressive, selfish, messy, careless, weak, immature, "
    "dishonest, failed, stupid, annoying, difficult), do NOT repeat "
    "those words verbatim in the report. Reframe them into "
    "constructive, strengths-based, future-focused language that "
    "still reflects the teacher's underlying observation, without "
    "sounding confrontational."
)


def find_tempered_words(answers: dict) -> list:
    text = " ".join(str(v) for v in answers.values()).lower()
    return [
        word
        for word in TONE_SOFTEN
        if re.search(r"\b" + re.escape(word) + r"\b", text)
    ]
