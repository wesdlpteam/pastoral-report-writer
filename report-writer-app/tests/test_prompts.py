from prompts import (
    FOLLOWUP_SYSTEM_PROMPT,
    build_followup_user_prompt,
    build_system_prompt,
    build_user_prompt,
)


def test_build_system_prompt_tutor_has_word_range():
    prompt = build_system_prompt("tutor")
    assert "100-150 words" in prompt


def test_build_system_prompt_includes_myp_subject_names():
    prompt = build_system_prompt("tutor")
    assert "Language and Literature" in prompt
    assert "Individuals and Societies" in prompt


def test_build_system_prompt_includes_digital_tool_formatting():
    prompt = build_system_prompt("tutor")
    assert "PowerPoint" in prompt
    assert "Microsoft Word" in prompt
    assert "Paint Shop Pro" in prompt
    assert "generalise it away" in prompt


def test_build_system_prompt_includes_title_italics_convention():
    prompt = build_system_prompt("tutor")
    assert "*To Kill a Mockingbird*" in prompt


def test_build_system_prompt_theme_three_is_tutor_group_participation():
    prompt = build_system_prompt("tutor")
    assert "participant in the Tutor Group" in prompt
    assert "achievements, participation, leadership" not in prompt


def test_build_system_prompt_includes_title_formatting_rules():
    prompt = build_system_prompt("tutor")
    assert "Units 3 & 4" in prompt
    assert "Years 7 & 8" in prompt
    assert "Senior School" in prompt and "not \"SS\"" in prompt
    assert "class members" in prompt
    assert "Principal's Honour Roll" in prompt


def test_build_system_prompt_tutor_includes_examples():
    prompt = build_system_prompt("tutor")
    assert "Example 1:" in prompt


def test_build_system_prompt_always_uses_placeholder_instruction():
    prompt = build_system_prompt("tutor")
    assert "[student name]" in prompt


def test_build_user_prompt_includes_answers():
    answers = {
        "person": "resilient and kind",
        "learner": "improving steadily",
        "participant": "engaged",
        "summary": "",
    }
    prompt = build_user_prompt("tutor", answers)
    assert "resilient and kind" in prompt
    assert "improving steadily" in prompt


def test_build_user_prompt_skips_empty_answers():
    answers = {"person": "", "learner": "improving", "participant": "", "summary": ""}
    prompt = build_user_prompt("tutor", answers)
    assert "The student as a person" not in prompt
    assert "improving" in prompt


def test_system_prompt_forbids_inventing_content_even_for_word_count():
    prompt = build_system_prompt("tutor")
    assert "never" in prompt.lower() or "must" in prompt.lower()
    assert "invent" in prompt.lower()


def test_followup_system_prompt_requires_json_response():
    assert "json" in FOLLOWUP_SYSTEM_PROMPT.lower()
    assert "question" in FOLLOWUP_SYSTEM_PROMPT.lower()


def test_followup_system_prompt_targets_student_not_teacher():
    lower = FOLLOWUP_SYSTEM_PROMPT.lower()
    assert "about the student" in lower
    assert "never" in lower and "teacher" in lower


def test_build_followup_user_prompt_includes_label_and_answer():
    prompt = build_followup_user_prompt("The student as a person", "resilient and kind")
    assert "The student as a person" in prompt
    assert "resilient and kind" in prompt


def test_build_followup_user_prompt_includes_pronouns():
    prompt = build_followup_user_prompt("The student as a person", "resilient", pronouns="she/her")
    assert "she/her" in prompt
