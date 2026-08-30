from word_count import get_range
from style_examples import TUTOR_EXAMPLES
from tone_guide import TONE_GUARD

STYLE_GUIDE_NOTES = (
    "Follow Wesley College's editorial style: no contractions (write "
    '"do not" not "don\'t"); write "Year 9" not "Y9"; write "Semester 1" '
    'and "Tutor Group" (two words, not class or tutorial group); use '
    "Australian English spelling (organisation, colour); avoid jargon "
    "and keep sentences clear; capitalise House when referring to the "
    "school house system. Use correct full MYP subject names, not "
    'abbreviations or informal names, e.g. "Language and Literature" '
    'not "English", "Individuals and Societies" not "Humanities", '
    '"Physical and Health Education" not "PE". If the teacher names a '
    "specific digital tool, program, or app, keep it in the draft "
    "exactly as mentioned - never generalise it away into something "
    'vague like "a computer program" - and use its correct official '
    'capitalisation, for example: "PowerPoint" (one word, capital P), '
    '"Microsoft Word" (two words, capital M and capital W), "Paint '
    'Shop Pro" (three words, each capitalised). Wrap the titles of '
    "novels, films, or other creative works in asterisks so they can "
    "be italicised after pasting into Word, e.g. *To Kill a "
    "Mockingbird*. Title formatting: write \"Units 3 & 4\" not \"Unit "
    '3/4"; "Years 7 & 8" not "Year 7 & 8"; "Year 10" not "Y10"; '
    '"Senior School" not "SS"; "Middle School" not "MS"; write '
    '"Homeroom" as one word and "Tutor Group" as two words; use '
    '"peers", "class members", or "others" instead of "classmates". '
    "If the teacher mentions a specific award, ensemble, event, or "
    "leadership title, keep it exactly as named and capitalised, for "
    "example: Middle School Award for Citizenship / Endeavour / "
    "Special Achievement; Middle School Award for Academic "
    "Achievement or General Excellence; Principal's Honour Roll; "
    "Senior School Colours, College Colours, or Honour Colours; Stage "
    "Band, Concert Band, TJ Band, Wastell Strings, Dolce Canto Choir, "
    "Wilkie Orchestra; Autumn Music Concert, BMW Edge Concert, winter "
    "music camp; Senior School Prefect, Junior School Leader, Middle "
    "School Leader, Middle School Executive. For a theatre production, "
    'use the actual title of the production rather than "Theatre".'
)

WESLEY_GRAMMAR_STYLE_NOTES = (
    "Further Wesley College style rules. Capitalisation: \"Term 1\" "
    "(capital T, number 1); subject and department names (Drama, "
    "Music, French, Mathematics) take a capital, but general "
    "principles do not, e.g. \"mathematical principles\" or "
    "\"linguistic difficulties\" stay lowercase; titles like Homeroom "
    "Teacher, Tutor, and Principal begin with a capital letter. "
    "Sports teams: capitalise properly, e.g. \"First VI Volleyball\", "
    "\"Second XI Soccer\" - never use \"1st\" etc. except for a "
    "result like \"1st place\"; the name of a sport itself stays "
    "lower case, e.g. \"Jane represented Adamson House in volleyball "
    "and tennis.\" Do not hyphenate: cocurricular, onstage, "
    "coeducation, coordinate, coordinator, cooperate, email. Write as "
    "one word: somewhat, overcome, website, handwriting. Write as two "
    "words: schoolwork, homework."
    ' Spelling: "practise" is the verb, "practice" is the noun (e.g. '
    '"she should practise her writing" but "it is common practice"); '
    '"effect" is usually the noun and "affect" the verb; "advice" is '
    'the noun and "advise" the verb; "complimentary" means flattering, '
    '"complementary" means things that go together; "conscientious" '
    "means hard-working. If referencing an IB assessment criterion, "
    'capitalise it, e.g. "Criterion A", and only use "criteria" for '
    "two or more."
    " Punctuation: no space before a comma, full stop, or other "
    "punctuation mark; no full stop after Mr, Ms, or Mrs. For "
    "possessives, a singular owner takes 's (a boy's hat) and a "
    "plural owner takes s' (two boys' hats); a name ending in s still "
    "takes 's (James's work). When \"however\" joins two related "
    "sentences it is preceded by a semicolon (or comma) and followed "
    'by a comma, e.g. "...is strong; however, her presentation needs '
    'work." At the start of a sentence, "however" is followed by a '
    "comma."
    " Acronyms do not need full stops between letters (VCE, MYP). "
    "Spell out a term in full the first time it is used, with the "
    "acronym in brackets immediately after, then use the acronym for "
    "the rest of the report - unless the acronym is already extremely "
    "well known (e.g. VCE) or its meaning is already obvious from the "
    "subject title given, in which case the full form is not needed."
    " Every sentence needs a verb, and the verb must agree with its "
    "subject in number. Make sure any participle (a describing word "
    "ending in -ing) clearly refers to the person doing the action, "
    "not to something else in the sentence."
    ' Useful synonyms for variety: instead of "developing" try '
    '"increasing" or "broadening"; instead of "however" try "although" '
    'or "whilst"; instead of "understands" try "comprehends" or '
    '"grasps"; instead of "shows" try "portrays", "demonstrates", or '
    '"expresses"; instead of "excellent" try "broad", '
    '"well-developed", or "advanced"; instead of "good" try "sound", '
    '"satisfactory", or "fair".'
)

