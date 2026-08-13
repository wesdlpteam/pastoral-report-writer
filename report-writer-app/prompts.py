from word_count import get_range
from style_examples import TUTOR_EXAMPLES
from tone_guide import TONE_GUARD

STYLE_GUIDE_NOTES = (
    "Follow Wesley College's editorial style: no contractions (write "
    '"do not" not "don\'t"); write "Year 9" not "Y9"; write "Semester 1" '
    'and "Tutor Group" (two words, not class or tutorial group); use '
    "Australian English spelling (organisation, colour); avoid jargon "
    "and keep sentences clear; capitalise House when referring to the "
    "school house system."
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
    "the report rather than inventing details."
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
        "(3) achievements, participation, leadership, or House/cocurricular "
        "involvement this term; (4) a forward-focused closing about their "
        "goals or next steps for development. Use pronouns {pronouns} "
        "throughout. Write in third person, past tense where natural, and "
        'always refer to the student as "[student name]" - never invent '
        "a real name."
    ),
    "pyp": (
        "You are drafting a Wesley College PYP (Prep-Year 6) Semester "
        "Report personal profile comment. The comment must be "
        "{low}-{high} words. It must cover: personal knowledge of the "
        "student (who they are as a learner and socially; consider IB "
        "Learner Profile attributes: Inquirer, Knowledgeable, Thinker, "
        "Communicator, Principled, Open-minded, Caring, Risk-taker, "
        "Balanced, Reflective), an Approaches to Learning skill with a "
        "specific example, an achievement or participation example, and "
        "clear, manageable next steps for the student as a learner with "
        "how school and parents can support. Use pronouns {pronouns} "
        "throughout. Write in third person, past tense where natural, and "
        'always refer to the student as "[student name]" - never invent '
        "a real name."
    ),
}

ANSWER_LABELS = {
    "tutor": {
        "person": "The student as a person (character, ROAR values, peer interaction)",
        "learner": "The student as a learner (academic progress, approach to learning)",
        "achievement": "Achievements, participation, or leadership this term",
        "next_steps": "Student's goals or next focus area",
    },
    "pyp": {
        "learner_social": "Who they are as a learner and socially (Learner Profile)",
        "atl": "Approaches to Learning strength with example",
        "achievement": "Achievement or participation example",
        "next_steps": "Next steps for learning (how school and parents can support)",
    },
}


def build_system_prompt(report_type: str, pronouns: str = "they/them") -> str:
    low, high = get_range(report_type)
    rules = REPORT_RULES[report_type].format(low=low, high=high, pronouns=pronouns)
    parts = [HALLUCINATION_GUARD, CONTEXT_REQUIREMENT, rules, STYLE_GUIDE_NOTES, TONE_GUARD]

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
) -> str:
    labels = ANSWER_LABELS[report_type]
    lines = [f"Teacher's notes about the student (using pronouns {pronouns}):"]
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
    "You are helping a teacher add more real detail to a short note "
    "about a student, before it becomes part of a school report "
    "comment. You know nothing about the student beyond what they "
    "type below - never invent or assume anything about them. Based "
    "on the question they were asked and what they wrote so far, "
    "write ONE short, specific follow-up question that would help "
    "them recall and add more concrete detail (not generic). Also "
    "give 2-3 short idea-prompts, a few words each, not full "
    "sentences, suggesting the kind of thing they could mention - "
    "these are prompts to spark their memory, not text for them to "
    'copy. Respond with JSON only, in this exact shape: {"question": '
    '"...", "suggestions": ["...", "...", "..."]}'
)


def build_followup_user_prompt(question_label: str, answer: str) -> str:
    return f"The teacher was asked: {question_label}\nThey wrote: {answer}"
