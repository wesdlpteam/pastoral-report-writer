from word_count import get_range
from style_examples import TUTOR_EXAMPLES

STYLE_GUIDE_NOTES = (
    "Follow Wesley College's editorial style: no contractions (write "
    '"do not" not "don\'t"); write "Year 9" not "Y9"; write "Semester 1" '
    'and "Tutor Group" (two words); use Australian English spelling '
    "(organisation, colour); avoid jargon and keep sentences clear."
)

REPORT_RULES = {
    "tutor": (
        "You are drafting a Wesley College Years 7-12 Tutor Report "
        "comment. The comment must be {low}-{high} words. It must cover "
        "exactly four themes in this order: (1) the student as a person "
        "- character, resilience, personal qualities; (2) the student as "
        "a learner - academic wellbeing and progress; (3) the student as "
        "a participant in the Tutor Group - engagement with the group; "
        "(4) a summarising, strengths-based, future-focused closing "
        "sentence. Write in third person, past tense where natural, and "
        'always refer to the student as "[student name]" - never invent '
        "a real name."
    ),
    "pyp": (
        "You are drafting a Wesley College PYP (Prep-Year 6) Semester "
        "Report personal profile comment. The comment must be "
        "{low}-{high} words. It must cover: personal knowledge of the "
        "student (who they are as a learner and socially), an "
        "Approaches to Learning skill with a specific example, an "
        "achievement or participation example, and clear, manageable "
        "next steps for the student as a learner. Write in third "
        "person, past tense where natural, and always refer to the "
        'student as "[student name]" - never invent a real name.'
    ),
}

ANSWER_LABELS = {
    "tutor": {
        "person": "The student as a person",
        "learner": "The student as a learner",
        "participant": "The student as a Tutor Group participant",
        "summary": "Additional closing notes",
    },
    "pyp": {
        "learner_social": "Who they are as a learner and socially",
        "atl": "Approaches to Learning strength and example",
        "achievement": "Achievement or participation example",
        "next_steps": "Next steps for the student as a learner",
    },
}


def build_system_prompt(report_type: str) -> str:
    low, high = get_range(report_type)
    rules = REPORT_RULES[report_type].format(low=low, high=high)
    parts = [rules, STYLE_GUIDE_NOTES]

    if report_type == "tutor":
        examples_block = "\n\n".join(
            f"Example {i}:\n{example}"
            for i, example in enumerate(TUTOR_EXAMPLES, start=1)
        )
        parts.append(
            "Here are real examples of Wesley's Tutor Report voice and "
            "structure to match in tone (do not copy content, only "
            "style):\n\n" + examples_block
        )

    return "\n\n".join(parts)


def build_user_prompt(report_type: str, answers: dict) -> str:
    labels = ANSWER_LABELS[report_type]
    lines = ["Teacher's notes about the student:"]
    for key, label in labels.items():
        value = str(answers.get(key, "")).strip()
        if value:
            lines.append(f"- {label}: {value}")
    lines.append("\nWrite the report comment now, following the rules above exactly.")
    return "\n".join(lines)