HALLUCINATION_GUARD = (
    "CRITICAL: Use ONLY the information the teacher provided in their "
    "answers below. You MAY elaborate on, rephrase, add context to, or "
    "draw out the natural implications of what the teacher wrote, to "
    "help reach the required word count. You must NEVER add a fact, "
    "example, achievement, activity, or detail the teacher did not "
    "mention - reaching the word count is never a reason to invent "
    "content. Do not copy phrases from the examples provided. Instead, "
    "reshape the teacher's own language into Wesley's voice. If a "
    "teacher answer is empty or missing, simply omit that topic from "
    "the report rather than inventing details. NAMES: use only the "
    "student name(s) given in the context block below, formatted "
    "exactly as instructed in the name formatting rule - never invent "
    "a different name or a nickname you were not given."
)

NAME_FORMATTING_GUIDE = (
    "NAME FORMATTING: the context block below gives you the student's "
    "formal name, and possibly a preferred name. If a preferred name "
    "is given, refer to the student by their formal name followed by "
    "the preferred name in brackets the FIRST time they are mentioned, "
    "e.g. \"Orson (Sonny) has completed a sound term's work.\" - then "
    "use ONLY the preferred name for every mention after that, e.g. "
    '"Sonny is a friendly and polite individual." Do not swap back '
    "and forth between the formal and preferred name. If no preferred "
    "name is given, use the formal name throughout, exactly as given."
)

MYP_LEARNER_PROFILE_NOTE = (
    "MYP NOTE: This student is in Years 7-10 (MYP). When appropriate, "
    "use the IB Learner Profile attributes (Inquirer, Knowledgeable, "
    "Thinker, Communicator, Principled, Open-minded, Caring, "
    "Risk-taker, Balanced, Reflective) and Approaches to Learning "
    "(ATL) skill categories (Thinking, Communication, Social, "
    "Self-management, Research) as ideas or language to help write "
    "the student-as-a-learner sentence."
)

CONTEXT_REQUIREMENT = (
    "REQUIRED: You MUST explicitly mention the student's Tutor Group and/or House "
    "at least once in the report. Reference it naturally in relevant sections: "
    "'Within [Tutor Group]', 'House [name]', '[Tutor Group] community', "
    "'House [name] events', etc. This context must appear in the output."
)

REPORT_RULES = {
    "tutor": (
        "You are drafting a Wesley College Years 7-12 Tutor Report "
        "comment. The comment must be {low}-{high} words. It must cover "
        "exactly four themes in this order: (1) the student as a person "
        "- character, resilience, personal qualities (consider ROAR values: "
        "Respect, Opportunity, Achievement, Resilience); (2) the student as "
        "a learner - academic wellbeing, progress, and approach to learning; "
        "(3) the student as a participant in the Tutor Group - their "
        "engagement with, and contribution to, Tutor Group discussions "
        "and activities, and how they support their peers; (4) a "
        "summarising comment - this may reflect on the student's "
        "chosen development stage or a Student Reflection Rubric "
        "element, other observations you have made as their Tutor, or "
        "how they have engaged with peers, Education Outdoors, or "
        "leadership positions this term. Use pronouns {pronouns} "
        "throughout. Write in third person, past tense where natural, and "
        "always refer to the student by name, following the name "
        "formatting rule below - never invent a name."
    ),
}

ANSWER_LABELS = {
    "tutor": {
        "person": "The student as a person (character, ROAR values, peer interaction)",
        "learner": "The student as a learner (academic progress, approach to learning)",
        "participant": "The student as a participant in the Tutor Group (engagement, contribution to discussions/activities, peer support)",
        "summary": "A summarising comment (development stage, Reflection Rubric element, peer engagement, leadership, Education Outdoors, or other observations)",
    },
}


