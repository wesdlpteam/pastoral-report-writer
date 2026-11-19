"""Deterministic Wesley house-style fixes applied to model output.

The prompts ask the model for these rules, but model output is inconsistent
(e.g. "tutor" capitalised in one report and not the next). Every rule that
can be decided mechanically is enforced here as well, so two reports checked
minutes apart come out the same.
"""

import re

# Wesley event, award, ensemble and leadership names. Shared with the prompt
# text in prompts.py so there is one list, not two.
EVENT_AND_AWARD_NAMES = (
    "Middle School Award for Citizenship",
    "Middle School Award for Endeavour",
    "Middle School Award for Special Achievement",
    "Middle School Award for Academic Achievement",
    "Middle School Award for General Excellence",
    "Principal's Honour Roll",
    "Senior School Colours",
    "College Colours",
    "Honour Colours",
    "Stage Band",
    "Concert Band",
    "TJ Band",
    "Wastell Strings",
    "Dolce Canto Choir",
    "Wilkie Orchestra",
    "Autumn Music Concert",
    "BMW Edge Concert",
    "winter music camp",
    "Senior School Prefect",
    "Junior School Leader",
    "Middle School Leader",
    "Middle School Executive",
)

# Other names that must never be wrapped in italics markers.
NEVER_ITALICISE = EVENT_AND_AWARD_NAMES + (
    "Education Outdoors",
    "Tutor Group",
    "Homeroom",
    "House",
)

# Asterisks are only for the titles of published creative works. A phrase
# ending in one of these words is an event, award or group, not a title.
# (A film title ending in "Day" would be stripped too, but an athletics or
# house event is far likelier in a pastoral report.)
_EVENT_SUFFIX_WORDS = frozenset(
    {
        "assembly",
        "award",
        "awards",
        "ball",
        "band",
        "camp",
        "captain",
        "carnival",
        "choir",
        "colours",
        "committee",
        "concert",
        "cup",
        "day",
        "dinner",
        "excursion",
        "executive",
        "expedition",
        "festival",
        "final",
        "finals",
        "group",
        "house",
        "leader",
        "night",
        "orchestra",
        "prefect",
        "program",
        "programme",
        "roll",
        "service",
        "shield",
        "strings",
        "tour",
        "trip",
        "week",
    }
)

_QUOTE_PAIRS = (('"', '"'), ("'", "'"), ("“", "”"), ("‘", "’"))

_ASTERISK_PHRASE = re.compile(r"\*([^*\n]{2,80}?)\*")
# A quoted phrase must open with a capital to be a candidate name, which also
# keeps the pattern off apostrophes in words like "student's".
_QUOTED_PHRASE_PATTERNS = (
    re.compile(r"\"([A-Z][^\"\n]{1,79})\""),
    re.compile(r"“([A-Z][^”\n]{1,79})”"),
    re.compile(r"'([A-Z][^'\n]{1,79})'"),
    re.compile(r"‘([A-Z][^’\n]{1,79})’"),
)
_MULTI_ASTERISK = re.compile(r"\*{2,}")
# "as her tutor", "their tutor" - a title, so it takes a capital. Deliberately
# anchored to a determiner so the verb in "he tutors his peers" is left alone.
_TITLE_TUTOR = re.compile(
    r"\b(as|the|a|an|my|our|your|their|her|his|its)(\s+)(tutors?)\b", re.IGNORECASE
)
_TUTOR_GROUP = re.compile(r"\b(?:tutor|tutorial|tute)(\s+)group\b", re.IGNORECASE)
_SEMESTER_NUMBERED = re.compile(r"\bsemester(\s+)(1|2|one|two)\b")
_SEMESTER_BARE = re.compile(r"\bSemester\b(?!\s+(?:1|2|[Oo]ne|[Tt]wo))")
_SENTENCE_END = re.compile(r"(?:^|[.!?:;…]['\"”’)]?\s+|\n\s*)$")


def _sub_and_record(pattern, replacement, text, reason, changes):
    """Apply a substitution, recording one plain-English change if it bites."""
    new_text, count = pattern.subn(replacement, text)
    if count and new_text != text:
        match = pattern.search(text)
        before = match.group(0)
        after = pattern.sub(replacement, before)
        if before != after:
            changes.append({"original": before, "corrected": after, "reason": reason})
    return new_text