def build_system_prompt(report_type: str, pronouns: str = "they/them", year_level: str = None) -> str:
    low, high = get_range(report_type)
    rules = REPORT_RULES[report_type].format(low=low, high=high, pronouns=pronouns)
    parts = [
        HALLUCINATION_GUARD,
        NAME_FORMATTING_GUIDE,
        CONTEXT_REQUIREMENT,
        rules,
        STYLE_GUIDE_NOTES,
        WESLEY_GRAMMAR_STYLE_NOTES,
        TONE_GUARD,
    ]

    if str(year_level) in {"7", "8", "9", "10"}:
        parts.append(MYP_LEARNER_PROFILE_NOTE)

    if report_type == "tutor":
        examples_block = "\n\n".join(
            f"Example {i}:\n{example}"
            for i, example in enumerate(TUTOR_EXAMPLES, start=1)
        )
        parts.append(
            "Here are real examples of Wesley's Tutor Report voice and "
            "structure to match in tone (do not copy content or phrases, "
            "only match the style and flow):\n\n" + examples_block
        )

    return "\n\n".join(parts)


def build_user_prompt(
    report_type: str,
    answers: dict,
    pronouns: str = "they/them",
    tutor_group: str = None,
    house: str = None,
    adjust: str = None,
    formal_name: str = None,
    preferred_name: str = None,
) -> str:
    labels = ANSWER_LABELS[report_type]
    lines = [f"Teacher's notes about the student (using pronouns {pronouns}):"]
    lines.append("")
    lines.append("*** STUDENT NAME (use exactly as instructed above) ***")
    lines.append(f"Formal name: {formal_name or '(not provided)'}")
    lines.append(f"Preferred name: {preferred_name or '(none given)'}")
    lines.append("*** END STUDENT NAME ***")
    lines.append("")
    lines.append("*** CONTEXT (MUST REFERENCE IN REPORT) ***")
    if tutor_group and tutor_group != "(not specified)":
        lines.append(f"Tutor Group: {tutor_group}")
    else:
        lines.append("Tutor Group: (not specified)")
    if house and house != "(not specified)":
        lines.append(f"House: {house}")
    else:
        lines.append("House: (not specified)")
    lines.append("*** END CONTEXT ***")
    lines.append("")
    for key, label in labels.items():
        value = str(answers.get(key, "")).strip()
        if value:
            lines.append(f"- {label}: {value}")
        else:
            lines.append(f"- {label}: (not provided)")
    lines.append("\nWrite the report comment now, following the rules above exactly.")

    if adjust == "shorter":
        lines.append(
            "\nIMPORTANT: Your previous draft was too long. Write this "
            "version noticeably shorter while keeping the same meaning "
            "and covering all required themes."
        )
    elif adjust == "longer":
        lines.append(
            "\nIMPORTANT: Your previous draft was too short. Write this "
            "version noticeably longer while keeping the same meaning "
            "and covering all required themes. Reach the extra length "
            "ONLY by more fully elaborating on, explaining, or adding "
            "natural context to the detail the teacher already gave you "
            "above - never by inventing a new fact, example, or detail "
            "they did not mention."
        )

    return "\n".join(lines)


FOLLOWUP_SYSTEM_PROMPT = (
    "You are helping a TEACHER add more real detail to a short note "
    "they wrote ABOUT A STUDENT, before it becomes part of a school "
    "report comment. You know nothing about the student beyond what "
    "the teacher typed below - never invent or assume anything about "
    "them. CRITICAL: the follow-up question is addressed TO the "
    "teacher but is always ABOUT THE STUDENT - it asks the teacher to "
    "recall more about the student's behaviour, skills, or experiences. "
    "It must NEVER ask about the teacher themself (never things like "
    "'how have you been a learner' or 'what did you do'). Use the "
    "student's pronouns given below when referring to the student. "
    "For example, if the teacher's note was about the student's "
    "learning, a good follow-up is 'Can you give a specific example "
    "of when {they} showed this?', not a question about the teacher. "
    "Based on the question the teacher was originally asked and what "
    "they wrote so far, write ONE short, specific follow-up question "
    "that would help the teacher recall and add more concrete detail "
    "about the STUDENT (not generic). Also give 2-3 short idea-prompts, "
    "a few words each, not full sentences, suggesting the kind of "
    "thing about the student they could mention - these are prompts "
    "to spark the teacher's memory, not text for them to copy. "
    'Respond with JSON only, in this exact shape: {"question": "...", '
    '"suggestions": ["...", "...", "..."]}'
)


def build_followup_user_prompt(question_label: str, answer: str, pronouns: str = "they/them") -> str:
    return (
        f"The student's pronouns are: {pronouns}\n"
        f"The teacher was originally asked, about the student: {question_label}\n"
        f"The teacher wrote about the student: {answer}"
    )