def _is_event_name(phrase):
    """Is this phrase an event, award, ensemble or group name?"""
    bare = phrase.strip().strip("\"'“”‘’")
    if not bare or bare[-1] in ",.!?;:":
        # Punctuation inside the marks means quoted speech, not a name.
        return False
    if any(name.lower() == bare.lower() for name in NEVER_ITALICISE):
        return True
    words = bare.split()
    last_word = re.sub(r"[^A-Za-z]", "", words[-1]).lower() if words else ""
    return last_word in _EVENT_SUFFIX_WORDS


def _strip_event_italics(text, changes):
    """Remove asterisks the model wrapped around an event, award or group."""

    def replace(match):
        phrase = match.group(1)
        return phrase if _is_event_name(phrase) else match.group(0)

    new_text = _ASTERISK_PHRASE.sub(replace, text)
    if new_text != text:
        changes.append(
            {
                "original": "*event or award name*",
                "corrected": "event or award name",
                "reason": (
                    "italics (asterisks) are only for the titles of books, films "
                    "and other published works, not for events, awards or groups"
                ),
            }
        )
    return new_text


def _strip_event_quotes(text, changes):
    """Event names are plain capitalised text, so drop quote marks around them.

    The style guide reserves quotation marks for quoting words or phrases, and
    handles event and award names under capitals instead. Real quoted speech
    carries its punctuation inside the marks, which is how it is told apart.
    """
    original = text

    for pattern in _QUOTED_PHRASE_PATTERNS:

        def replace(match):
            phrase = match.group(1)
            return phrase if _is_event_name(phrase) else match.group(0)

        text = pattern.sub(replace, text)

    if text != original:
        changes.append(
            {
                "original": '"event or award name"',
                "corrected": "event or award name",
                "reason": (
                    "event and award names are written as plain text with capital "
                    "letters, not inside quotation marks"
                ),
            }
        )
    return text


def restore_quoted_phrases(corrected, original):
    """Put back quotation marks the model swapped for asterisks."""
    changes = []
    for match in list(_ASTERISK_PHRASE.finditer(corrected)):
        phrase = match.group(1).strip()
        for open_quote, close_quote in _QUOTE_PAIRS:
            quoted = f"{open_quote}{phrase}{close_quote}"
            if quoted in original:
                corrected = corrected.replace(match.group(0), quoted)
                changes.append(
                    {
                        "original": match.group(0),
                        "corrected": quoted,
                        "reason": "kept your quotation marks instead of italics",
                    }
                )
                break
    return corrected, changes


def _fix_semester(text, changes):
    text = _sub_and_record(
        _SEMESTER_NUMBERED,
        lambda m: f"Semester{m.group(1)}{m.group(2).capitalize()}",
        text,
        'write "Semester 1" and "Semester 2" with a capital S',
        changes,
    )

    source = text

    def lower_bare(match):
        if _SENTENCE_END.search(source[: match.start()]):
            return match.group(0)
        return "semester"

    new_text = _SEMESTER_BARE.sub(lower_bare, source)
    if new_text != source:
        changes.append(
            {
                "original": "Semester",
                "corrected": "semester",
                "reason": 'semester takes a small s unless it is "Semester 1" or "Semester 2"',
            }
        )
    return new_text


def apply_house_style(text, original_text=None):
    """Return (text, changes) with the mechanical house-style rules enforced."""
    if not text:
        return text, []

    changes = []

    text = _sub_and_record(
        _MULTI_ASTERISK, "*", text, "single asterisks mark italics for Word", changes
    )
    text = _strip_event_italics(text, changes)

    # Only phrases that are not event names reach this point, so restoring the
    # teacher's quote marks cannot fight with the rule below.
    if original_text:
        text, quote_changes = restore_quoted_phrases(text, original_text)
        changes.extend(quote_changes)

    text = _strip_event_quotes(text, changes)

    text = _sub_and_record(
        _TUTOR_GROUP,
        lambda m: f"Tutor{m.group(1)}Group",
        text,
        '"Tutor Group" is two words, both capitalised',
        changes,
    )
    text = _sub_and_record(
        _TITLE_TUTOR,
        lambda m: f"{m.group(1)}{m.group(2)}{m.group(3).capitalize()}",
        text,
        "Tutor is a title, so it takes a capital T",
        changes,
    )
    text = _fix_semester(text, changes)

    return text, changes


def split_paragraphs(text):
    """Split on blank lines, keeping only paragraphs with content."""
    parts = re.split(r"\n\s*\n", text.strip())
    return [part.strip() for part in parts if part.strip()]


def join_paragraphs(paragraphs):
    return "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
